from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "export_expanded80_assistant_adjudication.py"
SPEC = importlib.util.spec_from_file_location("export_expanded80_assistant_adjudication", SCRIPT)
assert SPEC is not None
assert SPEC.loader is not None
adjudication = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(adjudication)


def test_build_adjudication_rows_preserves_provisional_boundary() -> None:
    frontier_rows = [
        {
            "issue_id": "a",
            "paper_title": "Paper A",
            "suggested_label": "unresolved",
            "tfidf_label": "partially_fixed",
            "modernbert_label": "fixed",
            "mpnet_label": "unresolved",
            "issue_ledger_label": "unresolved",
            "structured_label": "fixed",
            "review_excerpt": "Need a baseline.",
            "top_response_excerpt": "We will consider it.",
            "aligned_response_excerpt": "This baseline is beyond scope.",
            "revision_summary": "No new baseline was added.",
        }
    ]
    key_rows = [
        {
            "issue_id": "a",
            "assistant_label": "unresolved",
            "audit_bucket": "minority_unresolved",
        }
    ]

    rows = adjudication.build_adjudication_rows(frontier_rows=frontier_rows, key_rows=key_rows)

    assert len(rows) == 1
    row = rows[0]
    assert row["assistant_label"] == "unresolved"
    assert row["evidence_source"] == "aligned_response_excerpt"
    assert row["evidence_span"] == "This baseline is beyond scope."
    assert row["provenance"] == "provisional_assistant_adjudication_not_human_validation"
    assert row["assistant_confidence"] == "medium"
    assert "not_human_validated" in row["notes"]


def test_examples_from_rows_uses_assistant_label_as_provisional_gold() -> None:
    rows = [
        {
            "issue_id": "a",
            "paper_title": "Paper A",
            "assistant_label": "fixed",
            "review_excerpt": "Need ablation.",
            "aligned_response_excerpt": "We added Table 2.",
            "revision_summary": "Table 2 reports the ablation.",
            "evidence_span": "We added Table 2.",
            "evidence_source": "aligned_response_excerpt",
            "provenance": "provisional_assistant_adjudication_not_human_validation",
            "notes": "{}",
        }
    ]
    candidates = [{"issue_id": "a", "source": "openreview", "venue": "ICLR", "submission_id": "s1"}]

    examples = adjudication.examples_from_rows(adjudication_rows=rows, candidate_rows=candidates)

    assert len(examples) == 1
    assert examples[0].gold_label == "fixed"
    assert examples[0].metadata["provenance"] == "provisional_assistant_adjudication_not_human_validation"
