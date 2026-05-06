from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Callable

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from revtrack.io import load_examples
from revtrack.metrics import evaluate_predictions
from revtrack.schema import Prediction


DATASETS = [
    ("iclr2024_clean_dev_v7", ROOT / "data/processed/iclr2024_clean_dev_assistant_v7.jsonl"),
    ("iclr2025_expanded80", ROOT / "data/processed/iclr2025_expanded80_standard_validation_v1.jsonl"),
    ("neurips2024_limit100_resolved_candidate", ROOT / "data/processed/neurips2024_limit100_standard_validation_v1.jsonl"),
]
MODELS = ["gpt55_v2", "gpt-4.1-mini_full", "qwen2.5-72b-instruct_full"]
PREF_ORDER = MODELS


def load_predictions(dataset_key: str, model_key: str) -> dict[str, str]:
    path = ROOT / f"outputs/day1/prompted_llm_baselines/{dataset_key}_{model_key}_predictions.jsonl"
    rows: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        row = json.loads(line)
        rows[row["id"]] = row["predicted_label"]
    return rows


def vote_label(values: list[str], model_preds: dict[str, dict[str, str]], issue_id: str) -> str:
    counts = Counter(values)
    best = max(counts.values())
    candidates = [label for label, count in counts.items() if count == best]
    if len(candidates) == 1:
        return candidates[0]
    for model_key in PREF_ORDER:
        picked = model_preds[model_key][issue_id]
        if picked in candidates:
            return picked
    return sorted(candidates)[0]


def rule_base(base: str, values: list[str]) -> str:
    return base


def rule_u_any(base: str, values: list[str]) -> str:
    if base in {"fixed", "partially_fixed"} and "unresolved" in values:
        return "unresolved"
    return base


def rule_u_guard_fix_suppress(base: str, values: list[str]) -> str:
    if base in {"fixed", "partially_fixed"} and "unresolved" in values:
        return "unresolved"
    if base == "fixed" and len(set(values)) > 1:
        return "partially_fixed"
    return base


def rule_fixed_suppress(base: str, values: list[str]) -> str:
    if base == "fixed" and len(set(values)) > 1:
        return "partially_fixed"
    return base


RULES: dict[str, Callable[[str, list[str]], str]] = {
    "base": rule_base,
    "u_any": rule_u_any,
    "u_guard_fix_suppress": rule_u_guard_fix_suppress,
    "fixed_suppress": rule_fixed_suppress,
}


def evaluate_rule(rule_name: str, transform: Callable[[str, list[str]], str]) -> dict[str, object]:
    per_dataset = []
    macro_values = []
    for dataset_key, examples_path in DATASETS:
        examples = load_examples(examples_path)
        model_preds = {model_key: load_predictions(dataset_key, model_key) for model_key in MODELS}
        predictions = []
        for example in examples:
            values = [model_preds[model_key][example.id] for model_key in MODELS]
            base = vote_label(values, model_preds, example.id)
            pred = transform(base, values)
            predictions.append(Prediction(id=example.id, predicted_label=pred))
        summary, _ = evaluate_predictions(examples, predictions)
        macro = float(summary["macro_f1"])
        macro_values.append(macro)
        per_dataset.append(
            {
                "dataset_key": dataset_key,
                "accuracy": float(summary["accuracy"]),
                "macro_f1": macro,
                "unresolved_recall": float(summary["per_label"]["unresolved"]["recall"]),
                "fixed_recall": float(summary["per_label"]["fixed"]["recall"]),
                "regressed_recall": float(summary["per_label"]["regressed"]["recall"]),
            }
        )
    return {
        "rule": rule_name,
        "mean_macro_f1": sum(macro_values) / len(macro_values),
        "datasets": per_dataset,
    }


def main() -> None:
    results = [evaluate_rule(name, fn) for name, fn in RULES.items()]
    results.sort(key=lambda row: row["mean_macro_f1"], reverse=True)
    payload = {"models": MODELS, "rules": results}
    out = ROOT / "outputs/day1/prompted_llm_baselines/postprocess_rule_search.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
