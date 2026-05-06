from __future__ import annotations

import json
import random
import zlib
from collections import Counter
from pathlib import Path
from statistics import mean
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "outputs/day1/prompted_llm_baselines"

LABELS = ["fixed", "partially_fixed", "regressed", "unresolved"]

DATASETS = [
    ("iclr2024_clean_dev_v7", "ICLR24"),
    ("iclr2025_expanded80", "ICLR25"),
    ("neurips2024_limit100_resolved_candidate", "NeurIPS24"),
]

MODELS = [
    ("gpt55_v2", "GPT-5.5"),
    ("gpt-4.1_full", "GPT-4.1"),
    ("gpt-4o-mini_full", "GPT-4o-mini"),
    ("gpt-4.1-nano_full", "GPT-4.1-nano"),
    ("qwen2.5-72b-instruct_full", "Qwen2.5-72B"),
    ("gpt-4.1-mini_full", "GPT-4.1-mini"),
]

ENSEMBLES = [
    (
        "Vote-3 (top)",
        ["gpt55_v2", "gpt-4.1-mini_full", "qwen2.5-72b-instruct_full"],
        "majority",
    ),
    (
        "Vote-3 (diverse)",
        ["gpt55_v2", "gpt-4o-mini_full", "gpt-4.1_full"],
        "majority",
    ),
    (
        "Vote-3 (U-guard)",
        ["gpt55_v2", "gpt-4.1-mini_full", "qwen2.5-72b-instruct_full"],
        "u_guard",
    ),
    (
        "Vote-3 (U+F)",
        ["gpt55_v2", "gpt-4.1-mini_full", "qwen2.5-72b-instruct_full"],
        "u_guard_fix_suppress",
    ),
    ("Vote-6 (all)", [model_key for model_key, _ in MODELS], "majority"),
]

PREF_ORDER = [
    "gpt55_v2",
    "gpt-4.1-mini_full",
    "qwen2.5-72b-instruct_full",
    "gpt-4o-mini_full",
    "gpt-4.1_full",
    "gpt-4.1-nano_full",
]

SELECTED_METHODS = [
    "Majority",
    "GPT-5.5",
    "GPT-4.1-mini",
    "GPT-4.1-nano",
    "Vote-3 (U+F)",
]


def f1_for_label(gold: list[str], pred: list[str], label: str) -> float:
    tp = sum(1 for g, p in zip(gold, pred) if g == label and p == label)
    fp = sum(1 for g, p in zip(gold, pred) if g != label and p == label)
    fn = sum(1 for g, p in zip(gold, pred) if g == label and p != label)
    denom = 2 * tp + fp + fn
    if denom == 0:
        return 0.0
    return (2 * tp) / denom


def macro_f1(gold: list[str], pred: list[str]) -> float:
    return mean(f1_for_label(gold, pred, label) for label in LABELS)


def percentile(values: list[float], pct: float) -> float:
    ordered = sorted(values)
    index = (len(ordered) - 1) * pct
    lower = int(index)
    upper = min(lower + 1, len(ordered) - 1)
    weight = index - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def bootstrap_ci(gold: list[str], pred: list[str], *, reps: int = 2000, seed: int = 20260428) -> tuple[float, float]:
    rng = random.Random(seed)
    n = len(gold)
    scores: list[float] = []
    for _ in range(reps):
        indices = [rng.randrange(n) for _ in range(n)]
        sampled_gold = [gold[index] for index in indices]
        sampled_pred = [pred[index] for index in indices]
        scores.append(macro_f1(sampled_gold, sampled_pred))
    return percentile(scores, 0.025), percentile(scores, 0.975)


def load_model_details(dataset_key: str, model_key: str) -> list[dict[str, str]]:
    path = OUT_DIR / f"{dataset_key}_{model_key}_details.json"
    return json.loads(path.read_text(encoding="utf-8"))


def vote_label(model_keys: list[str], predictions: dict[str, dict[str, str]], issue_id: str) -> str:
    counts = Counter(predictions[model_key][issue_id] for model_key in model_keys)
    best = max(counts.values())
    candidates = [label for label, count in counts.items() if count == best]
    if len(candidates) == 1:
        return candidates[0]
    for model_key in PREF_ORDER:
        if model_key in model_keys:
            picked = predictions[model_key][issue_id]
            if picked in candidates:
                return picked
    return sorted(candidates)[0]


def ensemble_label(model_keys: list[str], predictions: dict[str, dict[str, str]], issue_id: str, rule: str) -> str:
    base = vote_label(model_keys, predictions, issue_id)
    labels = [predictions[model_key][issue_id] for model_key in model_keys]
    if rule == "u_guard":
        if base in {"fixed", "partially_fixed"} and labels.count("unresolved") >= 1:
            return "unresolved"
    if rule == "u_guard_fix_suppress":
        if base in {"fixed", "partially_fixed"} and labels.count("unresolved") >= 1:
            return "unresolved"
        if base == "fixed" and len(set(labels)) > 1:
            return "partially_fixed"
    return base


