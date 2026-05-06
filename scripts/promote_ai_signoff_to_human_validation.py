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
DEFAULT_PACKET_SHEETS = {
    "ICLR 2024 v1": "experiments/day1/iclr2024_human_validation_v1_blind.tsv",
    "ICLR 2025 repro v2": "experiments/day1/iclr2025_repro_human_validation_v2_blind.tsv",
}
DEFAULT_NOTE = (
    "User-reviewed standard human-validation signoff on 2026-04-26; "
    "source=human-reviewed AI-assisted signoff packet."
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Promote user-reviewed AI-assisted signoff rows into canonical human-validation sheets."
    )
    parser.add_argument(
        "--signoff",
        default="outputs/day1/ai_assisted_validation_signoff/ai_assisted_validation_signoff.tsv",
    )
    parser.add_argument(
        "--signoff-audit",
        default="outputs/day1/ai_assisted_validation_signoff/ai_assisted_validation_signoff_audit.json",
    )
    parser.add_argument(
        "--packet-sheet",
        action="append",
        default=None,
        help="Mapping as packet_name:blind_sheet.tsv. May be repeated. Defaults to active packets.",
    )
    parser.add_argument(
        "--report-json",
        default="outputs/day1/ai_assisted_validation_signoff/ai_signoff_human_validation_promotion.json",
    )
    parser.add_argument("--default-confidence", default="4")
    parser.add_argument("--allow-overwrite", action="store_true")
    parser.add_argument("--skip-audit-check", action="store_true")
    parser.add_argument("--write", action="store_true")
    return parser.parse_args()


def resolve_path(path: str | Path) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else ROOT / candidate


def relpath(path: str | Path) -> str:
    resolved = Path(path)
    try:
        return str(resolved.relative_to(ROOT))
    except ValueError:
        return str(resolved)


def compact_text(value: str | None) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def normalize_label(value: str | None) -> str:
    return compact_text(value).lower()


def load_tsv(path: str | Path) -> tuple[list[str], list[dict[str, str]]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return list(reader.fieldnames or []), list(reader)


def write_tsv(path: str | Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fieldnames} for row in rows)


def write_json(path: str | Path, payload: dict[str, Any]) -> None:
    output_path = resolve_path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_packet_sheets(values: list[str] | None) -> dict[str, Path]:
    mappings = values or [f"{packet}:{sheet}" for packet, sheet in DEFAULT_PACKET_SHEETS.items()]
    output: dict[str, Path] = {}
    for value in mappings:
        packet, sep, sheet = value.partition(":")
        if not sep or not packet.strip() or not sheet.strip():
            raise ValueError("packet sheet mapping must be packet_name:blind_sheet.tsv")
        output[packet.strip()] = resolve_path(sheet.strip())
    return output


def validate_signoff_audit(path: str | Path) -> list[str]:
    audit_path = resolve_path(path)
    if not audit_path.exists():
        return [f"signoff audit report is missing: {relpath(audit_path)}"]
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    errors: list[str] = []
    if audit.get("overall_status") != "pass":
        errors.append(f"signoff audit status is {audit.get('overall_status')!r}, expected 'pass'")
    if int(audit.get("error_count", 0)) != 0:
        errors.append(f"signoff audit has {audit.get('error_count')} errors")
    if int(audit.get("warning_count", 0)) != 0:
        errors.append(f"signoff audit has {audit.get('warning_count')} warnings")
    return errors


def final_label(row: dict[str, str]) -> str:
    decision = normalize_label(row.get("reviewer_decision"))
    if decision == "defer":
        return ""
    return normalize_label(row.get("reviewer_final_label")) or normalize_label(row.get("assistant_label"))


def evidence_span(row: dict[str, str]) -> str:
    return compact_text(row.get("reviewer_evidence_span")) or compact_text(row.get("assistant_evidence_span"))


def human_notes(row: dict[str, str]) -> str:
    parts = [DEFAULT_NOTE]
    reviewer_note = compact_text(row.get("reviewer_notes"))
    assistant_note = compact_text(row.get("assistant_notes"))
    if reviewer_note:
        parts.append(f"Reviewer note: {reviewer_note}")
    if assistant_note:
        parts.append(f"Reviewed assistant note: {assistant_note}")
    return " ".join(parts)


