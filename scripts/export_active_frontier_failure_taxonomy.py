from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


MODEL_DISPLAY = {
    "issue_ledger": "Issue ledger",
    "structured": "Structured",
    "tfidf": "TF-IDF",
    "modernbert": "ModernBERT",
    "mpnet": "MPNet",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export a failure taxonomy for a standard or provisional active-frontier transfer run."
    )
    parser.add_argument("--dataset-name", required=True)
    parser.add_argument("--label-sheet", required=True)
    parser.add_argument("--details-dir", required=True)
    parser.add_argument("--output-csv", required=True)
    parser.add_argument("--output-md", required=True)
    parser.add_argument("--label-field", default="human_label")
    parser.add_argument("--evidence-field", default="evidence_span")
    parser.add_argument(
        "--sample-design",
        choices=["active_frontier", "random_stratified"],
        default="active_frontier",
        help="Sampling provenance used for paper-facing reporting boundaries.",
    )
    parser.add_argument(
        "--validation-status",
        default="standard_single_user_confirmed",
        help="Boundary string printed in the markdown and CSV outputs.",
    )
    parser.add_argument("--max-patterns", type=int, default=10)
    return parser.parse_args()


def compact(value: str | None) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def clip(value: str | None, max_chars: int = 260) -> str:
    text = compact(value)
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(" ", 1)[0] + "..."


