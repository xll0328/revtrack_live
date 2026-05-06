from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from revtrack.io import load_examples
from revtrack.metrics import evaluate_predictions
from revtrack.schema import Prediction

LABEL_ORDER = ["fixed", "partially_fixed", "unresolved", "regressed"]
LABEL_SHORT = {"fixed": "F", "partially_fixed": "P", "unresolved": "U", "regressed": "R"}

DATASETS = [
    {
        "key": "iclr2024_clean_dev_v7",
        "name": "ICLR24",
        "examples": ROOT / "data/processed/iclr2024_clean_dev_assistant_v7.jsonl",
        "majority_macro_f1": 0.1838,
    },
    {
        "key": "iclr2025_expanded80",
        "name": "ICLR25",
        "examples": ROOT / "data/processed/iclr2025_expanded80_standard_validation_v1.jsonl",
        "majority_macro_f1": 0.2260,
    },
    {
        "key": "neurips2024_limit100_resolved_candidate",
        "name": "NeurIPS24",
        "examples": ROOT / "data/processed/neurips2024_limit100_standard_validation_v1.jsonl",
        "majority_macro_f1": 0.1774,
    },
]

MODEL_SPECS = [
    ("gpt55_v2", "GPT-5.5 (v2)"),
    ("gpt-4.1_full", "GPT-4.1"),
    ("gpt-4o-mini_full", "GPT-4o-mini"),
    ("gpt-4.1-nano_full", "GPT-4.1-nano"),
    ("qwen2.5-72b-instruct_full", "Qwen2.5-72B"),
    ("gpt-4.1-mini_full", "GPT-4.1-mini"),
]

ENSEMBLES = [
    {
        "key": "vote3_top",
        "name": "Vote-3 (top)",
        "models": ["gpt55_v2", "gpt-4.1-mini_full", "qwen2.5-72b-instruct_full"],
        "rule": "majority",
    },
    {
        "key": "vote3_div",
        "name": "Vote-3 (diverse)",
        "models": ["gpt55_v2", "gpt-4o-mini_full", "gpt-4.1_full"],
        "rule": "majority",
    },
    {
        "key": "vote3_u_guard",
        "name": "Vote-3 (+U-guard)",
        "models": ["gpt55_v2", "gpt-4.1-mini_full", "qwen2.5-72b-instruct_full"],
        "rule": "u_guard",
    },
    {
        "key": "vote3_u_f_cal",
        "name": "Vote-3 (+U+F-cal)",
        "models": ["gpt55_v2", "gpt-4.1-mini_full", "qwen2.5-72b-instruct_full"],
        "rule": "u_guard_fix_suppress",
    },
    {
        "key": "vote6_all",
        "name": "Vote-6 (all)",
        "models": [item[0] for item in MODEL_SPECS],
        "rule": "majority",
    },
]

