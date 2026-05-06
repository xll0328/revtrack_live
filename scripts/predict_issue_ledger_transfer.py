from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from revtrack.issue_ledger import calibrate_issue_label
from revtrack.io import save_predictions
from revtrack.schema import Prediction


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


def build_row(
    candidate: dict,
    base_predictions: dict[str, dict],
    silver_by_id: dict[str, dict],
    *,
    base_field: str,
) -> dict[str, str]:
    issue_id = candidate["issue_id"]
    base = base_predictions.get(issue_id)
    silver = silver_by_id.get(issue_id)
    return {
        "issue_id": issue_id,
        base_field: base.get("predicted_label", "") if base else "",
        "review_excerpt": candidate.get("review_excerpt", ""),
        "top_response_excerpt": candidate.get("response_candidates", [{}])[0].get("text", "") if candidate.get("response_candidates") else "",
        "aligned_response_excerpt": candidate.get("aligned_response_excerpt", ""),
        "revision_summary": candidate.get("revision_summary", ""),
        "silver_label": silver.get("gold_label", "") if silver else "",
        "silver_comment": silver.get("metadata", {}).get("silver_comment", "") if silver else "",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Apply the issue-ledger calibration logic to all candidate issues.")
    parser.add_argument("--candidates", required=True)
    parser.add_argument("--base-predictions", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--silver-data")
    parser.add_argument("--base-field", default="mpnet_label")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    candidates = load_jsonl(args.candidates)
    base_predictions = load_predictions(args.base_predictions)
    silver_by_id = load_silver(args.silver_data) if args.silver_data else {}

    predictions: list[Prediction] = []
    for candidate in candidates:
        row = build_row(
            candidate,
            base_predictions,
            silver_by_id,
            base_field=args.base_field,
        )
        label, rule = calibrate_issue_label(row, base_field=args.base_field)
        predictions.append(
            Prediction(
                id=candidate["issue_id"],
                predicted_label=label,
                raw_output=rule,
                metadata={
                    "backend": "issue_ledger_transfer",
                    "base_field": args.base_field,
                    "rule": rule,
                },
            )
        )

    save_predictions(args.output, predictions)
    print(f"Wrote {len(predictions)} predictions to {args.output}")


if __name__ == "__main__":
    main()

