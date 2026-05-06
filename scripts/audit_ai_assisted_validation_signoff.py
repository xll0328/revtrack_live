from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
VALID_LABELS = {"fixed", "partially_fixed", "unresolved", "regressed"}
REQUIRED_FIELDS = [
    "signoff_rank",
    "queue_rank",
    "packet",
    "issue_id",
    "paper_title",
    "review_rating",
    "review_confidence",
    "review_excerpt",
    "top_response_excerpt",
    "aligned_response_excerpt",
    "revision_summary",
    "assistant_label",
    "assistant_evidence_span",
    "assistant_notes",
    "suggested_label",
    "audit_bucket",
    "audit_score",
    "priority_score",
    "model_snapshot",
    "reviewer_decision",
    "reviewer_final_label",
    "reviewer_confidence",
    "reviewer_evidence_span",
    "reviewer_notes",
    "signoff_status",
]
CONTEXT_FIELDS = [
    "paper_title",
    "review_excerpt",
    "top_response_excerpt",
    "aligned_response_excerpt",
    "revision_summary",
]
REVIEWER_FIELDS = [
    "reviewer_decision",
    "reviewer_final_label",
    "reviewer_confidence",
    "reviewer_evidence_span",
    "reviewer_notes",
]
HIGH_RISK_BUCKETS = {
    "minority_regressed",
    "minority_unresolved",
    "structured_error",
    "model_high_conflict",
}
NON_BLIND_WARNING = "must not be reported as independent human validation"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a six-pass audit over the AI-assisted validation signoff artifact."
    )
    parser.add_argument(
        "--signoff",
        default="outputs/day1/ai_assisted_validation_signoff/ai_assisted_validation_signoff.tsv",
    )
    parser.add_argument(
        "--queue",
        default="outputs/day1/paper_assets/human_validation_work_queue.csv",
    )
    parser.add_argument(
        "--manifest-md",
        default="outputs/day1/ai_assisted_validation_signoff/ai_assisted_validation_signoff_manifest.md",
    )
    parser.add_argument(
        "--packet-html",
        default="outputs/day1/ai_assisted_validation_signoff/ai_assisted_validation_signoff.html",
    )
    parser.add_argument(
        "--output-json",
        default="outputs/day1/ai_assisted_validation_signoff/ai_assisted_validation_signoff_audit.json",
    )
    parser.add_argument(
        "--output-md",
        default="outputs/day1/ai_assisted_validation_signoff/ai_assisted_validation_signoff_audit.md",
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


def load_csv(path: str | Path) -> tuple[list[str], list[dict[str, str]]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def load_tsv(path: str | Path) -> tuple[list[str], list[dict[str, str]]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return list(reader.fieldnames or []), list(reader)


def integer(value: str | int | None, default: int = 999999) -> int:
    if value in (None, ""):
        return default
    try:
        return int(value)
    except ValueError:
        return default


def numeric(value: str | int | float | None, default: float = 0.0) -> float:
    if value in (None, ""):
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def normalize_label(value: str | None) -> str:
    return (value or "").strip().lower()


def nonempty(row: dict[str, str], field: str) -> bool:
    return bool((row.get(field) or "").strip())


def add_pass(
    passes: list[dict[str, Any]],
    *,
    pass_id: str,
    status: str,
    summary: str,
    errors: list[str] | None = None,
    warnings: list[str] | None = None,
    evidence: dict[str, Any] | None = None,
) -> None:
    passes.append(
        {
            "pass_id": pass_id,
            "status": status,
            "summary": summary,
            "errors": errors or [],
            "warnings": warnings or [],
            "evidence": evidence or {},
        }
    )


def pass_status(errors: list[str], warnings: list[str] | None = None) -> str:
    if errors:
        return "fail"
    if warnings:
        return "warning"
    return "pass"


def identity_key(row: dict[str, str]) -> tuple[str, str]:
    return (row.get("packet", "").strip(), row.get("issue_id", "").strip())


def pending_queue_keys(queue_rows: list[dict[str, str]]) -> list[tuple[str, str]]:
    pending = [
        row
        for row in queue_rows
        if row.get("status", "").strip().lower() == "pending"
        and row.get("human_label_present", "").strip().lower() != "true"
    ]
    return [identity_key(row) for row in sorted(pending, key=lambda row: integer(row.get("queue_rank")))]


def all_queue_keys(queue_rows: list[dict[str, str]]) -> list[tuple[str, str]]:
    return [identity_key(row) for row in sorted(queue_rows, key=lambda row: integer(row.get("queue_rank")))]


def audit_schema_and_identity(fields: list[str], rows: list[dict[str, str]]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    missing_fields = [field for field in REQUIRED_FIELDS if field not in fields]
    if missing_fields:
        errors.append(f"missing required fields: {missing_fields}")

    keys = [identity_key(row) for row in rows]
    blank_keys = [key for key in keys if not all(key)]
    if blank_keys:
        errors.append(f"rows with blank packet/issue_id: {len(blank_keys)}")

    duplicates = sorted(key for key, count in Counter(keys).items() if count > 1 and all(key))
    if duplicates:
        errors.append(f"duplicate packet/issue_id rows: {duplicates[:10]}")

    ranks = [integer(row.get("signoff_rank")) for row in rows]
    if ranks != list(range(1, len(rows) + 1)):
        errors.append("signoff_rank is not sequential from 1")

    queue_ranks = [integer(row.get("queue_rank")) for row in rows]
    if queue_ranks != sorted(queue_ranks):
        warnings.append("queue_rank is not sorted ascending")

    return {
        "errors": errors,
        "warnings": warnings,
        "evidence": {
            "rows": len(rows),
            "fields": len(fields),
            "missing_fields": missing_fields,
            "duplicate_rows": len(duplicates),
        },
    }


def audit_queue_coverage(rows: list[dict[str, str]], queue_rows: list[dict[str, str]]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    signoff_keys = [identity_key(row) for row in rows]
    pending_keys = pending_queue_keys(queue_rows)
    queue_keys = pending_keys or all_queue_keys(queue_rows)
    coverage_scope = "pending" if pending_keys else "all"
    signoff_set = set(signoff_keys)
    queue_set = set(queue_keys)
    missing = sorted(queue_set - signoff_set)
    extra = sorted(signoff_set - queue_set)
    if missing:
        errors.append(f"signoff is missing {coverage_scope} queue rows: {missing[:10]}")
    if extra:
        errors.append(f"signoff contains rows outside {coverage_scope} queue: {extra[:10]}")
    if signoff_keys != queue_keys:
        warnings.append(f"signoff row order differs from {coverage_scope} queue order")

    return {
        "errors": errors,
        "warnings": warnings,
        "evidence": {
            "coverage_scope": coverage_scope,
            "pending_queue_rows": len(pending_keys),
            "expected_queue_rows": len(queue_keys),
            "all_queue_rows": len(queue_rows),
            "signoff_rows": len(signoff_keys),
            "missing_rows": len(missing),
            "extra_rows": len(extra),
        },
    }


def audit_context_completeness(rows: list[dict[str, str]]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    missing_by_field: dict[str, list[str]] = {}
    for field in CONTEXT_FIELDS:
        missing = [row["issue_id"] for row in rows if not nonempty(row, field)]
        if missing:
            missing_by_field[field] = missing
            errors.append(f"{field} missing for {len(missing)} rows")
    short_review = [
        row["issue_id"]
        for row in rows
        if nonempty(row, "review_excerpt") and len(row["review_excerpt"].split()) < 8
    ]
    if short_review:
        warnings.append(f"review_excerpt is very short for {len(short_review)} rows")
    return {
        "errors": errors,
        "warnings": warnings,
        "evidence": {
            "missing_by_field": {field: len(values) for field, values in missing_by_field.items()},
            "short_review_rows": len(short_review),
        },
    }


def audit_assistant_evidence(rows: list[dict[str, str]]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    invalid_assistant = [
        row["issue_id"] for row in rows if normalize_label(row.get("assistant_label")) not in VALID_LABELS
    ]
    invalid_suggested = [
        row["issue_id"]
        for row in rows
        if nonempty(row, "suggested_label") and normalize_label(row.get("suggested_label")) not in VALID_LABELS
    ]
    if invalid_assistant:
        errors.append(f"invalid assistant_label for {len(invalid_assistant)} rows")
    if invalid_suggested:
        errors.append(f"invalid suggested_label for {len(invalid_suggested)} rows")

    missing_notes = [row["issue_id"] for row in rows if not nonempty(row, "assistant_notes")]
    missing_evidence = [row["issue_id"] for row in rows if not nonempty(row, "assistant_evidence_span")]
    fallback_evidence = [
        row["issue_id"]
        for row in rows
        if row.get("assistant_evidence_span", "").startswith("Context fallback from ")
    ]
    missing_snapshot = [row["issue_id"] for row in rows if not nonempty(row, "model_snapshot")]
    if missing_notes:
        errors.append(f"assistant_notes missing for {len(missing_notes)} rows")
    if missing_snapshot:
        warnings.append(f"model_snapshot missing for {len(missing_snapshot)} rows")
    if missing_evidence:
        warnings.append(f"assistant_evidence_span missing for {len(missing_evidence)} rows")

    return {
        "errors": errors,
        "warnings": warnings,
        "evidence": {
            "invalid_assistant_labels": invalid_assistant,
            "invalid_suggested_labels": invalid_suggested,
            "missing_assistant_notes": missing_notes,
            "missing_assistant_evidence_span": missing_evidence,
            "fallback_assistant_evidence_span": fallback_evidence,
            "missing_model_snapshot": missing_snapshot,
            "assistant_distribution": dict(sorted(Counter(row["assistant_label"] for row in rows).items())),
        },
    }


def audit_non_blind_isolation(
    rows: list[dict[str, str]],
    *,
    manifest_md: Path,
    packet_html: Path,
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    prefilled_reviewer = [
        row["issue_id"]
        for row in rows
        if any(nonempty(row, field) for field in REVIEWER_FIELDS)
    ]
    bad_status = [
        row["issue_id"]
        for row in rows
        if row.get("signoff_status", "").strip() != "needs_human_review"
    ]
    if prefilled_reviewer:
        errors.append(f"reviewer signoff fields are prefilled for {len(prefilled_reviewer)} rows")
    if bad_status:
        errors.append(f"signoff_status is not needs_human_review for {len(bad_status)} rows")

    manifest_text = manifest_md.read_text(encoding="utf-8") if manifest_md.exists() else ""
    html_text = packet_html.read_text(encoding="utf-8") if packet_html.exists() else ""
    if NON_BLIND_WARNING not in manifest_text:
        errors.append("manifest is missing non-independent-validation warning")
    if NON_BLIND_WARNING not in html_text:
        errors.append("HTML packet is missing non-independent-validation warning")

    if "human_validation_batches" in relpath(packet_html) or "human_validation_batches" in relpath(manifest_md):
        warnings.append("signoff artifacts are stored near blind batch artifacts")

    return {
        "errors": errors,
        "warnings": warnings,
        "evidence": {
            "prefilled_reviewer_rows": prefilled_reviewer,
            "bad_status_rows": bad_status,
            "manifest_has_warning": NON_BLIND_WARNING in manifest_text,
            "html_has_warning": NON_BLIND_WARNING in html_text,
        },
    }


def audit_high_risk_review_order(rows: list[dict[str, str]]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    bucket_counts = Counter(row.get("audit_bucket", "") for row in rows)
    assistant_counts = Counter(row.get("assistant_label", "") for row in rows)
    high_risk_rows = [
        row for row in rows if row.get("audit_bucket", "") in HIGH_RISK_BUCKETS
    ]
    high_risk_top = [
        row
        for row in rows[: min(25, len(rows))]
        if row.get("audit_bucket", "") in HIGH_RISK_BUCKETS
    ]
    if high_risk_rows and len(high_risk_top) < min(len(high_risk_rows), 10):
        warnings.append("high-risk rows are not concentrated in the early signoff queue")

    top_cases = [
        {
            "signoff_rank": row.get("signoff_rank", ""),
            "issue_id": row.get("issue_id", ""),
            "assistant_label": row.get("assistant_label", ""),
            "audit_bucket": row.get("audit_bucket", ""),
            "audit_score": row.get("audit_score", ""),
        }
        for row in sorted(rows, key=lambda row: -numeric(row.get("audit_score")))[:10]
    ]
    return {
        "errors": errors,
        "warnings": warnings,
        "evidence": {
            "assistant_distribution": dict(sorted(assistant_counts.items())),
            "audit_bucket_distribution": dict(sorted(bucket_counts.items())),
            "high_risk_rows": len(high_risk_rows),
            "high_risk_rows_in_top_25": len(high_risk_top),
            "top_audit_score_cases": top_cases,
        },
    }


def overall_status(passes: list[dict[str, Any]]) -> str:
    if any(item["status"] == "fail" for item in passes):
        return "fail"
    if any(item["status"] == "warning" for item in passes):
        return "warning"
    return "pass"


def audit_signoff(
    *,
    signoff_path: str | Path,
    queue_path: str | Path,
    manifest_md: str | Path,
    packet_html: str | Path,
) -> dict[str, Any]:
    fields, rows = load_tsv(resolve_path(signoff_path))
    _, queue_rows = load_csv(resolve_path(queue_path))
    manifest_path = resolve_path(manifest_md)
    html_path = resolve_path(packet_html)
    passes: list[dict[str, Any]] = []

    schema = audit_schema_and_identity(fields, rows)
    add_pass(
        passes,
        pass_id="pass_1_schema_identity",
        status=pass_status(schema["errors"], schema["warnings"]),
        summary="Required fields, row identity, and rank ordering are valid.",
        **schema,
    )

    coverage = audit_queue_coverage(rows, queue_rows)
    add_pass(
        passes,
        pass_id="pass_2_queue_coverage",
        status=pass_status(coverage["errors"], coverage["warnings"]),
        summary="Signoff rows should exactly cover pending queue rows, or all queue rows after promotion.",
        **coverage,
    )

    context = audit_context_completeness(rows)
    add_pass(
        passes,
        pass_id="pass_3_context_completeness",
        status=pass_status(context["errors"], context["warnings"]),
        summary="Every signoff row should include full review, response, aligned context, and revision text.",
        **context,
    )

    assistant = audit_assistant_evidence(rows)
    add_pass(
        passes,
        pass_id="pass_4_assistant_evidence",
        status=pass_status(assistant["errors"], assistant["warnings"]),
        summary="Assistant labels and evidence should be valid and inspectable.",
        **assistant,
    )

    isolation = audit_non_blind_isolation(rows, manifest_md=manifest_path, packet_html=html_path)
    add_pass(
        passes,
        pass_id="pass_5_non_blind_isolation",
        status=pass_status(isolation["errors"], isolation["warnings"]),
        summary="AI-assisted signoff must stay separate from independent blind validation.",
        **isolation,
    )

    risk = audit_high_risk_review_order(rows)
    add_pass(
        passes,
        pass_id="pass_6_high_risk_triage",
        status=pass_status(risk["errors"], risk["warnings"]),
        summary="High-risk and minority-label rows should be visible early for final review.",
        **risk,
    )

    return {
        "artifact": relpath(resolve_path(signoff_path)),
        "overall_status": overall_status(passes),
        "passes": passes,
        "error_count": sum(len(item["errors"]) for item in passes),
        "warning_count": sum(len(item["warnings"]) for item in passes),
        "rows": len(rows),
    }


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def write_report_md(path: str | Path, report: dict[str, Any]) -> None:
    pass_rows = [
        [
            item["pass_id"],
            item["status"],
            str(len(item["errors"])),
            str(len(item["warnings"])),
            item["summary"],
        ]
        for item in report["passes"]
    ]
    lines = [
        "# AI-Assisted Validation Signoff Audit",
        "",
        f"Artifact: `{report['artifact']}`",
        f"Overall status: `{report['overall_status']}`",
        f"Rows: `{report['rows']}`",
        f"Errors: `{report['error_count']}`",
        f"Warnings: `{report['warning_count']}`",
        "",
        "## Six Review Passes",
        "",
        markdown_table(["pass", "status", "errors", "warnings", "summary"], pass_rows),
        "",
    ]
    for item in report["passes"]:
        lines.extend([f"## {item['pass_id']}", "", item["summary"], ""])
        if item["errors"]:
            lines.append("Errors:")
            for error in item["errors"]:
                lines.append(f"- {error}")
            lines.append("")
        if item["warnings"]:
            lines.append("Warnings:")
            for warning in item["warnings"]:
                lines.append(f"- {warning}")
            lines.append("")
        if item["pass_id"] == "pass_4_assistant_evidence":
            missing = item["evidence"].get("missing_assistant_evidence_span", [])
            if missing:
                lines.append("Rows missing assistant evidence spans:")
                for issue_id in missing:
                    lines.append(f"- `{issue_id}`")
                lines.append("")
            fallback = item["evidence"].get("fallback_assistant_evidence_span", [])
            if fallback:
                lines.append("Rows using context fallback evidence spans:")
                for issue_id in fallback:
                    lines.append(f"- `{issue_id}`")
                lines.append("")
        if item["pass_id"] == "pass_6_high_risk_triage":
            top_cases = item["evidence"].get("top_audit_score_cases", [])
            lines.append("Top audit-score cases:")
            lines.append(
                markdown_table(
                    ["rank", "issue", "assistant", "bucket", "score"],
                    [
                        [
                            row["signoff_rank"],
                            row["issue_id"],
                            row["assistant_label"],
                            row["audit_bucket"],
                            row["audit_score"],
                        ]
                        for row in top_cases
                    ],
                )
            )
            lines.append("")

    lines.extend(["## Interpretation", ""])
    if report["overall_status"] == "pass":
        lines.append("All six review passes are clean. The signoff artifact is ready for human final review.")
    elif report["overall_status"] == "warning":
        lines.append(
            "The signoff artifact is structurally ready, but warning rows should receive extra attention during final review."
        )
    else:
        lines.append("Fix the reported errors before using this signoff artifact for final review.")

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    report = audit_signoff(
        signoff_path=args.signoff,
        queue_path=args.queue,
        manifest_md=args.manifest_md,
        packet_html=args.packet_html,
    )
    output_json = resolve_path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report_md(args.output_md, report)
    print(json.dumps(report, indent=2, sort_keys=True))
    if args.fail_on_error and report["overall_status"] == "fail":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
