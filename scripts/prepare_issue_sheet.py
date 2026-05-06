from __future__ import annotations

import argparse
import csv
import json
import random
from pathlib import Path


def load_rows(path: str | Path) -> list[dict]:
    rows: list[dict] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sample an annotation sheet from issue candidates.")
    parser.add_argument("--data", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--sample-size", type=int, default=25)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = load_rows(args.data)
    rng = random.Random(args.seed)
    rng.shuffle(rows)
    sampled = rows[: args.sample_size]

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "issue_id",
                "venue",
                "paper_title",
                "review_rating",
                "review_confidence",
                "review_excerpt",
                "aligned_response_excerpt",
                "revision_summary",
                "gold_label",
                "evidence_span",
                "notes",
            ],
            delimiter="\t",
        )
        writer.writeheader()
        for row in sampled:
            writer.writerow(
                {
                    "issue_id": row.get("issue_id", ""),
                    "venue": row.get("venue", ""),
                    "paper_title": row.get("paper_title", ""),
                    "review_rating": row.get("review_rating", ""),
                    "review_confidence": row.get("review_confidence", ""),
                    "review_excerpt": row.get("review_excerpt", ""),
                    "aligned_response_excerpt": row.get("aligned_response_excerpt", ""),
                    "revision_summary": row.get("revision_summary", ""),
                    "gold_label": "",
                    "evidence_span": "",
                    "notes": "",
                }
            )
    print(f"Wrote {len(sampled)} annotation rows to {output_path}")


if __name__ == "__main__":
    main()
