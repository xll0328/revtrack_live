from __future__ import annotations

import argparse
import csv
import json
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


LABELS = ["fixed", "partially_fixed", "unresolved", "regressed"]
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


def parse_named_path(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("Expected NAME=PATH")
    name, path = value.split("=", 1)
    name = name.strip()
    if not name:
        raise argparse.ArgumentTypeError("Prediction NAME cannot be empty")
    return name, Path(path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a random/stratified seed sheet for human validation."
    )
    parser.add_argument("--candidates", required=True)
    parser.add_argument(
        "--prediction",
        action="append",
        required=True,
        type=parse_named_path,
        help="Prediction file as NAME=PATH. Repeat for multiple models.",
    )
    parser.add_argument("--output", required=True)
    parser.add_argument("--summary-json")
    parser.add_argument("--sample-size", type=int, default=80)
    parser.add_argument("--min-per-label", type=int, default=8)
    parser.add_argument("--disagreement-share", type=float, default=0.35)
    parser.add_argument("--seed", type=int, default=20260428)
    return parser.parse_args()


def load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def normalize_label(value: str | None) -> str:
    return (value or "").strip().lower()


def load_predictions(path: str | Path) -> dict[str, str]:
    pred: dict[str, str] = {}
    for row in load_jsonl(path):
        issue_id = str(row.get("id") or row.get("issue_id") or "").strip()
        label = normalize_label(row.get("predicted_label") or row.get("label"))
        if issue_id and label in LABELS:
            pred[issue_id] = label
    return pred


def choose_suggested_label(labels_by_model: dict[str, str]) -> str:
    issue_ledger = normalize_label(labels_by_model.get("issue_ledger"))
    if issue_ledger in LABELS:
        return issue_ledger
    counts = Counter(label for label in labels_by_model.values() if label in LABELS)
    if not counts:
        return ""
    most_common = counts.most_common()
    best_count = most_common[0][1]
    tied = [label for label, count in most_common if count == best_count]
    if len(tied) == 1:
        return tied[0]
    tfidf = normalize_label(labels_by_model.get("tfidf"))
    if tfidf in tied:
        return tfidf
    for label in ["partially_fixed", "unresolved", "fixed", "regressed"]:
        if label in tied:
            return label
    return tied[0]


def split_disagreement(items: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    disagree: list[dict[str, Any]] = []
    agree_or_single: list[dict[str, Any]] = []
    for item in items:
        labels = [label for label in item["labels_by_model"].values() if label in LABELS]
        unique = set(labels)
        if len(unique) >= 2:
            disagree.append(item)
        else:
            agree_or_single.append(item)
    return disagree, agree_or_single


def compute_label_quota(
    *,
    counts: dict[str, int],
    sample_size: int,
    min_per_label: int,
) -> dict[str, int]:
    total = sum(counts.values())
    if total == 0:
        return {}
    quotas = {label: int(sample_size * (count / total)) for label, count in counts.items()}
    used = sum(quotas.values())

    # Enforce small floor per observed label.
    for label, count in counts.items():
        floor = min(min_per_label, count)
        if quotas[label] < floor:
            quotas[label] = floor
    used = sum(quotas.values())

    # Trim if floor expansion exceeded sample size.
    if used > sample_size:
        overflow = used - sample_size
        labels_by_surplus = sorted(
            quotas,
            key=lambda label: (quotas[label] - min(min_per_label, counts[label]), quotas[label]),
            reverse=True,
        )
        idx = 0
        while overflow > 0 and labels_by_surplus:
            label = labels_by_surplus[idx % len(labels_by_surplus)]
            floor = min(min_per_label, counts[label])
            if quotas[label] > floor:
                quotas[label] -= 1
                overflow -= 1
            idx += 1
            if idx > 10000:
                break

    used = sum(quotas.values())
    remainder = sample_size - used
    if remainder > 0:
        frac = {
            label: (sample_size * (count / total)) - int(sample_size * (count / total))
            for label, count in counts.items()
        }
        labels_by_frac = sorted(frac, key=lambda label: (frac[label], counts[label]), reverse=True)
        idx = 0
        while remainder > 0 and labels_by_frac:
            label = labels_by_frac[idx % len(labels_by_frac)]
            if quotas[label] < counts[label]:
                quotas[label] += 1
                remainder -= 1
            idx += 1
            if idx > 10000:
                break
    return quotas


def sample_items(
    *,
    items: list[dict[str, Any]],
    sample_size: int,
    min_per_label: int,
    disagreement_share: float,
    seed: int,
) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    by_label: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in items:
        by_label[item["suggested_label"]].append(item)
    label_counts = {label: len(rows) for label, rows in by_label.items()}
    quotas = compute_label_quota(counts=label_counts, sample_size=sample_size, min_per_label=min_per_label)

    selected: list[dict[str, Any]] = []
    selected_ids: set[str] = set()
    for label, label_items in by_label.items():
        target = quotas.get(label, 0)
        if target <= 0:
            continue
        disagree, agree_or_single = split_disagreement(label_items)
        rng.shuffle(disagree)
        rng.shuffle(agree_or_single)
        want_disagree = min(len(disagree), int(round(target * max(0.0, min(1.0, disagreement_share)))))
        chosen = disagree[:want_disagree]
        remaining = target - len(chosen)
        chosen.extend(agree_or_single[:remaining])
        remaining = target - len(chosen)
        if remaining > 0:
            pool = disagree[want_disagree:] + agree_or_single[len(agree_or_single[:remaining]):]
            rng.shuffle(pool)
            chosen.extend(pool[:remaining])
        for item in chosen[:target]:
            issue_id = item["issue_id"]
            if issue_id not in selected_ids:
                selected.append(item)
                selected_ids.add(issue_id)

    if len(selected) < sample_size:
        remaining_items = [item for item in items if item["issue_id"] not in selected_ids]
        rng.shuffle(remaining_items)
        for item in remaining_items:
            if len(selected) >= sample_size:
                break
            selected.append(item)
            selected_ids.add(item["issue_id"])

    rng.shuffle(selected)
    return selected[:sample_size]


def build_seed_items(
    *,
    candidates: list[dict[str, Any]],
    prediction_maps: dict[str, dict[str, str]],
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for candidate in candidates:
        issue_id = str(candidate.get("issue_id") or "").strip()
        if not issue_id:
            continue
        # Keep complete-field rows only for this slice.
        if not str(candidate.get("concern_text") or "").strip():
            continue
        if not str(candidate.get("aligned_response_excerpt") or "").strip():
            continue
        if not str(candidate.get("revision_summary") or "").strip():
            continue

        labels_by_model = {
            name: normalize_label(pred_map.get(issue_id))
            for name, pred_map in prediction_maps.items()
        }
        suggested = choose_suggested_label(labels_by_model)
        if suggested not in LABELS:
            continue
        items.append(
            {
                "issue_id": issue_id,
                "candidate": candidate,
                "labels_by_model": labels_by_model,
                "suggested_label": suggested,
            }
        )
    return items


def to_sheet_rows(items: list[dict[str, Any]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for rank, item in enumerate(items, 1):
        c = item["candidate"]
        labels_by_model = item["labels_by_model"]
        model_fields = {field: "" for field in MODEL_FIELDS}
        for model_name, label in labels_by_model.items():
            field = MODEL_FIELD_BY_NAME.get(model_name)
            if field:
                model_fields[field] = label
        disagreement_models = sorted(
            model_name
            for model_name, label in labels_by_model.items()
            if label in LABELS and label != item["suggested_label"]
        )
        row = {
            "priority_score": f"{1000 - rank:.3f}",
            "issue_id": item["issue_id"],
            "paper_title": str(c.get("paper_title") or ""),
            "review_rating": str(c.get("review_rating") or ""),
            "review_confidence": str(c.get("review_confidence") or ""),
            "suggested_label": item["suggested_label"],
            "suggestion_source": "random_stratified_seed",
            "suggestion_note": "; ".join(
                [f"{name}={label or 'missing'}" for name, label in sorted(labels_by_model.items())]
            ),
            "silver_label": "",
            **model_fields,
            "review_excerpt": str(c.get("review_excerpt") or ""),
            "top_response_excerpt": str(c.get("top_response_excerpt") or ""),
            "aligned_response_excerpt": str(c.get("aligned_response_excerpt") or ""),
            "revision_summary": str(c.get("revision_summary") or ""),
            "silver_comment": "",
            "gold_label": "",
            "evidence_span": "",
            "notes": json.dumps(
                {
                    "sampling": "random_stratified",
                    "disagreement_models": disagreement_models,
                    "source": "iclr2023_limit80_complete_subpool",
                },
                ensure_ascii=False,
            ),
        }
        rows.append(row)
    return rows


def write_tsv(path: str | Path, rows: list[dict[str, str]]) -> None:
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
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = parse_args()
    prediction_maps = {
        name: load_predictions(path)
        for name, path in args.prediction
    }
    candidates = load_jsonl(args.candidates)
    seed_items = build_seed_items(candidates=candidates, prediction_maps=prediction_maps)
    selected = sample_items(
        items=seed_items,
        sample_size=args.sample_size,
        min_per_label=args.min_per_label,
        disagreement_share=args.disagreement_share,
        seed=args.seed,
    )
    rows = to_sheet_rows(selected)
    write_tsv(args.output, rows)

    label_dist = Counter(item["suggested_label"] for item in selected)
    disagreement_rows = 0
    for item in selected:
        labels = [label for label in item["labels_by_model"].values() if label in LABELS]
        if len(set(labels)) >= 2:
            disagreement_rows += 1

    summary = {
        "status": "ok",
        "source_candidates": str(args.candidates),
        "sample_size": len(selected),
        "label_distribution": dict(sorted(label_dist.items())),
        "disagreement_rows": disagreement_rows,
        "seed": args.seed,
        "min_per_label": args.min_per_label,
        "disagreement_share": args.disagreement_share,
        "prediction_models": sorted(prediction_maps.keys()),
        "output": str(args.output),
    }
    if args.summary_json:
        out = Path(args.summary_json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