# Tie-break preference order for deterministic voting.
PREF_ORDER = [
    "gpt55_v2",
    "gpt-4.1-mini_full",
    "qwen2.5-72b-instruct_full",
    "gpt-4o-mini_full",
    "gpt-4.1_full",
    "gpt-4.1-nano_full",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_predictions(path: Path) -> dict[str, str]:
    rows: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        row = json.loads(line)
        rows[row["id"]] = row["predicted_label"]
    return rows


def vote_label(model_ids: list[str], pred_by_model: dict[str, dict[str, str]], issue_id: str) -> str:
    counts = Counter(pred_by_model[model_id][issue_id] for model_id in model_ids)
    best = max(counts.values())
    candidates = [label for label, count in counts.items() if count == best]
    if len(candidates) == 1:
        return candidates[0]
    for model_id in PREF_ORDER:
        if model_id in model_ids:
            picked = pred_by_model[model_id][issue_id]
            if picked in candidates:
                return picked
    return sorted(candidates)[0]


def ensemble_label(
    *,
    model_ids: list[str],
    pred_by_model: dict[str, dict[str, str]],
    issue_id: str,
    rule: str,
) -> str:
    base = vote_label(model_ids, pred_by_model, issue_id)
    labels = [pred_by_model[model_id][issue_id] for model_id in model_ids]
    if rule == "u_guard":
        if base in {"fixed", "partially_fixed"} and labels.count("unresolved") >= 1:
            return "unresolved"
    if rule == "u_guard_fix_suppress":
        if base in {"fixed", "partially_fixed"} and labels.count("unresolved") >= 1:
            return "unresolved"
        if base == "fixed" and len(set(labels)) > 1:
            return "partially_fixed"
    return base


def score_vote_ensemble(
    examples_path: Path,
    dataset_key: str,
    ensemble_models: list[str],
    rule: str,
) -> dict[str, Any]:
    examples = load_examples(examples_path)
    pred_by_model = {
        model_id: load_predictions(ROOT / f"outputs/day1/prompted_llm_baselines/{dataset_key}_{model_id}_predictions.jsonl")
        for model_id in ensemble_models
    }
    predictions = [
        Prediction(
            id=example.id,
            predicted_label=ensemble_label(
                model_ids=ensemble_models,
                pred_by_model=pred_by_model,
                issue_id=example.id,
                rule=rule,
            ),
        )
        for example in examples
    ]
    summary, _ = evaluate_predictions(examples, predictions)
    return summary


def majority_label(examples_path: Path) -> str:
    examples = load_examples(examples_path)
    counts = Counter(example.gold_label for example in examples)
    return max(LABEL_ORDER, key=lambda label: (counts[label], -LABEL_ORDER.index(label)))


def collect_rows() -> tuple[list[dict[str, Any]], dict[str, dict[str, dict[str, float]]]]:
    rows: list[dict[str, Any]] = []
    recall_payload: dict[str, dict[str, dict[str, float]]] = {}
    for dataset in DATASETS:
        dataset_key = dataset["key"]
        row: dict[str, Any] = {"dataset": dataset["name"], "majority": dataset["majority_macro_f1"]}
        model_summaries: dict[str, dict[str, Any]] = {}
        for model_id, model_name in MODEL_SPECS:
            metrics_path = ROOT / f"outputs/day1/prompted_llm_baselines/{dataset_key}_{model_id}_metrics.json"
            metrics = load_json(metrics_path)
            row[model_name] = float(metrics["macro_f1"])
            model_summaries[model_name] = metrics

        ensemble_summaries: dict[str, dict[str, Any]] = {}
        for ensemble in ENSEMBLES:
            summary = score_vote_ensemble(
                examples_path=dataset["examples"],
                dataset_key=dataset_key,
                ensemble_models=ensemble["models"],
                rule=ensemble["rule"],
            )
            row[ensemble["name"]] = float(summary["macro_f1"])
            ensemble_summaries[ensemble["name"]] = summary

        majority = majority_label(dataset["examples"])
        recall_payload[dataset["name"]] = {
            "Majority": {label: 1.0 if label == majority else 0.0 for label in LABEL_ORDER},
            "GPT-5.5 (v2)": {
                label: float(model_summaries["GPT-5.5 (v2)"]["per_label"][label]["recall"]) for label in LABEL_ORDER
            },
            "GPT-4.1-mini": {
                label: float(model_summaries["GPT-4.1-mini"]["per_label"][label]["recall"]) for label in LABEL_ORDER
            },
            "Qwen2.5-72B": {
                label: float(model_summaries["Qwen2.5-72B"]["per_label"][label]["recall"]) for label in LABEL_ORDER
            },
            "Vote-3 (top)": {
                label: float(ensemble_summaries["Vote-3 (top)"]["per_label"][label]["recall"]) for label in LABEL_ORDER
            },
            "Vote-3 (+U+F-cal)": {
                label: float(ensemble_summaries["Vote-3 (+U+F-cal)"]["per_label"][label]["recall"])
                for label in LABEL_ORDER
            },
        }
        rows.append(row)
    return rows, recall_payload


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_table(path: Path, rows: list[dict[str, Any]]) -> None:
    model_cols = [model_name for _, model_name in MODEL_SPECS]
    ensemble_cols = [ensemble["name"] for ensemble in ENSEMBLES]
    all_cols = ["Majority"] + model_cols + ensemble_cols
    table_names = {
        "Vote-3 (+U-guard)": "Vote-3 (U-guard)",
        "Vote-3 (+U+F-cal)": "Vote-3 (U+F)",
    }

    means: dict[str, float] = {}
    for col in all_cols:
        key = "majority" if col == "Majority" else col
        means[col] = sum(float(row[key]) for row in rows) / len(rows)

    lines = [
        r"\begin{table}[t]",
        r"\centering",
        r"\scriptsize",
        r"\setlength{\tabcolsep}{2pt}",
        r"\begin{tabular}{p{0.28\linewidth}cccc}",
        r"\toprule",
        r"Model & ICLR24 & ICLR25 & NeurIPS & Mean \\",
        r"\midrule",
    ]

    def add_line(name: str, key: str) -> None:
        d1 = rows[0][key]
        d2 = rows[1][key]
        d3 = rows[2][key]
        mean = means[name]
        display_name = table_names.get(name, name)
        lines.append(f"{display_name} & {d1:.3f} & {d2:.3f} & {d3:.3f} & {mean:.3f} \\\\")

    add_line("Majority", "majority")
    for _, model_name in MODEL_SPECS:
        add_line(model_name, model_name)
    lines.append(r"\midrule")
    for ensemble in ENSEMBLES:
        ensemble_name = ensemble["name"]
        add_line(ensemble_name, ensemble_name)
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}",
            r"\caption{Macro-F1 of prompted LLMs and vote ensembles on three standard-labeled splits. Voting improves in-domain stability but does not resolve cross-year brittleness on expanded80.}",
            r"\label{tab:prompted-llm-ensemble}",
            r"\end{table}",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_figure(path: Path, rows: list[dict[str, Any]]) -> None:
    labels = ["Majority", "GPT-5.5 (v2)", "GPT-4.1-mini", "Vote-3 (top)", "Vote-3 (+U+F-cal)"]
    colors = ["#3f3f46", "#0f766e", "#2563eb", "#b45309", "#dc2626"]
    keys = {
        "Majority": "majority",
        "GPT-5.5 (v2)": "GPT-5.5 (v2)",
        "GPT-4.1-mini": "GPT-4.1-mini",
        "Vote-3 (top)": "Vote-3 (top)",
        "Vote-3 (+U+F-cal)": "Vote-3 (+U+F-cal)",
    }

    fig, axes = plt.subplots(1, 3, figsize=(11.5, 3.4), sharey=True)
    for idx, dataset_row in enumerate(rows):
        ax = axes[idx]
        values = [float(dataset_row[keys[label]]) for label in labels]
        ax.bar(range(len(labels)), values, color=colors, alpha=0.9)
        ax.set_title(dataset_row["dataset"], fontsize=11, weight="bold")
        ax.set_ylim(0.0, 0.42)
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=35, ha="right", fontsize=8)
        ax.grid(axis="y", linestyle="--", alpha=0.35)
        if idx == 0:
            ax.set_ylabel("Macro-F1", fontsize=10)

    fig.suptitle("Prompted LLM Transfer: Strong In-Domain, Brittle Cross-Year", fontsize=12, weight="bold")
    fig.tight_layout(rect=[0.0, 0.02, 1.0, 0.92])
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=220)
    plt.close(fig)


