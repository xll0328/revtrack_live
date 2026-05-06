from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "export_active_frontier_review_queue.py"
SPEC = importlib.util.spec_from_file_location("export_active_frontier_review_queue", SCRIPT)
assert SPEC is not None
assert SPEC.loader is not None
export_queue = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(export_queue)


def test_review_queue_prioritizes_weak_regressed_review_evidence() -> None:
    rows = [
        {
            "issue_id": "u1",
            "paper_title": "Paper U",
            "assistant_label": "unresolved",
            "assistant_confidence": "low_medium",
            "evidence_source": "aligned_response_excerpt",
            "tfidf_label": "partially_fixed",
            "modernbert_label": "fixed",
            "mpnet_label": "unresolved",
            "issue_ledger_label": "unresolved",
            "structured_label": "fixed",
            "evidence_span": "The response acknowledges the limitation.",
            "review_excerpt": "Need stronger baselines.",
            "aligned_response_excerpt": "We acknowledge this limitation.",
            "revision_summary": "No new baseline.",
        },
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
            "aligned_response_excerpt": "The response says a test was rushed.",
            "revision_summary": "The interpretation was corrected.",
        },
    ]

    review_rows = export_queue.build_review_rows(
        dataset_name="NeurIPS 2024",
        adjudication_rows=rows,
        validation_status="provisional",
    )

    assert review_rows[0]["issue_id"] == "r1"
    assert "regressed_with_review_excerpt_evidence" in review_rows[0]["risk_flags"]
    assert review_rows[0]["support_count"] == "1"
    assert "relabel" in review_rows[0]["review_action"]
