from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_candidate_pool.py"
SPEC = importlib.util.spec_from_file_location("audit_candidate_pool", SCRIPT)
assert SPEC is not None
assert SPEC.loader is not None
audit_candidate_pool = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit_candidate_pool)


def make_candidate(issue_id: str, **overrides: str) -> dict[str, object]:
    row: dict[str, object] = {
        "issue_id": issue_id,
        "venue": "ICLR.cc/2025/Conference",
        "submission_id": issue_id.split("__")[0],
        "concern_text": "Need stronger ablations.",
        "aligned_response_excerpt": "We added a new ablation.",
        "revision_summary": "Added Table 2.",
        "review_fields": ["weaknesses", "questions"],
    }
    row.update(overrides)
    return row


def test_candidate_pool_audit_passes_complete_pool_with_disagreements() -> None:
    candidates = [make_candidate("p1__r01"), make_candidate("p2__r01")]
    prediction_maps = {
        "structured": {"p1__r01": "fixed", "p2__r01": "partially_fixed"},
        "mpnet": {"p1__r01": "partially_fixed", "p2__r01": "partially_fixed"},
    }

    report = audit_candidate_pool.audit_candidate_pool(
        candidates,
        prediction_maps=prediction_maps,
        min_candidates=2,
        min_complete_rate=1.0,
        min_disagreements=1,
    )

    assert report["ok"] is True
    assert report["rows"] == 2
    assert report["complete_rate"] == 1.0
    assert report["disagreement"]["disagreement_rows"] == 1


def test_candidate_pool_audit_flags_duplicates_and_incomplete_rows() -> None:
    candidates = [
        make_candidate("p1__r01"),
        make_candidate("p1__r01", revision_summary=""),
    ]

    report = audit_candidate_pool.audit_candidate_pool(
        candidates,
        min_candidates=3,
        min_complete_rate=0.75,
    )

    assert report["ok"] is False
    assert report["duplicate_issue_ids"] == ["p1__r01"]
    assert report["complete_rate"] == 0.5
    assert any("candidate count" in error for error in report["errors"])
