from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from revtrack.io import save_examples
from revtrack.schema import LABELS, IssueExample


def load_candidates(path: str | Path) -> dict[str, dict]:
    items: dict[str, dict] = {}
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            items[row["issue_id"]] = row
    return items


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert a labeled TSV sheet into RevTrack JSONL examples.")
    parser.add_argument("--candidates", required=True)
    parser.add_argument("--sheet", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    candidates = load_candidates(args.candidates)
    examples: list[IssueExample] = []

    with Path(args.sheet).open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for row in reader:
            issue_id = row.get("issue_id", "").strip()
            gold_label = row.get("gold_label", "").strip().lower()
            if not issue_id or not gold_label:
                continue
            if gold_label not in LABELS:
                raise ValueError(f"Invalid label for {issue_id}: {gold_label}")
            candidate = candidates.get(issue_id)
            if candidate is None:
                raise KeyError(f"Missing candidate for issue_id={issue_id}")

            examples.append(
                IssueExample(
                    id=issue_id,
                    source=candidate.get("source", "openreview"),
                    venue=candidate.get("venue", ""),
                    paper_title=candidate.get("paper_title", ""),
                    abstract=candidate.get("abstract", ""),
                    review_text=candidate.get("review_excerpt", ""),
                    author_response=candidate.get("aligned_response_excerpt", ""),
                    revision_summary=candidate.get("revision_summary", ""),
                    gold_label=gold_label,
                    metadata={
                        "submission_id": candidate.get("submission_id", ""),
                        "forum": candidate.get("forum", ""),
                        "review_id": candidate.get("review_id", ""),
                        "review_rating": candidate.get("review_rating", ""),
                        "review_confidence": candidate.get("review_confidence", ""),
                        "evidence_span": row.get("evidence_span", "").strip(),
                        "notes": row.get("notes", "").strip(),
                    },
                )
            )

    save_examples(args.output, examples)
    print(f"Wrote {len(examples)} labeled examples to {args.output}")


if __name__ == "__main__":
    main()
