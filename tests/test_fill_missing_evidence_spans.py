from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "fill_missing_evidence_spans.py"
SPEC = importlib.util.spec_from_file_location("fill_missing_evidence_spans", SCRIPT)
assert SPEC is not None
assert SPEC.loader is not None
fill_missing_evidence_spans = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(fill_missing_evidence_spans)


def test_synthesize_evidence_prefers_reviewer_followup() -> None:
    row = {
        "suggestion_source": "silver_followup_comment",
        "suggestion_note": "Thanks for the response. I will increase my score because the main concern was addressed.",
        "notes": "short note",
    }

    evidence = fill_missing_evidence_spans.synthesize_evidence(row)

    assert evidence.startswith("Assistant evidence from reviewer follow-up:")
    assert "increase my score" in evidence


def test_fill_rows_preserves_existing_evidence_and_fills_missing() -> None:
    rows = [
        {"issue_id": "a", "evidence_span": "Already has evidence.", "notes": "note"},
        {"issue_id": "b", "evidence_span": "", "notes": "The missing baseline was added."},
    ]

    filled, count = fill_missing_evidence_spans.fill_rows(rows)

    assert count == 1
    assert filled[0]["evidence_span"] == "Already has evidence."
    assert filled[1]["evidence_span"] == "Assistant evidence from adjudication note: The missing baseline was added."
