from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
VALID_LABELS = {"fixed", "partially_fixed", "unresolved", "regressed"}
ANNOTATION_FIELDS = ["human_label", "human_confidence", "evidence_span", "notes"]
DEFAULT_CONFIDENCE = "3"
DEFAULT_NOTE = (
    "AI prelabel draft on {today}; source={label_source}; requires human review "
    "before promotion; do not treat as independent IAA."
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Prefill second-annotator blind packet with assistant draft labels for "
            "faster human review."
        )
    )
    parser.add_argument(
        "--blind-sheet",
        default="experiments/day1/iaa_second_annotator_boundary160_v1_blind.tsv",
    )
    parser.add_argument(
        "--key-sheet",
        default="experiments/day1/iaa_second_annotator_boundary160_v1_key.tsv",
    )
    parser.add_argument(
        "--report-json",
        default="outputs/day1/paper_assets/iaa_second_annotator_boundary160_v1_prelabel_report.json",
    )
    parser.add_argument(
        "--report-md",
        default="outputs/day1/paper_assets/iaa_second_annotator_boundary160_v1_prelabel_report.md",
    )
    parser.add_argument(
        "--label-source",
        choices=["assistant_first", "first_pass_only", "assistant_only"],
        default="assistant_first",
        help=(
            "Label source priority: assistant_first uses assistant_label then first_pass_label; "
            "first_pass_only uses first_pass_label; assistant_only uses assistant_label."
        ),
    )
    parser.add_argument("--default-confidence", default=DEFAULT_CONFIDENCE)
    parser.add_argument(
        "--allow-overwrite",
        action="store_true",
        help="Overwrite existing human_label rows.",
    )
    parser.add_argument("--write", action="store_true")
    return parser.parse_args()


def resolve(path: str | Path) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else ROOT / candidate


def relpath(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def normalize(value: str | None) -> str:
    return (value or "").strip()


def normalize_label(value: str | None) -> str:
    return normalize(value).lower()


def load_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return list(reader.fieldnames or []), list(reader)


def write_tsv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fieldnames} for row in rows)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_md(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# IAA Prelabel Report",
        "",
        f"- status: `{payload['status']}`",
        f"- blind_sheet: `{payload['blind_sheet']}`",
        f"- key_sheet: `{payload['key_sheet']}`",
        f"- rows: `{payload['rows']}`",
        f"- prefilled_rows: `{payload['prefilled_rows']}`",
        f"- skipped_existing_rows: `{payload['skipped_existing_rows']}`",
        f"- missing_key_rows: `{payload['missing_key_rows']}`",
        f"- invalid_label_rows: `{payload['invalid_label_rows']}`",
        f"- missing_evidence_rows: `{payload['missing_evidence_rows']}`",
        "",
        "## Claim Boundary",
        "",
        "- This file is an AI prelabel draft for faster human review.",
        "- It is not an independent second-annotator IAA result until human review is completed.",
    ]
    if payload["errors"]:
        lines.extend(["", "## Errors", ""])
        lines.extend(f"- {message}" for message in payload["errors"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def pick_label(key_row: dict[str, str], mode: str) -> tuple[str, str]:
    assistant = normalize_label(key_row.get("assistant_label"))
    first_pass = normalize_label(key_row.get("first_pass_label"))

    if mode == "assistant_only":
        return assistant, "assistant_label"
    if mode == "first_pass_only":
        return first_pass, "first_pass_label"

    if assistant:
        return assistant, "assistant_label"
    return first_pass, "first_pass_label"


def pick_evidence(key_row: dict[str, str]) -> str:
    first_pass = normalize(key_row.get("first_pass_evidence_span"))
    if first_pass:
        return first_pass
    return normalize(key_row.get("assistant_evidence_span"))


def pick_confidence(key_row: dict[str, str], default_confidence: str) -> str:
    first_pass_conf = normalize(key_row.get("first_pass_confidence"))
    if first_pass_conf:
        return first_pass_conf
    return default_confidence


def prelabel(
    *,
    blind_sheet: Path,
    key_sheet: Path,
    report_json: Path,
    report_md: Path,
    label_source: str,
    default_confidence: str,
    allow_overwrite: bool,
    write: bool,
) -> dict[str, Any]:
    errors: list[str] = []
    blind_fields, blind_rows = load_tsv(blind_sheet)
    _, key_rows = load_tsv(key_sheet)

    for field in ANNOTATION_FIELDS:
        if field not in blind_fields:
            blind_fields.append(field)

    key_by_id = {
        normalize(row.get("issue_id")): row
        for row in key_rows
        if normalize(row.get("issue_id"))
    }

    prefilled_rows = 0
    skipped_existing_rows = 0
    missing_key_rows = 0
    invalid_label_rows = 0
    missing_evidence_rows = 0

    today = str(date.today())

    for row in blind_rows:
        issue_id = normalize(row.get("issue_id"))
        if not issue_id:
            continue

        key_row = key_by_id.get(issue_id)
        if key_row is None:
            missing_key_rows += 1
            errors.append(f"missing key row for issue_id={issue_id}")
            continue

        existing_label = normalize_label(row.get("human_label"))
        if existing_label and not allow_overwrite:
            skipped_existing_rows += 1
            continue

        label, picked_source = pick_label(key_row, label_source)
        if label not in VALID_LABELS:
            invalid_label_rows += 1
            errors.append(f"invalid label for issue_id={issue_id}: {label!r}")
            continue

        evidence = pick_evidence(key_row)
        if not evidence:
            missing_evidence_rows += 1

        row["human_label"] = label
        row["human_confidence"] = pick_confidence(key_row, default_confidence)
        row["evidence_span"] = evidence
        row["notes"] = DEFAULT_NOTE.format(today=today, label_source=picked_source)
        prefilled_rows += 1

    report = {
        "status": "ok" if not errors else "error",
        "write": bool(write),
        "blind_sheet": relpath(blind_sheet),
        "key_sheet": relpath(key_sheet),
        "rows": len(blind_rows),
        "prefilled_rows": prefilled_rows,
        "skipped_existing_rows": skipped_existing_rows,
        "missing_key_rows": missing_key_rows,
        "invalid_label_rows": invalid_label_rows,
        "missing_evidence_rows": missing_evidence_rows,
        "label_source": label_source,
        "allow_overwrite": allow_overwrite,
        "default_confidence": default_confidence,
        "claim_boundary": (
            "AI prelabel draft only; requires human confirmation before IAA claim usage."
        ),
        "errors": errors,
    }

    if write:
        write_tsv(blind_sheet, blind_fields, blind_rows)
    write_json(report_json, report)
    write_md(report_md, report)
    return report


def main() -> None:
    args = parse_args()

    report = prelabel(
        blind_sheet=resolve(args.blind_sheet),
        key_sheet=resolve(args.key_sheet),
        report_json=resolve(args.report_json),
        report_md=resolve(args.report_md),
        label_source=args.label_source,
        default_confidence=normalize(args.default_confidence) or DEFAULT_CONFIDENCE,
        allow_overwrite=args.allow_overwrite,
        write=args.write,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    if report["status"] != "ok":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
