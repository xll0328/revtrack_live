from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_human_validation_packet.py"
SPEC = importlib.util.spec_from_file_location("audit_human_validation_packet", SCRIPT)
assert SPEC is not None
assert SPEC.loader is not None
audit_human_validation_packet = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit_human_validation_packet)


def test_audit_packet_accepts_clean_blind_key_source() -> None:
    blind_fields = [
        "issue_id",
        "paper_title",
        "review_excerpt",
        "top_response_excerpt",
        "aligned_response_excerpt",
        "revision_summary",
        "human_label",
    ]
    blind_rows = [
        {
            "issue_id": "a",
            "paper_title": "Paper",
            "review_excerpt": "Need ablation.",
            "top_response_excerpt": "We added Table 2.",
            "aligned_response_excerpt": "We added Table 2.",
            "revision_summary": "Added Table 2.",
            "human_label": "",
        }
    ]
    key_rows = [
        {
            "issue_id": "a",
            "assistant_label": "fixed",
            "audit_bucket": "label_stratum",
            "structured_label": "fixed",
        }
    ]
    audit_rows = [
        {
            "issue_id": "a",
            "assistant_label": "fixed",
            "audit_bucket": "label_stratum",
        }
    ]
    source_rows = [
        {
            "issue_id": "a",
            "gold_label": "fixed",
            "paper_title": "Paper",
            "review_excerpt": "Need ablation.",
            "top_response_excerpt": "We added Table 2.",
            "aligned_response_excerpt": "We added Table 2.",
            "revision_summary": "Added Table 2.",
            "structured_label": "fixed",
        },
        {
            "issue_id": "outside_sample",
            "gold_label": "partially_fixed",
            "paper_title": "Another Paper",
        },
    ]

    report = audit_human_validation_packet.audit_packet(
        blind_fields=blind_fields,
        blind_rows=blind_rows,
        key_rows=key_rows,
        audit_rows=audit_rows,
        source_rows=source_rows,
    )

    assert report["ok"] is True
    assert report["errors"] == []
    assert report["assistant_distribution"] == {"fixed": 1}


def test_audit_packet_accepts_suggested_label_source_key() -> None:
    blind_fields = [
        "issue_id",
        "paper_title",
        "review_excerpt",
        "top_response_excerpt",
        "aligned_response_excerpt",
        "revision_summary",
        "human_label",
    ]
    blind_rows = [
        {
            "issue_id": "frontier_a",
            "paper_title": "Paper",
            "review_excerpt": "Concern.",
            "top_response_excerpt": "Response.",
            "aligned_response_excerpt": "Response.",
            "revision_summary": "Summary.",
            "human_label": "",
        }
    ]
    key_rows = [
        {
            "issue_id": "frontier_a",
            "assistant_label": "unresolved",
            "structured_label": "fixed",
        }
    ]
    source_rows = [
        {
            "issue_id": "frontier_a",
            "suggested_label": "unresolved",
            "paper_title": "Paper",
            "review_excerpt": "Concern.",
            "top_response_excerpt": "Response.",
            "aligned_response_excerpt": "Response.",
            "revision_summary": "Summary.",
            "structured_label": "fixed",
        }
    ]

    report = audit_human_validation_packet.audit_packet(
        blind_fields=blind_fields,
        blind_rows=blind_rows,
        key_rows=key_rows,
        source_rows=source_rows,
    )

    assert report["ok"] is True
    assert report["errors"] == []


def test_audit_packet_flags_blind_leakage_and_key_mismatch() -> None:
    blind_fields = ["issue_id", "paper_title", "gold_label", "human_label"]
    blind_rows = [
        {
            "issue_id": "a",
            "paper_title": "Paper",
            "gold_label": "fixed",
            "human_label": "",
        }
    ]
    key_rows = [{"issue_id": "b", "assistant_label": "fixed"}]

    report = audit_human_validation_packet.audit_packet(
        blind_fields=blind_fields,
        blind_rows=blind_rows,
        key_rows=key_rows,
    )

    assert report["ok"] is False
    assert any("forbidden" in error for error in report["errors"])
    assert any("missing" in error for error in report["errors"])
