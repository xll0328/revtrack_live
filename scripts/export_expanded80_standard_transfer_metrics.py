from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from export_expanded80_assistant_adjudication import DEFAULT_PREDICTIONS, load_jsonl, parse_named_path
from revtrack.io import load_predictions, save_examples
from revtrack.metrics import evaluate_predictions
from revtrack.schema import LABELS, IssueExample


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export standard transfer metrics for the user-confirmed ICLR 2025 expanded80 validation sheet."
    )
    parser.add_argument(
        "--human-sheet",
        default=str(ROOT / "experiments/day1/iclr2025_expanded80_human_validation_v1_blind.tsv"),
    )
    parser.add_argument(
        "--candidates",
        default=str(ROOT / "data/processed/iclr2025_expanded80_issue_candidates.jsonl"),
    )
    parser.add_argument(
        "--output-jsonl",
        default=str(ROOT / "data/processed/iclr2025_expanded80_standard_validation_v1.jsonl"),
    )
    parser.add_argument(
        "--metrics-csv",
        default=str(ROOT / "outputs/day1/paper_assets/iclr2025_expanded80_standard_transfer_metrics.csv"),
    )
    parser.add_argument(
        "--metrics-md",
        default=str(ROOT / "outputs/day1/paper_assets/iclr2025_expanded80_standard_transfer_metrics.md"),
    )
    parser.add_argument(
        "--details-dir",
        default=str(ROOT / "outputs/day1/iclr2025_expanded80_standard_transfer"),
    )
    parser.add_argument(
        "--manifest",
        default=str(ROOT / "outputs/day1/iclr2025_expanded80_standard_validation_v1_manifest.json"),
    )
    parser.add_argument("--prediction", action="append", type=parse_named_path, default=[])
    return parser.parse_args()


