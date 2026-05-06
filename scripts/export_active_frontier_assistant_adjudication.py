from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from revtrack.io import load_predictions, save_examples
from revtrack.metrics import evaluate_predictions
from revtrack.schema import LABELS, IssueExample


MODEL_FIELDS = [
    "tfidf_label",
    "modernbert_label",
    "mpnet_label",
    "issue_ledger_label",
    "structured_label",
]


def parse_named_path(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("Expected NAME=PATH")
    name, path = value.split("=", 1)
    name = name.strip()
    if not name:
        raise argparse.ArgumentTypeError("Prediction name cannot be empty")
    return name, Path(path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export a provisional assistant adjudication draft for an active frontier.")
    parser.add_argument("--dataset-name", required=True)
    parser.add_argument("--frontier-sheet", required=True)
    parser.add_argument("--key", required=True)
    parser.add_argument("--candidates", required=True)
    parser.add_argument("--output-tsv", required=True)
    parser.add_argument("--output-jsonl", required=True)
    parser.add_argument("--metrics-csv", required=True)
    parser.add_argument("--metrics-md", required=True)
    parser.add_argument("--details-dir", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--prediction", action="append", type=parse_named_path, default=[])
    return parser.parse_args()


def compact(value: str | None) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def clip(value: str | None, max_chars: int = 420) -> str:
    text = compact(value)
    if len(text) <= max_chars:
        return text
    clipped = text[:max_chars].rsplit(" ", 1)[0]
    return f"{clipped}..."


def load_tsv(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def by_issue_id(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(row.get("issue_id", "")): row for row in rows if row.get("issue_id")}


def normalize_label(value: str | None) -> str:
    return compact(value).lower()


def evidence_sources(row: dict[str, str], label: str) -> list[tuple[str, str]]:
    if label == "fixed":
        return [
            ("aligned_response_excerpt", row.get("aligned_response_excerpt", "")),
            ("revision_summary", row.get("revision_summary", "")),
            ("top_response_excerpt", row.get("top_response_excerpt", "")),
            ("review_excerpt", row.get("review_excerpt", "")),
        ]
    if label == "partially_fixed":
        return [
            ("revision_summary", row.get("revision_summary", "")),
            ("aligned_response_excerpt", row.get("aligned_response_excerpt", "")),
            ("top_response_excerpt", row.get("top_response_excerpt", "")),
            ("review_excerpt", row.get("review_excerpt", "")),
        ]
    if label == "regressed":
        return [
            ("revision_summary", row.get("revision_summary", "")),
            ("aligned_response_excerpt", row.get("aligned_response_excerpt", "")),
            ("top_response_excerpt", row.get("top_response_excerpt", "")),
            ("review_excerpt", row.get("review_excerpt", "")),
        ]
    return [
        ("aligned_response_excerpt", row.get("aligned_response_excerpt", "")),
        ("revision_summary", row.get("revision_summary", "")),
        ("top_response_excerpt", row.get("top_response_excerpt", "")),
        ("review_excerpt", row.get("review_excerpt", "")),
    ]


def choose_evidence(row: dict[str, str], label: str) -> tuple[str, str]:
    for source, value in evidence_sources(row, label):
        text = clip(value)
        if text:
            return source, text
    return "", ""


def model_label_snapshot(row: dict[str, str]) -> dict[str, str]:
    return {
        field.removesuffix("_label"): normalize_label(row.get(field))
        for field in MODEL_FIELDS
        if normalize_label(row.get(field))
    }


def confidence_from_models(label: str, model_labels: dict[str, str], evidence: str) -> str:
    matching = sum(1 for value in model_labels.values() if value == label)
    if matching >= 3 and evidence:
        return "medium"
    if matching >= 2 and evidence:
        return "low_medium"
    return "low"


def build_adjudication_rows(
    *,
    dataset_name: str,
    frontier_rows: list[dict[str, str]],
    key_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    frontier_by_id = by_issue_id(frontier_rows)
    rows: list[dict[str, str]] = []
    for key in key_rows:
        issue_id = key["issue_id"]
        source = frontier_by_id[issue_id]
        label = normalize_label(key.get("assistant_label") or source.get("suggested_label"))
        if label not in LABELS:
            raise ValueError(f"Invalid assistant label for {issue_id}: {label}")
        evidence_source, evidence_span = choose_evidence(source, label)
        model_labels = model_label_snapshot(source)
        note_payload = {
            "dataset": dataset_name,
            "provenance": "provisional_assistant_adjudication_from_active_frontier",
            "not_human_validated": True,
            "suggested_label": normalize_label(source.get("suggested_label")),
            "model_labels": model_labels,
            "audit_bucket": key.get("audit_bucket", ""),
            "evidence_source": evidence_source,
        }
        rows.append(
            {
                "issue_id": issue_id,
                "paper_title": source.get("paper_title", ""),
                "review_rating": source.get("review_rating", ""),
                "review_confidence": source.get("review_confidence", ""),
                "assistant_label": label,
                "assistant_confidence": confidence_from_models(label, model_labels, evidence_span),
                "evidence_source": evidence_source,
                "evidence_span": evidence_span,
                "notes": json.dumps(note_payload, ensure_ascii=False, sort_keys=True),
                "provenance": "provisional_assistant_adjudication_not_human_validation",
                "suggested_label": source.get("suggested_label", ""),
                **{field: source.get(field, "") for field in MODEL_FIELDS},
                "review_excerpt": source.get("review_excerpt", ""),
                "top_response_excerpt": source.get("top_response_excerpt", ""),
                "aligned_response_excerpt": source.get("aligned_response_excerpt", ""),
                "revision_summary": source.get("revision_summary", ""),
            }
        )
    return rows


def examples_from_rows(
    *,
    adjudication_rows: list[dict[str, str]],
    candidate_rows: list[dict[str, Any]],
) -> list[IssueExample]:
    candidates = by_issue_id(candidate_rows)
    examples: list[IssueExample] = []
    for row in adjudication_rows:
        issue_id = row["issue_id"]
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
                gold_label=row.get("assistant_label", ""),
                metadata={
                    "submission_id": str(candidate.get("submission_id", "")),
                    "forum": str(candidate.get("forum", "")),
                    "review_id": str(candidate.get("review_id", "")),
                    "evidence_span": row.get("evidence_span", ""),
                    "evidence_source": row.get("evidence_source", ""),
                    "provenance": row.get("provenance", ""),
                    "notes": row.get("notes", ""),
                },
            )
        )
    return examples


def write_tsv(path: str | Path, rows: list[dict[str, str]]) -> None:
    fields = [
        "issue_id",
        "paper_title",
        "review_rating",
        "review_confidence",
        "assistant_label",
        "assistant_confidence",
        "evidence_source",
        "evidence_span",
        "notes",
        "provenance",
        "suggested_label",
        *MODEL_FIELDS,
        "review_excerpt",
        "top_response_excerpt",
        "aligned_response_excerpt",
        "revision_summary",
    ]
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def write_metrics(
    *,
    examples: list[IssueExample],
    predictions: dict[str, Path],
    metrics_csv: str | Path,
    details_dir: str | Path,
) -> list[dict[str, Any]]:
    output_rows: list[dict[str, Any]] = []
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
        output_rows.append(
            {
                "model_key": name,
                "rows": int(summary["num_examples"]),
                "accuracy": summary["accuracy"],
                "macro_f1": summary["macro_f1"],
                "fixed_f1": per_label["fixed"]["f1"],
                "partially_fixed_f1": per_label["partially_fixed"]["f1"],
                "unresolved_f1": per_label["unresolved"]["f1"],
                "regressed_f1": per_label["regressed"]["f1"],
                "status": "provisional_assistant_adjudication",
            }
        )

    metrics_path = Path(metrics_csv)
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    with metrics_path.open("w", encoding="utf-8", newline="") as handle:
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
        writer.writerows(output_rows)
    return output_rows


def write_metrics_markdown(path: str | Path, dataset_name: str, rows: list[dict[str, Any]]) -> None:
    lines = [
        f"# {dataset_name} Provisional Transfer Metrics",
        "",
        "These metrics use provisional assistant-adjudicated labels from an active frontier. They are useful for internal triage and hypothesis generation, but they are not standard human-validation results and must not be reported as benchmark transfer performance.",
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
            "## Interpretation Boundary",
            "",
            "- The label distribution is frontier-biased and risk-heavy.",
            "- The result should guide adjudication and error analysis, not final claims.",
            "- The next publishable step is standard labeling of the blind validation sheet.",
        ]
    )
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_manifest(
    *,
    path: str | Path,
    dataset_name: str,
    adjudication_rows: list[dict[str, str]],
    metrics_rows: list[dict[str, Any]],
    output_tsv: str | Path,
    output_jsonl: str | Path,
    metrics_csv: str | Path,
    metrics_md: str | Path,
) -> None:
    label_counts = Counter(row["assistant_label"] for row in adjudication_rows)
    missing_evidence = [row["issue_id"] for row in adjudication_rows if not row.get("evidence_span")]
    best = max(metrics_rows, key=lambda row: (float(row["macro_f1"]), float(row["accuracy"]))) if metrics_rows else {}
    payload = {
        "dataset_name": dataset_name,
        "status": "provisional_assistant_adjudication",
        "human_validation_status": "not_human_validated",
        "rows": len(adjudication_rows),
        "label_distribution": dict(sorted(label_counts.items())),
        "missing_evidence_rows": missing_evidence,
        "best_provisional_model": best,
        "output_tsv": str(output_tsv),
        "output_jsonl": str(output_jsonl),
        "metrics_csv": str(metrics_csv),
        "metrics_md": str(metrics_md),
        "claim_boundary": (
            "Use only as provisional assistant-adjudicated active-frontier analysis; "
            "do not report as standard human validation, IAA, or benchmark transfer performance."
        ),
    }
    manifest_path = Path(path)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    predictions = dict(args.prediction)
    adjudication_rows = build_adjudication_rows(
        dataset_name=args.dataset_name,
        frontier_rows=load_tsv(args.frontier_sheet),
        key_rows=load_tsv(args.key),
    )
    examples = examples_from_rows(
        adjudication_rows=adjudication_rows,
        candidate_rows=load_jsonl(args.candidates),
    )

    write_tsv(args.output_tsv, adjudication_rows)
    save_examples(args.output_jsonl, examples)
    metrics_rows = write_metrics(
        examples=examples,
        predictions=predictions,
        metrics_csv=args.metrics_csv,
        details_dir=args.details_dir,
    )
    write_metrics_markdown(args.metrics_md, args.dataset_name, metrics_rows)
    write_manifest(
        path=args.manifest,
        dataset_name=args.dataset_name,
        adjudication_rows=adjudication_rows,
        metrics_rows=metrics_rows,
        output_tsv=args.output_tsv,
        output_jsonl=args.output_jsonl,
        metrics_csv=args.metrics_csv,
        metrics_md=args.metrics_md,
    )
    print(f"Wrote {len(adjudication_rows)} provisional assistant-adjudication rows to {args.output_tsv}")
    print(f"Wrote provisional metrics to {args.metrics_csv}")


if __name__ == "__main__":
    main()
