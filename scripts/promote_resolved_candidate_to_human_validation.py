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
DEFAULT_NOTE_PREFIX = "User-confirmed single-pass standard validation"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Promote a user-confirmed resolved-label candidate sheet into a canonical blind "
            "human-validation sheet. Defaults to a dry run."
        )
    )
    parser.add_argument(
        "--resolved-candidate",
        default="experiments/day1/neurips2024_limit100_resolved_adjudication_v1.tsv",
    )
    parser.add_argument(
        "--blind-sheet",
        default="experiments/day1/neurips2024_limit100_human_validation_v1_blind.tsv",
    )
    parser.add_argument(
        "--report-json",
        default="outputs/day1/neurips2024_limit100_standard_validation_promotion_dry_run.json",
    )
    parser.add_argument(
        "--confirmation-note",
        default="",
        help="Required with --write. Example: 'User confirmed NeurIPS resolved candidate on YYYY-MM-DD.'",
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


def provenance_note(row: dict[str, str], confirmation_note: str) -> str:
    parts = [
        f"{DEFAULT_NOTE_PREFIX}; {compact(confirmation_note)}",
        "source=resolved-label candidate reviewed by user; not an independent two-annotator IAA pass.",
    ]
    action = compact(row.get("resolution_action"))
    reason = compact(row.get("resolution_reason"))
    if action:
        parts.append(f"Resolution action: {action}.")
    if reason:
        parts.append(f"Resolution reason: {reason}")
    return " ".join(parts)


def validate_required_fields(fields: list[str]) -> list[str]:
    required = {
        "issue_id",
        "resolved_label",
        "resolved_confidence",
        "resolved_evidence_span",
        "resolution_provenance",
        "review_required",
    }
    missing = sorted(required - set(fields))
    return [f"resolved candidate sheet missing fields: {missing}"] if missing else []


def promote(
    *,
    resolved_candidate_path: str | Path,
    blind_sheet_path: str | Path,
    report_json: str | Path,
    confirmation_note: str = "",
    allow_overwrite: bool = False,
    write: bool = False,
) -> dict[str, Any]:
    errors: list[str] = []
    candidate_fields, candidate_rows = load_tsv(resolved_candidate_path)
    blind_fields, blind_rows = load_tsv(blind_sheet_path)

    errors.extend(validate_required_fields(candidate_fields))
    if write and not compact(confirmation_note):
        errors.append("--confirmation-note is required when --write is set")

    for field in ANNOTATION_FIELDS:
        if field not in blind_fields:
            blind_fields.append(field)

    blind_by_id = by_issue_id(blind_rows)
    seen: set[str] = set()
    promoted = 0
    label_counts: Counter[str] = Counter()
    confidence_counts: Counter[str] = Counter()
    action_counts: Counter[str] = Counter()
    provenance_counts: Counter[str] = Counter()

    for row in candidate_rows:
        issue_id = compact(row.get("issue_id"))
        if not issue_id:
            errors.append("resolved candidate row has missing issue_id")
            continue
        if issue_id in seen:
            errors.append(f"duplicate resolved candidate row: {issue_id}")
            continue
        seen.add(issue_id)

        blind = blind_by_id.get(issue_id)
        if blind is None:
            errors.append(f"blind sheet is missing resolved candidate issue_id={issue_id}")
            continue

        label = normalize_label(row.get("resolved_label"))
        if label not in VALID_LABELS:
            errors.append(f"invalid resolved label for {issue_id}: {label!r}")
            continue

        confidence = compact(row.get("resolved_confidence"))
        if not confidence:
            errors.append(f"missing resolved_confidence for {issue_id}")
            continue

        evidence = compact(row.get("resolved_evidence_span"))
        if not evidence:
            errors.append(f"missing resolved_evidence_span for {issue_id}")
            continue

        provenance = compact(row.get("resolution_provenance"))
        provenance_counts[provenance or "missing"] += 1
        if provenance != "assistant_resolved_candidate_not_human_validation":
            errors.append(f"unexpected resolution_provenance for {issue_id}: {provenance!r}")
            continue

        if compact(row.get("review_required")).lower() != "true":
            errors.append(f"review_required must be true before promotion for {issue_id}")
            continue

        existing_label = normalize_label(blind.get("human_label"))
        if existing_label in VALID_LABELS and existing_label != label and not allow_overwrite:
            errors.append(f"existing label conflict for {issue_id}: existing={existing_label}, promoted={label}")
            continue

        if not errors:
            blind["human_label"] = label
            blind["human_confidence"] = confidence
            blind["evidence_span"] = evidence
            blind["notes"] = provenance_note(row, confirmation_note)

        promoted += 1
        label_counts[label] += 1
        confidence_counts[confidence] += 1
        action_counts[compact(row.get("resolution_action")) or "missing"] += 1

    missing_from_candidate = sorted(set(blind_by_id) - seen)
    if missing_from_candidate:
        errors.append(f"resolved candidate sheet is missing blind rows: {missing_from_candidate[:10]}")

    report = {
        "status": "ok" if not errors else "error",
        "write": bool(write),
        "resolved_candidate": relpath(resolve(resolved_candidate_path)),
        "blind_sheet": relpath(resolve(blind_sheet_path)),
        "rows": len(blind_rows),
        "candidate_rows": len(candidate_rows),
        "promotable_rows": promoted if not errors else 0,
        "label_distribution": dict(sorted(label_counts.items())) if not errors else {},
        "confidence_distribution": dict(sorted(confidence_counts.items())) if not errors else {},
        "resolution_action_distribution": dict(sorted(action_counts.items())) if not errors else {},
        "resolution_provenance_distribution": dict(sorted(provenance_counts.items())),
        "confirmation_note": compact(confirmation_note),
        "claim_boundary": (
            "Use as user-confirmed single-pass standard validation only after --write with an explicit "
            "confirmation note; do not report as independent two-annotator IAA."
        ),
        "errors": errors,
    }

    if write and not errors:
        write_tsv(blind_sheet_path, blind_fields, blind_rows)
        report["promoted_rows"] = promoted
    else:
        report["promoted_rows"] = 0
    write_json(report_json, report)
    return report


def main() -> None:
    args = parse_args()
    report = promote(
        resolved_candidate_path=args.resolved_candidate,
        blind_sheet_path=args.blind_sheet,
        report_json=args.report_json,
        confirmation_note=args.confirmation_note,
        allow_overwrite=args.allow_overwrite,
        write=args.write,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    if report["status"] != "ok":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
