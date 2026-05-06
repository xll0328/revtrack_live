from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from revtrack.issue_ledger import load_sheet_rows, sheet_row_to_prediction
from revtrack.io import load_examples, save_predictions
from revtrack.metrics import evaluate_predictions


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the issue-ledger calibration baseline on an annotation sheet.")
    parser.add_argument("--sheet", required=True)
    parser.add_argument("--data", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--eval-json")
    parser.add_argument("--base-field", default="mpnet_label")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = load_sheet_rows(args.sheet)
    predictions = [sheet_row_to_prediction(row, base_field=args.base_field) for row in rows]
    save_predictions(args.output, predictions)
    print(f"Wrote {len(predictions)} predictions to {args.output}")

    if args.eval_json:
        examples = load_examples(args.data)
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

