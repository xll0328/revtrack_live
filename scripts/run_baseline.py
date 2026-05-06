from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from revtrack.backends import GenerationConfig, HeuristicBackend, TransformersBackend
from revtrack.io import load_examples, save_predictions
from revtrack.metrics import evaluate_predictions


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a baseline for RevTrack.")
    parser.add_argument("--backend", choices=["heuristic", "transformers"], default="heuristic")
    parser.add_argument("--data", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--eval-json")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--model")
    parser.add_argument("--max-new-tokens", type=int, default=128)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--top-p", type=float, default=1.0)
    parser.add_argument("--device-map", default="auto")
    parser.add_argument("--dtype", default="auto")
    parser.add_argument("--trust-remote-code", action="store_true")
    parser.add_argument("--local-files-only", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    examples = load_examples(args.data)
    if args.limit > 0:
        examples = examples[: args.limit]

    if args.backend == "heuristic":
        backend = HeuristicBackend()
    else:
        if not args.model:
            raise ValueError("--model is required when --backend transformers")
        backend = TransformersBackend(
            GenerationConfig(
                model_name=args.model,
                max_new_tokens=args.max_new_tokens,
                temperature=args.temperature,
                top_p=args.top_p,
                device_map=args.device_map,
                dtype=args.dtype,
                trust_remote_code=args.trust_remote_code,
                local_files_only=args.local_files_only,
            )
        )

    predictions = [backend.predict(example) for example in examples]
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