def write_label_recall_figure(path: Path, recall_payload: dict[str, dict[str, dict[str, float]]]) -> None:
    series = ["Majority", "GPT-5.5 (v2)", "GPT-4.1-mini", "Vote-3 (top)", "Vote-3 (+U+F-cal)"]
    colors = ["#3f3f46", "#0f766e", "#2563eb", "#b45309", "#dc2626"]
    dataset_names = ["ICLR24", "ICLR25", "NeurIPS24"]

    fig, axes = plt.subplots(1, 3, figsize=(12.2, 3.6), sharey=True)
    bar_width = 0.16
    x = list(range(len(LABEL_ORDER)))

    for idx, dataset_name in enumerate(dataset_names):
        ax = axes[idx]
        payload = recall_payload[dataset_name]
        for s_idx, series_name in enumerate(series):
            values = [float(payload[series_name][label]) for label in LABEL_ORDER]
            shifted = [v + (s_idx - 2) * bar_width for v in x]
            ax.bar(shifted, values, width=bar_width, color=colors[s_idx], alpha=0.92)
        ax.set_title(dataset_name, fontsize=11, weight="bold")
        ax.set_xticks(x)
        ax.set_xticklabels([LABEL_SHORT[label] for label in LABEL_ORDER], fontsize=9)
        ax.set_ylim(0.0, 1.02)
        ax.grid(axis="y", linestyle="--", alpha=0.35)
        if idx == 0:
            ax.set_ylabel("Recall", fontsize=10)

    handles = [plt.Rectangle((0, 0), 1, 1, color=colors[i]) for i in range(len(series))]
    fig.legend(handles, series, ncol=5, loc="upper center", bbox_to_anchor=(0.5, 1.03), frameon=False, fontsize=8.5)
    fig.suptitle("Label-Wise Recall: Transfer Failures Concentrate on Unresolved/Regressed", fontsize=12, weight="bold")
    fig.tight_layout(rect=[0.0, 0.02, 1.0, 0.90])
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=220)
    plt.close(fig)


