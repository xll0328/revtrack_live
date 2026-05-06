from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


MODEL_FIELD_BY_NAME = {
    "heuristic": "heuristic_label",
    "tfidf": "tfidf_label",
    "modernbert": "modernbert_label",
    "mpnet": "mpnet_label",
    "issue_ledger": "issue_ledger_label",
    "structured": "structured_label",
}
MODEL_FIELDS = [
    "heuristic_label",
    "tfidf_label",
    "modernbert_label",
    "mpnet_label",
    "issue_ledger_label",
    "structured_label",
]
RISK_LABELS = {"unresolved", "regressed"}


def parse_named_path(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("Expected NAME=PATH")
    name, path = value.split("=", 1)
    name = name.strip()
    if not name:
        raise argparse.ArgumentTypeError("Comparison name cannot be empty")
    return name, Path(path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a de-duplicated frontier sheet from one anchor model and multiple comparison models."
    )
    parser.add_argument("--candidates", required=True)
    parser.add_argument("--anchor-name", required=True)
    parser.add_argument("--anchor-predictions", required=True)
    parser.add_argument(
        "--comparison",
        action="append",
        type=parse_named_path,
        required=True,
        help="Comparison prediction file as NAME=PATH. Repeat for multiple models.",
    )
    parser.add_argument("--output", required=True)
    parser.add_argument("--sample-size", type=int, default=60)
    parser.add_argument("--include-agreements", action="store_true")
    return parser.parse_args()


def load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def load_predictions(path: str | Path) -> dict[str, str]:
    return {
        row["id"]: row["predicted_label"]
        for row in load_jsonl(path)
    }


def clip(text: str, max_chars: int) -> str:
    text = " ".join(str(text or "").split())
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3] + "..."


def mixed_signal_score(candidate: dict[str, Any]) -> float:
    text = f"{candidate.get('aligned_response_excerpt', '')} {candidate.get('revision_summary', '')}".lower()
    cue_groups = [
        ["we added", "new table", "new experiment", "revised", "now include"],
        ["clarified", "expanded discussion", "added discussion"],
        ["future work", "beyond scope", "not include", "unable", "limitation"],
    ]
    return 1.0 if sum(any(cue in text for cue in group) for group in cue_groups) >= 2 else 0.0


def density_score(candidate: dict[str, Any]) -> float:
    review_len = len(candidate.get("review_excerpt", ""))
    response_len = len(candidate.get("aligned_response_excerpt", ""))
    return min(review_len / 1200.0, 1.0) + min(response_len / 1800.0, 1.0)


def frontier_score(candidate: dict[str, Any], labels: dict[str, str], anchor_name: str) -> tuple[float, dict[str, Any]]:
    anchor_label = labels.get(anchor_name, "")
    comparisons = {name: label for name, label in labels.items() if name != anchor_name}
    disagreements = {
        name: label
        for name, label in comparisons.items()
        if label and anchor_label and label != anchor_label
    }
    label_counts = Counter(label for label in labels.values() if label)
    majority_label = label_counts.most_common(1)[0][0] if label_counts else ""
    risk_labels = sorted(label for label in set(labels.values()) if label in RISK_LABELS)
    score = (
        4.0 * len(disagreements)
        + 2.5 * len(risk_labels)
        + 1.5 * (1 if anchor_label and majority_label and anchor_label != majority_label else 0)
        + 1.2 * mixed_signal_score(candidate)
        + 0.5 * density_score(candidate)
    )
    debug = {
        "anchor_label": anchor_label,
        "majority_label": majority_label,
        "disagreement_count": len(disagreements),
        "disagreement_models": sorted(disagreements),
        "risk_labels": risk_labels,
        "labels": labels,
    }
    return score, debug


def choose_suggested_label(debug: dict[str, Any]) -> str:
    anchor_label = str(debug.get("anchor_label", ""))
    risk_labels = debug.get("risk_labels", [])
    if "regressed" in risk_labels:
        return "regressed"
    if "unresolved" in risk_labels and anchor_label != "unresolved":
        return "unresolved"
    return anchor_label or str(debug.get("majority_label", ""))


def build_rows(
    candidates: list[dict[str, Any]],
    *,
    anchor_name: str,
    prediction_maps: dict[str, dict[str, str]],
    sample_size: int,
    include_agreements: bool,
) -> list[dict[str, str]]:
    scored: list[tuple[float, dict[str, Any], dict[str, Any], dict[str, str]]] = []
    for candidate in candidates:
        issue_id = candidate["issue_id"]
        labels = {
            name: pred_map.get(issue_id, "")
            for name, pred_map in prediction_maps.items()
        }
        score, debug = frontier_score(candidate, labels, anchor_name)
        if not include_agreements and debug["disagreement_count"] == 0:
            continue
        scored.append((score, candidate, debug, labels))

    scored.sort(key=lambda item: (item[0], item[1].get("issue_id", "")), reverse=True)
    rows = []
    for score, candidate, debug, labels in scored[:sample_size]:
        top_response = ""
        if candidate.get("response_candidates"):
            top_response = candidate["response_candidates"][0].get("text", "")
        model_label_fields = {field: "" for field in MODEL_FIELDS}
        for name, label in labels.items():
            field = MODEL_FIELD_BY_NAME.get(name)
            if field:
                model_label_fields[field] = label
        note = {
            "frontier": "multi_model",
            "anchor": anchor_name,
            "disagreement_models": debug["disagreement_models"],
            "majority_label": debug["majority_label"],
            "risk_labels": debug["risk_labels"],
            "all_labels": labels,
        }
        rows.append(
            {
                "priority_score": f"{score:.3f}",
                "issue_id": candidate["issue_id"],
                "paper_title": candidate.get("paper_title", ""),
                "review_rating": candidate.get("review_rating", ""),
                "review_confidence": candidate.get("review_confidence", ""),
                "suggested_label": choose_suggested_label(debug),
                "suggestion_source": f"multi_frontier_{anchor_name}",
                "suggestion_note": "; ".join(f"{name}={label or 'missing'}" for name, label in sorted(labels.items())),
                "silver_label": "",
                **model_label_fields,
                "review_excerpt": candidate.get("review_excerpt", ""),
                "top_response_excerpt": clip(top_response, 1200),
                "aligned_response_excerpt": candidate.get("aligned_response_excerpt", ""),
                "revision_summary": candidate.get("revision_summary", ""),
                "silver_comment": "",
                "gold_label": "",
                "evidence_span": "",
                "notes": json.dumps(note, ensure_ascii=False),
            }
        )
    return rows


def main() -> None:
    args = parse_args()
    prediction_maps = {
        args.anchor_name: load_predictions(args.anchor_predictions),
    }
    for name, path in args.comparison:
        prediction_maps[name] = load_predictions(path)

    rows = build_rows(
        load_jsonl(args.candidates),
        anchor_name=args.anchor_name,
        prediction_maps=prediction_maps,
        sample_size=args.sample_size,
        include_agreements=args.include_agreements,
    )

    fieldnames = [
        "priority_score",
        "issue_id",
        "paper_title",
        "review_rating",
        "review_confidence",
        "suggested_label",
        "suggestion_source",
        "suggestion_note",
        "silver_label",
        *MODEL_FIELDS,
        "review_excerpt",
        "top_response_excerpt",
        "aligned_response_excerpt",
        "revision_summary",
        "silver_comment",
        "gold_label",
        "evidence_span",
        "notes",
    ]
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} multi-model frontier rows to {output_path}")


if __name__ == "__main__":
    main()
