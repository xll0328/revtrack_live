from __future__ import annotations

import csv
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_ai_assisted_validation_signoff.py"
SPEC = importlib.util.spec_from_file_location("audit_ai_assisted_validation_signoff", SCRIPT)
assert SPEC is not None
assert SPEC.loader is not None
audit_ai_assisted_validation_signoff = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit_ai_assisted_validation_signoff)


FIELDS = audit_ai_assisted_validation_signoff.REQUIRED_FIELDS


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_tsv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def signoff_row(**overrides: str) -> dict[str, str]:
    row = {
        "signoff_rank": "1",
        "queue_rank": "1",
        "packet": "P1",
        "issue_id": "a",
        "paper_title": "Paper A",
        "review_rating": "6",
        "review_confidence": "3",
        "review_excerpt": "The paper needs a clear ablation for the proposed module.",
        "top_response_excerpt": "We added the requested ablation.",
        "aligned_response_excerpt": "Table 2 contains the ablation.",
        "revision_summary": "Added Table 2.",
        "assistant_label": "fixed",
        "assistant_evidence_span": "Table 2 contains the ablation.",
        "assistant_notes": "The exact concern is addressed.",
        "suggested_label": "fixed",
        "audit_bucket": "label_stratum",
        "audit_score": "1.0",
        "priority_score": "1.0",
        "model_snapshot": "structured=fixed; tfidf=partially_fixed",
        "reviewer_decision": "",
        "reviewer_final_label": "",
        "reviewer_confidence": "",
        "reviewer_evidence_span": "",
        "reviewer_notes": "",
        "signoff_status": "needs_human_review",
    }
    row.update(overrides)
    return row


def write_support_files(tmp_path: Path) -> tuple[Path, Path, Path]:
    queue = tmp_path / "queue.csv"
    manifest = tmp_path / "manifest.md"
    html = tmp_path / "packet.html"
    write_csv(
        queue,
        [
            {
                "queue_rank": "1",
                "packet": "P1",
                "status": "pending",
                "issue_id": "a",
                "human_label_present": "false",
            }
        ],
        ["queue_rank", "packet", "status", "issue_id", "human_label_present"],
    )
    warning = audit_ai_assisted_validation_signoff.NON_BLIND_WARNING
    manifest.write_text(warning, encoding="utf-8")
    html.write_text(warning, encoding="utf-8")
    return queue, manifest, html


def test_audit_signoff_passes_clean_artifact(tmp_path: Path) -> None:
    signoff = tmp_path / "signoff.tsv"
    queue, manifest, html = write_support_files(tmp_path)
    write_tsv(signoff, [signoff_row()], FIELDS)

    report = audit_ai_assisted_validation_signoff.audit_signoff(
        signoff_path=signoff,
        queue_path=queue,
        manifest_md=manifest,
        packet_html=html,
    )

    assert report["overall_status"] == "pass"
    assert report["error_count"] == 0
    assert len(report["passes"]) == 6


def test_audit_signoff_accepts_completed_queue_after_promotion(tmp_path: Path) -> None:
    signoff = tmp_path / "signoff.tsv"
    queue, manifest, html = write_support_files(tmp_path)
    write_csv(
        queue,
        [
            {
                "queue_rank": "1",
                "packet": "P1",
                "status": "done",
                "issue_id": "a",
                "human_label_present": "true",
            }
        ],
        ["queue_rank", "packet", "status", "issue_id", "human_label_present"],
    )
    write_tsv(signoff, [signoff_row()], FIELDS)

    report = audit_ai_assisted_validation_signoff.audit_signoff(
        signoff_path=signoff,
        queue_path=queue,
        manifest_md=manifest,
        packet_html=html,
    )

    coverage_pass = next(
        item for item in report["passes"] if item["pass_id"] == "pass_2_queue_coverage"
    )
    assert report["overall_status"] == "pass"
    assert coverage_pass["evidence"]["coverage_scope"] == "all"
    assert coverage_pass["evidence"]["pending_queue_rows"] == 0


def test_audit_signoff_warns_on_missing_assistant_evidence(tmp_path: Path) -> None:
    signoff = tmp_path / "signoff.tsv"
    queue, manifest, html = write_support_files(tmp_path)
    write_tsv(signoff, [signoff_row(assistant_evidence_span="")], FIELDS)

    report = audit_ai_assisted_validation_signoff.audit_signoff(
        signoff_path=signoff,
        queue_path=queue,
        manifest_md=manifest,
        packet_html=html,
    )

    assert report["overall_status"] == "warning"
    assistant_pass = next(
        item for item in report["passes"] if item["pass_id"] == "pass_4_assistant_evidence"
    )
    assert assistant_pass["status"] == "warning"
    assert assistant_pass["evidence"]["missing_assistant_evidence_span"] == ["a"]


def test_audit_signoff_fails_prefilled_reviewer_fields(tmp_path: Path) -> None:
    signoff = tmp_path / "signoff.tsv"
    queue, manifest, html = write_support_files(tmp_path)
    write_tsv(signoff, [signoff_row(reviewer_decision="accept")], FIELDS)

    report = audit_ai_assisted_validation_signoff.audit_signoff(
        signoff_path=signoff,
        queue_path=queue,
        manifest_md=manifest,
        packet_html=html,
    )

    assert report["overall_status"] == "fail"
    isolation_pass = next(
        item for item in report["passes"] if item["pass_id"] == "pass_5_non_blind_isolation"
    )
    assert isolation_pass["status"] == "fail"
