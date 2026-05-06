from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


LABEL_ORDER = ["fixed", "partially_fixed", "unresolved", "regressed"]
VALID_LABELS = set(LABEL_ORDER)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate human validation labels against an assistant-label key."
    )
    parser.add_argument("--human-sheet", required=True)
    parser.add_argument("--key", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--mismatch-output", help="Optional TSV of human/assistant disagreements.")
    return parser.parse_args()


def load_tsv(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def normalize_label(value: str | None) -> str:
    return (value or "").strip().lower()


def safe_div(num: float, denom: float) -> float:
    return num / denom if denom else 0.0


def cohen_kappa(pairs: list[tuple[str, str]]) -> float | None:
    if not pairs:
        return None
    n = len(pairs)
    observed = sum(1 for assistant, human in pairs if assistant == human) / n
    assistant_counts = Counter(assistant for assistant, _ in pairs)
    human_counts = Counter(human for _, human in pairs)
    expected = sum(
        (assistant_counts[label] / n) * (human_counts[label] / n)
        for label in LABEL_ORDER
    )
    if expected >= 1.0:
        return 1.0 if observed >= 1.0 else 0.0
    return (observed - expected) / (1.0 - expected)


def per_label_scores(pairs: list[tuple[str, str]]) -> dict[str, dict[str, float | int]]:
    scores: dict[str, dict[str, float | int]] = {}
    for label in LABEL_ORDER:
        tp = sum(1 for assistant, human in pairs if assistant == label and human == label)
        fp = sum(1 for assistant, human in pairs if assistant == label and human != label)
        fn = sum(1 for assistant, human in pairs if assistant != label and human == label)
        precision = safe_div(tp, tp + fp)
        recall = safe_div(tp, tp + fn)
        f1 = safe_div(2 * precision * recall, precision + recall)
        scores[label] = {
            "support": sum(1 for _, human in pairs if human == label),
            "assistant_support": sum(1 for assistant, _ in pairs if assistant == label),
            "precision": precision,
            "recall": recall,
            "f1": f1,
        }
    return scores


def evaluate(
    human_rows: list[dict[str, str]],
    key_rows: list[dict[str, str]],
) -> tuple[dict[str, Any], list[dict[str, str]]]:
    key_by_id = {row["issue_id"]: row for row in key_rows}
    pairs: list[tuple[str, str]] = []
    mismatches: list[dict[str, str]] = []
    invalid_rows: list[dict[str, str]] = []
    missing_key = 0

    for row in human_rows:
        issue_id = row.get("issue_id", "")
        key = key_by_id.get(issue_id)
        if key is None:
            missing_key += 1
            continue

        human = normalize_label(row.get("human_label") or row.get("gold_label"))
        if not human:
            continue
        if human not in VALID_LABELS:
            invalid_rows.append({"issue_id": issue_id, "human_label": human})
            continue

        assistant = normalize_label(key.get("assistant_label"))
        if assistant not in VALID_LABELS:
            invalid_rows.append({"issue_id": issue_id, "assistant_label": assistant})
            continue

        pairs.append((assistant, human))
        if assistant != human:
            mismatches.append(
                {
                    "issue_id": issue_id,
                    "assistant_label": assistant,
                    "human_label": human,
                    "audit_bucket": key.get("audit_bucket", ""),
                    "assistant_evidence_span": key.get("assistant_evidence_span", ""),
                    "human_evidence_span": row.get("evidence_span", ""),
                    "human_notes": row.get("notes", ""),
                }
            )

    confusion: dict[str, dict[str, int]] = {
        assistant: {human: 0 for human in LABEL_ORDER}
        for assistant in LABEL_ORDER
    }
    for assistant, human in pairs:
        confusion[assistant][human] += 1

    bucket_totals: dict[str, int] = defaultdict(int)
    bucket_matches: dict[str, int] = defaultdict(int)
    for row in human_rows:
        issue_id = row.get("issue_id", "")
        key = key_by_id.get(issue_id)
        if key is None:
            continue
        human = normalize_label(row.get("human_label") or row.get("gold_label"))
        assistant = normalize_label(key.get("assistant_label"))
        if human not in VALID_LABELS or assistant not in VALID_LABELS:
            continue
        bucket = key.get("audit_bucket", "") or "unknown"
        bucket_totals[bucket] += 1
        if human == assistant:
            bucket_matches[bucket] += 1

    labeled = len(pairs)
    matches = sum(1 for assistant, human in pairs if assistant == human)
    summary: dict[str, Any] = {
        "rows": len(human_rows),
        "key_rows": len(key_rows),
        "labeled_rows": labeled,
        "unlabeled_rows": len(human_rows) - labeled - len(invalid_rows) - missing_key,
        "missing_key_rows": missing_key,
        "invalid_rows": invalid_rows,
        "agreement": safe_div(matches, labeled) if labeled else None,
        "cohen_kappa": cohen_kappa(pairs),
        "assistant_distribution": dict(Counter(assistant for assistant, _ in pairs)),
        "human_distribution": dict(Counter(human for _, human in pairs)),
        "confusion_assistant_to_human": confusion,
        "per_label": per_label_scores(pairs),
        "bucket_agreement": {
            bucket: {
                "matches": bucket_matches[bucket],
                "total": total,
                "agreement": safe_div(bucket_matches[bucket], total),
            }
            for bucket, total in sorted(bucket_totals.items())
        },
        "mismatches": len(mismatches),
    }
    return summary, mismatches


def write_tsv(path: str | Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = parse_args()
    summary, mismatches = evaluate(load_tsv(args.human_sheet), load_tsv(args.key))

    output_path = Path(args.output_json)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote validation metrics to {output_path}")

    if args.mismatch_output:
        write_tsv(
            args.mismatch_output,
            mismatches,
            [
                "issue_id",
                "assistant_label",
                "human_label",
                "audit_bucket",
                "assistant_evidence_span",
                "human_evidence_span",
                "human_notes",
            ],
        )
        print(f"Wrote {len(mismatches)} mismatches to {args.mismatch_output}")


if __name__ == "__main__":
    main()
