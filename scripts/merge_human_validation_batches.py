from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
LABEL_ORDER = ["fixed", "partially_fixed", "unresolved", "regressed"]
VALID_LABELS = set(LABEL_ORDER)
ANNOTATION_FIELDS = ["human_label", "human_confidence", "evidence_span", "notes"]
REQUIRED_BATCH_FIELDS = [
    "batch_rank",
    "global_queue_rank",
    "source_packet",
    "issue_id",
    *ANNOTATION_FIELDS,
]
FORBIDDEN_BATCH_FIELDS = {
    "assistant_label",
    "suggested_label",
    "audit_bucket",
    "heuristic_label",
    "tfidf_label",
    "modernbert_label",
    "mpnet_label",
    "issue_ledger_label",
    "structured_label",
    "gold_label",
    "silver_label",
    "assistant_evidence_span",
    "assistant_notes",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Merge completed blind batch annotations back into human-validation sheets."
    )
    parser.add_argument(
        "--queue",
        default="outputs/day1/paper_assets/human_validation_work_queue.csv",
        help="CSV queue exported by export_human_validation_queue.py.",
    )
    parser.add_argument("--batch-dir", default="outputs/day1/human_validation_batches")
    parser.add_argument("--batch-glob", default="*_blind.tsv")
    parser.add_argument("--output-dir", default="outputs/day1/human_validation_batch_ingest")
    parser.add_argument(
        "--write-canonical",
        action="store_true",
        help="Overwrite the original blind sheets referenced by the queue.",
    )
    parser.add_argument(
        "--allow-overwrite",
        action="store_true",
        help="Allow a batch annotation to replace an existing canonical human_label.",
    )
    parser.add_argument(
        "--output-json",
        default="outputs/day1/paper_assets/human_validation_batch_ingest_report.json",
    )
    parser.add_argument(
        "--output-md",
        default="outputs/day1/paper_assets/human_validation_batch_ingest_report.md",
    )
    parser.add_argument("--fail-on-error", action="store_true")
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


