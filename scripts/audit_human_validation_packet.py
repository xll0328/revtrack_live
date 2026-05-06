from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


VALID_LABELS = {"fixed", "partially_fixed", "unresolved", "regressed"}
MODEL_FIELDS = [
    "heuristic_label",
    "tfidf_label",
    "modernbert_label",
    "mpnet_label",
    "issue_ledger_label",
    "structured_label",
]
BLIND_FORBIDDEN_FIELDS = {
    "assistant_label",
    "gold_label",
    "silver_label",
    "suggested_label",
    "suggestion_source",
    "suggestion_note",
    "audit_score",
    "audit_bucket",
    *MODEL_FIELDS,
}
TEXT_FIELDS = [
    "paper_title",
    "review_rating",
    "review_confidence",
    "review_excerpt",
    "top_response_excerpt",
    "aligned_response_excerpt",
    "revision_summary",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit blind/key/audit TSV files for a human-validation packet."
    )
    parser.add_argument("--blind", required=True, help="Blind human-facing TSV.")
    parser.add_argument("--key", required=True, help="Hidden key TSV.")
    parser.add_argument("--audit", help="Optional audit TSV with assistant/model labels visible.")
    parser.add_argument("--source-sheet", help="Optional labeled source sheet used to create the packet.")
    parser.add_argument("--output-json", help="Optional machine-readable audit report.")
    parser.add_argument("--fail-on-error", action="store_true", help="Exit non-zero when errors are found.")
    return parser.parse_args()


