from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "export_active_frontier_regression_verification.py"
SPEC = importlib.util.spec_from_file_location("export_active_frontier_regression_verification", SCRIPT)
assert SPEC is not None
assert SPEC.loader is not None
verification = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verification)


def test_verification_blocks_regressed_label_without_revision_context() -> None:
    rows = verification.build_rows(
        dataset_name="NeurIPS 2024",
        adjudication_rows=[
            {
                "issue_id": "r1",
                "paper_title": "Paper R",
                "assistant_label": "regressed",
                "assistant_confidence": "low",
                "evidence_source": "review_excerpt",
                "tfidf_label": "partially_fixed",
                "modernbert_label": "fixed",
                "mpnet_label": "regressed",
                "issue_ledger_label": "partially_fixed",
                "structured_label": "fixed",
                "evidence_span": "Original review asks for statistical care.",
                "review_excerpt": "Need statistical care.",
                "aligned_response_excerpt": "",
                "revision_summary": "",
            }
        ],
        review_queue_rows=[{"issue_id": "r1", "review_rank": "1"}],
    )

    assert len(rows) == 1
    assert rows[0]["risk_tier"] == "tier_1_block_regressed"
    assert rows[0]["standard_label_gate"] == "do_not_promote_as_regressed"
    assert rows[0]["response_revision_context"] == "missing"


def test_verification_keeps_regressed_candidate_with_revision_cue() -> None:
    rows = verification.build_rows(
        dataset_name="NeurIPS 2024",
        adjudication_rows=[
            {
                "issue_id": "r2",
                "paper_title": "Paper R2",
                "assistant_label": "regressed",
                "assistant_confidence": "low_medium",
                "evidence_source": "revision_summary",
                "tfidf_label": "regressed",
                "modernbert_label": "regressed",
                "mpnet_label": "unresolved",
                "issue_ledger_label": "partially_fixed",
                "structured_label": "regressed",
                "evidence_span": "The revision introduced an inconsistent claim.",
                "review_excerpt": "Need statistical care.",
                "aligned_response_excerpt": "The response acknowledges the change.",
                "revision_summary": "The revision introduced an inconsistent claim.",
            }
        ],
        review_queue_rows=[{"issue_id": "r2", "review_rank": "2"}],
    )

    assert rows[0]["risk_tier"] == "tier_4_regressed_candidate"
    assert rows[0]["standard_label_gate"] == "candidate_keep_regressed"
    assert "introduced" in rows[0]["response_revision_regression_cues"]
