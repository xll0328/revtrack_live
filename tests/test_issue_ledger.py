from __future__ import annotations

from revtrack.issue_ledger import calibrate_issue_label


def make_row(**overrides: str) -> dict[str, str]:
    row = {
        "issue_id": "paper__r01",
        "silver_label": "",
        "mpnet_label": "fixed",
        "review_excerpt": "The paper should evaluate on different severity levels and broader scenarios.",
        "top_response_excerpt": "We conducted additional experiments at severity level 3 and under unbiased reliability conditions.",
        "aligned_response_excerpt": "",
        "revision_summary": "",
        "silver_comment": "",
    }
    row.update(overrides)
    return row


def test_silver_label_override() -> None:
    label, rule = calibrate_issue_label(make_row(silver_label="fixed", mpnet_label="partially_fixed"))
    assert label == "fixed"
    assert rule == "silver_label_override"


def test_broad_request_becomes_partial() -> None:
    label, rule = calibrate_issue_label(make_row())
    assert label == "partially_fixed"
    assert rule == "base_fixed_broad_request_only_partially_closed"


def test_negative_silver_comment_forces_regressed() -> None:
    label, rule = calibrate_issue_label(
        make_row(
            mpnet_label="partially_fixed",
            silver_comment="The size of the coreset is comparable to that of the full data, and the performance is worse.",
        )
    )
    assert label == "regressed"
    assert rule == "silver_comment_regressed"
