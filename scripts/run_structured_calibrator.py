from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from sklearn.feature_extraction import DictVectorizer

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from revtrack.io import load_examples, save_predictions
from revtrack.metrics import evaluate_predictions
from revtrack.schema import Prediction
from revtrack.structured_calibrator import (
    extract_row_features,
    hard_override_label,
    load_sheet_lookup,
    make_classifier,
    raw_output_from_model,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a learned structured calibrator with leave-one-out evaluation.")
    parser.add_argument("--sheet", required=True)
    parser.add_argument("--data", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--eval-json")
    parser.add_argument("--disable-hard-overrides", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    examples = load_examples(args.data)
    rows_by_id = load_sheet_lookup(args.sheet)

    examples = [example for example in examples if example.id in rows_by_id]
    labels = [example.gold_label for example in examples]
    feature_rows = [extract_row_features(rows_by_id[example.id]) for example in examples]

    predictions: list[Prediction] = []
    for idx, example in enumerate(examples):
        row = rows_by_id[example.id]
        override = None if args.disable_hard_overrides else hard_override_label(row)
        if override is not None:
            label, rule = override
            predictions.append(
                Prediction(
                    id=example.id,
                    predicted_label=label,
                    raw_output=rule,
                    metadata={"backend": "structured_calibrator_loo", "override": True, "rule": rule},
                )
            )
            continue

        train_features = [feature_rows[j] for j in range(len(examples)) if j != idx]
        train_labels = [labels[j] for j in range(len(examples)) if j != idx]
        test_feature = feature_rows[idx]

        vectorizer = DictVectorizer(sparse=True)
        train_matrix = vectorizer.fit_transform(train_features)
        clf = make_classifier()
        clf.fit(train_matrix, train_labels)

        raw_output = raw_output_from_model(clf, vectorizer, test_feature)
        pred_payload = json.loads(raw_output)
        predictions.append(
            Prediction(
                id=example.id,
                predicted_label=str(pred_payload["label"]),
                raw_output=raw_output,
                metadata={"backend": "structured_calibrator_loo", "override": False},
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