def load_tsv(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def by_issue_id(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row["issue_id"]: row for row in rows if compact(row.get("issue_id"))}


def model_key_from_details_path(path: Path) -> str:
    return path.name.removesuffix("_details.json")


def load_details(details_dir: str | Path) -> dict[str, list[dict[str, str]]]:
    root = Path(details_dir)
    details: dict[str, list[dict[str, str]]] = {}
    for path in sorted(root.glob("*_details.json")):
        details[model_key_from_details_path(path)] = load_json(path)
    if not details:
        raise FileNotFoundError(f"No *_details.json files found under {root}")
    return details


def failure_mode(gold: str, predicted: str) -> tuple[str, str, str]:
    if gold == "unresolved" and predicted in {"fixed", "partially_fixed"}:
        return (
            "over_crediting_unresolved",
            "over-credits an unresolved concern as resolved",
            "A revision assistant would stop tracking an issue that still needs attention.",
        )
    if gold == "fixed" and predicted != "fixed":
        return (
            "fixed_under_recovery",
            "keeps a fixed concern alive",
            "This is the stale-criticism risk: old reviewer text remains salient after a concrete fix.",
        )
    if gold == "regressed" and predicted != "regressed":
        return (
            "regression_blindness",
            "misses a regression or newly worsened concern",
            "Regression cases are rare but high-risk in revision workflows.",
        )
    if gold == "partially_fixed" and predicted == "fixed":
        return (
            "partial_vs_fixed_boundary",
            "upgrades partial evidence into a full fix",
            "This is the central rubric-boundary risk for evidence-based labels.",
        )
    if gold == "partially_fixed" and predicted == "unresolved":
        return (
            "partial_under_crediting",
            "ignores real but incomplete revision evidence",
            "The model misses incremental progress that should not be collapsed into unresolved.",
        )
    if predicted == "regressed" and gold != "regressed":
        return (
            "false_regression_alarm",
            "over-detects regression",
            "The model treats cautionary or limitation language as evidence that the paper got worse.",
        )
    return (
        "revision_status_confusion",
        f"confuses {gold} with {predicted}",
        "This pattern marks a general failure to align the original concern with revision evidence.",
    )


def build_rows(
    *,
    dataset_name: str,
    label_rows: list[dict[str, str]],
    details_by_model: dict[str, list[dict[str, str]]],
    label_field: str = "human_label",
    evidence_field: str = "evidence_span",
    validation_status: str = "standard_single_user_confirmed",
    max_patterns: int = 10,
) -> list[dict[str, str]]:
    labels = by_issue_id(label_rows)
    grouped: dict[tuple[str, str, str, str], list[dict[str, str]]] = defaultdict(list)
    for model_key, details in details_by_model.items():
        for item in details:
            gold = compact(item.get("gold_label")).lower()
            predicted = compact(item.get("predicted_label")).lower()
            if not gold or not predicted or gold == predicted:
                continue
            mode, model_risk, why_it_matters = failure_mode(gold, predicted)
            grouped[(mode, model_key, gold, predicted)].append(
                {
                    "issue_id": item.get("id", ""),
                    "paper_title": item.get("paper_title", ""),
                    "gold_label": gold,
                    "predicted_label": predicted,
                    "model_risk": model_risk,
                    "why_it_matters": why_it_matters,
                }
            )

    rows: list[dict[str, str]] = []
    ranked_groups = sorted(
        grouped.items(),
        key=lambda entry: (-len(entry[1]), entry[0][0], entry[0][1], entry[0][2], entry[0][3]),
    )
    for (mode, model_key, gold, predicted), examples in ranked_groups[:max_patterns]:
        example = examples[0]
        issue_id = example["issue_id"]
        label_row = labels.get(issue_id, {})
        row_label = compact(label_row.get(label_field)).lower()
        if row_label and row_label != gold:
            label_note = f"label_sheet={row_label}; details_gold={gold}"
        else:
            label_note = f"label_sheet={row_label or 'missing'}"
        rows.append(
            {
                "failure_mode": mode,
                "dataset_name": dataset_name,
                "validation_status": validation_status,
                "model_key": model_key,
                "support_count": str(len(examples)),
                "issue_id": issue_id,
                "paper_title": example["paper_title"] or label_row.get("paper_title", ""),
                "gold_label": gold,
                "predicted_label": predicted,
                "model_risk": example["model_risk"],
                "review_concern": clip(label_row.get("review_excerpt")),
                "revision_evidence": clip(label_row.get(evidence_field)),
                "why_it_matters": example["why_it_matters"],
                "label_consistency_note": label_note,
            }
        )
    return rows


def write_csv(path: str | Path, rows: list[dict[str, str]]) -> None:
    fields = [
        "failure_mode",
        "dataset_name",
        "validation_status",
        "model_key",
        "support_count",
        "issue_id",
        "paper_title",
        "gold_label",
        "predicted_label",
        "model_risk",
        "review_concern",
        "revision_evidence",
        "why_it_matters",
        "label_consistency_note",
    ]
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(
    path: str | Path,
    *,
    dataset_name: str,
    rows: list[dict[str, str]],
    validation_status: str,
    sample_design: str,
    details_by_model: dict[str, list[dict[str, str]]],
) -> None:
    labels_by_issue: dict[str, str] = {}
    model_errors: dict[str, int] = {}
    for model_key, details in details_by_model.items():
        model_errors[model_key] = sum(1 for row in details if row.get("gold_label") != row.get("predicted_label"))
        for row in details:
            issue_id = compact(row.get("id"))
            label = compact(row.get("gold_label")).lower()
            if issue_id and label:
                labels_by_issue[issue_id] = label
    label_counts = Counter(labels_by_issue.values())
    if sample_design == "random_stratified":
        summary_sentence = (
            "This taxonomy summarizes model error patterns for a user-confirmed random/stratified slice. "
            "Report it by measured slice design; do not use it as an unmeasured natural-prevalence estimate."
        )
        boundary_sentence = (
            "- Random/stratified slice counts should be reported by measured design, not as unmeasured natural venue prevalence."
        )
    else:
        summary_sentence = (
            "This taxonomy summarizes model error patterns for the active frontier. If the validation status is provisional, "
            "use it for review planning only; do not report it as benchmark evidence."
        )
        boundary_sentence = "- Active-frontier counts should not be described as natural venue prevalence."

    lines = [
        f"# {dataset_name} Failure Taxonomy",
        "",
        f"Validation status: `{validation_status}`",
        "",
        summary_sentence,
        "",
        "## Distribution",
        "",
        "- Labels: "
        + ", ".join(f"`{label}`={count}" for label, count in sorted(label_counts.items()) if label),
        "- Model errors: "
        + ", ".join(
            f"`{MODEL_DISPLAY.get(model, model)}`={count}" for model, count in sorted(model_errors.items())
        ),
        "",
        "## Patterns",
        "",
        "| failure mode | model | n | gold -> predicted | issue | risk | paper use |",
        "| --- | --- | ---: | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    row["failure_mode"],
                    MODEL_DISPLAY.get(row["model_key"], row["model_key"]),
                    row["support_count"],
                    f"{row['gold_label']} -> {row['predicted_label']}",
                    f"`{row['issue_id']}`",
                    row["model_risk"],
                    row["why_it_matters"],
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- Standard-label taxonomy requires a user-confirmed validation sheet.",
            "- Provisional taxonomy is only a queue-prioritization and reviewer-risk artifact.",
            boundary_sentence,
        ]
    )
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    details_by_model = load_details(args.details_dir)
    rows = build_rows(
        dataset_name=args.dataset_name,
        label_rows=load_tsv(args.label_sheet),
        details_by_model=details_by_model,
        label_field=args.label_field,
        evidence_field=args.evidence_field,
        validation_status=args.validation_status,
        max_patterns=args.max_patterns,
    )
    write_csv(args.output_csv, rows)
    write_markdown(
        args.output_md,
        dataset_name=args.dataset_name,
        rows=rows,
        validation_status=args.validation_status,
        sample_design=args.sample_design,
        details_by_model=details_by_model,
    )
    print(f"Wrote {len(rows)} {args.sample_design} taxonomy rows to {args.output_csv}")


if __name__ == "__main__":
    main()
