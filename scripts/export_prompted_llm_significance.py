from __future__ import annotations

import csv
import json
import random
from collections import Counter
from pathlib import Path
from typing import Any

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from revtrack.io import load_examples


LABELS = ("fixed", "partially_fixed", "unresolved", "regressed")

DATASETS = [
    {
        "key": "iclr2024_clean_dev_v7",
        "name": "ICLR24",
        "examples": ROOT / "data/processed/iclr2024_clean_dev_assistant_v7.jsonl",
    },
    {
        "key": "iclr2025_expanded80",
        "name": "ICLR25",
        "examples": ROOT / "data/processed/iclr2025_expanded80_standard_validation_v1.jsonl",
    },
    {
        "key": "neurips2024_limit100_resolved_candidate",
        "name": "NeurIPS24",
        "examples": ROOT / "data/processed/neurips2024_limit100_standard_validation_v1.jsonl",
    },
]

BASE_MODELS = [
    ("gpt55_v2", "GPT-5.5 (v2)"),
    ("gpt-4.1-mini_full", "GPT-4.1-mini"),
    ("qwen2.5-72b-instruct_full", "Qwen2.5-72B"),
]

PREF_ORDER = [item[0] for item in BASE_MODELS]


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


def macro_f1(y_true: list[str], y_pred: list[str]) -> float:
    tp = Counter()
    pred_counts = Counter()
    gold_counts = Counter(y_true)
    for gold, pred in zip(y_true, y_pred):
        pred_counts[pred] += 1
        if gold == pred:
            tp[gold] += 1

    total = 0.0
    for label in LABELS:
        precision = tp[label] / pred_counts[label] if pred_counts[label] else 0.0
        recall = tp[label] / gold_counts[label] if gold_counts[label] else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
        total += f1
    return total / len(LABELS)


def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    if p <= 0:
        return min(values)
    if p >= 100:
        return max(values)
    ordered = sorted(values)
    rank = (len(ordered) - 1) * (p / 100.0)
    lo = int(rank)
    hi = min(lo + 1, len(ordered) - 1)
    frac = rank - lo
    return ordered[lo] * (1.0 - frac) + ordered[hi] * frac


def stratified_sample_indices(gold: list[str], rng: random.Random) -> list[int]:
    by_label: dict[str, list[int]] = {label: [] for label in LABELS}
    for idx, label in enumerate(gold):
        by_label.setdefault(label, []).append(idx)
    sampled: list[int] = []
    for label in LABELS:
        indices = by_label.get(label, [])
        if not indices:
            continue
        sampled.extend(rng.choice(indices) for _ in range(len(indices)))
    rng.shuffle(sampled)
    return sampled


def vote_label(model_preds: dict[str, dict[str, str]], issue_id: str) -> str:
    votes = [model_preds[key][issue_id] for key in PREF_ORDER]
    counts = Counter(votes)
    best = max(counts.values())
    candidates = [label for label, c in counts.items() if c == best]
    if len(candidates) == 1:
        return candidates[0]
    for model_key in PREF_ORDER:
        picked = model_preds[model_key][issue_id]
        if picked in candidates:
            return picked
    return sorted(candidates)[0]


def calibrated_vote_label(model_preds: dict[str, dict[str, str]], issue_id: str) -> str:
    base = vote_label(model_preds, issue_id)
    votes = [model_preds[key][issue_id] for key in PREF_ORDER]
    if base in {"fixed", "partially_fixed"} and "unresolved" in votes:
        return "unresolved"
    if base == "fixed" and len(set(votes)) > 1:
        return "partially_fixed"
    return base


def load_method_predictions(dataset_key: str, ids: list[str], gold: list[str]) -> dict[str, list[str]]:
    model_preds: dict[str, dict[str, str]] = {}
    for model_key, _ in BASE_MODELS:
        path = ROOT / f"outputs/day1/prompted_llm_baselines/{dataset_key}_{model_key}_predictions.jsonl"
        pred_map = {
            str(row["id"]): normalize_label(row.get("predicted_label"))
            for row in load_jsonl(path)
        }
        model_preds[model_key] = pred_map

    majority = Counter(gold).most_common(1)[0][0]
    methods = {
        "Majority": [majority for _ in ids],
        "GPT-5.5 (v2)": [model_preds["gpt55_v2"][issue_id] for issue_id in ids],
        "GPT-4.1-mini": [model_preds["gpt-4.1-mini_full"][issue_id] for issue_id in ids],
        "Qwen2.5-72B": [model_preds["qwen2.5-72b-instruct_full"][issue_id] for issue_id in ids],
        "Vote-3 (top)": [vote_label(model_preds, issue_id) for issue_id in ids],
        "Vote-3 (+U+F-cal)": [calibrated_vote_label(model_preds, issue_id) for issue_id in ids],
    }
    return methods


