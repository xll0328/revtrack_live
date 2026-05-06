from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import LeaveOneOut
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from revtrack.io import load_examples, save_predictions
from revtrack.metrics import evaluate_predictions
from revtrack.schema import Prediction


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a TF-IDF + LinearSVC baseline with leave-one-out CV.")
    parser.add_argument("--data", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--eval-json")
    parser.add_argument("--max-features", type=int, default=5000)
    return parser.parse_args()


def build_text(example) -> str:
    return (
        f"TITLE: {example.paper_title}\n"
        f"ABSTRACT: {example.abstract}\n"
        f"REVIEW: {example.review_text}\n"
        f"AUTHOR_RESPONSE: {example.author_response}\n"
        f"REVISION_SUMMARY: {example.revision_summary}\n"
    )


def main() -> None:
    args = parse_args()
    examples = load_examples(args.data)
    texts = [build_text(example) for example in examples]
    labels = [example.gold_label for example in examples]

    loo = LeaveOneOut()
    predictions: list[Prediction] = []
    for train_idx, test_idx in loo.split(texts, labels):
        train_texts = [texts[i] for i in train_idx]
        train_labels = [labels[i] for i in train_idx]
        test_text = texts[test_idx[0]]
        test_example = examples[test_idx[0]]

        model = Pipeline(
            steps=[
                ("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=args.max_features)),
                (
                    "clf",
                    LinearSVC(class_weight="balanced"),
                ),
            ]
        )
        model.fit(train_texts, train_labels)
        pred_label = str(model.predict([test_text])[0])
        decision = model.decision_function([test_text])
        raw_output = json.dumps(
            {
                "label": pred_label,
                "scores": decision.tolist(),
                "classes": list(model.named_steps["clf"].classes_),
            },
            ensure_ascii=False,
        )
        predictions.append(
            Prediction(
                id=test_example.id,
                predicted_label=pred_label,
                raw_output=raw_output,
                metadata={"backend": "tfidf_logreg_loo"},
            )
        )

    save_predictions(args.output, predictions)
    print(f"Wrote {len(predictions)} predictions to {args.output}")

    if args.eval_json:
        summary, details = evaluate_predictions(examples, predictions)
        target = Path(args.eval_json)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps({"summary": summary, "details": details}, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
