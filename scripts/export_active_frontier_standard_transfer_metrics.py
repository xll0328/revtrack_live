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
sys.path.insert(0, str(ROOT / "scripts"))

from export_active_frontier_assistant_adjudication import load_jsonl, parse_named_path
from revtrack.io import load_predictions, save_examples
from revtrack.metrics import evaluate_predictions
from revtrack.schema import LABELS, IssueExample


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export standard transfer metrics for a user-confirmed active-frontier validation sheet."
    )
    parser.add_argument("--dataset-name", required=True)
    parser.add_argument("--human-sheet", required=True)
    parser.add_argument("--candidates", required=True)
    parser.add_argument("--output-jsonl", required=True)
    parser.add_argument("--metrics-csv", required=True)
    parser.add_argument("--metrics-md", required=True)
    parser.add_argument("--details-dir", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--prediction", action="append", type=parse_named_path, default=[])
    parser.add_argument("--label-field", default="human_label")
    parser.add_argument("--confidence-field", default="human_confidence")
    parser.add_argument("--evidence-field", default="evidence_span")
    parser.add_argument("--notes-field", default="notes")
    parser.add_argument(
        "--sample-design",
        choices=["active_frontier", "random_stratified"],
        default="active_frontier",
        help="Sampling provenance used for paper-facing reporting boundaries.",
    )
    parser.add_argument(
        "--validation-status",
        default="standard_single_user_confirmed",
        help="Provenance string written into example metadata and output manifests.",
    )
    return parser.parse_args()


def compact(value: str | None) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def load_tsv(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def by_issue_id(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(row.get("issue_id", "")): row for row in rows if row.get("issue_id")}


def examples_from_standard_rows(
    *,
    dataset_name: str,
    human_rows: list[dict[str, str]],
    candidate_rows: list[dict[str, Any]],
    label_field: str = "human_label",
    confidence_field: str = "human_confidence",
    evidence_field: str = "evidence_span",
    notes_field: str = "notes",
    validation_status: str = "standard_single_user_confirmed",
) -> list[IssueExample]:
    candidates = by_issue_id(candidate_rows)
    examples: list[IssueExample] = []
    invalid: list[str] = []
    missing_evidence: list[str] = []
    for row in human_rows:
        issue_id = compact(row.get("issue_id"))
        if not issue_id:
            invalid.append("<missing issue_id>")
            continue
        label = compact(row.get(label_field)).lower()
        if label not in LABELS:
            invalid.append(issue_id)
            continue
        evidence = compact(row.get(evidence_field))
        if not evidence:
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
                    "dataset_name": dataset_name,
                    "submission_id": str(candidate.get("submission_id", "")),
                    "forum": str(candidate.get("forum", "")),
                    "review_id": str(candidate.get("review_id", "")),
                    "evidence_span": evidence,
                    "human_confidence": row.get(confidence_field, ""),
                    "notes": row.get(notes_field, ""),
                    "provenance": validation_status,
                },
            )
        )
    if invalid:
        raise ValueError(f"invalid or missing label rows: {invalid[:10]}")
    if missing_evidence:
        raise ValueError(f"missing evidence_span rows: {missing_evidence[:10]}")
    return examples


