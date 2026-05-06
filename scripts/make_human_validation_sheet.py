from __future__ import annotations

import argparse
import csv
from pathlib import Path


LABEL_ORDER = ["fixed", "partially_fixed", "unresolved", "regressed"]
MODEL_FIELDS = [
    "heuristic_label",
    "tfidf_label",
    "modernbert_label",
    "mpnet_label",
    "issue_ledger_label",
    "structured_label",
]

BLIND_FIELDS = [
    "issue_id",
    "paper_title",
    "review_rating",
    "review_confidence",
    "review_excerpt",
    "top_response_excerpt",
    "aligned_response_excerpt",
    "revision_summary",
    "human_label",
    "human_confidence",
    "evidence_span",
    "notes",
]

AUDIT_FIELDS = [
    "audit_rank",
    "audit_score",
    "audit_bucket",
    "priority_score",
    "issue_id",
    "paper_title",
    "review_rating",
    "review_confidence",
    "suggested_label",
    "suggestion_source",
    "suggestion_note",
    "assistant_label",
    "human_label",
    "human_confidence",
    "silver_label",
    *MODEL_FIELDS,
    "review_excerpt",
    "top_response_excerpt",
    "aligned_response_excerpt",
    "revision_summary",
    "silver_comment",
    "gold_label",
    "evidence_span",
    "notes",
]

KEY_FIELDS = [
    "audit_rank",
    "audit_score",
    "audit_bucket",
    "issue_id",
    "assistant_label",
    "priority_score",
    "suggested_label",
    "silver_label",
    *MODEL_FIELDS,
    "assistant_evidence_span",
    "assistant_notes",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a stratified human-validation sheet from an adjudicated clean-dev sheet."
    )
    parser.add_argument("--sheet", required=True, help="Adjudicated TSV sheet, e.g. clean dev v7.")
    parser.add_argument("--output", required=True, help="Human-facing TSV output.")
    parser.add_argument("--key-output", help="Optional sidecar TSV with hidden assistant/model labels.")
    parser.add_argument("--sample-size", type=int, default=40)
    parser.add_argument("--min-per-label", type=int, default=6)
    parser.add_argument(
        "--mode",
        choices=["blind", "audit"],
        default="blind",
        help="blind hides assistant/model labels; audit shows them for adjudication review.",
    )
    return parser.parse_args()


