from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


DEFAULTS = {
    "claim_ledger": ROOT / "outputs/day1/paper_assets/claim_evidence_ledger.csv",
    "iclr2024_gate": ROOT / "outputs/day1/iclr2024_candidate_pool_quality_gate.json",
    "iclr2025_gate": ROOT / "outputs/day1/iclr2025_expanded80_candidate_pool_quality_gate.json",
    "iclr2024_human_metrics": ROOT / "outputs/day1/iclr2024_human_validation_v1_pending_metrics.json",
    "iclr2025_human_metrics": ROOT / "outputs/day1/iclr2025_repro_human_validation_v2_pending_metrics.json",
    "iclr2025_expanded80_human_metrics": ROOT
    / "outputs/day1/iclr2025_expanded80_human_validation_v1_standard_metrics.json",
    "neurips2024_standard_manifest": ROOT / "outputs/day1/neurips2024_limit100_standard_validation_manifest.json",
    "iclr2023_random80_human_metrics": ROOT
    / "outputs/day1/iclr2023_limit80_random80_human_validation_v1_standard_metrics.json",
    "iclr2023_random80_standard_manifest": ROOT
    / "outputs/day1/iclr2023_limit80_random80_standard_transfer_manifest.json",
    "human_validation_queue": ROOT / "outputs/day1/paper_assets/human_validation_work_queue.csv",
    "human_validation_batch_manifest": ROOT / "outputs/day1/human_validation_batches/human_validation_priority_manifest.csv",
    "human_validation_batch_ingest": ROOT
    / "outputs/day1/paper_assets/human_validation_batch_ingest_report.json",
    "human_validation_provenance": ROOT
    / "outputs/day1/ai_assisted_validation_signoff/ai_signoff_human_validation_promotion.json",
    "expanded80_human_validation_provenance": ROOT
    / "outputs/day1/iclr2025_expanded80_standard_validation_promotion.json",
    "neurips2024_human_validation_provenance": ROOT
    / "outputs/day1/neurips2024_limit100_standard_validation_promotion.json",
    "iclr2023_random80_human_validation_provenance": ROOT
    / "outputs/day1/iclr2023_limit80_random80_standard_validation_promotion.json",
    "citation_audit": ROOT / "outputs/day1/paper_assets/paper_citation_audit.json",
    "packet_audits": [
        ROOT / "outputs/day1/iclr2024_human_validation_v1_packet_audit.json",
        ROOT / "outputs/day1/iclr2025_repro_human_validation_v1_packet_audit.json",
        ROOT / "outputs/day1/iclr2025_repro_human_validation_v2_packet_audit.json",
        ROOT / "outputs/day1/iclr2025_expanded80_human_validation_v1_packet_audit.json",
        ROOT / "outputs/day1/neurips2024_limit100_human_validation_v1_packet_audit.json",
        ROOT / "outputs/day1/iclr2023_limit80_random80_human_validation_v1_packet_audit.json",
    ],
    "label_evidence_audits": [
        ROOT / "outputs/day1/iclr2024_clean_dev_v7_evidence_filled_label_evidence_audit.json",
        ROOT / "outputs/day1/iclr2025_repro_v2_label_evidence_audit.json",
        ROOT / "outputs/day1/iclr2025_expanded80_standard_label_evidence_audit.json",
        ROOT / "outputs/day1/iclr2023_limit80_random80_standard_label_evidence_audit.json",
    ],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit RevTrack paper-readiness from local evidence artifacts.")
    parser.add_argument("--claim-ledger", default=str(DEFAULTS["claim_ledger"]))
    parser.add_argument("--iclr2024-gate", default=str(DEFAULTS["iclr2024_gate"]))
    parser.add_argument("--iclr2025-gate", default=str(DEFAULTS["iclr2025_gate"]))
    parser.add_argument("--iclr2024-human-metrics", default=str(DEFAULTS["iclr2024_human_metrics"]))
    parser.add_argument("--iclr2025-human-metrics", default=str(DEFAULTS["iclr2025_human_metrics"]))
    parser.add_argument(
        "--iclr2025-expanded80-human-metrics",
        default=str(DEFAULTS["iclr2025_expanded80_human_metrics"]),
    )
    parser.add_argument("--neurips2024-standard-manifest", default=str(DEFAULTS["neurips2024_standard_manifest"]))
    parser.add_argument(
        "--iclr2023-random80-human-metrics",
        default=str(DEFAULTS["iclr2023_random80_human_metrics"]),
    )
    parser.add_argument(
        "--iclr2023-random80-standard-manifest",
        default=str(DEFAULTS["iclr2023_random80_standard_manifest"]),
    )
    parser.add_argument("--human-validation-queue", default=str(DEFAULTS["human_validation_queue"]))
    parser.add_argument(
        "--human-validation-batch-manifest",
        default=str(DEFAULTS["human_validation_batch_manifest"]),
    )
    parser.add_argument(
        "--human-validation-batch-ingest",
        default=str(DEFAULTS["human_validation_batch_ingest"]),
    )
    parser.add_argument(
        "--human-validation-provenance",
        default=str(DEFAULTS["human_validation_provenance"]),
    )
    parser.add_argument(
        "--expanded80-human-validation-provenance",
        default=str(DEFAULTS["expanded80_human_validation_provenance"]),
    )
    parser.add_argument(
        "--neurips2024-human-validation-provenance",
        default=str(DEFAULTS["neurips2024_human_validation_provenance"]),
    )
    parser.add_argument(
        "--iclr2023-random80-human-validation-provenance",
        default=str(DEFAULTS["iclr2023_random80_human_validation_provenance"]),
    )
    parser.add_argument("--citation-audit", default=str(DEFAULTS["citation_audit"]))
    parser.add_argument("--packet-audit", action="append", default=[str(path) for path in DEFAULTS["packet_audits"]])
    parser.add_argument(
        "--label-evidence-audit",
        action="append",
        default=[str(path) for path in DEFAULTS["label_evidence_audits"]],
    )
    parser.add_argument("--output-json", default="outputs/day1/paper_assets/paper_readiness_audit.json")
    parser.add_argument("--output-md", default="outputs/day1/paper_assets/paper_readiness_audit.md")
    return parser.parse_args()


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_claim_rows(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def load_csv_rows(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def add_check(
    checks: list[dict[str, str]],
    *,
    check_id: str,
    status: str,
    summary: str,
    evidence: str,
    next_action: str,
) -> None:
    checks.append(
        {
            "check_id": check_id,
            "status": status,
            "summary": summary,
            "evidence": evidence,
            "next_action": next_action,
        }
    )


def readiness_status(checks: list[dict[str, str]]) -> str:
    if any(check["status"] == "blocker" for check in checks):
        return "blocked"
    if any(check["status"] == "warning" for check in checks):
        return "provisional"
    return "ready"


def audit_readiness(
    *,
    claim_rows: list[dict[str, str]],
    iclr2024_gate: dict[str, Any],
    iclr2025_gate: dict[str, Any],
    iclr2024_human: dict[str, Any],
    iclr2025_human: dict[str, Any],
    iclr2025_expanded80_human: dict[str, Any] | None = None,
    neurips2024_standard: dict[str, Any] | None = None,
    iclr2023_random80_human: dict[str, Any] | None = None,
    iclr2023_random80_standard: dict[str, Any] | None = None,
    packet_audits: list[dict[str, Any]],
    label_evidence_audits: list[dict[str, Any]] | None = None,
    human_validation_queue_rows: list[dict[str, str]] | None = None,
    human_validation_batch_rows: list[dict[str, str]] | None = None,
    human_validation_batch_ingest: dict[str, Any] | None = None,
    human_validation_provenance: dict[str, Any] | None = None,
    expanded80_human_validation_provenance: dict[str, Any] | None = None,
    neurips2024_human_validation_provenance: dict[str, Any] | None = None,
    iclr2023_random80_human_validation_provenance: dict[str, Any] | None = None,
    citation_audit: dict[str, Any] | None = None,
) -> dict[str, Any]:
    checks: list[dict[str, str]] = []
    label_evidence_audits = label_evidence_audits or []
    claim_counts = Counter(row.get("status", "") for row in claim_rows)

    ready_claims = claim_counts.get("ready", 0)
    add_check(
        checks,
        check_id="claims_ready",
        status="pass" if ready_claims >= 3 else "blocker",
        summary="Core paper claims are separated into ready/stress/not-ready buckets.",
        evidence=f"ready={ready_claims}, integrity_ready={claim_counts.get('integrity_ready', 0)}, stress={claim_counts.get('stress_evidence', 0)}, not_ready={claim_counts.get('not_ready', 0)}",
        next_action="Keep the claim ledger updated after every new experiment.",
    )

    add_check(
        checks,
        check_id="iclr2024_pool_quality",
        status="pass" if iclr2024_gate.get("ok") else "blocker",
        summary="ICLR 2024 in-domain pool passes candidate quality gates.",
        evidence=f"ok={iclr2024_gate.get('ok')}, rows={iclr2024_gate.get('rows')}, complete_rate={iclr2024_gate.get('complete_rate')}, disagreements={iclr2024_gate.get('disagreement', {}).get('disagreement_rows')}",
        next_action="Freeze exact split/version metadata for the eventual benchmark release.",
    )

    iclr2025_ok = bool(iclr2025_gate.get("ok"))
    add_check(
        checks,
        check_id="iclr2025_pool_quality",
        status="pass" if iclr2025_ok else "warning",
        summary=(
            "ICLR 2025 scaled pool passes candidate quality gates."
            if iclr2025_ok
            else "ICLR 2025 pool is still a stress sample, not a publishable cross-year benchmark."
        ),
        evidence=f"ok={iclr2025_gate.get('ok')}, rows={iclr2025_gate.get('rows')}, complete_rate={iclr2025_gate.get('complete_rate')}, disagreements={iclr2025_gate.get('disagreement', {}).get('disagreement_rows')}",
        next_action=(
            "Use the scaled ICLR 2025 frontier as hardened cross-year evidence; add another venue/year before broad generalization claims."
            if iclr2025_ok
            else "Collect enough ICLR 2025 v2-notes data to exceed 150 candidates and 25 disagreement rows."
        ),
    )

    packet_failures = [audit for audit in packet_audits if not audit.get("ok")]
    add_check(
        checks,
        check_id="packet_integrity",
        status="pass" if not packet_failures else "blocker",
        summary="Blind/key/audit validation packet integrity checks pass.",
        evidence=f"packet_audits={len(packet_audits)}, failures={len(packet_failures)}",
        next_action="Run packet audit before every human-validation release.",
    )

    evidence_issue_total = sum(int(audit.get("evidence_issue_count", 0)) for audit in label_evidence_audits)
    evidence_rows_total = sum(int(audit.get("rows", 0)) for audit in label_evidence_audits)
    add_check(
        checks,
        check_id="label_evidence_complete",
        status="pass" if evidence_issue_total == 0 else "warning",
        summary="Labeled sheets should have explicit evidence spans and notes for release-quality auditing.",
        evidence=f"audited_rows={evidence_rows_total}, evidence_issues={evidence_issue_total}",
        next_action="Fill missing evidence_span values before freezing the benchmark release.",
    )

    expanded80_human = iclr2025_expanded80_human or {}
    neurips_human = neurips2024_standard or {}
    neurips_rows = int(neurips_human.get("rows", 0))
    iclr2023_human = iclr2023_random80_human or {}
    iclr2023_standard = iclr2023_random80_standard or {}
    iclr2023_rows = int(iclr2023_human.get("rows", 0))
    iclr2023_labeled_rows = int(iclr2023_human.get("labeled_rows", 0))
    iclr2023_status = str(iclr2023_standard.get("status", ""))
    human_labeled = (
        int(iclr2024_human.get("labeled_rows", 0))
        + int(iclr2025_human.get("labeled_rows", 0))
        + int(expanded80_human.get("labeled_rows", 0))
        + neurips_rows
        + iclr2023_labeled_rows
    )
    human_total = (
        int(iclr2024_human.get("rows", 0))
        + int(iclr2025_human.get("rows", 0))
        + int(expanded80_human.get("rows", 0))
        + neurips_rows
        + iclr2023_rows
    )
    provenance_parts = ["canonical blind-sheet labels"]
    if human_validation_provenance and human_validation_provenance.get("status") == "ok":
        provenance_parts.append(
            "standard human-validation signoff; "
            f"promoted_rows={human_validation_provenance.get('promoted_rows')}; "
            "second annotator only needed for inter-annotator reliability claims"
        )
    if expanded80_human_validation_provenance and expanded80_human_validation_provenance.get("status") == "ok":
        provenance_parts.append(
            "expanded80 user-confirmed standard validation; "
            f"promoted_rows={expanded80_human_validation_provenance.get('promoted_rows')}; "
            "not an independent two-annotator IAA pass"
        )
    if neurips2024_human_validation_provenance and neurips2024_human_validation_provenance.get("status") == "ok":
        provenance_parts.append(
            "NeurIPS2024 user-confirmed standard validation; "
            f"promoted_rows={neurips2024_human_validation_provenance.get('promoted_rows')}; "
            "not an independent two-annotator IAA pass"
        )
    if (
        iclr2023_random80_human_validation_provenance
        and iclr2023_random80_human_validation_provenance.get("status") == "ok"
    ):
        provenance_parts.append(
            "ICLR2023 random80 user-confirmed standard validation; "
            f"promoted_rows={iclr2023_random80_human_validation_provenance.get('promoted_rows')}; "
            f"transfer_status={iclr2023_status or 'missing'}; "
            "not an independent two-annotator IAA pass"
        )
    provenance = " | ".join(provenance_parts)
    add_check(
        checks,
        check_id="human_validation_completed",
        status="pass" if human_labeled > 0 else "blocker",
        summary="Human validation labels are required before final benchmark claims.",
        evidence=f"labeled_rows={human_labeled}, total_rows={human_total}, provenance={provenance}",
        next_action=(
            "Use the human-validation work queue to fill blind validation sheets, run evaluate_human_validation.py, and adjudicate mismatches."
            if human_labeled < human_total
            else "Use these standard human-validation labels for current claims; add a second annotator only for inter-annotator reliability claims."
        ),
    )

    if human_validation_queue_rows is not None:
        queue_rows = len(human_validation_queue_rows)
        queue_pending = sum(1 for row in human_validation_queue_rows if row.get("status") == "pending")
        queue_done = sum(1 for row in human_validation_queue_rows if row.get("status") == "done")
        queue_packets = sorted({row.get("packet", "") for row in human_validation_queue_rows if row.get("packet", "")})
        queue_expected_pending = max(human_total - human_labeled, 0)
        queue_ok = queue_pending == queue_expected_pending and queue_done <= human_labeled
        add_check(
            checks,
            check_id="human_validation_queue_ready",
            status="pass" if queue_ok else "warning",
            summary="A prioritized human-validation work queue points to the active blind sheets.",
            evidence=f"queue_rows={queue_rows}, pending={queue_pending}, done={queue_done}, packets={queue_packets}",
            next_action="Regenerate outputs/day1/paper_assets/human_validation_work_queue.csv after packet or label updates.",
        )

    if human_validation_batch_rows is not None:
        batch_count = len(human_validation_batch_rows)
        batch_rows = sum(int(row.get("rows", 0)) for row in human_validation_batch_rows)
        expected_batch_rows = max(human_total - human_labeled, 0)
        batch_ok = batch_rows == expected_batch_rows and (expected_batch_rows == 0 or batch_count > 0)
        add_check(
            checks,
            check_id="human_validation_batches_ready",
            status="pass" if batch_ok else "warning",
            summary="Blind human-validation batches cover the active pending queue.",
            evidence=f"batches={batch_count}, batch_rows={batch_rows}, expected_pending_rows={expected_batch_rows}",
            next_action="Regenerate outputs/day1/human_validation_batches after queue or blind-sheet updates.",
        )

    if human_validation_batch_ingest is not None:
        ingest_error_count = int(human_validation_batch_ingest.get("error_count", 0))
        ingest_ok = human_validation_batch_ingest.get("status") == "ok" and ingest_error_count == 0
        add_check(
            checks,
            check_id="human_validation_batch_ingest_ready",
            status="pass" if ingest_ok else "blocker",
            summary="Completed batch annotations can be mapped back to the canonical blind sheets.",
            evidence=(
                f"status={human_validation_batch_ingest.get('status')}, "
                f"batch_rows={human_validation_batch_ingest.get('batch_rows')}, "
                f"completed_batch_rows={human_validation_batch_ingest.get('completed_batch_rows')}, "
                f"merged_rows={human_validation_batch_ingest.get('merged_rows')}, "
                f"errors={ingest_error_count}"
            ),
            next_action="Rerun merge_human_validation_batches.py after batch edits; write canonical sheets only after an error-free dry run.",
        )

    if citation_audit is not None:
        citation_status = str(citation_audit.get("status", "warning"))
        citation_problem_count = (
            len(citation_audit.get("missing_bib_keys", []))
            + len(citation_audit.get("unused_bib_keys", []))
            + len(citation_audit.get("duplicate_bib_keys", []))
            + len(citation_audit.get("missing_required_fields", []))
            + len(citation_audit.get("log_problems", []))
        )
        add_check(
            checks,
            check_id="paper_citations_ready",
            status="pass" if citation_audit.get("ok") else ("blocker" if citation_status == "blocker" else "warning"),
            summary="Paper citations resolve against the BibTeX file and the final LaTeX log.",
            evidence=(
                f"status={citation_status}, cited_keys={citation_audit.get('cited_key_count')}, "
                f"bib_entries={citation_audit.get('bib_entry_count')}, problems={citation_problem_count}"
            ),
            next_action="Rerun audit_paper_citations.py after related-work or BibTeX edits.",
        )

    not_ready_claims = [row["claim_id"] for row in claim_rows if row.get("status") == "not_ready"]
    add_check(
        checks,
        check_id="not_ready_claims_blocked",
        status="pass" if not not_ready_claims else "warning",
        summary="Not-ready claims are explicitly blocked from paper claims.",
        evidence=f"not_ready_claims={not_ready_claims}",
        next_action="Keep not-ready claims out of the main claim set until gates pass.",
    )

    status = readiness_status(checks)
    blockers = [check for check in checks if check["status"] == "blocker"]
    warnings = [check for check in checks if check["status"] == "warning"]
    return {
        "overall_status": status,
        "claim_status_counts": dict(sorted(claim_counts.items())),
        "checks": checks,
        "blockers": blockers,
        "warnings": warnings,
        "next_actions": [check["next_action"] for check in blockers + warnings],
    }


def write_markdown(path: str | Path, report: dict[str, Any]) -> None:
    lines = [
        "# Paper Readiness Audit",
        "",
        f"Overall status: `{report['overall_status']}`",
        "",
        "## Claim Counts",
        "",
    ]
    for status, count in report["claim_status_counts"].items():
        lines.append(f"- `{status}`: `{count}`")
    lines.extend(["", "## Checks", ""])
    for check in report["checks"]:
        lines.extend(
            [
                f"### {check['check_id']} ({check['status']})",
                "",
                check["summary"],
                "",
                f"Evidence: {check['evidence']}",
                "",
                f"Next action: {check['next_action']}",
                "",
            ]
        )
    lines.extend(["## Immediate Next Actions", ""])
    for action in report["next_actions"]:
        lines.append(f"- {action}")
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    report = audit_readiness(
        claim_rows=load_claim_rows(args.claim_ledger),
        iclr2024_gate=load_json(args.iclr2024_gate),
        iclr2025_gate=load_json(args.iclr2025_gate),
        iclr2024_human=load_json(args.iclr2024_human_metrics),
        iclr2025_human=load_json(args.iclr2025_human_metrics),
        iclr2025_expanded80_human=load_json(args.iclr2025_expanded80_human_metrics)
        if Path(args.iclr2025_expanded80_human_metrics).exists()
        else None,
        neurips2024_standard=load_json(args.neurips2024_standard_manifest)
        if Path(args.neurips2024_standard_manifest).exists()
        else None,
        iclr2023_random80_human=load_json(args.iclr2023_random80_human_metrics)
        if Path(args.iclr2023_random80_human_metrics).exists()
        else None,
        iclr2023_random80_standard=load_json(args.iclr2023_random80_standard_manifest)
        if Path(args.iclr2023_random80_standard_manifest).exists()
        else None,
        packet_audits=[load_json(path) for path in args.packet_audit],
        label_evidence_audits=[load_json(path) for path in args.label_evidence_audit if Path(path).exists()],
        human_validation_queue_rows=load_csv_rows(args.human_validation_queue)
        if Path(args.human_validation_queue).exists()
        else None,
        human_validation_batch_rows=load_csv_rows(args.human_validation_batch_manifest)
        if Path(args.human_validation_batch_manifest).exists()
        else None,
        human_validation_batch_ingest=load_json(args.human_validation_batch_ingest)
        if Path(args.human_validation_batch_ingest).exists()
        else None,
        human_validation_provenance=load_json(args.human_validation_provenance)
        if Path(args.human_validation_provenance).exists()
        else None,
        expanded80_human_validation_provenance=load_json(args.expanded80_human_validation_provenance)
        if Path(args.expanded80_human_validation_provenance).exists()
        else None,
        neurips2024_human_validation_provenance=load_json(args.neurips2024_human_validation_provenance)
        if Path(args.neurips2024_human_validation_provenance).exists()
        else None,
        iclr2023_random80_human_validation_provenance=load_json(
            args.iclr2023_random80_human_validation_provenance
        )
        if Path(args.iclr2023_random80_human_validation_provenance).exists()
        else None,
        citation_audit=load_json(args.citation_audit) if Path(args.citation_audit).exists() else None,
    )

    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(args.output_md, report)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
