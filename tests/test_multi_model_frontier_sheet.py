from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "make_multi_model_frontier_sheet.py"
SPEC = importlib.util.spec_from_file_location("make_multi_model_frontier_sheet", SCRIPT)
assert SPEC is not None
assert SPEC.loader is not None
frontier = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(frontier)


def test_frontier_score_prioritizes_disagreement_and_risk() -> None:
    candidate = {
        "issue_id": "p1__r01",
        "review_excerpt": "Need stronger experiments.",
        "aligned_response_excerpt": "We added a new experiment but leave broader analysis to future work.",
        "revision_summary": "Added discussion.",
    }
    score, debug = frontier.frontier_score(
        candidate,
        {
            "structured": "partially_fixed",
            "mpnet": "unresolved",
            "issue_ledger": "fixed",
        },
        "structured",
    )

    assert score > 8.0
    assert debug["disagreement_count"] == 2
    assert debug["risk_labels"] == ["unresolved"]
    assert frontier.choose_suggested_label(debug) == "unresolved"


def test_build_rows_deduplicates_one_row_per_candidate() -> None:
    candidates = [
        {
            "issue_id": "p1__r01",
            "paper_title": "Paper 1",
            "review_excerpt": "Need experiments.",
            "aligned_response_excerpt": "We added an experiment.",
            "revision_summary": "Added Table 2.",
            "response_candidates": [{"text": "We added Table 2."}],
        },
        {
            "issue_id": "p1__r02",
            "paper_title": "Paper 1",
            "review_excerpt": "Typo.",
            "aligned_response_excerpt": "Fixed.",
            "revision_summary": "Fixed typo.",
            "response_candidates": [],
        },
    ]
    prediction_maps = {
        "structured": {"p1__r01": "partially_fixed", "p1__r02": "fixed"},
        "mpnet": {"p1__r01": "fixed", "p1__r02": "fixed"},
        "issue_ledger": {"p1__r01": "unresolved", "p1__r02": "fixed"},
    }

    rows = frontier.build_rows(
        candidates,
        anchor_name="structured",
        prediction_maps=prediction_maps,
        sample_size=10,
        include_agreements=False,
    )

    assert [row["issue_id"] for row in rows] == ["p1__r01"]
    assert rows[0]["structured_label"] == "partially_fixed"
    assert rows[0]["mpnet_label"] == "fixed"
    assert rows[0]["issue_ledger_label"] == "unresolved"
