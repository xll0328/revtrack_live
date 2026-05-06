from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from sklearn.feature_extraction import DictVectorizer

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from revtrack.io import save_predictions
from revtrack.schema import Prediction
from revtrack.structured_calibrator import (
    extract_row_features,
    hard_override_label,
    load_sheet_rows,
    make_classifier,
    raw_output_from_model,
)


def load_jsonl(path: str | Path) -> list[dict]:
    rows: list[dict] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def load_predictions(path: str | Path) -> dict[str, dict]:
    return {row["id"]: row for row in load_jsonl(path)}


def load_silver(path: str | Path) -> dict[str, dict]:
    return {row["id"]: row for row in load_jsonl(path)}


def build_candidate_row(
    candidate: dict,
    *,
    tfidf_predictions: dict[str, dict],
    modernbert_predictions: dict[str, dict],
    mpnet_predictions: dict[str, dict],
    silver_by_id: dict[str, dict],
) -> dict[str, str]:
    issue_id = candidate["issue_id"]
    silver = silver_by_id.get(issue_id)

    def predicted_label(pred_map: dict[str, dict]) -> str:
        pred = pred_map.get(issue_id)
        return pred.get("predicted_label", "") if pred else ""

    top_response = ""
    if candidate.get("response_candidates"):
        top_response = candidate["response_candidates"][0].get("text", "")

    return {
        "issue_id": issue_id,
        "tfidf_label": predicted_label(tfidf_predictions),
        "modernbert_label": predicted_label(modernbert_predictions),
        "mpnet_label": predicted_label(mpnet_predictions),
        "review_excerpt": candidate.get("review_excerpt", ""),
        "top_response_excerpt": top_response,
        "aligned_response_excerpt": candidate.get("aligned_response_excerpt", ""),
        "revision_summary": candidate.get("revision_summary", ""),
        "silver_label": silver.get("gold_label", "") if silver else "",
        "silver_comment": silver.get("metadata", {}).get("silver_comment", "") if silver else "",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train a learned structured calibrator on labeled rows and predict unlabeled candidates.")
    parser.add_argument("--train-sheet", required=True)
    parser.add_argument("--candidates", required=True)
    parser.add_argument("--tfidf-predictions", required=True)
    parser.add_argument("--modernbert-predictions", required=True)
    parser.add_argument("--mpnet-predictions", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--silver-data")
    parser.add_argument("--disable-hard-overrides", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    train_rows = load_sheet_rows(args.train_sheet)
    train_rows = [row for row in train_rows if row.get("gold_label", "").strip()]
    train_labels = [row["gold_label"].strip().lower() for row in train_rows]
    train_features = [extract_row_features(row) for row in train_rows]

    tfidf_predictions = load_predictions(args.tfidf_predictions)
    modernbert_predictions = load_predictions(args.modernbert_predictions)
    mpnet_predictions = load_predictions(args.mpnet_predictions)
    silver_by_id = load_silver(args.silver_data) if args.silver_data else {}

    candidates = load_jsonl(args.candidates)
    candidate_rows = [
        build_candidate_row(
            candidate,
            tfidf_predictions=tfidf_predictions,
            modernbert_predictions=modernbert_predictions,
            mpnet_predictions=mpnet_predictions,
            silver_by_id=silver_by_id,
        )
        for candidate in candidates
    ]
    candidate_features = [extract_row_features(row) for row in candidate_rows]

    vectorizer = DictVectorizer(sparse=True)
    train_matrix = vectorizer.fit_transform(train_features)
    clf = make_classifier()
    clf.fit(train_matrix, train_labels)

    predictions: list[Prediction] = []
    for row in candidate_rows:
        override = None if args.disable_hard_overrides else hard_override_label(row)
        if override is not None:
            label, rule = override
            predictions.append(
                Prediction(
                    id=row["issue_id"],
                    predicted_label=label,
                    raw_output=rule,
                    metadata={"backend": "structured_calibrator_transfer", "override": True, "rule": rule},
                )
            )
            continue

        feature_row = extract_row_features(row)
        raw_output = raw_output_from_model(clf, vectorizer, feature_row)
        payload = json.loads(raw_output)
        predictions.append(
            Prediction(
                id=row["issue_id"],
                predicted_label=str(payload["label"]),
                raw_output=raw_output,
                metadata={"backend": "structured_calibrator_transfer", "override": False},
            )
        )

    save_predictions(args.output, predictions)
    print(f"Wrote {len(predictions)} predictions to {args.output}")


if __name__ == "__main__":
    main()
