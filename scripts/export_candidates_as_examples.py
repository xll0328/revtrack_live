from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from revtrack.io import save_examples
from revtrack.schema import IssueExample


def load_rows(path: str | Path) -> list[dict]:
    rows: list[dict] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export issue candidates as unlabeled RevTrack examples.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = load_rows(args.input)
    examples = [
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
                "review_rating": row.get("review_rating", ""),
                "review_confidence": row.get("review_confidence", ""),
            },
        )
        for row in rows
    ]
    save_examples(args.output, examples)
    print(f"Wrote {len(examples)} examples to {args.output}")


if __name__ == "__main__":
    main()