def confusion_counts(examples: list[Any], pred_by_id: dict[str, str]) -> list[list[int]]:
    idx = {label: i for i, label in enumerate(LABEL_ORDER)}
    matrix = [[0 for _ in LABEL_ORDER] for _ in LABEL_ORDER]
    for example in examples:
        gold = example.gold_label
        pred = pred_by_id.get(example.id, "")
        if gold not in idx or pred not in idx:
            continue
        matrix[idx[gold]][idx[pred]] += 1
    return matrix


def row_normalize(matrix: list[list[int]]) -> list[list[float]]:
    normalized: list[list[float]] = []
    for row in matrix:
        total = sum(row)
        if total == 0:
            normalized.append([0.0 for _ in row])
        else:
            normalized.append([value / total for value in row])
    return normalized


def write_expanded80_confusion_figure(path: Path) -> None:
    dataset_key = "iclr2025_expanded80"
    examples = load_examples(ROOT / "data/processed/iclr2025_expanded80_standard_validation_v1.jsonl")

    majority = majority_label(ROOT / "data/processed/iclr2025_expanded80_standard_validation_v1.jsonl")
    majority_pred = {example.id: majority for example in examples}

    gpt55_pred = load_predictions(ROOT / f"outputs/day1/prompted_llm_baselines/{dataset_key}_gpt55_v2_predictions.jsonl")

    vote_models = ["gpt55_v2", "gpt-4.1-mini_full", "qwen2.5-72b-instruct_full"]
    vote_pred_by_model = {
        model_id: load_predictions(ROOT / f"outputs/day1/prompted_llm_baselines/{dataset_key}_{model_id}_predictions.jsonl")
        for model_id in vote_models
    }
    vote_guard_pred = {
        example.id: ensemble_label(
            model_ids=vote_models,
            pred_by_model=vote_pred_by_model,
            issue_id=example.id,
            rule="u_guard_fix_suppress",
        )
        for example in examples
    }

    panels = [
        ("Majority", majority_pred),
        ("GPT-5.5 (v2)", gpt55_pred),
        ("Vote-3 (+U+F-cal)", vote_guard_pred),
    ]

    fig, axes = plt.subplots(1, 3, figsize=(12.0, 3.8), sharey=True)
    labels = [LABEL_SHORT[label] for label in LABEL_ORDER]

    for i, (title, pred_map) in enumerate(panels):
        counts = confusion_counts(examples, pred_map)
        norms = row_normalize(counts)
        ax = axes[i]
        image = ax.imshow(norms, cmap="YlOrRd", vmin=0.0, vmax=1.0)
        ax.set_title(title, fontsize=11, weight="bold")
        ax.set_xticks(range(len(LABEL_ORDER)))
        ax.set_yticks(range(len(LABEL_ORDER)))
        ax.set_xticklabels(labels, fontsize=9)
        ax.set_yticklabels(labels, fontsize=9)
        ax.set_xlabel("Pred", fontsize=9)
        if i == 0:
            ax.set_ylabel("Gold", fontsize=9)
        for r in range(len(LABEL_ORDER)):
            for c in range(len(LABEL_ORDER)):
                ratio = norms[r][c]
                count = counts[r][c]
                color = "black" if ratio < 0.6 else "white"
                ax.text(c, r, f"{count}\n{ratio:.2f}", ha="center", va="center", fontsize=7.5, color=color)

    cbar = fig.colorbar(image, ax=axes.ravel().tolist(), fraction=0.02, pad=0.02)
    cbar.ax.set_ylabel("Row-normalized ratio", rotation=90, fontsize=9)
    fig.suptitle("Expanded80 Confusion: Unresolved Collapse Under Prompted Transfer", fontsize=12, weight="bold")
    fig.subplots_adjust(left=0.05, right=0.94, bottom=0.12, top=0.84, wspace=0.25)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=220)
    plt.close(fig)


