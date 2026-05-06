from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


VALID_LABELS = {"fixed", "partially_fixed", "unresolved", "regressed"}


def load_jsonl(path: str | Path) -> list[dict]:
    rows: list[dict] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def load_predictions(path: str | Path) -> dict[str, dict]:
    return {row["id"]: row for row in load_jsonl(path)}


def load_priority_rows(path: str | Path) -> list[dict]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def parse_raw_scores(prediction: dict | None) -> tuple[float | None, str]:
    if not prediction:
        return None, ""
    raw = prediction.get("raw_output", "")
    if not raw:
        return None, ""
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return None, ""
    scores = payload.get("scores")
    classes = payload.get("classes", [])
    if not isinstance(scores, list):
        return None, ""
    if scores and isinstance(scores[0], list):
        scores = scores[0]
    if not isinstance(scores, list) or len(scores) == 0:
        return None, ""
    ranked = sorted((float(score), idx) for idx, score in enumerate(scores))
    if len(ranked) == 1:
        margin = abs(ranked[-1][0])
    else:
        margin = ranked[-1][0] - ranked[-2][0]
    best_label = ""
    best_idx = ranked[-1][1]
    if isinstance(classes, list) and best_idx < len(classes):
        best_label = str(classes[best_idx])
    return margin, best_label


def clip(text: str, max_chars: int) -> str:
    text = " ".join(str(text).split())
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3] + "..."


def choose_suggestion(
    issue_id: str,
    priority_row: dict,
    silver_by_id: dict[str, dict],
    prediction_order: list[tuple[str, dict[str, dict]]],
) -> tuple[str, str, str]:
    silver = silver_by_id.get(issue_id)
    if silver is not None and silver.get("gold_label") in VALID_LABELS:
        return (
            silver["gold_label"],
            "silver_followup_comment",
            clip(silver.get("metadata", {}).get("silver_comment", ""), 320),
        )

    available = []
    for name, pred_map in prediction_order:
        pred = pred_map.get(issue_id)
        if pred is None:
            continue
        margin, best_label = parse_raw_scores(pred)
        label = pred.get("predicted_label", "")
        available.append((name, label, margin if margin is not None else -1.0, best_label))

    if not available:
        return "", "none", ""

    available.sort(key=lambda item: (item[2], item[0]), reverse=True)
    chosen = available[0]
    reason = f"best_margin_from_{chosen[0]}"
    note = f"{chosen[0]}={chosen[1]}"

    primary_label = priority_row.get("primary_label", "")
    secondary_label = priority_row.get("secondary_label", "")
    if secondary_label in VALID_LABELS:
        reason = f"priority_secondary_{priority_row.get('secondary_name', 'model')}"
        note = f"{priority_row.get('secondary_name', 'secondary')}={secondary_label}; {priority_row.get('primary_name', 'primary')}={primary_label}"
        return secondary_label, reason, note

    return chosen[1], reason, note


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a prefilled annotation sheet with model suggestions and evidence hints.")
    parser.add_argument("--priority-sheet", required=True)
    parser.add_argument("--candidates", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--silver-data")
    parser.add_argument("--heuristic-predictions")
    parser.add_argument("--tfidf-predictions")
    parser.add_argument("--modernbert-predictions")
    parser.add_argument("--mpnet-predictions")
    parser.add_argument("--issue-ledger-predictions")
    parser.add_argument("--structured-predictions")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    priority_rows = load_priority_rows(args.priority_sheet)
    candidates = {row["issue_id"]: row for row in load_jsonl(args.candidates)}
    silver_by_id = {row["id"]: row for row in load_jsonl(args.silver_data)} if args.silver_data else {}

    prediction_order: list[tuple[str, dict[str, dict]]] = []
    for name, value in [
        ("mpnet", args.mpnet_predictions),
        ("issue_ledger", args.issue_ledger_predictions),
        ("structured", args.structured_predictions),
        ("modernbert", args.modernbert_predictions),
        ("tfidf", args.tfidf_predictions),
        ("heuristic", args.heuristic_predictions),
    ]:
        if value:
            prediction_order.append((name, load_predictions(value)))

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "priority_score",
                "issue_id",
                "paper_title",
                "review_rating",
                "review_confidence",
                "suggested_label",
                "suggestion_source",
                "suggestion_note",
                "silver_label",
                "heuristic_label",
                "tfidf_label",
                "modernbert_label",
                "mpnet_label",
                "issue_ledger_label",
                "structured_label",
                "review_excerpt",
                "top_response_excerpt",
                "aligned_response_excerpt",
                "revision_summary",
                "silver_comment",
                "gold_label",
                "evidence_span",
                "notes",
            ],
            delimiter="\t",
        )
        writer.writeheader()

        for row in priority_rows:
            issue_id = row["issue_id"]
            candidate = candidates[issue_id]
            silver = silver_by_id.get(issue_id)

            suggested_label, suggestion_source, suggestion_note = choose_suggestion(
                issue_id=issue_id,
                priority_row=row,
                silver_by_id=silver_by_id,
                prediction_order=prediction_order,
            )

            top_response = ""
            if candidate.get("response_candidates"):
                top_response = candidate["response_candidates"][0].get("text", "")

            label_lookup = {}
            for name, pred_map in prediction_order:
                pred = pred_map.get(issue_id)
                label_lookup[name] = pred.get("predicted_label", "") if pred else ""

            writer.writerow(
                {
                    "priority_score": row.get("priority_score", ""),
                    "issue_id": issue_id,
                    "paper_title": candidate.get("paper_title", ""),
                    "review_rating": candidate.get("review_rating", ""),
                    "review_confidence": candidate.get("review_confidence", ""),
                    "suggested_label": suggested_label,
                    "suggestion_source": suggestion_source,
                    "suggestion_note": suggestion_note,
                    "silver_label": silver.get("gold_label", "") if silver else "",
                    "heuristic_label": label_lookup.get("heuristic", row.get("primary_label", "")),
                    "tfidf_label": label_lookup.get("tfidf", ""),
                    "modernbert_label": label_lookup.get("modernbert", ""),
                    "mpnet_label": label_lookup.get("mpnet", row.get("secondary_label", "")),
                    "issue_ledger_label": label_lookup.get("issue_ledger", ""),
                    "structured_label": label_lookup.get("structured", ""),
                    "review_excerpt": candidate.get("review_excerpt", ""),
                    "top_response_excerpt": clip(top_response, 1200),
                    "aligned_response_excerpt": candidate.get("aligned_response_excerpt", ""),
                    "revision_summary": candidate.get("revision_summary", ""),
                    "silver_comment": clip(silver.get("metadata", {}).get("silver_comment", ""), 1200) if silver else "",
                    "gold_label": "",
                    "evidence_span": "",
                    "notes": "",
                }
            )

    print(f"Wrote {len(priority_rows)} prefilled annotation rows to {output_path}")


if __name__ == "__main__":
    main()