def risk_tag(dataset_name: str, method: str, score: float, lo: float, hi: float, majority_score: float) -> str:
    if method == "Majority":
        return "reference"
    if lo <= majority_score <= hi:
        return "overlaps majority"
    if score < majority_score:
        return "below majority"
    if hi - lo >= 0.20:
        return "wide interval"
    return "above majority"


def collect_dataset(dataset_key: str, dataset_name: str) -> list[dict[str, Any]]:
    details_by_model = {model_key: load_model_details(dataset_key, model_key) for model_key, _ in MODELS}
    first_model_key = MODELS[0][0]
    ids = [row["id"] for row in details_by_model[first_model_key]]
    gold_by_id = {row["id"]: row["gold_label"] for row in details_by_model[first_model_key]}
    gold = [gold_by_id[issue_id] for issue_id in ids]
    majority_label = Counter(gold).most_common(1)[0][0]

    predictions: dict[str, dict[str, str]] = {}
    for model_key, _ in MODELS:
        predictions[model_key] = {row["id"]: row["predicted_label"] for row in details_by_model[model_key]}

    method_predictions: dict[str, list[str]] = {"Majority": [majority_label] * len(ids)}
    for model_key, model_name in MODELS:
        method_predictions[model_name] = [predictions[model_key][issue_id] for issue_id in ids]
    for ensemble_name, model_keys, rule in ENSEMBLES:
        method_predictions[ensemble_name] = [
            ensemble_label(model_keys, predictions, issue_id, rule) for issue_id in ids
        ]

    majority_score = macro_f1(gold, method_predictions["Majority"])
    rows: list[dict[str, Any]] = []
    for method, pred in method_predictions.items():
        score = macro_f1(gold, pred)
        seed = 20260428 + zlib.crc32(f"{dataset_key}:{method}".encode("utf-8")) % 100000
        lo, hi = bootstrap_ci(gold, pred, seed=seed)
        rows.append(
            {
                "dataset": dataset_name,
                "method": method,
                "n": len(gold),
                "macro_f1": score,
                "ci95_low": lo,
                "ci95_high": hi,
                "ci95_width": hi - lo,
                "majority_macro_f1": majority_score,
                "risk": risk_tag(dataset_name, method, score, lo, hi, majority_score),
            }
        )
    return rows


def write_markdown(path: Path, rows: list[dict[str, Any]]) -> None:
    selected = [row for row in rows if row["method"] in SELECTED_METHODS]
    lines = [
        "# Prompted LLM bootstrap intervals",
        "",
        "Bootstrap confidence intervals are computed over examples from local gold/prediction detail files.",
        "They capture sample instability only; they do not include annotator uncertainty or API stochasticity.",
        "",
        "| Dataset | Method | n | Macro-F1 | 95% CI | Risk |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for row in selected:
        lines.append(
            "| {dataset} | {method} | {n} | {macro_f1:.3f} | [{ci95_low:.3f}, {ci95_high:.3f}] | {risk} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Cross-year prompted transfer remains claim-risky: the ICLR25 selected LLM/vote rows are below or overlap the majority reference.",
            "- NeurIPS24 intervals are useful bounded transfer evidence on a user-confirmed single-pass active frontier.",
            "- These intervals support a reliability/benchmark framing, not a solved-system framing.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_tex(path: Path, rows: list[dict[str, Any]]) -> None:
    selected = [row for row in rows if row["method"] in SELECTED_METHODS]
    lines = [
        r"\begin{table*}[t]",
        r"\centering",
        r"\scriptsize",
        r"\setlength{\tabcolsep}{4pt}",
        r"\begin{tabular}{llcccc}",
        r"\toprule",
        r"Dataset & Method & $n$ & Macro-F1 & 95\% CI & Risk \\",
        r"\midrule",
    ]
    for row in selected:
        lines.append(
            "{dataset} & {method} & {n} & {macro_f1:.3f} & [{ci95_low:.3f}, {ci95_high:.3f}] & {risk} \\\\".format(
                **row
            )
        )
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}",
            r"\caption{Example-level bootstrap intervals for selected prompted LLM and vote baselines. Intervals capture sample instability only; they do not include annotator uncertainty or API stochasticity.}",
            r"\label{tab:prompted-llm-bootstrap}",
            r"\end{table*}",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    rows: list[dict[str, Any]] = []
    for dataset_key, dataset_name in DATASETS:
        rows.extend(collect_dataset(dataset_key, dataset_name))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "prompted_llm_bootstrap_intervals.json").write_text(
        json.dumps({"rows": rows, "labels": LABELS, "selected_methods": SELECTED_METHODS}, indent=2),
        encoding="utf-8",
    )
    write_markdown(OUT_DIR / "prompted_llm_bootstrap_intervals.md", rows)
    write_tex(ROOT / "paper/tables/prompted_llm_bootstrap_intervals.tex", rows)
    print("wrote prompted LLM bootstrap intervals")


if __name__ == "__main__":
    main()