def error_category(gold: str, pred: str) -> str:
    if gold == pred:
        return "correct"
    if gold == "unresolved" and pred in {"fixed", "partially_fixed"}:
        return "overcredit_unresolved"
    if gold == "fixed" and pred in {"partially_fixed", "unresolved", "regressed"}:
        return "fixed_under_recovery"
    if gold == "regressed" and pred != "regressed":
        return "regression_blindness"
    if gold == "partially_fixed" and pred == "fixed":
        return "partial_to_fixed"
    return "other_error"


def write_expanded80_error_stack(path: Path) -> None:
    dataset_key = "iclr2025_expanded80"
    examples = load_examples(ROOT / "data/processed/iclr2025_expanded80_standard_validation_v1.jsonl")
    gold_by_id = {example.id: example.gold_label for example in examples}

    majority = majority_label(ROOT / "data/processed/iclr2025_expanded80_standard_validation_v1.jsonl")
    majority_pred = {example.id: majority for example in examples}
    gpt55_pred = load_predictions(ROOT / f"outputs/day1/prompted_llm_baselines/{dataset_key}_gpt55_v2_predictions.jsonl")
    gpt55_u_pred = load_predictions(ROOT / f"outputs/day1/prompted_llm_baselines/{dataset_key}_gpt55_v2_u_strict_predictions.jsonl")
    mini_pred = load_predictions(ROOT / f"outputs/day1/prompted_llm_baselines/{dataset_key}_gpt-4.1-mini_full_predictions.jsonl")
    mini_u_pred = load_predictions(ROOT / f"outputs/day1/prompted_llm_baselines/{dataset_key}_gpt-4.1-mini_u_strict_predictions.jsonl")
    nano_pred = load_predictions(ROOT / f"outputs/day1/prompted_llm_baselines/{dataset_key}_gpt-4.1-nano_full_predictions.jsonl")
    nano_u_pred = load_predictions(ROOT / f"outputs/day1/prompted_llm_baselines/{dataset_key}_gpt-4.1-nano_u_strict_predictions.jsonl")

    vote_models = ["gpt55_v2", "gpt-4.1-mini_full", "qwen2.5-72b-instruct_full"]
    vote_pred_by_model = {
        model_id: load_predictions(ROOT / f"outputs/day1/prompted_llm_baselines/{dataset_key}_{model_id}_predictions.jsonl")
        for model_id in vote_models
    }
    vote_guard_pred = {
        example.id: ensemble_label(
            model_ids=vote_models,
            pred_by_model=vote_pred_by_model,
            issue_id=example.id,
            rule="u_guard_fix_suppress",
        )
        for example in examples
    }

    methods = [
        ("Majority", majority_pred),
        ("GPT-5.5 (v2)", gpt55_pred),
        ("GPT-5.5 (+U-strict)", gpt55_u_pred),
        ("GPT-4.1-mini", mini_pred),
        ("GPT-4.1-mini (+U-strict)", mini_u_pred),
        ("GPT-4.1-nano", nano_pred),
        ("GPT-4.1-nano (+U-strict)", nano_u_pred),
        ("Vote-3 (+U+F-cal)", vote_guard_pred),
    ]
    categories = [
        ("overcredit_unresolved", "Over-credit U"),
        ("fixed_under_recovery", "Miss fixed"),
        ("regression_blindness", "Miss regressed"),
        ("partial_to_fixed", "P->F boundary"),
        ("other_error", "Other"),
    ]
    colors = {
        "overcredit_unresolved": "#dc2626",
        "fixed_under_recovery": "#f59e0b",
        "regression_blindness": "#7c3aed",
        "partial_to_fixed": "#0ea5e9",
        "other_error": "#6b7280",
    }

    counts_by_method: dict[str, Counter[str]] = {}
    for method_name, pred_map in methods:
        counter: Counter[str] = Counter()
        for issue_id, gold in gold_by_id.items():
            pred = pred_map.get(issue_id, "")
            cat = error_category(gold, pred)
            counter[cat] += 1
        counts_by_method[method_name] = counter

    fig, ax = plt.subplots(figsize=(12.4, 4.0))
    x = list(range(len(methods)))
    bottoms = [0] * len(methods)

    for cat_key, cat_label in categories:
        vals = [counts_by_method[method_name][cat_key] for method_name, _ in methods]
        ax.bar(
            x,
            vals,
            bottom=bottoms,
            color=colors[cat_key],
            alpha=0.92,
            label=cat_label,
            width=0.68,
        )
        bottoms = [bottoms[i] + vals[i] for i in range(len(vals))]

    ax.set_xticks(x)
    ax.set_xticklabels([name for name, _ in methods], rotation=20, ha="right", fontsize=9)
    ax.set_ylabel("Error count (80 examples)", fontsize=10)
    ax.set_title("Expanded80 Error Decomposition by Failure Type", fontsize=12, weight="bold")
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    ax.legend(ncol=3, fontsize=8, frameon=False, loc="upper right")

    for i, (_, _) in enumerate(methods):
        total_err = sum(counts_by_method[methods[i][0]][cat_key] for cat_key, _ in categories)
        ax.text(i, total_err + 0.8, str(total_err), ha="center", va="bottom", fontsize=8.5, color="#111827")

    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=220)
    plt.close(fig)


def main() -> None:
    rows, recall_payload = collect_rows()
    means: dict[str, float] = {}
    for key in rows[0].keys():
        if key == "dataset":
            continue
        means[key] = sum(float(row[key]) for row in rows) / len(rows)
    write_json(
        ROOT / "outputs/day1/prompted_llm_baselines/prompted_llm_ensemble_summary.json",
        {"rows": rows, "means": means, "label_recall": recall_payload},
    )
    write_table(ROOT / "paper/tables/prompted_llm_ensemble.tex", rows)
    write_figure(ROOT / "paper/figures/figure3_prompted_llm_transfer.pdf", rows)
    write_label_recall_figure(ROOT / "paper/figures/figure4_prompted_llm_label_recall.pdf", recall_payload)
    write_expanded80_confusion_figure(ROOT / "paper/figures/figure5_expanded80_confusion.pdf")
    write_expanded80_error_stack(ROOT / "paper/figures/figure6_expanded80_error_stack.pdf")
    print("wrote prompted llm ensemble assets")


if __name__ == "__main__":
    main()
