from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


VALID_LABELS = {"fixed", "partially_fixed", "unresolved", "regressed"}
MODEL_FIELDS = [
    "tfidf_label",
    "modernbert_label",
    "mpnet_label",
    "issue_ledger_label",
    "structured_label",
]
REGRESSION_CUES = {
    "worse",
    "worsen",
    "regress",
    "decrease",
    "decreased",
    "degrade",
    "degraded",
    "hurt",
    "harm",
    "incorrect",
    "inconsistent",
    "fail",
    "failure",
    "removed",
    "introduce",
    "introduced",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run six self-checks over an assistant adjudication draft.")
    parser.add_argument("--dataset-name", required=True)
    parser.add_argument("--adjudication", required=True)
    parser.add_argument("--blind", required=True)
    parser.add_argument("--key", required=True)
    parser.add_argument("--frontier", required=True)
    parser.add_argument("--packet-audit", required=True)
    parser.add_argument("--candidate-gate", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    return parser.parse_args()


def load_tsv(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def normalize(value: str | None) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def norm_label(value: str | None) -> str:
    return normalize(value).lower()


def by_id(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row["issue_id"]: row for row in rows if row.get("issue_id")}


def duplicate_ids(rows: list[dict[str, str]]) -> list[str]:
    counts = Counter(row.get("issue_id", "") for row in rows)
    return sorted(issue_id for issue_id, count in counts.items() if issue_id and count > 1)


def add_check(checks: list[dict[str, Any]], check_id: str, status: str, summary: str, evidence: dict[str, Any]) -> None:
    checks.append({"check_id": check_id, "status": status, "summary": summary, "evidence": evidence})


def label_distribution_check(rows: list[dict[str, str]]) -> tuple[str, dict[str, Any]]:
    labels = Counter(norm_label(row.get("assistant_label")) for row in rows)
    total = sum(labels.values())
    max_label, max_count = labels.most_common(1)[0] if labels else ("", 0)
    regressed_rate = labels.get("regressed", 0) / total if total else 0.0
    max_rate = max_count / total if total else 0.0
    status = "pass"
    if max_rate >= 0.85 or regressed_rate >= 0.50:
        status = "warning"
    return status, {
        "label_distribution": dict(sorted(labels.items())),
        "max_label": max_label,
        "max_rate": max_rate,
        "regressed_rate": regressed_rate,
    }


def model_support_check(rows: list[dict[str, str]]) -> tuple[str, dict[str, Any]]:
    support_counts: Counter[int] = Counter()
    weak_rows: list[str] = []
    for row in rows:
        label = norm_label(row.get("assistant_label"))
        support = sum(1 for field in MODEL_FIELDS if norm_label(row.get(field)) == label)
        support_counts[support] += 1
        if support <= 1:
            weak_rows.append(row.get("issue_id", ""))
    weak_rate = len(weak_rows) / len(rows) if rows else 0.0
    status = "warning" if weak_rate >= 0.50 else "pass"
    return status, {
        "support_count_distribution": dict(sorted(support_counts.items())),
        "weak_support_rows": len(weak_rows),
        "weak_support_rate": weak_rate,
        "weak_support_examples": weak_rows[:10],
    }


def regression_cue_check(rows: list[dict[str, str]]) -> tuple[str, dict[str, Any]]:
    regressed = [row for row in rows if norm_label(row.get("assistant_label")) == "regressed"]
    missing: list[str] = []
    for row in regressed:
        text = " ".join(
            [
                row.get("evidence_span", ""),
                row.get("aligned_response_excerpt", ""),
                row.get("revision_summary", ""),
                row.get("notes", ""),
            ]
        ).lower()
        if not any(cue in text for cue in REGRESSION_CUES):
            missing.append(row.get("issue_id", ""))
    missing_rate = len(missing) / len(regressed) if regressed else 0.0
    status = "warning" if regressed and missing_rate >= 0.50 else "pass"
    return status, {
        "regressed_rows": len(regressed),
        "regressed_rows_without_explicit_regression_cue": len(missing),
        "missing_cue_rate": missing_rate,
        "missing_cue_examples": missing[:10],
    }


def audit(
    *,
    dataset_name: str,
    adjudication_rows: list[dict[str, str]],
    blind_rows: list[dict[str, str]],
    key_rows: list[dict[str, str]],
    frontier_rows: list[dict[str, str]],
    packet_audit: dict[str, Any],
    candidate_gate: dict[str, Any],
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    add_check(
        checks,
        "pass_1_packet_integrity",
        "pass" if packet_audit.get("ok") else "blocker",
        "Blind/key/audit packet must have passed its packet audit before draft review.",
        {
            "ok": packet_audit.get("ok"),
            "blind_rows": packet_audit.get("blind_rows"),
            "key_rows": packet_audit.get("key_rows"),
            "audit_rows": packet_audit.get("audit_rows"),
            "errors": packet_audit.get("errors", []),
            "warnings": packet_audit.get("warnings", []),
        },
    )

    add_check(
        checks,
        "pass_2_candidate_gate",
        "pass" if candidate_gate.get("ok") else "blocker",
        "Candidate pool must pass count, completeness, duplicate-ID, and disagreement gates.",
        {
            "ok": candidate_gate.get("ok"),
            "rows": candidate_gate.get("rows"),
            "complete_rate": candidate_gate.get("complete_rate"),
            "disagreement_rows": candidate_gate.get("disagreement", {}).get("disagreement_rows"),
            "high_disagreement_rows": candidate_gate.get("disagreement", {}).get("high_disagreement_rows"),
            "errors": candidate_gate.get("errors", []),
            "warnings": candidate_gate.get("warnings", []),
        },
    )

    ids = {
        "adjudication": set(by_id(adjudication_rows)),
        "blind": set(by_id(blind_rows)),
        "key": set(by_id(key_rows)),
        "frontier": set(by_id(frontier_rows)),
    }
    duplicate_report = {
        "adjudication": duplicate_ids(adjudication_rows),
        "blind": duplicate_ids(blind_rows),
        "key": duplicate_ids(key_rows),
        "frontier": duplicate_ids(frontier_rows),
    }
    identity_ok = (
        ids["adjudication"] == ids["blind"] == ids["key"] == ids["frontier"]
        and not any(duplicate_report.values())
    )
    add_check(
        checks,
        "pass_3_row_identity",
        "pass" if identity_ok else "blocker",
        "Adjudication, blind, key, and source frontier rows must align exactly.",
        {
            "row_counts": {
                "adjudication": len(adjudication_rows),
                "blind": len(blind_rows),
                "key": len(key_rows),
                "frontier": len(frontier_rows),
            },
            "duplicate_issue_ids": duplicate_report,
            "id_set_match": identity_ok,
        },
    )

    invalid_labels = [
        row.get("issue_id", "")
        for row in adjudication_rows
        if norm_label(row.get("assistant_label")) not in VALID_LABELS
    ]
    missing_evidence = [row.get("issue_id", "") for row in adjudication_rows if not normalize(row.get("evidence_span"))]
    missing_confidence = [
        row.get("issue_id", "") for row in adjudication_rows if not normalize(row.get("assistant_confidence"))
    ]
    add_check(
        checks,
        "pass_4_label_evidence_completeness",
        "pass" if not invalid_labels and not missing_evidence and not missing_confidence else "blocker",
        "Every draft row must have a valid label, confidence, and evidence span.",
        {
            "invalid_labels": invalid_labels,
            "missing_evidence": missing_evidence,
            "missing_confidence": missing_confidence,
        },
    )

    bad_provenance = [
        row.get("issue_id", "")
        for row in adjudication_rows
        if row.get("provenance") != "provisional_assistant_adjudication_not_human_validation"
    ]
    add_check(
        checks,
        "pass_5_provenance_boundary",
        "pass" if not bad_provenance else "blocker",
        "Draft rows must remain explicitly marked as not human validation.",
        {"bad_provenance_rows": bad_provenance},
    )

    status, evidence = label_distribution_check(adjudication_rows)
    add_check(
        checks,
        "pass_6_distribution_sanity",
        status,
        "Extreme label concentration should block promotion until a human reviews the frontier.",
        evidence,
    )

    status, evidence = model_support_check(adjudication_rows)
    add_check(
        checks,
        "pass_7_model_support_sanity",
        status,
        "Rows with labels supported by only one model are useful for review but risky as auto labels.",
        evidence,
    )

    status, evidence = regression_cue_check(adjudication_rows)
    add_check(
        checks,
        "pass_8_regression_cue_sanity",
        status,
        "Regressed labels should be treated cautiously when explicit regression cues are absent.",
        evidence,
    )

    blockers = [check for check in checks if check["status"] == "blocker"]
    warnings = [check for check in checks if check["status"] == "warning"]
    return {
        "dataset_name": dataset_name,
        "status": "blocked" if blockers else ("needs_review" if warnings else "pass"),
        "human_validation_status": "not_human_validated",
        "checks": checks,
        "blockers": blockers,
        "warnings": warnings,
        "review_recommendation": (
            "Do not promote automatically. Use as an assistant-adjudication draft for user review."
            if warnings or blockers
            else "Draft passes automated checks, but still requires user confirmation before standard validation."
        ),
    }


def write_markdown(path: str | Path, report: dict[str, Any]) -> None:
    lines = [
        f"# {report['dataset_name']} Adjudication Draft Audit",
        "",
        f"Status: `{report['status']}`",
        "",
        f"Human-validation status: `{report['human_validation_status']}`",
        "",
        f"Recommendation: {report['review_recommendation']}",
        "",
        "## Checks",
        "",
    ]
    for check in report["checks"]:
        lines.extend(
            [
                f"### {check['check_id']} ({check['status']})",
                "",
                check["summary"],
                "",
                "Evidence:",
                "",
                "```json",
                json.dumps(check["evidence"], indent=2, sort_keys=True),
                "```",
                "",
            ]
        )
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    report = audit(
        dataset_name=args.dataset_name,
        adjudication_rows=load_tsv(args.adjudication),
        blind_rows=load_tsv(args.blind),
        key_rows=load_tsv(args.key),
        frontier_rows=load_tsv(args.frontier),
        packet_audit=load_json(args.packet_audit),
        candidate_gate=load_json(args.candidate_gate),
    )
    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(args.output_md, report)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
