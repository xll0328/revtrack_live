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


MODEL_SPECS = {
    "majority": {
        "name": "Majority label",
        "predictions": None,
    },
    "tfidf": {
        "name": "TF-IDF + LinearSVC",
        "predictions": "outputs/day1/iclr2024_clean_dev_assistant_v7_tfidf_predictions.jsonl",
    },
    "modernbert": {
        "name": "ModernBERT + LinearSVC",
        "predictions": "outputs/day1/iclr2024_clean_dev_assistant_v7_modernbert_predictions.jsonl",
    },
    "mpnet": {
        "name": "MPNet + LinearSVC",
        "predictions": "outputs/day1/iclr2024_clean_dev_assistant_v7_mpnet_predictions.jsonl",
    },
    "structured_no_overrides": {
        "name": "Structured (No Overrides)",
        "predictions": "outputs/day1/iclr2024_clean_dev_assistant_v7_structured_no_overrides_predictions.jsonl",
    },
    "structured": {
        "name": "Structured",
        "predictions": "outputs/day1/iclr2024_clean_dev_assistant_v7_structured_predictions.jsonl",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export bootstrap significance assets for ICLR 2024 clean-dev v7 main results."
    )
    parser.add_argument(
        "--dataset",
        default="data/processed/iclr2024_clean_dev_assistant_v7.jsonl",
    )
    parser.add_argument(
        "--output-dir",
        default="outputs/day1/paper_assets",
    )
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


def load_gold(path: str | Path) -> tuple[list[str], list[str]]:
    rows = load_jsonl(path)
    ids = [str(row["id"]) for row in rows]
    gold = [str(row.get("gold_label", "")).strip().lower() for row in rows]
    return ids, gold


def load_model_predictions(ids: list[str], spec: dict[str, Any], gold: list[str]) -> list[str]:
    pred_path = spec.get("predictions")
    if pred_path is None:
        # Majority label baseline defined on evaluation labels.
        majority = Counter(gold).most_common(1)[0][0]
        return [majority for _ in ids]
    pred_rows = load_jsonl(ROOT / str(pred_path))
    pred_by_id = {str(row["id"]): str(row.get("predicted_label", "")).strip().lower() for row in pred_rows}
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
    for i, label in enumerate(gold):
        if label in by_label_indices:
            by_label_indices[label].append(i)
        else:
            by_label_indices[label] = [i]
    dist = {model_key: [] for model_key in preds_by_model}
    for _ in range(iters):
        # Stratified bootstrap to preserve severe label skew.
        idx: list[int] = []
        for label, label_indices in by_label_indices.items():
            if not label_indices:
                continue
            idx.extend(rng.choice(label_indices) for _ in range(len(label_indices)))
        rng.shuffle(idx)
        sampled_gold = [gold[i] for i in idx]
        for model_key, preds in preds_by_model.items():
            sampled_pred = [preds[i] for i in idx]
            dist[model_key].append(macro_f1(sampled_gold, sampled_pred))
    return dist


def main() -> None:
    args = parse_args()
    output_dir = ROOT / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    ids, gold = load_gold(ROOT / args.dataset)
    preds_by_model = {
        model_key: load_model_predictions(ids, spec, gold)
        for model_key, spec in MODEL_SPECS.items()
    }

    point_estimates = {
        model_key: macro_f1(gold, preds)
        for model_key, preds in preds_by_model.items()
    }
    dist = bootstrap_distributions(
        gold=gold,
        preds_by_model=preds_by_model,
        iters=args.bootstrap_iters,
        seed=args.seed,
    )

    structured_key = "structured"
    rows: list[dict[str, Any]] = []
    for model_key, spec in MODEL_SPECS.items():
        boot = dist[model_key]
        lower = percentile(boot, 2.5)
        upper = percentile(boot, 97.5)
        delta = point_estimates[structured_key] - point_estimates[model_key]
        delta_boot = [dist[structured_key][i] - boot[i] for i in range(len(boot))]
        # one-sided probability that Structured is not better than model
        p_not_better = sum(1 for item in delta_boot if item <= 0) / len(delta_boot)
        rows.append(
            {
                "model_key": model_key,
                "model": spec["name"],
                "rows": len(gold),
                "macro_f1": round(point_estimates[model_key], 6),
                "ci95_low": round(lower, 6),
                "ci95_high": round(upper, 6),
                "delta_to_structured": round(delta, 6),
                "structured_not_better_prob": round(p_not_better, 6),
            }
        )

    csv_path = output_dir / "iclr2024_main_results_significance.csv"
    fieldnames = [
        "model_key",
        "model",
        "rows",
        "macro_f1",
        "ci95_low",
        "ci95_high",
        "delta_to_structured",
        "structured_not_better_prob",
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    md_lines = [
        "# ICLR 2024 Main-Results Significance",
        "",
        f"- Dataset: `{args.dataset}`",
        f"- Rows: `{len(gold)}`",
        f"- Bootstrap iterations: `{args.bootstrap_iters}`",
        f"- Seed: `{args.seed}`",
        "",
        "| Model | Macro-F1 | 95% CI | Δ vs Structured | P(Structured not better) |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in sorted(rows, key=lambda r: r["macro_f1"], reverse=True):
        md_lines.append(
            "| "
            + " | ".join(
                [
                    str(row["model"]),
                    f"{float(row['macro_f1']):.3f}",
                    f"[{float(row['ci95_low']):.3f}, {float(row['ci95_high']):.3f}]",
                    f"{float(row['delta_to_structured']):.3f}",
                    f"{float(row['structured_not_better_prob']):.3f}",
                ]
            )
            + " |"
        )

    md_lines.extend(
        [
            "",
            "Interpretation:",
            "- `P(Structured not better)` is a paired-bootstrap risk indicator; lower is stronger evidence for Structured.",
            "- This assesses sample uncertainty only on the current labeled split and does not include annotator uncertainty.",
            "",
        ]
    )
    md_path = output_dir / "iclr2024_main_results_significance.md"
    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    tex_lines = [
        "\\begin{table}[t]",
        "\\centering",
        "\\scriptsize",
        "\\setlength{\\tabcolsep}{3pt}",
        "\\begin{tabular}{p{0.36\\linewidth}rrrr}",
        "\\toprule",
        "Model & Macro-F1 & 95\\% CI & $\\Delta$ to Structured & $P(\\leq 0)$ \\\\",
        "\\midrule",
    ]
    for row in sorted(rows, key=lambda r: r["macro_f1"], reverse=True):
        tex_lines.append(
            f"{row['model']} & "
            f"{float(row['macro_f1']):.3f} & "
            f"[{float(row['ci95_low']):.3f}, {float(row['ci95_high']):.3f}] & "
            f"{float(row['delta_to_structured']):.3f} & "
            f"{float(row['structured_not_better_prob']):.3f} \\\\"
        )
    tex_lines.extend(
        [
            "\\bottomrule",
            "\\end{tabular}",
            "\\caption{Stratified-bootstrap significance summary on ICLR 2024 clean dev v7. "
            "$P(\\leq 0)$ is the paired-bootstrap probability that Structured is not better than the compared model on macro-F1.}",
            "\\label{tab:iclr2024-significance}",
            "\\end{table}",
            "",
        ]
    )
    tex_path = ROOT / "paper/tables/iclr2024_significance.tex"
    tex_path.write_text("\n".join(tex_lines), encoding="utf-8")

    json_path = output_dir / "iclr2024_main_results_significance.json"
    json_payload = {
        "status": "ok",
        "dataset": args.dataset,
        "rows": len(gold),
        "bootstrap_iters": args.bootstrap_iters,
        "seed": args.seed,
        "results": rows,
    }
    json_path.write_text(json.dumps(json_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"Wrote {csv_path}")
    print(f"Wrote {md_path}")
    print(f"Wrote {tex_path}")
    print(f"Wrote {json_path}")


if __name__ == "__main__":
    main()
