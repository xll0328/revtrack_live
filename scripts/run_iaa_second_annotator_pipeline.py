from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANNOTATION_FIELDS = ["human_label", "human_confidence", "evidence_span", "notes"]
DEFAULT_BATCH_SHEETS = [
    ROOT / "experiments/day1/iaa_second_annotator_mini60_v1_blind_batch1.tsv",
    ROOT / "experiments/day1/iaa_second_annotator_mini60_v1_blind_batch2.tsv",
    ROOT / "experiments/day1/iaa_second_annotator_mini60_v1_blind_batch3.tsv",
]
DEFAULT_BLIND_SHEET = ROOT / "experiments/day1/iaa_second_annotator_mini60_v1_blind.tsv"
DEFAULT_KEY_SHEET = ROOT / "experiments/day1/iaa_second_annotator_mini60_v1_key.tsv"
DEFAULT_MERGED_OUTPUT = ROOT / "outputs/day1/iaa_second_annotator_mini60_v1_blind_merged.tsv"
DEFAULT_METRICS_JSON = ROOT / "outputs/day1/paper_assets/iaa_second_annotator_mini60_v1_metrics.json"
DEFAULT_MISMATCH_TSV = ROOT / "outputs/day1/paper_assets/iaa_second_annotator_mini60_v1_mismatches.tsv"
DEFAULT_REPORT_JSON = ROOT / "outputs/day1/paper_assets/iaa_second_annotator_mini60_v1_pipeline_report.json"
DEFAULT_REPORT_MD = ROOT / "outputs/day1/paper_assets/iaa_second_annotator_mini60_v1_pipeline_report.md"
DEFAULT_READINESS_JSON = ROOT / "outputs/day1/paper_assets/paper_readiness_audit.json"
DEFAULT_READINESS_MD = ROOT / "outputs/day1/paper_assets/paper_readiness_audit.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Merge second-annotator IAA batch files, evaluate agreement, and optionally "
            "refresh paper readiness."
        )
    )
    parser.add_argument(
        "--batch-sheet",
        action="append",
        default=[str(path) for path in DEFAULT_BATCH_SHEETS],
        help="TSV batch sheet path (repeatable). Defaults to the 3 mini60 batches.",
    )
    parser.add_argument("--blind-sheet", default=str(DEFAULT_BLIND_SHEET))
    parser.add_argument("--key-sheet", default=str(DEFAULT_KEY_SHEET))
    parser.add_argument(
        "--merged-output",
        default=str(DEFAULT_MERGED_OUTPUT),
        help="Merged blind-sheet output path (used when --write-canonical is not set).",
    )
    parser.add_argument(
        "--write-canonical",
        action="store_true",
        help="Overwrite --blind-sheet with merged annotations.",
    )
    parser.add_argument("--output-json", default=str(DEFAULT_METRICS_JSON))
    parser.add_argument("--mismatch-output", default=str(DEFAULT_MISMATCH_TSV))
    parser.add_argument("--report-json", default=str(DEFAULT_REPORT_JSON))
    parser.add_argument("--report-md", default=str(DEFAULT_REPORT_MD))
    parser.add_argument(
        "--require-complete",
        action="store_true",
        help="Fail if labeled rows are fewer than total blind rows.",
    )
    parser.add_argument(
        "--refresh-readiness",
        action="store_true",
        help="Run scripts/audit_paper_readiness.py with merged IAA inputs.",
    )
    parser.add_argument("--readiness-json", default=str(DEFAULT_READINESS_JSON))
    parser.add_argument("--readiness-md", default=str(DEFAULT_READINESS_MD))
    return parser.parse_args()


def resolve(path: str | Path) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else ROOT / candidate


def relpath(path: str | Path) -> str:
    absolute = resolve(path)
    try:
        return str(absolute.relative_to(ROOT))
    except ValueError:
        return str(absolute)


def load_tsv(path: str | Path) -> tuple[list[str], list[dict[str, str]]]:
    with resolve(path).open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return list(reader.fieldnames or []), list(reader)


