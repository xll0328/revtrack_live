from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
VALID_LABELS = {"fixed", "partially_fixed", "unresolved", "regressed"}
ANNOTATION_FIELDS = ["human_label", "human_confidence", "evidence_span", "notes"]
DEFAULT_NOTE = (
    "User-confirmed standard expanded80 validation on 2026-04-26; "
    "source=user-reviewed expanded80 assistant-adjudication draft; "
    "not an independent two-annotator IAA pass."
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Promote user-confirmed expanded80 assistant adjudication into the canonical blind validation sheet."
    )
    parser.add_argument(
        "--adjudication",
        default="experiments/day1/iclr2025_expanded80_assistant_adjudication_v1.tsv",
    )
    parser.add_argument(
        "--blind-sheet",
        default="experiments/day1/iclr2025_expanded80_human_validation_v1_blind.tsv",
    )
    parser.add_argument(
        "--report-json",
        default="outputs/day1/iclr2025_expanded80_standard_validation_promotion.json",
    )
    parser.add_argument("--allow-overwrite", action="store_true")
    parser.add_argument("--write", action="store_true")
    return parser.parse_args()


def resolve(path: str | Path) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else ROOT / candidate


def relpath(path: str | Path) -> str:
    resolved = Path(path)
    try:
        return str(resolved.relative_to(ROOT))
    except ValueError:
        return str(resolved)


def compact(value: str | None) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def normalize_label(value: str | None) -> str:
    return compact(value).lower()


def load_tsv(path: str | Path) -> tuple[list[str], list[dict[str, str]]]:
    with resolve(path).open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return list(reader.fieldnames or []), list(reader)


def write_tsv(path: str | Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    output = resolve(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t")
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fields} for row in rows)


def write_json(path: str | Path, payload: dict[str, Any]) -> None:
    output = resolve(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def by_issue_id(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row["issue_id"]: row for row in rows if compact(row.get("issue_id"))}


def confidence_to_human(value: str | None) -> str:
    normalized = compact(value).lower()
    if normalized == "medium":
        return "4"
    if normalized == "low_medium":
        return "3"
    if normalized == "low":
        return "2"
    return "3"


def promoted_note(row: dict[str, str]) -> str:
    parts = [DEFAULT_NOTE]
    evidence_source = compact(row.get("evidence_source"))
    if evidence_source:
        parts.append(f"Evidence source: {evidence_source}.")
    source_note = compact(row.get("notes"))
    if source_note:
        parts.append(f"Source adjudication note: {source_note}")
    return " ".join(parts)


def promote(
    *,
    adjudication_path: str | Path,
    blind_sheet_path: str | Path,
    report_json: str | Path,
    allow_overwrite: bool = False,
    write: bool = False,
) -> dict[str, Any]:
    errors: list[str] = []
    adjudication_fields, adjudication_rows = load_tsv(adjudication_path)
    blind_fields, blind_rows = load_tsv(blind_sheet_path)

    for field in ANNOTATION_FIELDS:
        if field not in blind_fields:
            blind_fields.append(field)

    required = {"issue_id", "assistant_label", "evidence_span", "assistant_confidence"}
    missing_adjudication_fields = sorted(required - set(adjudication_fields))
    if missing_adjudication_fields:
        errors.append(f"adjudication sheet missing fields: {missing_adjudication_fields}")

    blind_by_id = by_issue_id(blind_rows)
    seen: set[str] = set()
    promoted = 0
    label_counts: Counter[str] = Counter()
    confidence_counts: Counter[str] = Counter()
    evidence_source_counts: Counter[str] = Counter()

    for row in adjudication_rows:
        issue_id = compact(row.get("issue_id"))
        if not issue_id:
            errors.append("adjudication row has missing issue_id")
            continue
        if issue_id in seen:
            errors.append(f"duplicate adjudication row: {issue_id}")
            continue
        seen.add(issue_id)

        blind = blind_by_id.get(issue_id)
        if blind is None:
            errors.append(f"blind sheet is missing adjudicated issue_id={issue_id}")
            continue

        label = normalize_label(row.get("assistant_label"))
        if label not in VALID_LABELS:
            errors.append(f"invalid label for {issue_id}: {label!r}")
            continue

        evidence = compact(row.get("evidence_span"))
        if not evidence:
            errors.append(f"missing evidence_span for {issue_id}")
            continue

        existing_label = normalize_label(blind.get("human_label"))
        if existing_label in VALID_LABELS and existing_label != label and not allow_overwrite:
            errors.append(f"existing label conflict for {issue_id}: existing={existing_label}, promoted={label}")
            continue

        confidence = confidence_to_human(row.get("assistant_confidence"))
        blind["human_label"] = label
        blind["human_confidence"] = confidence
        blind["evidence_span"] = evidence
        blind["notes"] = promoted_note(row)
        promoted += 1
        label_counts[label] += 1
        confidence_counts[confidence] += 1
        evidence_source_counts[compact(row.get("evidence_source")) or "missing"] += 1

    missing_from_adjudication = sorted(set(blind_by_id) - seen)
    if missing_from_adjudication:
        errors.append(f"adjudication sheet is missing blind rows: {missing_from_adjudication[:10]}")

    report = {
        "status": "ok" if not errors else "error",
        "write": bool(write),
        "adjudication": relpath(resolve(adjudication_path)),
        "blind_sheet": relpath(resolve(blind_sheet_path)),
        "rows": len(blind_rows),
        "adjudication_rows": len(adjudication_rows),
        "promoted_rows": promoted,
        "label_distribution": dict(sorted(label_counts.items())),
        "confidence_distribution": dict(sorted(confidence_counts.items())),
        "evidence_source_distribution": dict(sorted(evidence_source_counts.items())),
        "provenance": DEFAULT_NOTE,
        "claim_boundary": (
            "Use as user-confirmed single-pass standard validation; "
            "do not report as independent two-annotator IAA."
        ),
        "errors": errors,
    }

    if write and not errors:
        write_tsv(blind_sheet_path, blind_fields, blind_rows)
    write_json(report_json, report)
    return report


def main() -> None:
    args = parse_args()
    report = promote(
        adjudication_path=args.adjudication,
        blind_sheet_path=args.blind_sheet,
        report_json=args.report_json,
        allow_overwrite=args.allow_overwrite,
        write=args.write,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    if report["status"] != "ok":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
