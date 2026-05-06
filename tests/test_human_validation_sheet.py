from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "make_human_validation_sheet.py"
SPEC = importlib.util.spec_from_file_location("make_human_validation_sheet", SCRIPT)
assert SPEC is not None
assert SPEC.loader is not None
validation_sheet = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validation_sheet)


def make_row(issue_id: str, gold_label: str, **overrides: str) -> dict[str, str]:
    row = {
        "issue_id": issue_id,
        "paper_title": "Paper",
        "priority_score": "5.0",
        "gold_label": gold_label,
        "heuristic_label": gold_label,
        "tfidf_label": gold_label,
        "modernbert_label": gold_label,
        "mpnet_label": gold_label,
        "issue_ledger_label": gold_label,
        "structured_label": gold_label,
        "review_excerpt": "Need more experiments.",
        "top_response_excerpt": "We added an ablation.",
        "aligned_response_excerpt": "",
        "revision_summary": "",
        "evidence_span": "",
        "notes": "",
    }
    row.update(overrides)
    return row


def test_select_validation_rows_keeps_minority_and_conflict() -> None:
    rows = [
        make_row("fixed_a", "fixed"),
        make_row("fixed_b", "fixed", structured_label="partially_fixed"),
        make_row("partial_a", "partially_fixed"),
        make_row("partial_b", "partially_fixed", tfidf_label="fixed", mpnet_label="unresolved"),
        make_row("unresolved_a", "unresolved"),
        make_row("regressed_a", "regressed", tfidf_label="fixed"),
    ]

    selected = validation_sheet.select_validation_rows(rows, sample_size=4, min_per_label=1)
    selected_ids = {row["issue_id"] for row in selected}

    assert "regressed_a" in selected_ids
    assert "unresolved_a" in selected_ids
    assert "fixed_b" in selected_ids
    assert len(selected) == 4


def test_blind_row_hides_assistant_and_model_labels() -> None:
    row = make_row("fixed_b", "fixed", structured_label="partially_fixed")

    blind = validation_sheet.as_blind_row(row)
    key = validation_sheet.as_key_row(row, 1)

    assert blind["issue_id"] == "fixed_b"
    assert "gold_label" not in blind
    assert "structured_label" not in blind
    assert blind["human_label"] == ""
    assert key["assistant_label"] == "fixed"
    assert key["structured_label"] == "partially_fixed"


def test_frontier_suggested_label_can_seed_hidden_assistant_key() -> None:
    row = make_row("frontier_a", "", suggested_label="unresolved", structured_label="fixed")

    selected = validation_sheet.select_validation_rows([row], sample_size=1, min_per_label=1)
    key = validation_sheet.as_key_row(selected[0], 1)

    assert key["assistant_label"] == "unresolved"
    assert key["suggested_label"] == "unresolved"