def evaluate_split(
    *,
    dataset: dict[str, Any],
    bootstrap_iters: int = 5000,
    seed: int = 20260506,
) -> list[dict[str, Any]]:
    examples = load_examples(dataset["examples"])
    ids = [example.id for example in examples]
    gold = [normalize_label(example.gold_label) for example in examples]
    methods = load_method_predictions(dataset["key"], ids, gold)

    majority_preds = methods["Majority"]
    majority_macro_f1 = macro_f1(gold, majority_preds)
    rows: list[dict[str, Any]] = []
    for method_name, preds in methods.items():
        method_macro_f1 = macro_f1(gold, preds)
        delta = method_macro_f1 - majority_macro_f1
        if method_name == "Majority":
            rows.append(
                {
                    "dataset": dataset["name"],
                    "method": method_name,
                    "n": len(gold),
                    "macro_f1": method_macro_f1,
                    "majority_macro_f1": majority_macro_f1,
                    "delta_vs_majority": 0.0,
                    "delta_ci95_low": 0.0,
                    "delta_ci95_high": 0.0,
                    "p_delta_le_zero": 1.0,
                    "status": "reference",
                }
            )
            continue

        rng = random.Random(seed + hash((dataset["key"], method_name)) % 1000000)
        boot_deltas: list[float] = []
        for _ in range(bootstrap_iters):
            sampled = stratified_sample_indices(gold, rng)
            sg = [gold[i] for i in sampled]
            sm = [preds[i] for i in sampled]
            sb = [majority_preds[i] for i in sampled]
            boot_deltas.append(macro_f1(sg, sm) - macro_f1(sg, sb))

        ci_low = percentile(boot_deltas, 2.5)
        ci_high = percentile(boot_deltas, 97.5)
        p_nonpos = sum(1 for value in boot_deltas if value <= 0.0) / float(len(boot_deltas))
        status = "above_majority" if ci_low > 0.0 else "overlap_or_below"
        rows.append(
            {
                "dataset": dataset["name"],
                "method": method_name,
                "n": len(gold),
                "macro_f1": method_macro_f1,
                "majority_macro_f1": majority_macro_f1,
                "delta_vs_majority": delta,
                "delta_ci95_low": ci_low,
                "delta_ci95_high": ci_high,
                "p_delta_le_zero": p_nonpos,
                "status": status,
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "dataset",
        "method",
        "n",
        "macro_f1",
        "majority_macro_f1",
        "delta_vs_majority",
        "delta_ci95_low",
        "delta_ci95_high",
        "p_delta_le_zero",
        "status",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, Any]]) -> None:
    lines = [
        "# Prompted LLM Significance vs Majority",
        "",
        "Paired stratified bootstrap on macro-F1 deltas (method - majority).",
        "",
        "| Dataset | Method | n | Macro-F1 | Delta vs Majority | 95% CI (Delta) | p(Delta<=0) | Status |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row['dataset']} | {row['method']} | {row['n']} | {row['macro_f1']:.3f} | "
            f"{row['delta_vs_majority']:.3f} | [{row['delta_ci95_low']:.3f}, {row['delta_ci95_high']:.3f}] | "
            f"{row['p_delta_le_zero']:.3f} | {row['status']} |"
        )
    lines.extend(
        [
            "",
            "Interpretation boundary: this is split-level sample uncertainty only; it does not include annotator uncertainty or API stochasticity.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_tex(path: Path, rows: list[dict[str, Any]]) -> None:
    chosen = [row for row in rows if row["method"] in {"GPT-5.5 (v2)", "GPT-4.1-mini", "Vote-3 (+U+F-cal)"}]
    lines = [
        r"\begin{table*}[t]",
        r"\centering",
        r"\scriptsize",
        r"\setlength{\tabcolsep}{3pt}",
        r"\begin{tabular}{llccccc}",
        r"\toprule",
        r"Dataset & Method & $n$ & Macro-F1 & $\Delta$ vs Majority & 95\% CI ($\Delta$) & $p(\Delta\le0)$ \\",
        r"\midrule",
    ]
    for row in chosen:
        lines.append(
            f"{row['dataset']} & {row['method']} & {row['n']} & {row['macro_f1']:.3f} & "
            f"{row['delta_vs_majority']:.3f} & "
            f"[{row['delta_ci95_low']:.3f}, {row['delta_ci95_high']:.3f}] & "
            f"{row['p_delta_le_zero']:.3f} \\\\"
        )
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}",
            r"\caption{Prompted LLM paired stratified-bootstrap significance against the majority baseline on standard-labeled splits. $\Delta$ is macro-F1(method) minus macro-F1(majority).}",
            r"\label{tab:prompted-llm-significance}",
            r"\end{table*}",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    rows: list[dict[str, Any]] = []
    for dataset in DATASETS:
        rows.extend(evaluate_split(dataset=dataset))

    out_dir = ROOT / "outputs/day1/paper_assets"
    json_path = out_dir / "prompted_llm_significance.json"
    csv_path = out_dir / "prompted_llm_significance.csv"
    md_path = out_dir / "prompted_llm_significance.md"
    tex_path = ROOT / "paper/tables/prompted_llm_significance.tex"

    out_dir.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps({"rows": rows}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_csv(csv_path, rows)
    write_markdown(md_path, rows)
    write_tex(tex_path, rows)
    print(json_path)


if __name__ == "__main__":
    main()
