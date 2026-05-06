from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from revtrack.openreview_tasks import build_issue_candidates


def load_rows(path: str | Path) -> list[dict]:
    rows: list[dict] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert raw OpenReview submissions into issue candidates.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--top-k-responses", type=int, default=3)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    submissions = load_rows(args.input)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    num_candidates = 0
    with output_path.open("w", encoding="utf-8") as handle:
        for submission in submissions:
            candidates = build_issue_candidates(submission, top_k_responses=args.top_k_responses)
            for candidate in candidates:
                handle.write(json.dumps(candidate, ensure_ascii=False) + "\n")
            num_candidates += len(candidates)

    print(f"Wrote {num_candidates} issue candidates to {output_path}")


if __name__ == "__main__":
    main()
