from revtrack.metrics import evaluate_predictions
from revtrack.schema import IssueExample, Prediction


def test_metrics_accuracy_and_macro_f1() -> None:
    examples = [
        IssueExample(
            id="1",
            source="test",
            venue="demo",
            paper_title="A",
            review_text="x",
            author_response="y",
            revision_summary="z",
            gold_label="fixed",
        ),
        IssueExample(
            id="2",
            source="test",
            venue="demo",
            paper_title="B",
            review_text="x",
            author_response="y",
            revision_summary="z",
            gold_label="unresolved",
        ),
    ]
    predictions = [
        Prediction(id="1", predicted_label="fixed"),
        Prediction(id="2", predicted_label="partially_fixed"),
    ]
    summary, details = evaluate_predictions(examples, predictions)
    assert summary["accuracy"] == 0.5
    assert len(details) == 2
    assert "per_label" in summary
