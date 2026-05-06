from __future__ import annotations

from revtrack.structured_calibrator import extract_row_features, hard_override_label


def make_row(**overrides: str) -> dict[str, str]:
    row = {
        "issue_id": "paper__r01",
        "tfidf_label": "partially_fixed",
        "modernbert_label": "unresolved",
        "mpnet_label": "fixed",
        "silver_label": "",
        "review_excerpt": "The paper should include broader experiments, runtime analysis, and release code.",
        "top_response_excerpt": "We added two new datasets, a runtime table, and are working on releasing an anonymized version of our code in the next few days.",
        "aligned_response_excerpt": "",
        "revision_summary": "Appendix B now includes new results and runtime details.",
        "silver_comment": "",
    }
    row.update(overrides)
    return row


def test_extract_row_features_captures_request_response_structure() -> None:
    features = extract_row_features(make_row())
    assert features["review_broad"] == 1
    assert features["review_experiment"] == 1
    assert features["review_code"] == 1
    assert features["response_experiment"] == 1
    assert features["response_code_promise"] == 1
    assert features["request_experiment_answered"] == 1
    assert features["request_code_answered"] == 1


def test_extract_row_features_includes_ledger_signal() -> None:
    features = extract_row_features(
        make_row(
            mpnet_label="unresolved",
            review_excerpt="The writing is unclear and the notation should be clarified.",
            top_response_excerpt="We rewrote the introduction with more clarity and focus and updated the notation.",
        )
    )
    assert features["ledger_label"] == "partially_fixed"
    assert features["ledger_rule"] == "base_unresolved_upgraded_by_new_scope_and_clarity"


def test_hard_override_uses_regressed_silver_comment() -> None:
    override = hard_override_label(
        make_row(
            silver_comment="The performance is worse and the size of the coreset is comparable to the full data.",
        )
    )
    assert override == ("regressed", "hard_override_regressed_silver_comment")