def write_tsv(path: str | Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    output = resolve(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def normalize(value: str | None) -> str:
    return (value or "").strip()


def has_annotation(row: dict[str, str]) -> bool:
    return any(normalize(row.get(field)) for field in ANNOTATION_FIELDS)


def annotation_payload(row: dict[str, str]) -> dict[str, str]:
    payload = {field: normalize(row.get(field)) for field in ANNOTATION_FIELDS}
    if payload["human_label"]:
        payload["human_label"] = payload["human_label"].lower()
    return payload


def merge_batch_annotations(
    *,
    blind_rows: list[dict[str, str]],
    batch_entries: list[tuple[str, list[dict[str, str]]]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    blind_by_id = {normalize(row.get("issue_id")): row for row in blind_rows}
    blind_issue_ids = {issue_id for issue_id in blind_by_id if issue_id}
    seen_batch_issue_ids: set[str] = set()
    batch_coverage_by_file: dict[str, int] = {}
    annotation_by_id: dict[str, dict[str, str]] = {}
    errors: list[str] = []

    for batch_file, rows in batch_entries:
        covered = 0
        for row in rows:
            issue_id = normalize(row.get("issue_id"))
            if not issue_id:
                errors.append(f"{batch_file}: row with empty issue_id")
                continue
            if issue_id not in blind_issue_ids:
                errors.append(f"{batch_file}: unknown issue_id {issue_id}")
                continue
            covered += 1
            if issue_id in seen_batch_issue_ids:
                existing = annotation_by_id.get(issue_id)
                incoming = annotation_payload(row) if has_annotation(row) else None
                if existing and incoming and existing != incoming:
                    errors.append(
                        f"{batch_file}: conflicting annotations for issue_id {issue_id}"
                    )
                continue
            seen_batch_issue_ids.add(issue_id)

            if has_annotation(row):
                annotation_by_id[issue_id] = annotation_payload(row)
        batch_coverage_by_file[batch_file] = covered

    if errors:
        raise ValueError("; ".join(errors))

    merged_rows: list[dict[str, str]] = []
    for row in blind_rows:
        issue_id = normalize(row.get("issue_id"))
        updated = dict(row)
        annotation = annotation_by_id.get(issue_id)
        if annotation:
            for field in ANNOTATION_FIELDS:
                updated[field] = annotation[field]
        merged_rows.append(updated)

    labeled_rows = sum(1 for row in merged_rows if normalize(row.get("human_label")))
    summary = {
        "blind_rows": len(blind_rows),
        "batch_issue_rows": len(seen_batch_issue_ids),
        "labeled_rows": labeled_rows,
        "unlabeled_rows": len(blind_rows) - labeled_rows,
        "batch_coverage_by_file": batch_coverage_by_file,
        "missing_batch_issue_rows": len(blind_issue_ids - seen_batch_issue_ids),
    }
    return merged_rows, summary


def write_markdown(path: str | Path, payload: dict[str, Any]) -> None:
    lines = [
        "# IAA Second Annotator Pipeline Report",
        "",
        f"Status: `{payload['status']}`",
        "",
        "## Inputs",
        "",
        f"- blind_sheet: `{payload['blind_sheet']}`",
        f"- key_sheet: `{payload['key_sheet']}`",
        f"- batch_sheets: `{len(payload['batch_sheets'])}`",
    ]
    for batch in payload["batch_sheets"]:
        lines.append(f"  - `{batch}`")
    lines.extend(
        [
            "",
            "## Merge Summary",
            "",
            f"- merged_output: `{payload['merged_output']}`",
            f"- blind_rows: `{payload['merge']['blind_rows']}`",
            f"- labeled_rows: `{payload['merge']['labeled_rows']}`",
            f"- unlabeled_rows: `{payload['merge']['unlabeled_rows']}`",
            f"- missing_batch_issue_rows: `{payload['merge']['missing_batch_issue_rows']}`",
            "",
            "## Agreement",
            "",
            f"- agreement: `{payload['metrics'].get('agreement')}`",
            f"- cohen_kappa: `{payload['metrics'].get('cohen_kappa')}`",
            f"- mismatches: `{payload['metrics'].get('mismatches')}`",
            f"- metrics_json: `{payload['metrics_json']}`",
            f"- mismatch_tsv: `{payload['mismatch_tsv']}`",
        ]
    )
    if payload.get("readiness"):
        lines.extend(
            [
                "",
                "## Readiness Refresh",
                "",
                f"- readiness_status: `{payload['readiness']['overall_status']}`",
                f"- readiness_json: `{payload['readiness']['output_json']}`",
                f"- readiness_md: `{payload['readiness']['output_md']}`",
            ]
        )
    output = resolve(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def refresh_readiness(
    *,
    blind_sheet: Path,
    metrics_json: Path,
    output_json: Path,
    output_md: Path,
) -> dict[str, str]:
    cmd = [
        sys.executable,
        str(ROOT / "scripts" / "audit_paper_readiness.py"),
        "--iaa-second-annotator-blind-sheet",
        str(blind_sheet),
        "--iaa-second-annotator-metrics",
        str(metrics_json),
        "--output-json",
        str(output_json),
        "--output-md",
        str(output_md),
    ]
    subprocess.run(cmd, cwd=str(ROOT), check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    readiness = json.loads(output_json.read_text(encoding="utf-8"))
    return {
        "overall_status": readiness.get("overall_status", "unknown"),
        "output_json": relpath(output_json),
        "output_md": relpath(output_md),
    }


def main() -> None:
    args = parse_args()

    blind_sheet = resolve(args.blind_sheet)
    key_sheet = resolve(args.key_sheet)
    batch_sheets = [resolve(path) for path in args.batch_sheet]
    merged_output = blind_sheet if args.write_canonical else resolve(args.merged_output)

    blind_fields, blind_rows = load_tsv(blind_sheet)
    batch_entries: list[tuple[str, list[dict[str, str]]]] = []
    for path in batch_sheets:
        fields, rows = load_tsv(path)
        missing = [field for field in ["issue_id", *ANNOTATION_FIELDS] if field not in fields]
        if missing:
            raise SystemExit(f"{path}: missing required fields {missing}")
        batch_entries.append((relpath(path), rows))

    merged_rows, merge_summary = merge_batch_annotations(blind_rows=blind_rows, batch_entries=batch_entries)
    if args.require_complete and merge_summary["labeled_rows"] < merge_summary["blind_rows"]:
        raise SystemExit(
            "--require-complete set, but labeled_rows="
            f"{merge_summary['labeled_rows']} < blind_rows={merge_summary['blind_rows']}"
        )

    write_tsv(merged_output, blind_fields, merged_rows)

    from evaluate_human_validation import evaluate, load_tsv as eval_load_tsv, write_tsv as eval_write_tsv  # type: ignore

    metrics, mismatches = evaluate(merged_rows, eval_load_tsv(key_sheet))
    output_json = resolve(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    mismatch_output = resolve(args.mismatch_output)
    eval_write_tsv(
        mismatch_output,
        mismatches,
        [
            "issue_id",
            "assistant_label",
            "human_label",
            "audit_bucket",
            "assistant_evidence_span",
            "human_evidence_span",
            "human_notes",
        ],
    )

    payload: dict[str, Any] = {
        "status": "ok",
        "blind_sheet": relpath(blind_sheet),
        "key_sheet": relpath(key_sheet),
        "batch_sheets": [relpath(path) for path in batch_sheets],
        "merged_output": relpath(merged_output),
        "metrics_json": relpath(output_json),
        "mismatch_tsv": relpath(mismatch_output),
        "merge": merge_summary,
        "metrics": {
            "rows": metrics.get("rows"),
            "labeled_rows": metrics.get("labeled_rows"),
            "agreement": metrics.get("agreement"),
            "cohen_kappa": metrics.get("cohen_kappa"),
            "mismatches": metrics.get("mismatches"),
        },
    }

    if args.refresh_readiness:
        payload["readiness"] = refresh_readiness(
            blind_sheet=merged_output,
            metrics_json=output_json,
            output_json=resolve(args.readiness_json),
            output_md=resolve(args.readiness_md),
        )

    report_json = resolve(args.report_json)
    report_json.parent.mkdir(parents=True, exist_ok=True)
    report_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(args.report_md, payload)

    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