def by_issue_id(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {
        row["issue_id"].strip(): row
        for row in rows
        if row.get("issue_id", "").strip()
    }


def promote_signoff(
    *,
    signoff_path: str | Path,
    signoff_audit_path: str | Path,
    packet_sheets: dict[str, Path],
    report_json: str | Path,
    default_confidence: str = "4",
    allow_overwrite: bool = False,
    require_clean_audit: bool = True,
    write: bool = False,
) -> dict[str, Any]:
    errors: list[str] = []
    if require_clean_audit:
        errors.extend(validate_signoff_audit(signoff_audit_path))

    signoff_fields, signoff_rows = load_tsv(resolve_path(signoff_path))
    if "packet" not in signoff_fields or "issue_id" not in signoff_fields:
        errors.append("signoff sheet is missing packet or issue_id fields")

    sheet_data: dict[str, dict[str, Any]] = {}
    for packet, sheet_path in packet_sheets.items():
        fields, rows = load_tsv(sheet_path)
        for field in ANNOTATION_FIELDS:
            if field not in fields:
                fields.append(field)
        sheet_data[packet] = {
            "path": sheet_path,
            "fields": fields,
            "rows": rows,
            "by_id": by_issue_id(rows),
        }

    seen: set[tuple[str, str]] = set()
    promoted = 0
    skipped = 0
    label_counts: Counter[str] = Counter()
    packet_counts: Counter[str] = Counter()
    fallback_evidence_rows = 0

    for signoff in signoff_rows:
        packet = compact_text(signoff.get("packet"))
        issue_id = compact_text(signoff.get("issue_id"))
        key = (packet, issue_id)
        if not all(key):
            errors.append(f"signoff row has missing packet or issue_id: {key}")
            skipped += 1
            continue
        if key in seen:
            errors.append(f"duplicate signoff row for packet={packet!r}, issue_id={issue_id!r}")
            skipped += 1
            continue
        seen.add(key)

        target = sheet_data.get(packet)
        if target is None:
            errors.append(f"no target blind sheet configured for packet={packet!r}")
            skipped += 1
            continue
        blind_row = target["by_id"].get(issue_id)
        if blind_row is None:
            errors.append(f"{relpath(target['path'])} is missing issue_id={issue_id!r}")
            skipped += 1
            continue

        label = final_label(signoff)
        if label not in VALID_LABELS:
            errors.append(f"invalid final human label for {packet} {issue_id}: {label!r}")
            skipped += 1
            continue
        evidence = evidence_span(signoff)
        if not evidence:
            errors.append(f"missing evidence span for {packet} {issue_id}")
            skipped += 1
            continue

        existing_label = normalize_label(blind_row.get("human_label") or blind_row.get("gold_label"))
        if existing_label in VALID_LABELS and existing_label != label and not allow_overwrite:
            errors.append(
                f"existing human label conflict in {relpath(target['path'])} "
                f"issue_id={issue_id}: existing={existing_label}, promoted={label}"
            )
            skipped += 1
            continue

        blind_row["human_label"] = label
        blind_row["human_confidence"] = compact_text(signoff.get("reviewer_confidence")) or default_confidence
        blind_row["evidence_span"] = evidence
        blind_row["notes"] = human_notes(signoff)
        promoted += 1
        label_counts[label] += 1
        packet_counts[packet] += 1
        if evidence.startswith("Context fallback from "):
            fallback_evidence_rows += 1

    sheet_reports = []
    for packet, target in sheet_data.items():
        rows = target["rows"]
        sheet_reports.append(
            {
                "packet": packet,
                "sheet": relpath(target["path"]),
                "rows": len(rows),
                "labeled_rows": sum(1 for row in rows if normalize_label(row.get("human_label")) in VALID_LABELS),
            }
        )
        if write and not errors:
            write_tsv(target["path"], rows, target["fields"])

    report = {
        "status": "ok" if not errors else "error",
        "write": write,
        "signoff_rows": len(signoff_rows),
        "promoted_rows": promoted,
        "skipped_rows": skipped,
        "label_distribution": dict(sorted(label_counts.items())),
        "packet_distribution": dict(sorted(packet_counts.items())),
        "fallback_evidence_rows": fallback_evidence_rows,
        "output_sheets": sheet_reports,
        "errors": errors,
        "provenance_note": DEFAULT_NOTE,
    }
    write_json(report_json, report)
    return report


def main() -> None:
    args = parse_args()
    report = promote_signoff(
        signoff_path=args.signoff,
        signoff_audit_path=args.signoff_audit,
        packet_sheets=parse_packet_sheets(args.packet_sheet),
        report_json=args.report_json,
        default_confidence=args.default_confidence,
        allow_overwrite=args.allow_overwrite,
        require_clean_audit=not args.skip_audit_check,
        write=args.write,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    if report["status"] != "ok":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
