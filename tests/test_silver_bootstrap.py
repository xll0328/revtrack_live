from revtrack.silver_bootstrap import infer_silver_label_from_comment


def test_infer_silver_fixed() -> None:
    result = infer_silver_label_from_comment(
        "I have read the author's response. The authors addressed my main concern and I increased my score."
    )
    assert result is not None
    assert result["label"] == "fixed"


def test_infer_silver_partial() -> None:
    result = infer_silver_label_from_comment(
        "Thank you for your responses, which have partially addressed my concerns. However, one issue remains."
    )
    assert result is not None
    assert result["label"] == "partially_fixed"


def test_infer_silver_unresolved() -> None:
    result = infer_silver_label_from_comment(
        "I still think the larger dataset experiment is necessary and I am not convinced by the current evidence."
    )
    assert result is not None
    assert result["label"] == "unresolved"