def write_metrics(
    *,
    examples: list[IssueExample],
    predictions: dict[str, Path],
    metrics_csv: str | Path,
    details_dir: str | Path,
    validation_status: str,
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
                "status": validation_status,
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


def write_metrics_markdown(
    path: str | Path,
    *,
    dataset_name: str,
    rows: list[dict[str, Any]],
    validation_status: str,
    sample_design: str,
) -> None:
    is_standard = validation_status == "standard_single_user_confirmed"
    title_suffix = "Standard Transfer Metrics" if is_standard else "Transfer Metrics (Proxy / Pre-Confirmation)"
    if is_standard:
        boundary_summary = (
            f"These metrics use a validation sheet with status `{validation_status}`. "
            "Report them only under that provenance boundary; this is not an independent two-annotator IAA result unless a separate IAA pass exists."
        )
    else:
        boundary_summary = (
            f"These metrics use a validation sheet with status `{validation_status}`. "
            "This is a proxy/pre-confirmation artifact and not standard human-validation evidence."
        )

    lines = [
        f"# {dataset_name} {title_suffix}",
        "",
        boundary_summary,
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
            (
                "- Report as standard single-user validation unless a separate second-annotator pass is added."
                if is_standard
                else "- Do not report as standard human validation or IAA; this is a pre-confirmation proxy artifact."
            ),
            (
                "- Treat this as queue triage only when labels come from assistant-resolved candidates."
                if not is_standard
                else (
                    "- Treat random/stratified samples as bounded slice evidence by measured design, not natural venue prevalence."
                    if sample_design == "random_stratified"
                    else "- Treat active-frontier samples as hard-case/frontier evidence, not natural venue prevalence."
                )
            ),
            "- Keep provisional assistant-adjudication metrics separate from claim-ready benchmark tables.",
        ]
    )
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_manifest(
    *,
    path: str | Path,
    dataset_name: str,
    examples: list[IssueExample],
    metrics_rows: list[dict[str, Any]],
    output_jsonl: str | Path,
    metrics_csv: str | Path,
    metrics_md: str | Path,
    validation_status: str,
    sample_design: str,
) -> None:
    label_counts = Counter(example.gold_label for example in examples)
    best = max(metrics_rows, key=lambda row: (float(row["macro_f1"]), float(row["accuracy"]))) if metrics_rows else {}
    is_standard = validation_status == "standard_single_user_confirmed"
    if is_standard:
        if sample_design == "random_stratified":
            claim_boundary = (
                "Use as standard single-user random/stratified slice validation only when the source sheet has been user-confirmed; "
                "do not report as independent two-annotator IAA or unmeasured natural venue prevalence."
            )
        else:
            claim_boundary = (
                "Use as standard single-user validation only when the source sheet has been user-confirmed; "
                "do not report as independent two-annotator IAA."
            )
    else:
        claim_boundary = (
            "Use only as proxy/pre-confirmation analysis; do not report as standard human validation, "
            "IAA, or final benchmark transfer evidence."
        )
    payload = {
        "dataset_name": dataset_name,
        "status": validation_status,
        "human_validation_status": validation_status,
        "rows": len(examples),
        "label_distribution": dict(sorted(label_counts.items())),
        "best_model": best,
        "output_jsonl": str(output_jsonl),
        "metrics_csv": str(metrics_csv),
        "metrics_md": str(metrics_md),
        "sample_design": sample_design,
        "claim_boundary": claim_boundary,
    }
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    predictions = dict(args.prediction)
    if not predictions:
        raise SystemExit("At least one --prediction NAME=PATH argument is required.")
    examples = examples_from_standard_rows(
        dataset_name=args.dataset_name,
        human_rows=load_tsv(args.human_sheet),
        candidate_rows=load_jsonl(args.candidates),
        label_field=args.label_field,
        confidence_field=args.confidence_field,
        evidence_field=args.evidence_field,
        notes_field=args.notes_field,
        validation_status=args.validation_status,
    )
    save_examples(args.output_jsonl, examples)
    metrics_rows = write_metrics(
        examples=examples,
        predictions=predictions,
        metrics_csv=args.metrics_csv,
        details_dir=args.details_dir,
        validation_status=args.validation_status,
    )
    write_metrics_markdown(
        args.metrics_md,
        dataset_name=args.dataset_name,
        rows=metrics_rows,
        validation_status=args.validation_status,
        sample_design=args.sample_design,
    )
    write_manifest(
        path=args.manifest,
        dataset_name=args.dataset_name,
        examples=examples,
        metrics_rows=metrics_rows,
        output_jsonl=args.output_jsonl,
        metrics_csv=args.metrics_csv,
        metrics_md=args.metrics_md,
        validation_status=args.validation_status,
        sample_design=args.sample_design,
    )
    print(f"Wrote {len(examples)} standard {args.sample_design} examples to {args.output_jsonl}")
    print(f"Wrote standard {args.sample_design} transfer metrics to {args.metrics_csv}")


if __name__ == "__main__":
    main()
