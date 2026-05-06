from __future__ import annotations

import argparse
import csv
import json
import random
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
LABELS = ("fixed", "partially_fixed", "unresolved", "regressed")


SPLIT_SPECS: dict[str, dict[str, Any]] = {
    "iclr2024_clean_dev_v7": {
        "title": "ICLR 2024 clean dev v7",
        "anchor_model": "structured",
        "gold_source": {
            "type": "jsonl",
            "path": "data/processed/iclr2024_clean_dev_assistant_v7.jsonl",
            "id_key": "id",
            "label_key": "gold_label",
        },
        "models": {
            "majority": {
                "name": "Majority label",
                "prediction_source": None,
            },
            "tfidf": {
                "name": "TF-IDF + LinearSVC",
                "prediction_source": {
                    "type": "jsonl",
                    "path": "outputs/day1/iclr2024_clean_dev_assistant_v7_tfidf_predictions.jsonl",
                    "id_key": "id",
                    "pred_key": "predicted_label",
                },
            },
            "modernbert": {
                "name": "ModernBERT + LinearSVC",
                "prediction_source": {
                    "type": "jsonl",
                    "path": "outputs/day1/iclr2024_clean_dev_assistant_v7_modernbert_predictions.jsonl",
                    "id_key": "id",
                    "pred_key": "predicted_label",
                },
            },
            "mpnet": {
                "name": "MPNet + LinearSVC",
                "prediction_source": {
                    "type": "jsonl",
                    "path": "outputs/day1/iclr2024_clean_dev_assistant_v7_mpnet_predictions.jsonl",
                    "id_key": "id",
                    "pred_key": "predicted_label",
                },
            },
            "structured_no_overrides": {
                "name": "Structured (No Overrides)",
                "prediction_source": {
                    "type": "jsonl",
                    "path": "outputs/day1/iclr2024_clean_dev_assistant_v7_structured_no_overrides_predictions.jsonl",
                    "id_key": "id",
                    "pred_key": "predicted_label",
                },
            },
            "structured": {
                "name": "Structured",
                "prediction_source": {
                    "type": "jsonl",
                    "path": "outputs/day1/iclr2024_clean_dev_assistant_v7_structured_predictions.jsonl",
                    "id_key": "id",
                    "pred_key": "predicted_label",
                },
            },
        },
    },
    "iclr2025_expanded80_standard": {
        "title": "ICLR 2025 expanded80 standard frontier",
        "anchor_model": "issue_ledger",
        "gold_source": {
            "type": "details_json",
            "path": "outputs/day1/iclr2025_expanded80_standard_transfer/structured_details.json",
            "id_key": "id",
            "label_key": "gold_label",
        },
        "models": {
            "majority": {
                "name": "Majority label",
                "prediction_source": None,
            },
            "tfidf": {
                "name": "TF-IDF",
                "prediction_source": {
                    "type": "details_json",
                    "path": "outputs/day1/iclr2025_expanded80_standard_transfer/tfidf_details.json",
                    "id_key": "id",
                    "pred_key": "predicted_label",
                },
            },
            "modernbert": {
                "name": "ModernBERT",
                "prediction_source": {
                    "type": "details_json",
                    "path": "outputs/day1/iclr2025_expanded80_standard_transfer/modernbert_details.json",
                    "id_key": "id",
                    "pred_key": "predicted_label",
                },
            },
            "mpnet": {
                "name": "MPNet",
                "prediction_source": {
                    "type": "details_json",
                    "path": "outputs/day1/iclr2025_expanded80_standard_transfer/mpnet_details.json",
                    "id_key": "id",
                    "pred_key": "predicted_label",
                },
            },
            "structured": {
                "name": "Structured",
                "prediction_source": {
                    "type": "details_json",
                    "path": "outputs/day1/iclr2025_expanded80_standard_transfer/structured_details.json",
                    "id_key": "id",
                    "pred_key": "predicted_label",
                },
            },
            "issue_ledger": {
                "name": "Issue ledger",
                "prediction_source": {
                    "type": "details_json",
                    "path": "outputs/day1/iclr2025_expanded80_standard_transfer/issue_ledger_details.json",
                    "id_key": "id",
                    "pred_key": "predicted_label",
                },
            },
        },
    },
    "neurips2024_limit100_standard": {
        "title": "NeurIPS 2024 limit100 standard frontier",
        "anchor_model": "mpnet",
        "gold_source": {
            "type": "details_json",
            "path": "outputs/day1/neurips2024_limit100_standard_transfer/structured_details.json",
            "id_key": "id",
            "label_key": "gold_label",
        },
        "models": {
            "majority": {
                "name": "Majority label",
                "prediction_source": None,
            },
            "tfidf": {
                "name": "TF-IDF",
                "prediction_source": {
                    "type": "details_json",
                    "path": "outputs/day1/neurips2024_limit100_standard_transfer/tfidf_details.json",
                    "id_key": "id",
                    "pred_key": "predicted_label",
                },
            },
            "modernbert": {
                "name": "ModernBERT",
                "prediction_source": {
                    "type": "details_json",
                    "path": "outputs/day1/neurips2024_limit100_standard_transfer/modernbert_details.json",
                    "id_key": "id",
                    "pred_key": "predicted_label",
                },
            },
            "mpnet": {
                "name": "MPNet",
                "prediction_source": {
                    "type": "details_json",
                    "path": "outputs/day1/neurips2024_limit100_standard_transfer/mpnet_details.json",
                    "id_key": "id",
                    "pred_key": "predicted_label",
                },
            },
            "structured": {
                "name": "Structured",
                "prediction_source": {
                    "type": "details_json",
                    "path": "outputs/day1/neurips2024_limit100_standard_transfer/structured_details.json",
                    "id_key": "id",
                    "pred_key": "predicted_label",
                },
            },
            "issue_ledger": {
                "name": "Issue ledger",
                "prediction_source": {
                    "type": "details_json",
                    "path": "outputs/day1/neurips2024_limit100_standard_transfer/issue_ledger_details.json",
                    "id_key": "id",
                    "pred_key": "predicted_label",
                },
            },
        },
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export bootstrap significance summaries across standard RevTrack splits."
    )
    parser.add_argument("--output-dir", default="outputs/day1/paper_assets")
    parser.add_argument("--bootstrap-iters", type=int, default=5000)
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


def load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def normalize_label(value: str) -> str:
    return str(value or "").strip().lower()


def macro_f1(y_true: list[str], y_pred: list[str]) -> float:
    tp = Counter()
    pred_counts = Counter()
    gold_counts = Counter(y_true)
    for gold, pred in zip(y_true, y_pred):
        pred_counts[pred] += 1
        if gold == pred:
            tp[gold] += 1
    f1_sum = 0.0
    for label in LABELS:
        precision = tp[label] / pred_counts[label] if pred_counts[label] else 0.0
        recall = tp[label] / gold_counts[label] if gold_counts[label] else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
        f1_sum += f1
    return f1_sum / len(LABELS)


def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    if p <= 0:
        return min(values)
    if p >= 100:
        return max(values)
    sorted_vals = sorted(values)
    rank = (len(sorted_vals) - 1) * (p / 100.0)
    lo = int(rank)
    hi = min(lo + 1, len(sorted_vals) - 1)
    frac = rank - lo
    return sorted_vals[lo] * (1.0 - frac) + sorted_vals[hi] * frac


def load_gold(split_spec: dict[str, Any]) -> tuple[list[str], list[str]]:
    source = split_spec["gold_source"]
    source_type = source["type"]
    path = ROOT / source["path"]
    id_key = source["id_key"]
    label_key = source["label_key"]
    if source_type == "jsonl":
        rows = load_jsonl(path)
    elif source_type == "details_json":
        rows = load_json(path)
        if not isinstance(rows, list):
            raise ValueError(f"Expected list payload in {path}")
    else:
        raise ValueError(f"Unsupported gold source type: {source_type}")
    ids = [str(row[id_key]) for row in rows]
    gold = [normalize_label(row.get(label_key, "")) for row in rows]
    return ids, gold


def load_predictions(
    *,
    ids: list[str],
    gold: list[str],
    prediction_source: dict[str, Any] | None,
) -> list[str]:
    if prediction_source is None:
        majority = Counter(gold).most_common(1)[0][0]
        return [majority for _ in ids]

    source_type = prediction_source["type"]
    path = ROOT / prediction_source["path"]
    id_key = prediction_source["id_key"]
    pred_key = prediction_source["pred_key"]

    if source_type == "jsonl":
        rows = load_jsonl(path)
    elif source_type == "details_json":
        rows = load_json(path)
        if not isinstance(rows, list):
            raise ValueError(f"Expected list payload in {path}")
    else:
        raise ValueError(f"Unsupported prediction source type: {source_type}")

    pred_by_id = {
        str(row[id_key]): normalize_label(row.get(pred_key, ""))
        for row in rows
    }
    return [pred_by_id.get(issue_id, "") for issue_id in ids]


def bootstrap_distributions(
    *,
    gold: list[str],
    preds_by_model: dict[str, list[str]],
    iters: int,
    seed: int,
) -> dict[str, list[float]]:
    rng = random.Random(seed)
    by_label_indices: dict[str, list[int]] = {label: [] for label in LABELS}
    for idx, label in enumerate(gold):
        by_label_indices.setdefault(label, []).append(idx)

    dist = {model_key: [] for model_key in preds_by_model}
    for _ in range(iters):
        sampled_indices: list[int] = []
        for label_indices in by_label_indices.values():
            if not label_indices:
                continue
            sampled_indices.extend(rng.choice(label_indices) for _ in range(len(label_indices)))
        rng.shuffle(sampled_indices)
        sampled_gold = [gold[i] for i in sampled_indices]
        for model_key, preds in preds_by_model.items():
            sampled_pred = [preds[i] for i in sampled_indices]
            dist[model_key].append(macro_f1(sampled_gold, sampled_pred))
    return dist


def compute_split_rows(
    *,
    split_key: str,
    split_spec: dict[str, Any],
    bootstrap_iters: int,
    seed: int,
) -> list[dict[str, Any]]:
    ids, gold = load_gold(split_spec)
    model_specs = split_spec["models"]
    anchor_key = split_spec["anchor_model"]

    preds_by_model = {
        model_key: load_predictions(
            ids=ids,
            gold=gold,
            prediction_source=model_spec["prediction_source"],
        )
        for model_key, model_spec in model_specs.items()
    }

    point_estimates = {
        model_key: macro_f1(gold, preds)
        for model_key, preds in preds_by_model.items()
    }
    dist = bootstrap_distributions(
        gold=gold,
        preds_by_model=preds_by_model,
        iters=bootstrap_iters,
        seed=seed,
    )

    split_rows: list[dict[str, Any]] = []
    for model_key, model_spec in model_specs.items():
        boot = dist[model_key]
        anchor_boot = dist[anchor_key]
        lower = percentile(boot, 2.5)
        upper = percentile(boot, 97.5)
        delta = point_estimates[anchor_key] - point_estimates[model_key]
        delta_boot = [anchor_boot[i] - boot[i] for i in range(len(boot))]
        anchor_not_better_prob = sum(1 for item in delta_boot if item <= 0) / len(delta_boot)
        split_rows.append(
            {
                "split_key": split_key,
                "split": split_spec["title"],
                "rows": len(gold),
                "anchor_key": anchor_key,
                "anchor_model": model_specs[anchor_key]["name"],
                "model_key": model_key,
                "model": model_spec["name"],
                "macro_f1": round(point_estimates[model_key], 6),
                "ci95_low": round(lower, 6),
                "ci95_high": round(upper, 6),
                "delta_to_anchor": round(delta, 6),
                "anchor_not_better_prob": round(anchor_not_better_prob, 6),
            }
        )
    return split_rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "split_key",
        "split",
        "rows",
        "anchor_key",
        "anchor_model",
        "model_key",
        "model",
        "macro_f1",
        "ci95_low",
        "ci95_high",
        "delta_to_anchor",
        "anchor_not_better_prob",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(
    path: Path,
    *,
    rows: list[dict[str, Any]],
    bootstrap_iters: int,
    seed: int,
) -> None:
    lines = [
        "# Cross-split Significance Summary",
        "",
        f"- Splits: `{len(SPLIT_SPECS)}`",
        f"- Bootstrap iterations: `{bootstrap_iters}`",
        f"- Seed: `{seed}`",
        "",
        "Interpretation:",
        "- `P(anchor not better)` is paired-bootstrap risk for each split anchor.",
        "- This captures sample uncertainty on the current labeled rows; it does not include annotator uncertainty.",
        "",
    ]

    for split_key, split_spec in SPLIT_SPECS.items():
        split_rows = [row for row in rows if row["split_key"] == split_key]
        split_rows.sort(key=lambda row: row["macro_f1"], reverse=True)
        lines.extend(
            [
                f"## {split_spec['title']}",
                "",
                f"- Rows: `{split_rows[0]['rows']}`",
                f"- Anchor model: `{split_rows[0]['anchor_model']}`",
                "",
                "| Model | Macro-F1 | 95% CI | Delta to anchor | P(anchor not better) |",
                "| --- | ---: | ---: | ---: | ---: |",
            ]
        )
        for row in split_rows:
            lines.append(
                "| "
                + " | ".join(
                    [
                        str(row["model"]),
                        f"{float(row['macro_f1']):.3f}",
                        f"[{float(row['ci95_low']):.3f}, {float(row['ci95_high']):.3f}]",
                        f"{float(row['delta_to_anchor']):.3f}",
                        f"{float(row['anchor_not_better_prob']):.3f}",
                    ]
                )
                + " |"
            )
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def write_tex(path: Path, rows: list[dict[str, Any]]) -> None:
    lines = [
        "\\begin{table*}[t]",
        "\\centering",
        "\\scriptsize",
        "\\setlength{\\tabcolsep}{3pt}",
        "\\begin{tabular}{p{0.24\\textwidth}p{0.22\\textwidth}rrrr}",
        "\\toprule",
        "Split & Model & Macro-F1 & 95\\% CI & $\\Delta$ to anchor & $P(\\leq 0)$ \\\\",
        "\\midrule",
    ]

    for split_key, split_spec in SPLIT_SPECS.items():
        split_rows = [row for row in rows if row["split_key"] == split_key]
        split_rows.sort(key=lambda row: row["macro_f1"], reverse=True)
        anchor_model = split_rows[0]["anchor_model"]
        first = True
        for row in split_rows:
            split_name = split_spec["title"] if first else ""
            model_name = row["model"]
            if model_name == anchor_model:
                model_name = model_name + " (anchor)"
            lines.append(
                f"{split_name} & "
                f"{model_name} & "
                f"{float(row['macro_f1']):.3f} & "
                f"[{float(row['ci95_low']):.3f}, {float(row['ci95_high']):.3f}] & "
                f"{float(row['delta_to_anchor']):.3f} & "
                f"{float(row['anchor_not_better_prob']):.3f} \\\\"
            )
            first = False
        lines.append("\\midrule")

    if lines[-1] == "\\midrule":
        lines.pop()
    lines.extend(
        [
            "\\bottomrule",
            "\\end{tabular}",
            "\\caption{Stratified-bootstrap macro-F1 confidence intervals across standard RevTrack splits. "
            "$P(\\leq 0)$ is the paired-bootstrap probability that the split anchor is not better than the compared model.}",
            "\\label{tab:cross-split-significance}",
            "\\end{table*}",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    output_dir = ROOT / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    all_rows: list[dict[str, Any]] = []
    for split_key, split_spec in SPLIT_SPECS.items():
        all_rows.extend(
            compute_split_rows(
                split_key=split_key,
                split_spec=split_spec,
                bootstrap_iters=args.bootstrap_iters,
                seed=args.seed,
            )
        )

    csv_path = output_dir / "cross_split_significance.csv"
    md_path = output_dir / "cross_split_significance.md"
    json_path = output_dir / "cross_split_significance.json"
    tex_path = ROOT / "paper/tables/cross_split_significance.tex"

    write_csv(csv_path, all_rows)
    write_markdown(md_path, rows=all_rows, bootstrap_iters=args.bootstrap_iters, seed=args.seed)
    write_tex(tex_path, all_rows)
    json_payload = {
        "status": "ok",
        "bootstrap_iters": args.bootstrap_iters,
        "seed": args.seed,
        "splits": list(SPLIT_SPECS.keys()),
        "results": all_rows,
    }
    json_path.write_text(json.dumps(json_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"Wrote {csv_path}")
    print(f"Wrote {md_path}")
    print(f"Wrote {tex_path}")
    print(f"Wrote {json_path}")


if __name__ == "__main__":
    main()