def load_sheet(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def normalize_label(value: str | None) -> str:
    return (value or "").strip().lower()


def assistant_label(row: dict[str, str]) -> str:
    return normalize_label(row.get("gold_label") or row.get("assistant_label") or row.get("suggested_label"))


def unique_model_labels(row: dict[str, str]) -> set[str]:
    return {
        normalize_label(row.get(field))
        for field in MODEL_FIELDS
        if normalize_label(row.get(field))
    }


def disagreement_count(row: dict[str, str]) -> int:
    return max(0, len(unique_model_labels(row)) - 1)


def high_conflict(row: dict[str, str]) -> bool:
    labels = unique_model_labels(row)
    return len(labels) >= 3 or {"fixed", "regressed"}.issubset(labels)


def parse_priority(row: dict[str, str]) -> float:
    try:
        return float(row.get("priority_score", "") or 0.0)
    except ValueError:
        return 0.0


def audit_score(row: dict[str, str]) -> float:
    label = assistant_label(row)
    structured = normalize_label(row.get("structured_label"))
    score = 0.1 * parse_priority(row)
    if structured and structured != label:
        score += 8.0
    if high_conflict(row):
        score += 5.0
    score += 2.0 * disagreement_count(row)
    if label == "unresolved":
        score += 4.0
    if label == "regressed":
        score += 7.0
    if any(normalize_label(row.get(field)) != structured for field in ["tfidf_label", "modernbert_label", "mpnet_label"]):
        score += 1.0
    return score


def audit_bucket(row: dict[str, str]) -> str:
    label = assistant_label(row)
    structured = normalize_label(row.get("structured_label"))
    if label == "regressed":
        return "minority_regressed"
    if label == "unresolved":
        return "minority_unresolved"
    if structured and structured != label:
        return "structured_error"
    if high_conflict(row):
        return "model_high_conflict"
    if disagreement_count(row) > 0:
        return "model_disagreement"
    return "label_stratum"


def sort_key(row: dict[str, str]) -> tuple[float, int, str]:
    label = assistant_label(row)
    label_rank = LABEL_ORDER.index(label) if label in LABEL_ORDER else len(LABEL_ORDER)
    return (-audit_score(row), label_rank, row.get("issue_id", ""))


def select_validation_rows(
    rows: list[dict[str, str]],
    *,
    sample_size: int,
    min_per_label: int,
) -> list[dict[str, str]]:
    eligible = [row for row in rows if assistant_label(row) in LABEL_ORDER]
    if sample_size <= 0 or sample_size >= len(eligible):
        return sorted(eligible, key=sort_key)

    selected: list[dict[str, str]] = []
    selected_ids: set[str] = set()
    for label in LABEL_ORDER:
        label_rows = sorted(
            [row for row in eligible if assistant_label(row) == label],
            key=sort_key,
        )
        for row in label_rows[: min(min_per_label, len(label_rows))]:
            selected.append(row)
            selected_ids.add(row["issue_id"])

    remaining = sorted(
        [row for row in eligible if row["issue_id"] not in selected_ids],
        key=sort_key,
    )
    for row in remaining:
        if len(selected) >= sample_size:
            break
        selected.append(row)
        selected_ids.add(row["issue_id"])

    return sorted(selected[:sample_size], key=sort_key)


def write_tsv(path: str | Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def as_blind_row(row: dict[str, str]) -> dict[str, str]:
    return {
        "issue_id": row.get("issue_id", ""),
        "paper_title": row.get("paper_title", ""),
        "review_rating": row.get("review_rating", ""),
        "review_confidence": row.get("review_confidence", ""),
        "review_excerpt": row.get("review_excerpt", ""),
        "top_response_excerpt": row.get("top_response_excerpt", ""),
        "aligned_response_excerpt": row.get("aligned_response_excerpt", ""),
        "revision_summary": row.get("revision_summary", ""),
        "human_label": "",
        "human_confidence": "",
        "evidence_span": "",
        "notes": "",
    }


def as_audit_row(row: dict[str, str], rank: int) -> dict[str, str]:
    label = assistant_label(row)
    model_snapshot = "; ".join(
        f"{field.removesuffix('_label')}={normalize_label(row.get(field)) or 'missing'}"
        for field in MODEL_FIELDS
    )
    return {
        "audit_rank": str(rank),
        "audit_score": f"{audit_score(row):.3f}",
        "audit_bucket": audit_bucket(row),
        "priority_score": row.get("priority_score", ""),
        "issue_id": row.get("issue_id", ""),
        "paper_title": row.get("paper_title", ""),
        "review_rating": row.get("review_rating", ""),
        "review_confidence": row.get("review_confidence", ""),
        "suggested_label": label,
        "suggestion_source": "assistant_clean_dev",
        "suggestion_note": f"{audit_bucket(row)}; {model_snapshot}",
        "assistant_label": label,
        "human_label": "",
        "human_confidence": "",
        "silver_label": row.get("silver_label", ""),
        **{field: row.get(field, "") for field in MODEL_FIELDS},
        "review_excerpt": row.get("review_excerpt", ""),
        "top_response_excerpt": row.get("top_response_excerpt", ""),
        "aligned_response_excerpt": row.get("aligned_response_excerpt", ""),
        "revision_summary": row.get("revision_summary", ""),
        "silver_comment": row.get("silver_comment", ""),
        "gold_label": "",
        "evidence_span": row.get("evidence_span", ""),
        "notes": row.get("notes", ""),
    }


def as_key_row(row: dict[str, str], rank: int) -> dict[str, str]:
    label = assistant_label(row)
    return {
        "audit_rank": str(rank),
        "audit_score": f"{audit_score(row):.3f}",
        "audit_bucket": audit_bucket(row),
        "issue_id": row.get("issue_id", ""),
        "assistant_label": label,
        "priority_score": row.get("priority_score", ""),
        "suggested_label": row.get("suggested_label", ""),
        "silver_label": row.get("silver_label", ""),
        **{field: row.get(field, "") for field in MODEL_FIELDS},
        "assistant_evidence_span": row.get("evidence_span", ""),
        "assistant_notes": row.get("notes", ""),
    }


def main() -> None:
    args = parse_args()
    selected = select_validation_rows(
        load_sheet(args.sheet),
        sample_size=args.sample_size,
        min_per_label=args.min_per_label,
    )

    if args.mode == "blind":
        write_tsv(args.output, [as_blind_row(row) for row in selected], BLIND_FIELDS)
    else:
        write_tsv(args.output, [as_audit_row(row, rank) for rank, row in enumerate(selected, 1)], AUDIT_FIELDS)

    if args.key_output:
        key_rows = [as_key_row(row, rank) for rank, row in enumerate(selected, 1)]
        write_tsv(args.key_output, key_rows, KEY_FIELDS)

    print(f"Wrote {len(selected)} human-validation rows to {args.output}")
    if args.key_output:
        print(f"Wrote validation key to {args.key_output}")


if __name__ == "__main__":
    main()
