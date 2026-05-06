from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict, deque
from pathlib import Path


def load_jsonl(path: str | Path) -> list[dict]:
    rows: list[dict] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def load_predictions(path: str | Path) -> dict[str, dict]:
    items: dict[str, dict] = {}
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            items[row["id"]] = row
    return items


def score_candidate(candidate: dict, primary: dict | None, secondary: dict | None) -> tuple[float, dict]:
    response_count = len(candidate.get("response_candidates", []))
    review_len = len(candidate.get("review_excerpt", ""))
    response_len = len(candidate.get("aligned_response_excerpt", ""))
    disagreement = 0.0
    if primary and secondary:
        disagreement = 1.0 if primary.get("predicted_label") != secondary.get("predicted_label") else 0.0

    mixed_signals = 0.0
    text = f"{candidate.get('aligned_response_excerpt', '')} {candidate.get('revision_summary', '')}".lower()
    cue_groups = [
        ("fixed", ["we added", "revised", "new table", "new experiment", "section"]),
        ("partial", ["clarified", "however", "still", "partially"]),
        ("negative", ["future work", "beyond scope", "not included", "unable"]),
    ]
    active_groups = sum(any(cue in text for cue in cues) for _, cues in cue_groups)
    if active_groups >= 2:
        mixed_signals = 1.0

    density = min(review_len / 1200.0, 1.0) + min(response_len / 1800.0, 1.0)
    score = 3.0 * disagreement + 1.8 * mixed_signals + 0.6 * min(response_count / 3.0, 1.0) + 0.4 * density

    debug = {
        "disagreement": disagreement,
        "mixed_signals": mixed_signals,
        "response_count": response_count,
        "density": density,
        "primary_label": primary.get("predicted_label", "") if primary else "",
        "secondary_label": secondary.get("predicted_label", "") if secondary else "",
    }
    return score, debug


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a priority annotation sheet from issue candidates and model disagreement.")
    parser.add_argument("--candidates", required=True)
    parser.add_argument("--primary-predictions", required=True)
    parser.add_argument("--secondary-predictions", required=True)
    parser.add_argument("--primary-name", default="heuristic")
    parser.add_argument("--secondary-name", default="secondary")
    parser.add_argument("--output", required=True)
    parser.add_argument("--sample-size", type=int, default=30)
    parser.add_argument("--require-disagreement", action="store_true")
    parser.add_argument(
        "--balance-by",
        choices=["none", "primary_label", "secondary_label", "pair"],
        default="none",
    )
    parser.add_argument("--exclude-sheet")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    candidates = load_jsonl(args.candidates)
    primary = load_predictions(args.primary_predictions)
    secondary = load_predictions(args.secondary_predictions)
    excluded_ids: set[str] = set()
    if args.exclude_sheet:
        with Path(args.exclude_sheet).open("r", encoding="utf-8", newline="") as handle:
            excluded_ids = {
                row.get("issue_id", "").strip()
                for row in csv.DictReader(handle, delimiter="\t")
                if row.get("issue_id", "").strip()
            }

    scored_rows = []
    for candidate in candidates:
        issue_id = candidate["issue_id"]
        if issue_id in excluded_ids:
            continue
        score, debug = score_candidate(candidate, primary.get(issue_id), secondary.get(issue_id))
        if args.require_disagreement and debug["primary_label"] == debug["secondary_label"]:
            continue
        scored_rows.append((score, candidate, debug))

    scored_rows.sort(key=lambda item: item[0], reverse=True)
    if args.balance_by == "none":
        sampled = scored_rows[: args.sample_size]
    else:
        grouped: dict[str, deque] = defaultdict(deque)
        for item in scored_rows:
            _, _, debug = item
            if args.balance_by == "primary_label":
                key = debug["primary_label"] or "missing"
            elif args.balance_by == "secondary_label":
                key = debug["secondary_label"] or "missing"
            else:
                key = f"{debug['primary_label']} -> {debug['secondary_label']}"
            grouped[key].append(item)

        group_order = sorted(grouped, key=lambda key: (len(grouped[key]), key))
        sampled = []
        while len(sampled) < args.sample_size:
            progressed = False
            for key in group_order:
                if grouped[key]:
                    sampled.append(grouped[key].popleft())
                    progressed = True
                    if len(sampled) >= args.sample_size:
                        break
            if not progressed:
                break

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "priority_score",
                "issue_id",
                "venue",
                "paper_title",
                "primary_name",
                "primary_label",
                "secondary_name",
                "secondary_label",
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
        for score, candidate, debug in sampled:
            writer.writerow(
                {
                    "priority_score": f"{score:.3f}",
                    "issue_id": candidate["issue_id"],
                    "venue": candidate.get("venue", ""),
                    "paper_title": candidate.get("paper_title", ""),
                    "primary_name": args.primary_name,
                    "primary_label": debug["primary_label"],
                    "secondary_name": args.secondary_name,
                    "secondary_label": debug["secondary_label"],
                    "review_excerpt": candidate.get("review_excerpt", ""),
                    "aligned_response_excerpt": candidate.get("aligned_response_excerpt", ""),
                    "revision_summary": candidate.get("revision_summary", ""),
                    "gold_label": "",
                    "evidence_span": "",
                    "notes": json.dumps(debug, ensure_ascii=False),
                }
            )

    print(f"Wrote {len(sampled)} priority annotation rows to {output_path}")
    if excluded_ids:
        print(f"Excluded {len(excluded_ids)} issue_ids from prior sheets")


if __name__ == "__main__":
    main()
