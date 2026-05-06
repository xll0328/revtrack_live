from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


VALID_LABELS = {"fixed", "partially_fixed", "unresolved", "regressed"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit a manual annotation sheet for missing labels and distribution issues.")
    parser.add_argument("--sheet", required=True)
    return parser.parse_args()


def main() -> None:
    path = Path(parse_args().sheet)
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))

    ids = [row.get("issue_id", "").strip() for row in rows]
    duplicates = [issue_id for issue_id, count in Counter(ids).items() if issue_id and count > 1]
    labels = [row.get("gold_label", "").strip().lower() for row in rows]
    missing = sum(1 for label in labels if not label)
    invalid = sorted({label for label in labels if label and label not in VALID_LABELS})
    label_counts = Counter(label for label in labels if label in VALID_LABELS)
    evidence_filled = sum(1 for row in rows if row.get("evidence_span", "").strip())

    print(f"Sheet: {path}")
    print(f"Rows: {len(rows)}")
    print(f"Missing labels: {missing}")
    print(f"Evidence spans filled: {evidence_filled}")
    print(f"Label counts: {dict(label_counts)}")
    print(f"Duplicate issue_ids: {duplicates if duplicates else 'none'}")
    print(f"Invalid labels: {invalid if invalid else 'none'}")

    if rows and "suggested_label" in rows[0]:
        comparable = [
            row for row in rows
            if row.get("gold_label", "").strip().lower() in VALID_LABELS and row.get("suggested_label", "").strip().lower() in VALID_LABELS
        ]
        if comparable:
            agree = sum(
                row["gold_label"].strip().lower() == row["suggested_label"].strip().lower()
                for row in comparable
            )
            print(f"Agreement with suggested_label: {agree}/{len(comparable)} = {agree/len(comparable):.3f}")


if __name__ == "__main__":
    main()
