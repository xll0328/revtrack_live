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


def choose_bootstrap_label(row: dict[str, str]) -> tuple[str, str]:
    silver = row.get("silver_label", "").strip().lower()
    if silver in LABELS:
        return silver, "silver_label"

    issue_ledger = row.get("issue_ledger_label", "").strip().lower()
    tfidf = row.get("tfidf_label", "").strip().lower()
    if issue_ledger in LABELS and issue_ledger == tfidf:
        return issue_ledger, "issue_ledger_tfidf_agree"

    return "", ""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a high-confidence bootstrap dataset from a prefilled annotation sheet.")
    parser.add_argument("--candidates", required=True)
    parser.add_argument("--sheet", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--output-sheet")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    candidates = load_candidates(args.candidates)
    examples: list[IssueExample] = []
    boot_rows: list[dict[str, str]] = []

    with Path(args.sheet).open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        fieldnames = list(reader.fieldnames or [])
        for row in reader:
            issue_id = row.get("issue_id", "").strip()
            if not issue_id:
                continue
            label, source = choose_bootstrap_label(row)
            if label not in LABELS:
                continue

            candidate = candidates.get(issue_id)
            if candidate is None:
                raise KeyError(f"Missing candidate for issue_id={issue_id}")

            row = dict(row)
            row["gold_label"] = label
            note = row.get("notes", "").strip()
            source_note = f"bootstrap_source={source}"
            row["notes"] = f"{note} | {source_note}" if note else source_note
            if not row.get("evidence_span", "").strip():
                if source == "silver_label":
                    row["evidence_span"] = row.get("silver_comment", "").strip()[:320]
                else:
                    row["evidence_span"] = row.get("suggestion_note", "").strip()[:320]
            boot_rows.append(row)

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
                    gold_label=label,
                    metadata={
                        "submission_id": candidate.get("submission_id", ""),
                        "forum": candidate.get("forum", ""),
                        "review_id": candidate.get("review_id", ""),
                        "review_rating": candidate.get("review_rating", ""),
                        "review_confidence": candidate.get("review_confidence", ""),
                        "bootstrap_source": source,
                        "suggested_label": row.get("suggested_label", ""),
                        "silver_label": row.get("silver_label", ""),
                    },
                )
            )

    save_examples(args.output, examples)
    print(f"Wrote {len(examples)} bootstrap examples to {args.output}")

    if args.output_sheet:
        output_path = Path(args.output_sheet)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
            writer.writeheader()
            writer.writerows(boot_rows)
        print(f"Wrote {len(boot_rows)} bootstrap rows to {output_path}")


if __name__ == "__main__":
    main()

