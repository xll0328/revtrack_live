from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from revtrack.io import load_examples, save_predictions
from revtrack.schema import IssueExample, Prediction


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train a TF-IDF + LinearSVC model on labeled examples and predict unlabeled candidates.")
    parser.add_argument("--train-data", required=True)
    parser.add_argument("--candidate-data", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--max-features", type=int, default=5000)
    return parser.parse_args()


def build_text(example: IssueExample) -> str:
    return (
        f"TITLE: {example.paper_title}\n"
        f"ABSTRACT: {example.abstract}\n"
        f"REVIEW: {example.review_text}\n"
        f"AUTHOR_RESPONSE: {example.author_response}\n"
        f"REVISION_SUMMARY: {example.revision_summary}\n"
    )


def load_candidate_examples(path: str | Path) -> list[IssueExample]:
    rows = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if "issue_id" in row:
                rows.append(
                    IssueExample(
                        id=row["issue_id"],
                        source=row.get("source", "openreview"),
                        venue=row.get("venue", ""),
                        paper_title=row.get("paper_title", ""),
                        abstract=row.get("abstract", ""),
                        review_text=row.get("review_excerpt", ""),
                        author_response=row.get("aligned_response_excerpt", ""),
                        revision_summary=row.get("revision_summary", ""),
                        gold_label="",
                        metadata={
                            "submission_id": row.get("submission_id", ""),
                            "review_id": row.get("review_id", ""),
                        },
                    )
                )
                continue
            rows.append(
                IssueExample(
                    id=row["id"],
                    source=row.get("source", "openreview"),
                    venue=row.get("venue", ""),
                    paper_title=row.get("paper_title", ""),
                    abstract=row.get("abstract", ""),
                    review_text=row.get("review_text", ""),
                    author_response=row.get("author_response", ""),
                    revision_summary=row.get("revision_summary", ""),
                    gold_label="",
                    metadata=row.get("metadata", {}),
                )
            )
    return rows


def main() -> None:
    args = parse_args()
    train_examples = load_examples(args.train_data)
    candidate_examples = load_candidate_examples(args.candidate_data)

    model = Pipeline(
        steps=[
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=args.max_features)),
            ("clf", LinearSVC(class_weight="balanced")),
        ]
    )
    train_texts = [build_text(example) for example in train_examples]
    train_labels = [example.gold_label for example in train_examples]
    model.fit(train_texts, train_labels)

    candidate_texts = [build_text(example) for example in candidate_examples]
    pred_labels = model.predict(candidate_texts)
    decision = model.decision_function(candidate_texts)
    classes = list(model.named_steps["clf"].classes_)

    predictions = []
    for example, pred_label, scores in zip(candidate_examples, pred_labels, decision, strict=False):
        payload = {
            "label": str(pred_label),
            "classes": classes,
            "scores": scores.tolist() if hasattr(scores, "tolist") else list(scores),
        }
        predictions.append(
            Prediction(
                id=example.id,
                predicted_label=str(pred_label),
                raw_output=json.dumps(payload, ensure_ascii=False),
                metadata={"backend": "tfidf_transfer"},
            )
        )

    save_predictions(args.output, predictions)
    print(f"Wrote {len(predictions)} predictions to {args.output}")


if __name__ == "__main__":
    main()