def load_tsv(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def normalize_label(value: str | None) -> str:
    return (value or "").strip().lower()


def by_issue_id(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(row.get("issue_id", "")): row for row in rows if row.get("issue_id")}


def examples_from_human_rows(
    *,
    human_rows: list[dict[str, str]],
    candidate_rows: list[dict[str, Any]],
) -> list[IssueExample]:
    candidates = by_issue_id(candidate_rows)
    examples: list[IssueExample] = []
    invalid: list[str] = []
    missing_evidence: list[str] = []
    for row in human_rows:
        issue_id = row["issue_id"]
        label = normalize_label(row.get("human_label"))
        if label not in LABELS:
            invalid.append(issue_id)
            continue
        if not row.get("evidence_span", "").strip():
            missing_evidence.append(issue_id)
        candidate = candidates.get(issue_id, {})
        examples.append(
            IssueExample(
                id=issue_id,
                source=str(candidate.get("source", "openreview")),
                venue=str(candidate.get("venue", "")),
                paper_title=row.get("paper_title", ""),
                abstract=str(candidate.get("abstract", "")),
                review_text=row.get("review_excerpt", ""),
                author_response=row.get("aligned_response_excerpt", ""),
                revision_summary=row.get("revision_summary", ""),
                gold_label=label,
                metadata={
                    "submission_id": str(candidate.get("submission_id", "")),
                    "forum": str(candidate.get("forum", "")),
                    "review_id": str(candidate.get("review_id", "")),
                    "evidence_span": row.get("evidence_span", ""),
                    "human_confidence": row.get("human_confidence", ""),
                    "notes": row.get("notes", ""),
                    "provenance": "user_confirmed_standard_expanded80_validation",
                },
            )
        )
    if invalid:
        raise ValueError(f"invalid or missing human_label rows: {invalid[:10]}")
    if missing_evidence:
        raise ValueError(f"missing evidence_span rows: {missing_evidence[:10]}")
    return examples


def write_metrics(
    *,
    examples: list[IssueExample],
    predictions: dict[str, Path],
    metrics_csv: str | Path,
    details_dir: str | Path,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    details_root = Path(details_dir)
    details_root.mkdir(parents=True, exist_ok=True)
    for name, path in sorted(predictions.items()):
        summary, details = evaluate_predictions(examples, load_predictions(path))
        (details_root / f"{name}_metrics.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        (details_root / f"{name}_details.json").write_text(
            json.dumps(details, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        per_label = summary["per_label"]
        rows.append(
            {
                "model_key": name,
                "rows": int(summary["num_examples"]),
                "accuracy": summary["accuracy"],
                "macro_f1": summary["macro_f1"],
                "fixed_f1": per_label["fixed"]["f1"],
                "partially_fixed_f1": per_label["partially_fixed"]["f1"],
                "unresolved_f1": per_label["unresolved"]["f1"],
                "regressed_f1": per_label["regressed"]["f1"],
                "status": "standard_user_confirmed_validation",
            }
        )

    output = Path(metrics_csv)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "model_key",
                "rows",
                "accuracy",
                "macro_f1",
                "fixed_f1",
                "partially_fixed_f1",
                "unresolved_f1",
                "regressed_f1",
                "status",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)
    return rows


def write_metrics_markdown(path: str | Path, rows: list[dict[str, Any]]) -> None:
    lines = [
        "# ICLR 2025 Expanded80 Standard Transfer Metrics",
        "",
        "These metrics use the user-confirmed standard expanded80 validation sheet. This is single-pass standard validation, not an independent two-annotator IAA result.",
        "",
        "| model | rows | accuracy | macro-F1 | fixed F1 | partial F1 | unresolved F1 | regressed F1 |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in sorted(rows, key=lambda item: float(item["macro_f1"]), reverse=True):
        lines.append(
            "| "
            + " | ".join(
                [
                    str(row["model_key"]),
                    str(row["rows"]),
                    f"{float(row['accuracy']):.3f}",
                    f"{float(row['macro_f1']):.3f}",
                    f"{float(row['fixed_f1']):.3f}",
                    f"{float(row['partially_fixed_f1']):.3f}",
                    f"{float(row['unresolved_f1']):.3f}",
                    f"{float(row['regressed_f1']):.3f}",
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Reporting Boundary",
            "",
            "- Report as standard single-user validation, not as inter-annotator agreement.",
            "- The sample is a disagreement-focused standard single-user active frontier and should be described as hardened cross-year frontier evidence.",
            "- Keep the 21-row ICLR 2025 repro result as a separate stress sample.",
        ]
    )
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_manifest(
    *,
    path: str | Path,
    examples: list[IssueExample],
    metrics_rows: list[dict[str, Any]],
    output_jsonl: str | Path,
    metrics_csv: str | Path,
    metrics_md: str | Path,
) -> None:
    label_counts = Counter(example.gold_label for example in examples)
    best = max(metrics_rows, key=lambda row: (float(row["macro_f1"]), float(row["accuracy"]))) if metrics_rows else {}
    payload = {
        "status": "standard_user_confirmed_validation",
        "human_validation_status": "standard_single_user_confirmed",
        "rows": len(examples),
        "label_distribution": dict(sorted(label_counts.items())),
        "best_model": best,
        "output_jsonl": str(output_jsonl),
        "metrics_csv": str(metrics_csv),
        "metrics_md": str(metrics_md),
        "claim_boundary": "Not an independent two-annotator IAA result; disagreement-focused standard single-user active-frontier cross-year validation.",
    }
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    predictions = dict(DEFAULT_PREDICTIONS)
    predictions.update(dict(args.prediction))
    examples = examples_from_human_rows(
        human_rows=load_tsv(args.human_sheet),
        candidate_rows=load_jsonl(args.candidates),
    )
    save_examples(args.output_jsonl, examples)
    metrics_rows = write_metrics(
        examples=examples,
        predictions=predictions,
        metrics_csv=args.metrics_csv,
        details_dir=args.details_dir,
    )
    write_metrics_markdown(args.metrics_md, metrics_rows)
    write_manifest(
        path=args.manifest,
        examples=examples,
        metrics_rows=metrics_rows,
        output_jsonl=args.output_jsonl,
        metrics_csv=args.metrics_csv,
        metrics_md=args.metrics_md,
    )
    print(f"Wrote {len(examples)} standard expanded80 examples to {args.output_jsonl}")
    print(f"Wrote standard expanded80 transfer metrics to {args.metrics_csv}")


if __name__ == "__main__":
    main()