def load_csv(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def load_tsv_with_fields(path: str | Path) -> tuple[list[str], list[dict[str, str]]]:
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


def normalize_label(value: str | None) -> str:
    return (value or "").strip().lower()


def clean_annotation(row: dict[str, str]) -> dict[str, str]:
    output = {field: (row.get(field, "") or "").strip() for field in ANNOTATION_FIELDS}
    output["human_label"] = normalize_label(output["human_label"])
    return output


def has_annotation_text(row: dict[str, str]) -> bool:
    return any((row.get(field, "") or "").strip() for field in ANNOTATION_FIELDS)


def queue_index(queue_rows: list[dict[str, str]]) -> dict[tuple[str, str], dict[str, str]]:
    index: dict[tuple[str, str], dict[str, str]] = {}
    for row in queue_rows:
        key = (row.get("packet", "").strip(), row.get("issue_id", "").strip())
        if not all(key):
            continue
        if key in index:
            raise ValueError(f"Duplicate queue key: packet={key[0]!r}, issue_id={key[1]!r}")
        index[key] = row
    return index


def load_batch_rows(
    *,
    batch_dir: str | Path,
    batch_glob: str,
) -> tuple[list[dict[str, Any]], list[dict[str, str]], list[str]]:
    batch_root = resolve_path(batch_dir)
    files = sorted(batch_root.glob(batch_glob))
    errors: list[str] = []
    batch_reports: list[dict[str, Any]] = []
    rows: list[dict[str, str]] = []

    if not files:
        errors.append(f"No batch files matched {batch_root / batch_glob}")

    for path in files:
        fields, batch_rows = load_tsv_with_fields(path)
        leaked_fields = sorted(FORBIDDEN_BATCH_FIELDS.intersection(fields))
        missing_fields = [field for field in REQUIRED_BATCH_FIELDS if field not in fields]
        if leaked_fields:
            errors.append(f"{relpath(path)} exposes forbidden fields: {leaked_fields}")
        if missing_fields:
            errors.append(f"{relpath(path)} is missing required fields: {missing_fields}")

        annotated_rows = sum(1 for row in batch_rows if has_annotation_text(row))
        batch_reports.append(
            {
                "batch_file": relpath(path),
                "rows": len(batch_rows),
                "annotated_rows": annotated_rows,
                "leaked_fields": leaked_fields,
                "missing_fields": missing_fields,
            }
        )
        for row in batch_rows:
            row["_batch_file"] = relpath(path)
            rows.append(row)

    return batch_reports, rows, errors


def collect_updates(
    batch_rows: list[dict[str, str]],
    queue_rows: list[dict[str, str]],
) -> tuple[dict[str, dict[str, dict[str, str]]], dict[str, Any]]:
    index = queue_index(queue_rows)
    seen_batch_keys: set[tuple[str, str]] = set()
    updates: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    invalid_label_rows: list[dict[str, str]] = []
    missing_queue_rows: list[dict[str, str]] = []
    duplicate_batch_rows: list[dict[str, str]] = []
    incomplete_detail_rows: list[dict[str, str]] = []
    blank_rows = 0

    for row in batch_rows:
        packet = row.get("source_packet", "").strip()
        issue_id = row.get("issue_id", "").strip()
        batch_file = row.get("_batch_file", "")
        key = (packet, issue_id)
        if not all(key):
            missing_queue_rows.append(
                {"batch_file": batch_file, "source_packet": packet, "issue_id": issue_id}
            )
            continue
        if key in seen_batch_keys:
            duplicate_batch_rows.append(
                {"batch_file": batch_file, "source_packet": packet, "issue_id": issue_id}
            )
            continue
        seen_batch_keys.add(key)

        queue_row = index.get(key)
        if queue_row is None:
            missing_queue_rows.append(
                {"batch_file": batch_file, "source_packet": packet, "issue_id": issue_id}
            )
            continue

        if not has_annotation_text(row):
            blank_rows += 1
            continue

        annotation = clean_annotation(row)
        human_label = annotation["human_label"]
        if human_label not in VALID_LABELS:
            invalid_label_rows.append(
                {
                    "batch_file": batch_file,
                    "source_packet": packet,
                    "issue_id": issue_id,
                    "human_label": row.get("human_label", ""),
                }
            )
            continue
        if any(not annotation[field] for field in ["human_confidence", "evidence_span", "notes"]):
            incomplete_detail_rows.append(
                {"batch_file": batch_file, "source_packet": packet, "issue_id": issue_id}
            )

        blind_sheet = queue_row.get("blind_sheet", "").strip()
        updates[blind_sheet][issue_id] = annotation

    diagnostics = {
        "blank_batch_rows": blank_rows,
        "invalid_label_rows": invalid_label_rows,
        "missing_queue_rows": missing_queue_rows,
        "duplicate_batch_rows": duplicate_batch_rows,
        "incomplete_detail_rows": incomplete_detail_rows,
    }
    return updates, diagnostics


def output_sheet_path(output_dir: str | Path, blind_sheet: str) -> Path:
    return resolve_path(output_dir) / "sheets" / Path(blind_sheet).name


def merge_sheets(
    *,
    queue_rows: list[dict[str, str]],
    updates: dict[str, dict[str, dict[str, str]]],
    output_dir: str | Path,
    write_canonical: bool,
    allow_overwrite: bool,
) -> tuple[list[dict[str, Any]], list[dict[str, str]], list[str]]:
    sheets = sorted({row.get("blind_sheet", "").strip() for row in queue_rows if row.get("blind_sheet", "").strip()})
    sheet_reports: list[dict[str, Any]] = []
    conflicts: list[dict[str, str]] = []
    errors: list[str] = []

    for blind_sheet in sheets:
        source_path = resolve_path(blind_sheet)
        fields, rows = load_tsv_with_fields(source_path)
        for field in ANNOTATION_FIELDS:
            if field not in fields:
                fields.append(field)

        sheet_updates = updates.get(blind_sheet, {})
        seen_issue_ids: set[str] = set()
        merged_rows = 0
        for row in rows:
            issue_id = row.get("issue_id", "").strip()
            if not issue_id:
                continue
            seen_issue_ids.add(issue_id)
            annotation = sheet_updates.get(issue_id)
            if annotation is None:
                continue
            existing_label = normalize_label(row.get("human_label") or row.get("gold_label"))
            if existing_label in VALID_LABELS and existing_label != annotation["human_label"] and not allow_overwrite:
                conflicts.append(
                    {
                        "blind_sheet": blind_sheet,
                        "issue_id": issue_id,
                        "existing_label": existing_label,
                        "batch_label": annotation["human_label"],
                    }
                )
                continue
            for field in ANNOTATION_FIELDS:
                row[field] = annotation[field]
            merged_rows += 1

        missing_issue_ids = sorted(set(sheet_updates) - seen_issue_ids)
        if missing_issue_ids:
            errors.append(f"{blind_sheet} is missing batch issue_ids: {missing_issue_ids}")

        target_path = source_path if write_canonical else output_sheet_path(output_dir, blind_sheet)
        write_tsv(target_path, rows, fields)
        labeled_rows = sum(1 for row in rows if normalize_label(row.get("human_label")) in VALID_LABELS)
        sheet_reports.append(
            {
                "blind_sheet": blind_sheet,
                "output_sheet": relpath(target_path),
                "rows": len(rows),
                "merged_rows": merged_rows,
                "labeled_rows": labeled_rows,
            }
        )

    return sheet_reports, conflicts, errors


def count_by_packet(batch_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    packet_counts: Counter[str] = Counter()
    annotated_counts: Counter[str] = Counter()
    for row in batch_rows:
        packet = row.get("source_packet", "") or "unknown"
        packet_counts[packet] += 1
        if normalize_label(row.get("human_label")) in VALID_LABELS:
            annotated_counts[packet] += 1
    return [
        {"source_packet": packet, "rows": count, "completed_rows": annotated_counts[packet]}
        for packet, count in sorted(packet_counts.items())
    ]


def report_errors(report: dict[str, Any]) -> list[str]:
    errors = list(report.get("errors", []))
    errors.extend(
        f"invalid label in {row['batch_file']} issue_id={row['issue_id']}: {row['human_label']!r}"
        for row in report.get("invalid_label_rows", [])
    )
    errors.extend(
        f"missing queue row for {row['batch_file']} packet={row['source_packet']!r} issue_id={row['issue_id']!r}"
        for row in report.get("missing_queue_rows", [])
    )
    errors.extend(
        f"duplicate batch row for packet={row['source_packet']!r} issue_id={row['issue_id']!r}"
        for row in report.get("duplicate_batch_rows", [])
    )
    errors.extend(
        f"canonical label conflict in {row['blind_sheet']} issue_id={row['issue_id']}"
        for row in report.get("merge_conflicts", [])
    )
    return errors


def build_report(
    *,
    queue_rows: list[dict[str, str]],
    batch_reports: list[dict[str, Any]],
    batch_rows: list[dict[str, str]],
    updates: dict[str, dict[str, dict[str, str]]],
    diagnostics: dict[str, Any],
    sheet_reports: list[dict[str, Any]],
    merge_conflicts: list[dict[str, str]],
    errors: list[str],
    output_dir: str | Path,
    write_canonical: bool,
) -> dict[str, Any]:
    completed_batch_rows = sum(len(sheet_updates) for sheet_updates in updates.values())
    merged_rows = sum(int(sheet["merged_rows"]) for sheet in sheet_reports)
    report = {
        "status": "ok",
        "queue_rows": len(queue_rows),
        "batch_files": batch_reports,
        "batch_rows": len(batch_rows),
        "completed_batch_rows": completed_batch_rows,
        "blank_batch_rows": diagnostics["blank_batch_rows"],
        "merged_rows": merged_rows,
        "write_canonical": write_canonical,
        "output_dir": relpath(resolve_path(output_dir)),
        "by_packet": count_by_packet(batch_rows),
        "sheets": sheet_reports,
        "invalid_label_rows": diagnostics["invalid_label_rows"],
        "missing_queue_rows": diagnostics["missing_queue_rows"],
        "duplicate_batch_rows": diagnostics["duplicate_batch_rows"],
        "incomplete_detail_rows": diagnostics["incomplete_detail_rows"],
        "merge_conflicts": merge_conflicts,
        "errors": errors,
    }
    flattened_errors = report_errors(report)
    report["error_count"] = len(flattened_errors)
    report["status"] = "ok" if not flattened_errors else "error"
    report["error_messages"] = flattened_errors
    return report


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def write_report_md(path: str | Path, report: dict[str, Any]) -> None:
    sheet_rows = [
        [
            sheet["blind_sheet"],
            sheet["output_sheet"],
            str(sheet["rows"]),
            str(sheet["merged_rows"]),
            str(sheet["labeled_rows"]),
        ]
        for sheet in report["sheets"]
    ]
    packet_rows = [
        [row["source_packet"], str(row["rows"]), str(row["completed_rows"])]
        for row in report["by_packet"]
    ]
    lines = [
        "# Human Validation Batch Ingest Report",
        "",
        f"Status: `{report['status']}`",
        "",
        "## Summary",
        "",
        f"- Queue rows: `{report['queue_rows']}`",
        f"- Batch rows scanned: `{report['batch_rows']}`",
        f"- Completed valid batch rows: `{report['completed_batch_rows']}`",
        f"- Blank batch rows: `{report['blank_batch_rows']}`",
        f"- Merged rows: `{report['merged_rows']}`",
        f"- Canonical write: `{str(report['write_canonical']).lower()}`",
        f"- Error count: `{report['error_count']}`",
        "",
        "## By Packet",
        "",
        markdown_table(["source packet", "batch rows", "completed rows"], packet_rows),
        "",
        "## Sheets",
        "",
        markdown_table(["blind sheet", "output sheet", "rows", "merged", "labeled"], sheet_rows),
        "",
    ]
    if report["incomplete_detail_rows"]:
        lines.extend(
            [
                "## Incomplete Detail Rows",
                "",
                "These rows have a valid human_label but are missing at least one of human_confidence, evidence_span, or notes.",
                "",
            ]
        )
        for row in report["incomplete_detail_rows"]:
            lines.append(
                f"- {row['batch_file']} `{row['source_packet']}` `{row['issue_id']}`"
            )
        lines.append("")
    if report["error_messages"]:
        lines.extend(["## Errors", ""])
        for message in report["error_messages"]:
            lines.append(f"- {message}")
        lines.append("")
    lines.extend(["## Next Step", ""])
    if report["completed_batch_rows"] == 0:
        lines.append("No completed human labels were found in the exported batch TSVs yet.")
    elif not report["write_canonical"]:
        lines.append(
            "Review the merged sheet copies, then rerun with `--write-canonical` to update the original blind sheets before agreement evaluation."
        )
    else:
        lines.append(
            "Run `scripts/evaluate_human_validation.py` on the updated blind sheets and regenerate the human-validation queue, batch artifacts, and paper-readiness audit."
        )

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def ingest_batches(
    *,
    queue_path: str | Path,
    batch_dir: str | Path,
    batch_glob: str = "*_blind.tsv",
    output_dir: str | Path,
    write_canonical: bool = False,
    allow_overwrite: bool = False,
) -> dict[str, Any]:
    queue_rows = load_csv(resolve_path(queue_path))
    pending_rows = [
        row
        for row in queue_rows
        if row.get("status", "").strip().lower() == "pending"
        and row.get("human_label_present", "").strip().lower() != "true"
    ]
    batch_reports, batch_rows, batch_errors = load_batch_rows(batch_dir=batch_dir, batch_glob=batch_glob)
    if not pending_rows:
        batch_errors = [
            error for error in batch_errors if not error.startswith("No batch files matched ")
        ]
    updates, diagnostics = collect_updates(batch_rows, queue_rows)
    sheet_reports, merge_conflicts, merge_errors = merge_sheets(
        queue_rows=queue_rows,
        updates=updates,
        output_dir=output_dir,
        write_canonical=write_canonical,
        allow_overwrite=allow_overwrite,
    )
    return build_report(
        queue_rows=queue_rows,
        batch_reports=batch_reports,
        batch_rows=batch_rows,
        updates=updates,
        diagnostics=diagnostics,
        sheet_reports=sheet_reports,
        merge_conflicts=merge_conflicts,
        errors=[*batch_errors, *merge_errors],
        output_dir=output_dir,
        write_canonical=write_canonical,
    )


def main() -> None:
    args = parse_args()
    report = ingest_batches(
        queue_path=args.queue,
        batch_dir=args.batch_dir,
        batch_glob=args.batch_glob,
        output_dir=args.output_dir,
        write_canonical=args.write_canonical,
        allow_overwrite=args.allow_overwrite,
    )
    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report_md(args.output_md, report)
    print(json.dumps(report, indent=2, sort_keys=True))
    if args.fail_on_error and report["status"] != "ok":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
