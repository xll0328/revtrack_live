from __future__ import annotations

from collections import Counter, defaultdict

from revtrack.schema import LABELS, IssueExample, Prediction


def _safe_div(num: float, den: float) -> float:
    return 0.0 if den == 0 else num / den


def evaluate_predictions(
    examples: list[IssueExample],
    predictions: list[Prediction],
) -> tuple[dict[str, float | dict[str, dict[str, float]]], list[dict[str, str]]]:
    pred_by_id = {item.id: item for item in predictions}
    details: list[dict[str, str]] = []
    confusion: dict[str, Counter[str]] = defaultdict(Counter)

    correct = 0
    gold_counts: Counter[str] = Counter()
    pred_counts: Counter[str] = Counter()
    tp_counts: Counter[str] = Counter()

    for example in examples:
        predicted = pred_by_id.get(example.id)
        pred_label = predicted.predicted_label if predicted else "missing"
        gold_label = example.gold_label
        confusion[gold_label][pred_label] += 1
        gold_counts[gold_label] += 1
        pred_counts[pred_label] += 1
        if pred_label == gold_label:
            correct += 1
            tp_counts[gold_label] += 1
        details.append(
            {
                "id": example.id,
                "gold_label": gold_label,
                "predicted_label": pred_label,
                "paper_title": example.paper_title,
            }
        )

    per_label: dict[str, dict[str, float]] = {}
    f1_sum = 0.0
    for label in LABELS:
        precision = _safe_div(tp_counts[label], pred_counts[label])
        recall = _safe_div(tp_counts[label], gold_counts[label])
        f1 = _safe_div(2 * precision * recall, precision + recall)
        per_label[label] = {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "support": float(gold_counts[label]),
        }
        f1_sum += f1

    summary: dict[str, float | dict[str, dict[str, float]]] = {
        "num_examples": float(len(examples)),
        "accuracy": _safe_div(correct, len(examples)),
        "macro_f1": f1_sum / len(LABELS),
        "per_label": per_label,
        "confusion": {gold: dict(counts) for gold, counts in confusion.items()},
    }
    return summary, details
