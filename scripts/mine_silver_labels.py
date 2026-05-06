from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from revtrack.io import save_examples
from revtrack.schema import IssueExample
from revtrack.silver_bootstrap import collect_followup_comments, infer_silver_label_from_comment


def load_jsonl(path: str | Path) -> list[dict]:
    rows: list[dict] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Mine silver labels from reviewer follow-up comments.")
    parser.add_argument("--raw-submissions", required=True)
    parser.add_argument("--candidates", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    submissions = load_jsonl(args.raw_submissions)
    candidates = load_jsonl(args.candidates)

    submission_by_id = {row["id"]: row for row in submissions}
    comment_map: dict[str, list[dict]] = {}
    for submission in submissions:
        comment_map.update(collect_followup_comments(submission))

    examples: list[IssueExample] = []
    label_counts: Counter[str] = Counter()

    for candidate in candidates:
        review_id = candidate.get("review_id", "")
        matched_comments = comment_map.get(review_id, [])
        inferred = []
        for comment in matched_comments:
            text = str(comment.get("content", {}).get("comment", ""))
            label_info = infer_silver_label_from_comment(text)
            if label_info is not None:
                inferred.append((label_info, text))

        if not inferred:
            continue

        inferred.sort(key=lambda item: item[0]["confidence"], reverse=True)
        best, evidence_text = inferred[0]

        examples.append(
            IssueExample(
                id=candidate["issue_id"],
                source=candidate.get("source", "openreview"),
                venue=candidate.get("venue", ""),
                paper_title=candidate.get("paper_title", ""),
                abstract=candidate.get("abstract", ""),
                review_text=candidate.get("review_excerpt", ""),
                author_response=candidate.get("aligned_response_excerpt", ""),
                revision_summary=candidate.get("revision_summary", ""),
                gold_label=best["label"],
                metadata={
                    "submission_id": candidate.get("submission_id", ""),
                    "forum": candidate.get("forum", ""),
                    "review_id": review_id,
                    "review_rating": candidate.get("review_rating", ""),
                    "review_confidence": candidate.get("review_confidence", ""),
                    "label_source": "silver_followup_comment",
                    "label_confidence": best["confidence"],
                    "label_rule": best["rule"],
                    "silver_comment": evidence_text,
                    "num_followup_comments": len(matched_comments),
                },
            )
        )
        label_counts[best["label"]] += 1

    save_examples(args.output, examples)
    print(f"Wrote {len(examples)} silver-labeled examples to {args.output}")
    print(dict(label_counts))


if __name__ == "__main__":
    main()
