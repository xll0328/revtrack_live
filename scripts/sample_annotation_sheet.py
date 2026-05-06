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


def pick_issue_text(reply: dict) -> str:
    fields = reply.get("long_text_fields", [])
    if fields:
        return fields[0]["text"]
    content = reply.get("content", {})
    return " ".join(str(value) for value in content.values() if isinstance(value, str))


def build_rows(submissions: list[dict]) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for submission in submissions:
        title = submission.get("content", {}).get("title", "")
        replies = submission.get("replies", [])
        reviews = [reply for reply in replies if reply.get("type") == "official_review"]
        responses = [reply for reply in replies if reply.get("type") == "author_response"]
        if not reviews:
            continue
        response_text = pick_issue_text(responses[0]) if responses else ""
        for review in reviews:
            items.append(
                {
                    "submission_id": submission.get("id", ""),
                    "title": title,
                    "review_id": review.get("id", ""),
                    "review_excerpt": pick_issue_text(review)[:1200],
                    "author_response_excerpt": response_text[:1200],
                    "gold_label": "",
                    "notes": "",
                }
            )
    return items


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sample a TSV annotation sheet from OpenReview data.")
    parser.add_argument("--data", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--sample-size", type=int, default=25)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    submissions = load_rows(args.data)
    candidates = build_rows(submissions)
    rng = random.Random(args.seed)
    rng.shuffle(candidates)
    sampled = candidates[: args.sample_size]

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "submission_id",
                "title",
                "review_id",
                "review_excerpt",
                "author_response_excerpt",
                "gold_label",
                "notes",
            ],
            delimiter="\t",
        )
        writer.writeheader()
        writer.writerows(sampled)

    print(f"Wrote {len(sampled)} annotation rows to {output_path}")


if __name__ == "__main__":
    main()
