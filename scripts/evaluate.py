from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from revtrack.io import load_examples, load_predictions
from revtrack.metrics import evaluate_predictions


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate RevTrack predictions.")
    parser.add_argument("--data", required=True)
    parser.add_argument("--predictions", required=True)
    parser.add_argument("--eval-json")
    parser.add_argument("--details-json")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    examples = load_examples(args.data)
    predictions = load_predictions(args.predictions)
    summary, details = evaluate_predictions(examples, predictions)
    print(json.dumps(summary, indent=2))
    print(f"Detailed rows: {len(details)}")
    if args.eval_json:
        output_path = Path(args.eval_json)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.details_json:
        output_path = Path(args.details_json)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(details, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