def load_tsv(path: str | Path) -> tuple[list[str], list[dict[str, str]]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return list(reader.fieldnames or []), list(reader)


def normalize_label(value: str | None) -> str:
    return (value or "").strip().lower()


def row_label(row: dict[str, str]) -> str:
    return normalize_label(row.get("gold_label") or row.get("assistant_label") or row.get("suggested_label"))


def duplicate_ids(rows: list[dict[str, str]]) -> list[str]:
    counts = Counter(row.get("issue_id", "").strip() for row in rows)
    return sorted(issue_id for issue_id, count in counts.items() if issue_id and count > 1)


def by_id(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row.get("issue_id", "").strip(): row for row in rows if row.get("issue_id", "").strip()}


def compare_id_sets(
    *,
    left_name: str,
    left_rows: list[dict[str, str]],
    right_name: str,
    right_rows: list[dict[str, str]],
) -> list[str]:
    left_ids = set(by_id(left_rows))
    right_ids = set(by_id(right_rows))
    errors: list[str] = []
    missing = sorted(left_ids - right_ids)
    extra = sorted(right_ids - left_ids)
    if missing:
        errors.append(f"{right_name} is missing {len(missing)} ids from {left_name}: {missing}")
    if extra:
        errors.append(f"{right_name} has {len(extra)} ids not in {left_name}: {extra}")
    return errors


def require_id_subset(
    *,
    subset_name: str,
    subset_rows: list[dict[str, str]],
    superset_name: str,
    superset_rows: list[dict[str, str]],
) -> list[str]:
    subset_ids = set(by_id(subset_rows))
    superset_ids = set(by_id(superset_rows))
    missing = sorted(subset_ids - superset_ids)
    if not missing:
        return []
    return [f"{superset_name} is missing {len(missing)} ids from {subset_name}: {missing}"]


def audit_packet(
    *,
    blind_fields: list[str],
    blind_rows: list[dict[str, str]],
    key_rows: list[dict[str, str]],
    audit_rows: list[dict[str, str]] | None = None,
    source_rows: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    for name, rows in [
        ("blind", blind_rows),
        ("key", key_rows),
        ("audit", audit_rows or []),
        ("source", source_rows or []),
    ]:
        duplicates = duplicate_ids(rows)
        if duplicates:
            errors.append(f"{name} has duplicate issue_ids: {duplicates}")

    errors.extend(
        compare_id_sets(
            left_name="blind",
            left_rows=blind_rows,
            right_name="key",
            right_rows=key_rows,
        )
    )
    if audit_rows is not None:
        errors.extend(
            compare_id_sets(
                left_name="blind",
                left_rows=blind_rows,
                right_name="audit",
                right_rows=audit_rows,
            )
        )
    if source_rows is not None:
        errors.extend(
            require_id_subset(
                subset_name="blind",
                subset_rows=blind_rows,
                superset_name="source",
                superset_rows=source_rows,
            )
        )

    leaked_header_fields = sorted(BLIND_FORBIDDEN_FIELDS.intersection(blind_fields))
    if leaked_header_fields:
        errors.append(f"blind sheet exposes forbidden label/model columns: {leaked_header_fields}")

    for row in blind_rows:
        issue_id = row.get("issue_id", "").strip()
        for field in BLIND_FORBIDDEN_FIELDS:
            if row.get(field, "").strip():
                errors.append(f"blind row {issue_id} leaks non-empty {field}")
        human_label = normalize_label(row.get("human_label"))
        if human_label and human_label not in VALID_LABELS:
            errors.append(f"blind row {issue_id} has invalid prefilled human_label={human_label!r}")

    key_by_id = by_id(key_rows)
    invalid_key_labels = []
    for row in key_rows:
        issue_id = row.get("issue_id", "").strip()
        label = normalize_label(row.get("assistant_label"))
        if label not in VALID_LABELS:
            invalid_key_labels.append({"issue_id": issue_id, "assistant_label": label})
    if invalid_key_labels:
        errors.append(f"key has invalid assistant labels: {invalid_key_labels}")

    if audit_rows is not None:
        for issue_id, row in by_id(audit_rows).items():
            key = key_by_id.get(issue_id)
            if not key:
                continue
            audit_label = normalize_label(row.get("assistant_label"))
            key_label = normalize_label(key.get("assistant_label"))
            if audit_label != key_label:
                errors.append(
                    f"audit/key assistant_label mismatch for {issue_id}: audit={audit_label!r}, key={key_label!r}"
                )

    if source_rows is not None:
        source_by_id = by_id(source_rows)
        for issue_id, key in key_by_id.items():
            source = source_by_id.get(issue_id)
            if not source:
                continue
            source_label = row_label(source)
            key_label = normalize_label(key.get("assistant_label"))
            if source_label != key_label:
                errors.append(
                    f"source/key label mismatch for {issue_id}: source={source_label!r}, key={key_label!r}"
                )
            for field in MODEL_FIELDS:
                if source.get(field, "") != key.get(field, ""):
                    errors.append(f"source/key {field} mismatch for {issue_id}")

        blind_by_id = by_id(blind_rows)
        for issue_id, blind in blind_by_id.items():
            source = source_by_id.get(issue_id)
            if not source:
                continue
            for field in TEXT_FIELDS:
                if field in blind and field in source and blind.get(field, "") != source.get(field, ""):
                    errors.append(f"blind/source {field} mismatch for {issue_id}")

    assistant_distribution = Counter(
        normalize_label(row.get("assistant_label"))
        for row in key_rows
        if normalize_label(row.get("assistant_label"))
    )
    audit_bucket_distribution = Counter(
        row.get("audit_bucket", "").strip()
        for row in key_rows
        if row.get("audit_bucket", "").strip()
    )

    if not blind_rows:
        warnings.append("blind sheet has no rows")
    if not key_rows:
        warnings.append("key sheet has no rows")

    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "blind_rows": len(blind_rows),
        "key_rows": len(key_rows),
        "audit_rows": len(audit_rows) if audit_rows is not None else None,
        "source_rows": len(source_rows) if source_rows is not None else None,
        "assistant_distribution": dict(sorted(assistant_distribution.items())),
        "audit_bucket_distribution": dict(sorted(audit_bucket_distribution.items())),
    }


def main() -> None:
    args = parse_args()
    blind_fields, blind_rows = load_tsv(args.blind)
    _, key_rows = load_tsv(args.key)
    audit_rows = load_tsv(args.audit)[1] if args.audit else None
    source_rows = load_tsv(args.source_sheet)[1] if args.source_sheet else None

    report = audit_packet(
        blind_fields=blind_fields,
        blind_rows=blind_rows,
        key_rows=key_rows,
        audit_rows=audit_rows,
        source_rows=source_rows,
    )

    if args.output_json:
        output_path = Path(args.output_json)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps(report, indent=2, sort_keys=True))
    if args.fail_on_error and report["errors"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
