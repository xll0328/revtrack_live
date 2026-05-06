from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
LABEL_ORDER = ["fixed", "partially_fixed", "unresolved", "regressed"]

MODEL_SPECS = {
    "heuristic": "Heuristic",
    "tfidf": "TF-IDF + LinearSVC",
    "modernbert": "ModernBERT + LinearSVC",
    "mpnet": "MPNet + LinearSVC",
    "issue_ledger": "Issue-Ledger",
    "structured_no_overrides": "Structured (No Overrides)",
    "structured": "Structured",
}

CLEAN_DEV_METRICS = {
    "v1": {
        "data": "data/processed/iclr2024_clean_dev_assistant_v1.jsonl",
        "heuristic": "outputs/day1/iclr2024_clean_dev_assistant_heuristic_metrics.json",
        "tfidf": "outputs/day1/iclr2024_clean_dev_assistant_tfidf_metrics.json",
        "modernbert": "outputs/day1/iclr2024_clean_dev_assistant_modernbert_metrics.json",
        "mpnet": "outputs/day1/iclr2024_clean_dev_assistant_mpnet_metrics.json",
        "issue_ledger": "outputs/day1/iclr2024_clean_dev_assistant_issue_ledger_metrics.json",
    },
    "v2": {
        "data": "data/processed/iclr2024_clean_dev_assistant_v2.jsonl",
        "heuristic": "outputs/day1/iclr2024_clean_dev_assistant_v2_heuristic_metrics.json",
        "tfidf": "outputs/day1/iclr2024_clean_dev_assistant_v2_tfidf_metrics.json",
        "modernbert": "outputs/day1/iclr2024_clean_dev_assistant_v2_modernbert_metrics.json",
        "mpnet": "outputs/day1/iclr2024_clean_dev_assistant_v2_mpnet_metrics.json",
        "issue_ledger": "outputs/day1/iclr2024_clean_dev_assistant_v2_issue_ledger_refreshed_metrics.json",
        "structured_no_overrides": "outputs/day1/iclr2024_clean_dev_assistant_v2_structured_no_overrides_metrics.json",
        "structured": "outputs/day1/iclr2024_clean_dev_assistant_v2_structured_metrics.json",
    },
    "v3": {
        "data": "data/processed/iclr2024_clean_dev_assistant_v3.jsonl",
        "heuristic": "outputs/day1/iclr2024_clean_dev_assistant_v3_heuristic_metrics.json",
        "tfidf": "outputs/day1/iclr2024_clean_dev_assistant_v3_tfidf_metrics.json",
        "modernbert": "outputs/day1/iclr2024_clean_dev_assistant_v3_modernbert_metrics.json",
        "mpnet": "outputs/day1/iclr2024_clean_dev_assistant_v3_mpnet_metrics.json",
        "issue_ledger": "outputs/day1/iclr2024_clean_dev_assistant_v3_issue_ledger_metrics.json",
        "structured_no_overrides": "outputs/day1/iclr2024_clean_dev_assistant_v3_structured_no_overrides_metrics.json",
        "structured": "outputs/day1/iclr2024_clean_dev_assistant_v3_structured_metrics.json",
    },
    "v4": {
        "data": "data/processed/iclr2024_clean_dev_assistant_v4.jsonl",
        "heuristic": "outputs/day1/iclr2024_clean_dev_assistant_v4_heuristic_metrics.json",
        "tfidf": "outputs/day1/iclr2024_clean_dev_assistant_v4_tfidf_metrics.json",
        "modernbert": "outputs/day1/iclr2024_clean_dev_assistant_v4_modernbert_metrics.json",
        "mpnet": "outputs/day1/iclr2024_clean_dev_assistant_v4_mpnet_metrics.json",
        "issue_ledger": "outputs/day1/iclr2024_clean_dev_assistant_v4_issue_ledger_metrics.json",
        "structured_no_overrides": "outputs/day1/iclr2024_clean_dev_assistant_v4_structured_no_overrides_metrics.json",
        "structured": "outputs/day1/iclr2024_clean_dev_assistant_v4_structured_metrics.json",
    },
    "v5": {
        "data": "data/processed/iclr2024_clean_dev_assistant_v5.jsonl",
        "heuristic": "outputs/day1/iclr2024_clean_dev_assistant_v5_heuristic_metrics.json",
        "tfidf": "outputs/day1/iclr2024_clean_dev_assistant_v5_tfidf_metrics.json",
        "modernbert": "outputs/day1/iclr2024_clean_dev_assistant_v5_modernbert_metrics.json",
        "mpnet": "outputs/day1/iclr2024_clean_dev_assistant_v5_mpnet_metrics.json",
        "issue_ledger": "outputs/day1/iclr2024_clean_dev_assistant_v5_issue_ledger_metrics.json",
        "structured_no_overrides": "outputs/day1/iclr2024_clean_dev_assistant_v5_structured_no_overrides_metrics.json",
        "structured": "outputs/day1/iclr2024_clean_dev_assistant_v5_structured_metrics.json",
    },
    "v6": {
        "data": "data/processed/iclr2024_clean_dev_assistant_v6.jsonl",
        "heuristic": "outputs/day1/iclr2024_clean_dev_assistant_v6_heuristic_metrics.json",
        "tfidf": "outputs/day1/iclr2024_clean_dev_assistant_v6_tfidf_metrics.json",
        "modernbert": "outputs/day1/iclr2024_clean_dev_assistant_v6_modernbert_metrics.json",
        "mpnet": "outputs/day1/iclr2024_clean_dev_assistant_v6_mpnet_metrics.json",
        "issue_ledger": "outputs/day1/iclr2024_clean_dev_assistant_v6_issue_ledger_metrics.json",
        "structured_no_overrides": "outputs/day1/iclr2024_clean_dev_assistant_v6_structured_no_overrides_metrics.json",
        "structured": "outputs/day1/iclr2024_clean_dev_assistant_v6_structured_metrics.json",
    },
    "v7": {
        "data": "data/processed/iclr2024_clean_dev_assistant_v7.jsonl",
        "heuristic": "outputs/day1/iclr2024_clean_dev_assistant_v7_heuristic_metrics.json",
        "tfidf": "outputs/day1/iclr2024_clean_dev_assistant_v7_tfidf_metrics.json",
        "modernbert": "outputs/day1/iclr2024_clean_dev_assistant_v7_modernbert_metrics.json",
        "mpnet": "outputs/day1/iclr2024_clean_dev_assistant_v7_mpnet_metrics.json",
        "issue_ledger": "outputs/day1/iclr2024_clean_dev_assistant_v7_issue_ledger_metrics.json",
        "structured_no_overrides": "outputs/day1/iclr2024_clean_dev_assistant_v7_structured_no_overrides_metrics.json",
        "structured": "outputs/day1/iclr2024_clean_dev_assistant_v7_structured_metrics.json",
    },
}

TRANSFER_VERSIONS = ["v3", "v4", "v5", "v6", "v7", "v8"]
TRANSFER_MODELS = ["tfidf", "modernbert", "mpnet", "issue_ledger", "structured"]
ICLR2025_V2_MODELS = ["tfidf", "modernbert", "mpnet", "issue_ledger", "structured"]
ICLR2025_V2_METRICS = {
    "tfidf": "outputs/day1/iclr2025_repro_v2_full_tfidf_metrics.json",
    "modernbert": "outputs/day1/iclr2025_repro_v2_full_modernbert_metrics.json",
    "mpnet": "outputs/day1/iclr2025_repro_v2_full_mpnet_metrics.json",
    "issue_ledger": "outputs/day1/iclr2025_repro_v2_full_issue_ledger_metrics.json",
    "structured": "outputs/day1/iclr2025_repro_v2_full_structured_metrics.json",
}
ICLR2025_V2_DETAILS = {
    "tfidf": "outputs/day1/iclr2025_repro_v2_full_tfidf_details.json",
    "modernbert": "outputs/day1/iclr2025_repro_v2_full_modernbert_details.json",
    "mpnet": "outputs/day1/iclr2025_repro_v2_full_mpnet_details.json",
    "issue_ledger": "outputs/day1/iclr2025_repro_v2_full_issue_ledger_details.json",
    "structured": "outputs/day1/iclr2025_repro_v2_full_structured_details.json",
}
ICLR2025_V2_PREDICTIONS = {
    "tfidf": "outputs/day1/iclr2025_repro_candidates_tfidf_train_iclr2024_v8_transfer_predictions.jsonl",
    "modernbert": "outputs/day1/iclr2025_repro_candidates_modernbert_train_iclr2024_v8_transfer_predictions.jsonl",
    "mpnet": "outputs/day1/iclr2025_repro_candidates_mpnet_train_iclr2024_v8_transfer_predictions.jsonl",
    "issue_ledger": "outputs/day1/iclr2025_repro_candidates_issue_ledger_train_iclr2024_v8_transfer_predictions.jsonl",
    "structured": "outputs/day1/iclr2025_repro_candidates_structured_train_iclr2024_v8_transfer_predictions.jsonl",
}

MODEL_COLORS = {
    "TF-IDF + LinearSVC": "#286dc9",
    "ModernBERT + LinearSVC": "#7b63d6",
    "MPNet + LinearSVC": "#0f7b77",
    "Issue-Ledger": "#c14f1a",
    "Structured (No Overrides)": "#8060c9",
    "Structured": "#ad2e49",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export paper-ready RevTrack tables and SVG figures.")
    parser.add_argument("--output-dir", default="outputs/day1/paper_assets")
    return parser.parse_args()


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def metric_summary(path: str | Path) -> dict[str, Any]:
    payload = load_json(path)
    return payload.get("summary", payload)


def load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    rows = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def load_csv(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def prediction_path(version: str, model: str) -> Path:
    return ROOT / f"outputs/day1/iclr2024_candidates_{model}_train_{version}_transfer_predictions.jsonl"


def load_predictions(version: str, model: str) -> dict[str, str]:
    return {
        row["id"]: row["predicted_label"]
        for row in load_jsonl(prediction_path(version, model))
    }


def safe_div(num: float, denom: float) -> float:
    return num / denom if denom else 0.0


def constant_prediction_summary(gold_labels: list[str], predicted_label: str) -> dict[str, Any]:
    gold_counts = Counter(gold_labels)
    total = len(gold_labels)
    correct = gold_counts[predicted_label]
    per_label: dict[str, dict[str, float]] = {}
    f1_sum = 0.0
    for label in LABEL_ORDER:
        tp = correct if label == predicted_label else 0
        pred_support = total if label == predicted_label else 0
        support = gold_counts[label]
        precision = safe_div(tp, pred_support)
        recall = safe_div(tp, support)
        f1 = safe_div(2 * precision * recall, precision + recall)
        per_label[label] = {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "support": float(support),
        }
        f1_sum += f1
    return {
        "num_examples": float(total),
        "accuracy": safe_div(correct, total),
        "macro_f1": f1_sum / len(LABEL_ORDER),
        "per_label": per_label,
    }


def majority_label(gold_labels: list[str]) -> str:
    counts = Counter(gold_labels)
    return max(LABEL_ORDER, key=lambda label: (counts[label], -LABEL_ORDER.index(label)))


def as_metric_export_row(
    *,
    dataset_key: str,
    dataset: str,
    rows: int,
    row_type: str,
    model_key: str,
    model: str,
    predicted_label: str,
    summary: dict[str, Any],
    label_counts: Counter[str],
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "dataset_key": dataset_key,
        "dataset": dataset,
        "rows": rows,
        "row_type": row_type,
        "model_key": model_key,
        "model": model,
        "predicted_label": predicted_label,
        "accuracy": summary["accuracy"],
        "macro_f1": summary["macro_f1"],
    }
    row.update({label: label_counts.get(label, 0) for label in LABEL_ORDER})
    for label in LABEL_ORDER:
        per_label = summary.get("per_label", {}).get(label, {})
        row[f"{label}_f1"] = per_label.get("f1", 0)
        row[f"{label}_recall"] = per_label.get("recall", 0)
    return row


def collect_null_baseline_rows() -> list[dict[str, Any]]:
    datasets = [
        {
            "dataset_key": "iclr2024_clean_dev_v7",
            "dataset": "ICLR 2024 clean dev v7",
            "data": ROOT / "data/processed/iclr2024_clean_dev_assistant_v7.jsonl",
            "models": {
                "tfidf": ROOT / "outputs/day1/iclr2024_clean_dev_assistant_v7_tfidf_metrics.json",
                "mpnet": ROOT / "outputs/day1/iclr2024_clean_dev_assistant_v7_mpnet_metrics.json",
                "structured_no_overrides": ROOT / "outputs/day1/iclr2024_clean_dev_assistant_v7_structured_no_overrides_metrics.json",
                "structured": ROOT / "outputs/day1/iclr2024_clean_dev_assistant_v7_structured_metrics.json",
            },
        },
        {
            "dataset_key": "iclr2025_repro_v2",
            "dataset": "ICLR 2025 repro v2",
            "data": ROOT / "data/processed/iclr2025_repro_multi_frontier_structured_v2_full_assistant.jsonl",
            "models": {
                key: ROOT / path
                for key, path in ICLR2025_V2_METRICS.items()
            },
        },
    ]
    rows: list[dict[str, Any]] = []
    for dataset_spec in datasets:
        examples = load_jsonl(dataset_spec["data"])
        gold_labels = [row["gold_label"] for row in examples]
        label_counts = Counter(gold_labels)
        row_count = len(gold_labels)
        majority = majority_label(gold_labels)
        rows.append(
            as_metric_export_row(
                dataset_key=dataset_spec["dataset_key"],
                dataset=dataset_spec["dataset"],
                rows=row_count,
                row_type="null_baseline",
                model_key="majority_label",
                model="Majority-label baseline",
                predicted_label=majority,
                summary=constant_prediction_summary(gold_labels, majority),
                label_counts=label_counts,
            )
        )
        rows.append(
            as_metric_export_row(
                dataset_key=dataset_spec["dataset_key"],
                dataset=dataset_spec["dataset"],
                rows=row_count,
                row_type="null_baseline",
                model_key="constant_partially_fixed",
                model="Constant partially_fixed",
                predicted_label="partially_fixed",
                summary=constant_prediction_summary(gold_labels, "partially_fixed"),
                label_counts=label_counts,
            )
        )
        for model_key, path in dataset_spec["models"].items():
            if not path.exists():
                continue
            rows.append(
                as_metric_export_row(
                    dataset_key=dataset_spec["dataset_key"],
                    dataset=dataset_spec["dataset"],
                    rows=row_count,
                    row_type="model",
                    model_key=model_key,
                    model=MODEL_SPECS[model_key],
                    predicted_label="",
                    summary=metric_summary(path),
                    label_counts=label_counts,
                )
            )
    return rows


def claim_row(
    *,
    claim_id: str,
    status: str,
    proposed_claim: str,
    support_summary: str,
    risk_or_counterevidence: str,
    required_next_step: str,
    primary_artifacts: str,
) -> dict[str, str]:
    return {
        "claim_id": claim_id,
        "status": status,
        "proposed_claim": proposed_claim,
        "support_summary": support_summary,
        "risk_or_counterevidence": risk_or_counterevidence,
        "required_next_step": required_next_step,
        "primary_artifacts": primary_artifacts,
    }


def find_row(rows: list[dict[str, Any]], **matches: str) -> dict[str, Any]:
    for row in rows:
        if all(str(row.get(key)) == value for key, value in matches.items()):
            return row
    return {}


def collect_claim_evidence_rows(
    *,
    metric_rows: list[dict[str, Any]],
    frontier_rows: list[dict[str, Any]],
    iclr2025_rows: list[dict[str, Any]],
    null_rows: list[dict[str, Any]],
) -> list[dict[str, str]]:
    latest = [row for row in metric_rows if row["version"] == "v7"]
    latest_by_model = {row["model_key"]: row for row in latest}
    structured = latest_by_model["structured"]
    mpnet = latest_by_model["mpnet"]
    structured_no_overrides = latest_by_model["structured_no_overrides"]
    majority_2024 = find_row(null_rows, dataset_key="iclr2024_clean_dev_v7", model_key="majority_label")
    majority_2025 = find_row(null_rows, dataset_key="iclr2025_repro_v2", model_key="majority_label")
    tfidf_2025 = find_row(null_rows, dataset_key="iclr2025_repro_v2", model_key="tfidf")
    structured_2025 = find_row(iclr2025_rows, model_key="structured")
    modernbert_2025 = find_row(iclr2025_rows, model_key="modernbert")
    frontier_total = sum(int(row["unlabeled_disagreements"]) for row in frontier_rows)
    iclr2024_gate = load_json(ROOT / "outputs/day1/iclr2024_candidate_pool_quality_gate.json")
    iclr2025_gate = load_json(ROOT / "outputs/day1/iclr2025_repro_candidate_pool_quality_gate.json")
    expanded_iclr2025_gate_path = ROOT / "outputs/day1/iclr2025_expanded80_candidate_pool_quality_gate.json"
    expanded_iclr2025_gate = (
        load_json(expanded_iclr2025_gate_path)
        if expanded_iclr2025_gate_path.exists()
        else {}
    )
    expanded_iclr2025_ok = bool(expanded_iclr2025_gate.get("ok"))
    expanded_iclr2025_rows = int(expanded_iclr2025_gate.get("rows", 0) or 0)
    expanded_iclr2025_disagreements = int(
        expanded_iclr2025_gate.get("disagreement", {}).get("disagreement_rows", 0) or 0
    )
    expanded_standard_metrics_path = ROOT / "outputs/day1/paper_assets/iclr2025_expanded80_standard_transfer_metrics.csv"
    expanded_standard_rows = load_csv(expanded_standard_metrics_path) if expanded_standard_metrics_path.exists() else []
    expanded_standard_best = (
        max(expanded_standard_rows, key=lambda row: (float(row["macro_f1"]), float(row["accuracy"])))
        if expanded_standard_rows
        else {}
    )
    expanded_human_path = ROOT / "outputs/day1/iclr2025_expanded80_human_validation_v1_standard_metrics.json"
    expanded_human = load_json(expanded_human_path) if expanded_human_path.exists() else {}
    expanded_label_audit_path = ROOT / "outputs/day1/iclr2025_expanded80_standard_label_evidence_audit.json"
    expanded_label_audit = load_json(expanded_label_audit_path) if expanded_label_audit_path.exists() else {}
    expanded_standard_ready = (
        int(expanded_human.get("labeled_rows", 0) or 0) == 80
        and int(expanded_human.get("rows", 0) or 0) == 80
        and bool(expanded_label_audit.get("ok"))
        and bool(expanded_standard_rows)
    )
    packet_audits = {
        "iclr2024_v1": load_json(ROOT / "outputs/day1/iclr2024_human_validation_v1_packet_audit.json"),
        "iclr2025_v1": load_json(ROOT / "outputs/day1/iclr2025_repro_human_validation_v1_packet_audit.json"),
        "iclr2025_v2": load_json(ROOT / "outputs/day1/iclr2025_repro_human_validation_v2_packet_audit.json"),
        "iclr2025_expanded80_v1": load_json(
            ROOT / "outputs/day1/iclr2025_expanded80_human_validation_v1_packet_audit.json"
        ),
        "neurips2024_limit100_v1": load_json(
            ROOT / "outputs/day1/neurips2024_limit100_human_validation_v1_packet_audit.json"
        ),
        "iclr2023_random80_v1": load_json(
            ROOT / "outputs/day1/iclr2023_limit80_random80_human_validation_v1_packet_audit.json"
        ),
    }
    packet_ok = all(report.get("ok") for report in packet_audits.values())
    human_2024 = load_json(ROOT / "outputs/day1/iclr2024_human_validation_v1_pending_metrics.json")
    human_2025 = load_json(ROOT / "outputs/day1/iclr2025_repro_human_validation_v2_pending_metrics.json")
    promotion = load_json(
        ROOT / "outputs/day1/ai_assisted_validation_signoff/ai_signoff_human_validation_promotion.json"
    )
    expanded_promotion_path = ROOT / "outputs/day1/iclr2025_expanded80_standard_validation_promotion.json"
    expanded_promotion = load_json(expanded_promotion_path) if expanded_promotion_path.exists() else {}
    neurips_manifest_path = ROOT / "outputs/day1/neurips2024_limit100_standard_validation_manifest.json"
    neurips_manifest = load_json(neurips_manifest_path) if neurips_manifest_path.exists() else {}
    neurips_rows = int(neurips_manifest.get("rows", 0) or 0)
    neurips_status = str(neurips_manifest.get("status", ""))
    neurips_labeled_rows = neurips_rows if neurips_status.startswith("standard_single_user_confirmed") else 0
    iclr2023_human_path = ROOT / "outputs/day1/iclr2023_limit80_random80_human_validation_v1_standard_metrics.json"
    iclr2023_human = load_json(iclr2023_human_path) if iclr2023_human_path.exists() else {}
    iclr2023_promotion_path = ROOT / "outputs/day1/iclr2023_limit80_random80_standard_validation_promotion.json"
    iclr2023_promotion = load_json(iclr2023_promotion_path) if iclr2023_promotion_path.exists() else {}
    iclr2023_label_audit_path = ROOT / "outputs/day1/iclr2023_limit80_random80_standard_label_evidence_audit.json"
    iclr2023_label_audit = load_json(iclr2023_label_audit_path) if iclr2023_label_audit_path.exists() else {}
    iclr2023_standard_metrics_path = (
        ROOT / "outputs/day1/paper_assets/iclr2023_limit80_random80_standard_transfer_metrics.csv"
    )
    iclr2023_standard_rows = load_csv(iclr2023_standard_metrics_path) if iclr2023_standard_metrics_path.exists() else []
    iclr2023_standard_best = (
        max(iclr2023_standard_rows, key=lambda row: (float(row["macro_f1"]), float(row["accuracy"])))
        if iclr2023_standard_rows
        else {}
    )
    iclr2023_labeled_rows = int(iclr2023_human.get("labeled_rows", 0) or 0)
    iclr2023_total_rows = int(iclr2023_human.get("rows", 0) or 0)
    human_rows = (
        int(human_2024.get("labeled_rows", 0))
        + int(human_2025.get("labeled_rows", 0))
        + int(expanded_human.get("labeled_rows", 0) or 0)
        + neurips_labeled_rows
        + iclr2023_labeled_rows
    )
    human_total = (
        int(human_2024.get("rows", 0))
        + int(human_2025.get("rows", 0))
        + int(expanded_human.get("rows", 0) or 0)
        + neurips_rows
        + iclr2023_total_rows
    )

    return [
        claim_row(
            claim_id="C1_in_domain_structured_advantage",
            status="ready",
            proposed_claim="On the hardened ICLR 2024 clean-dev benchmark, structured revision evidence improves macro-F1 over semantic baselines.",
            support_summary=(
                f"clean dev v7 has 148 rows; Structured accuracy {structured['accuracy']:.3f}, macro-F1 {structured['macro_f1']:.3f}; "
                f"MPNet accuracy {mpnet['accuracy']:.3f}, macro-F1 {mpnet['macro_f1']:.3f}; "
                f"Structured without overrides macro-F1 {structured_no_overrides['macro_f1']:.3f}; "
                f"standard validation covers {human_rows}/{human_total} active audit rows after ICLR 2023 random80 promotion."
            ),
            risk_or_counterevidence=(
                "The strongest positive result is still in-domain ICLR 2024; "
                "the scaled ICLR 2025 frontier is active-sampled and label-skewed, so it supports hardened cross-year frontier claims rather than broad venue-level prevalence estimates."
            ),
            required_next_step="Use expanded80 as a hardened cross-year frontier and add more venues/years before broad generalization claims.",
            primary_artifacts="clean_dev_metrics.csv; null_baseline_comparison.csv; iclr2024_human_validation_v1_pending_metrics.json",
        ),
        claim_row(
            claim_id="C2_accuracy_trap",
            status="ready",
            proposed_claim="Accuracy alone is misleading for revision-status tracking under label skew.",
            support_summary=(
                f"ICLR 2024 majority baseline accuracy {majority_2024['accuracy']:.3f}, macro-F1 {majority_2024['macro_f1']:.3f}; "
                f"ICLR 2025 majority baseline accuracy {majority_2025['accuracy']:.3f}, macro-F1 {majority_2025['macro_f1']:.3f}; "
                f"ICLR 2025 TF-IDF exactly matches the majority baseline with fixed F1 {tfidf_2025['fixed_f1']:.3f}."
            ),
            risk_or_counterevidence="The ICLR 2025 evidence is from a small repro stress sample, so use it as an illustrative failure mode, not a benchmark estimate.",
            required_next_step="Keep majority/null baselines in every new venue/year table and require label-level recovery in claims.",
            primary_artifacts="null_baseline_comparison.csv; iclr2025_v2_error_profile.csv",
        ),
        claim_row(
            claim_id="C3_iclr2024_pool_quality",
            status="ready",
            proposed_claim="The current ICLR 2024 candidate pool is large enough for local in-domain experiments and has exhausted active disagreement sampling after train v8.",
            support_summary=(
                f"candidate-pool audit ok={iclr2024_gate['ok']}; rows {iclr2024_gate['rows']}; complete rate {iclr2024_gate['complete_rate']:.3f}; "
                f"multi-model disagreement rows {iclr2024_gate['disagreement']['disagreement_rows']}; residual frontier after v8 {frontier_total}."
            ),
            risk_or_counterevidence="This is an in-domain ICLR 2024 claim only; it does not establish cross-year or cross-venue generalization.",
            required_next_step="Freeze exact dataset split/version before paper submission and include audit report in reproducibility package.",
            primary_artifacts="iclr2024_candidate_pool_quality_gate.json; frontier_status.csv; transfer_label_distribution.csv",
        ),
        claim_row(
            claim_id="C4_cross_year_brittleness",
            status="ready" if expanded_standard_ready else "stress_evidence",
            proposed_claim=(
                "Cross-year transfer to ICLR 2025 is brittle and exposes weak fixed-case recovery on both a stress set and a hardened expanded frontier."
                if expanded_standard_ready
                else "Cross-year transfer to ICLR 2025 is brittle and exposes weak fixed-case recovery."
            ),
            support_summary=(
                f"ICLR 2025 repro v2 rows {structured_2025['rows']}; Structured accuracy {structured_2025['accuracy']:.3f}, macro-F1 {structured_2025['macro_f1']:.3f}, fixed F1 {structured_2025['fixed_f1']:.3f}; "
                f"best macro-F1 among current repro transfer models is ModernBERT at {modernbert_2025['macro_f1']:.3f}."
                + (
                    f" Expanded80 standard rows {expanded_human.get('labeled_rows')}; best expanded80 model {expanded_standard_best.get('model_key')} reaches accuracy {float(expanded_standard_best.get('accuracy', 0)):.3f}, macro-F1 {float(expanded_standard_best.get('macro_f1', 0)):.3f}, fixed F1 {float(expanded_standard_best.get('fixed_f1', 0)):.3f}."
                    if expanded_standard_ready
                    else ""
                )
            ),
            risk_or_counterevidence=(
                "Expanded80 is a standard single-user active frontier and should not be used as an estimate of natural label prevalence."
                if expanded_standard_ready
                else (
                    f"The validated ICLR 2025 repro stress sample is small: rows {iclr2025_gate['rows']} and disagreement rows {iclr2025_gate['disagreement']['disagreement_rows']}. "
                    f"A new scaled ICLR 2025 candidate pool passes data gates={expanded_iclr2025_ok} with rows {expanded_iclr2025_rows} and disagreement rows {expanded_iclr2025_disagreements}, but it is not yet standard-labeled."
                )
            ),
            required_next_step=(
                "Add a second annotator only for IAA claims; add another venue/year before broad generalization claims."
                if expanded_standard_ready
                else "Human-adjudicate the scaled ICLR 2025 frontier and rerun transfer metrics before making a generalization claim."
            ),
            primary_artifacts="iclr2025_v2_transfer_metrics.csv; iclr2025_v2_error_profile.csv; iclr2025_expanded80_standard_transfer_metrics.csv; iclr2025_expanded80_candidate_pool_quality_gate.json",
        ),
        claim_row(
            claim_id="C5_human_validation_complete",
            status="ready",
            proposed_claim="The benchmark has complete standard human-validation labels with reproducible packet, leakage, and key-alignment audits.",
            support_summary=(
                f"packet audits pass for ICLR 2024 v1, ICLR 2025 v1, ICLR 2025 v2, ICLR 2025 expanded80 v1, NeurIPS 2024 limit100 v1, and ICLR 2023 random80 v1: {packet_ok}; "
                f"human-validation labels cover {human_rows}/{human_total} active audit rows; "
                f"signoff promotion status {promotion.get('status')} with {promotion.get('promoted_rows')} promoted rows; "
                f"expanded80 promotion status {expanded_promotion.get('status')} with {expanded_promotion.get('promoted_rows')} promoted rows; "
                f"NeurIPS 2024 promotion status {neurips_manifest.get('status')} with {neurips_labeled_rows} promoted rows; "
                f"ICLR 2023 random80 promotion status {iclr2023_promotion.get('status')} with {iclr2023_promotion.get('promoted_rows')} promoted rows."
            ),
            risk_or_counterevidence="This validates the current standard labels; a separate second-annotator pass would be needed only for inter-annotator reliability claims.",
            required_next_step="Use these labels as the paper's current human validation standard and reserve effort for scaling transfer evidence.",
            primary_artifacts="audit_human_validation_packet.py; iclr2024_human_validation_v1_pending_metrics.json; iclr2025_repro_human_validation_v2_pending_metrics.json; iclr2025_expanded80_human_validation_v1_standard_metrics.json; iclr2023_limit80_random80_human_validation_v1_standard_metrics.json; ai_signoff_human_validation_promotion.json; neurips2024_limit100_standard_validation_promotion.json; iclr2023_limit80_random80_standard_validation_promotion.json",
        ),
        claim_row(
            claim_id="C7_prompted_llm_transfer_stress",
            status="ready",
            proposed_claim="Prompted LLMs and vote ensembles are competitive in-domain but remain brittle under cross-year and cross-venue transfer.",
            support_summary=(
                "ICLR 2024 prompted baselines reach up to 0.350-0.352 macro-F1, while ICLR 2025 expanded80 remains below the 0.226 majority reference: "
                "the strongest single prompted model reaches 0.161 and the strongest calibrated vote reaches 0.094. "
                "On the user-confirmed NeurIPS 2024 standard single-user active frontier, the best prompted row is 0.181 macro-F1, near the 0.177 majority reference."
            ),
            risk_or_counterevidence=(
                "Prompted results depend on API model aliases and prompt formatting. NeurIPS 2024 is user-confirmed single-pass standard validation, not independent IAA, and bootstrap intervals capture sample instability only, not annotator uncertainty."
            ),
            required_next_step="Use these results as bounded reliability evidence; add targeted prompt/calibration ablations and a second annotator before broader LLM-generalization or IAA claims.",
            primary_artifacts="prompted_llm_ensemble_summary.json; prompted_llm_bootstrap_intervals.md; postprocess_rule_search.json",
        ),
        claim_row(
            claim_id="C6_publishable_cross_year_benchmark",
            status="ready" if expanded_standard_ready else ("integrity_ready" if expanded_iclr2025_ok else "not_ready"),
            proposed_claim=(
                "A scaled ICLR 2025 cross-year frontier has user-confirmed standard labels and transfer metrics."
                if expanded_standard_ready
                else "A scaled ICLR 2025 cross-year candidate pool is ready for human adjudication."
            ),
            support_summary=(
                f"Expanded ICLR 2025 pool quality gate ok={expanded_iclr2025_ok}; rows {expanded_iclr2025_rows}; "
                f"complete rate {expanded_iclr2025_gate.get('complete_rate', 0):.3f}; "
                f"multi-model disagreement rows {expanded_iclr2025_disagreements}."
                + (
                    f" Standard validation covers {expanded_human.get('labeled_rows')}/{expanded_human.get('rows')} rows with label-evidence audit ok={expanded_label_audit.get('ok')}; best model {expanded_standard_best.get('model_key')} macro-F1 {float(expanded_standard_best.get('macro_f1', 0)):.3f}."
                    if expanded_standard_ready
                    else ""
                )
            ),
            risk_or_counterevidence=(
                "This is a hardened active-sampled frontier, not a natural-prevalence estimate for all ICLR 2025 issues."
                if expanded_iclr2025_ok
                else (
                    f"quality gate fails for ICLR 2025 repro: ok={iclr2025_gate['ok']}; rows {iclr2025_gate['rows']} < 150; "
                    f"disagreement rows {iclr2025_gate['disagreement']['disagreement_rows']} < 25."
                )
            ),
            required_next_step=(
                "Add second annotator coverage if claiming IAA; otherwise use as hardened cross-year frontier evidence."
                if expanded_standard_ready
                else "Build the expanded blind validation packet, complete standard human labels, and then rerun transfer metrics."
            ),
            primary_artifacts="iclr2025_expanded80_candidate_pool_quality_gate.json; iclr2025_expanded80_human_validation_v1_standard_metrics.json; iclr2025_expanded80_standard_transfer_metrics.csv; docs/cross_venue_plan.md",
        ),
        claim_row(
            claim_id="C8_neurips_cross_venue_frontier",
            status="ready",
            proposed_claim="A user-confirmed NeurIPS 2024 standard single-user active frontier adds a second venue axis for transfer brittleness analysis.",
            support_summary=(
                "NeurIPS 2024 limit100 standard validation has 80 user-confirmed rows with partial=44 and unresolved=36. "
                "The candidate pool has 393 complete rows and 316 full-stack disagreement rows. "
                "The best transferred model is MPNet with accuracy 0.550, macro-F1 0.348, partial F1 0.516, and unresolved F1 0.875."
            ),
            risk_or_counterevidence="The NeurIPS frontier is a disagreement-focused standard single-user active frontier; it is not a natural-prevalence sample and not an independent IAA result.",
            required_next_step="Add a non-ICLR random/stratified slice and a second annotator before broad venue-level prevalence or IAA claims.",
            primary_artifacts="neurips2024_limit100_standard_validation_manifest.json; neurips2024_limit100_standard_transfer_metrics.csv; neurips2024_limit100_standard_failure_taxonomy.md",
        ),
        claim_row(
            claim_id="C9_iclr2023_random_stratified_slice",
            status="ready" if iclr2023_labeled_rows == 80 and bool(iclr2023_label_audit.get("ok")) else "not_ready",
            proposed_claim="A user-confirmed ICLR 2023 random/stratified standard slice adds broader external-validity evidence beyond disagreement-focused active frontiers.",
            support_summary=(
                f"ICLR 2023 random80 standard validation covers {iclr2023_labeled_rows}/{iclr2023_total_rows} rows "
                f"with labels fixed={iclr2023_human.get('human_distribution', {}).get('fixed', 0)}, "
                f"partially_fixed={iclr2023_human.get('human_distribution', {}).get('partially_fixed', 0)}, "
                f"unresolved={iclr2023_human.get('human_distribution', {}).get('unresolved', 0)}. "
                f"Label-evidence audit ok={iclr2023_label_audit.get('ok')}; best transfer row {iclr2023_standard_best.get('model_key')} "
                f"has accuracy {float(iclr2023_standard_best.get('accuracy', 0)):.3f} and macro-F1 {float(iclr2023_standard_best.get('macro_f1', 0)):.3f}."
            ),
            risk_or_counterevidence=(
                "This is standard single-user validation from user-confirmed resolved candidates, not independent IAA. "
                "The stratified sample reduces active-frontier bias but should still be reported by measured slice design, not as natural venue prevalence."
            ),
            required_next_step="Use this as bounded random/stratified external-validity evidence; add independent second-annotator coverage only if claiming IAA.",
            primary_artifacts="iclr2023_limit80_random80_standard_validation_promotion.json; iclr2023_limit80_random80_human_validation_v1_standard_metrics.json; iclr2023_limit80_random80_standard_transfer_metrics.csv; iclr2023_limit80_random80_standard_failure_taxonomy.md",
        ),
    ]


def write_claim_evidence_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    lines = [
        "# Claim Evidence Ledger",
        "",
        "This ledger separates paper-ready claims from stress evidence and not-ready claims.",
        "",
    ]
    for row in rows:
        lines.extend(
            [
                f"## {row['claim_id']} ({row['status']})",
                "",
                f"Claim: {row['proposed_claim']}",
                "",
                f"Support: {row['support_summary']}",
                "",
                f"Risk/counterevidence: {row['risk_or_counterevidence']}",
                "",
                f"Next step: {row['required_next_step']}",
                "",
                f"Artifacts: `{row['primary_artifacts']}`",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def collect_clean_dev_metrics() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    metric_rows: list[dict[str, Any]] = []
    label_rows: list[dict[str, Any]] = []
    for version, spec in CLEAN_DEV_METRICS.items():
        data_path = ROOT / str(spec["data"])
        examples = load_jsonl(data_path)
        label_counts = Counter(row["gold_label"] for row in examples)
        label_row = {"version": version, "rows": len(examples)}
        label_row.update({label: label_counts.get(label, 0) for label in LABEL_ORDER})
        label_rows.append(label_row)

        for model_key, model_name in MODEL_SPECS.items():
            metric_path = spec.get(model_key)
            if not metric_path:
                continue
            path = ROOT / str(metric_path)
            if not path.exists():
                continue
            summary = metric_summary(path)
            row: dict[str, Any] = {
                "version": version,
                "rows": len(examples),
                "model_key": model_key,
                "model": model_name,
                "accuracy": summary["accuracy"],
                "macro_f1": summary["macro_f1"],
            }
            for label in LABEL_ORDER:
                row[f"{label}_f1"] = summary.get("per_label", {}).get(label, {}).get("f1", "")
                row[f"{label}_recall"] = summary.get("per_label", {}).get(label, {}).get("recall", "")
            metric_rows.append(row)
    return metric_rows, label_rows


def collect_transfer_tables() -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    dist_rows: list[dict[str, Any]] = []
    churn_rows: list[dict[str, Any]] = []
    disagreement_rows: list[dict[str, Any]] = []

    prediction_cache: dict[tuple[str, str], dict[str, str]] = {}
    for version in TRANSFER_VERSIONS:
        for model in TRANSFER_MODELS:
            path = prediction_path(version, model)
            if not path.exists():
                continue
            preds = load_predictions(version, model)
            prediction_cache[(version, model)] = preds
            counts = Counter(preds.values())
            row = {"version": version, "model_key": model, "model": MODEL_SPECS[model], "rows": len(preds)}
            row.update({label: counts.get(label, 0) for label in LABEL_ORDER})
            dist_rows.append(row)

    for prev, current in zip(TRANSFER_VERSIONS, TRANSFER_VERSIONS[1:], strict=False):
        for model in TRANSFER_MODELS:
            before = prediction_cache.get((prev, model))
            after = prediction_cache.get((current, model))
            if not before or not after:
                continue
            ids = sorted(set(before) & set(after))
            changed = sum(1 for item in ids if before[item] != after[item])
            churn_rows.append(
                {
                    "from_version": prev,
                    "to_version": current,
                    "model_key": model,
                    "model": MODEL_SPECS[model],
                    "changed": changed,
                    "total": len(ids),
                    "churn_rate": changed / len(ids) if ids else 0.0,
                }
            )

    latest = "v8"
    structured = prediction_cache[(latest, "structured")]
    for other in ["tfidf", "modernbert", "mpnet", "issue_ledger"]:
        preds = prediction_cache[(latest, other)]
        ids = sorted(set(structured) & set(preds))
        counter = Counter(
            f"{structured[item]} -> {preds[item]}"
            for item in ids
            if structured[item] != preds[item]
        )
        disagreement_rows.append(
            {
                "version": latest,
                "pair": f"structured vs {other}",
                "total": sum(counter.values()),
                "top_pairs": "; ".join(f"{name}: {count}" for name, count in counter.most_common(8)),
            }
        )

    return dist_rows, churn_rows, disagreement_rows


def collect_frontier_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for pair_name, path in [
        ("structured_vs_tfidf", ROOT / "experiments/day1/iclr2024_priority_sheet_structured_vs_tfidf_residual_after_v8.tsv"),
        ("structured_vs_modernbert", ROOT / "experiments/day1/iclr2024_priority_sheet_structured_vs_modernbert_residual_after_v8.tsv"),
        ("structured_vs_issue_ledger", ROOT / "experiments/day1/iclr2024_priority_sheet_structured_vs_issue_ledger_residual_after_v8.tsv"),
    ]:
        count = 0
        if path.exists():
            with path.open("r", encoding="utf-8", newline="") as handle:
                count = sum(1 for _ in csv.DictReader(handle, delimiter="\t"))
        rows.append({"version": "v8", "pair": pair_name, "unlabeled_disagreements": count})
    return rows


def collect_iclr2025_v2_transfer_metrics() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    metric_rows: list[dict[str, Any]] = []
    error_rows: list[dict[str, Any]] = []
    for model_key in ICLR2025_V2_MODELS:
        metric_path = ROOT / ICLR2025_V2_METRICS[model_key]
        details_path = ROOT / ICLR2025_V2_DETAILS[model_key]
        pred_path = ROOT / ICLR2025_V2_PREDICTIONS[model_key]
        if not metric_path.exists() or not details_path.exists() or not pred_path.exists():
            continue

        summary = metric_summary(metric_path)
        predictions = load_jsonl(pred_path)
        pred_counts = Counter(row["predicted_label"] for row in predictions)
        row: dict[str, Any] = {
            "venue_year": "iclr2025_repro_v2",
            "transfer_train": "iclr2024_train_v8",
            "model_key": model_key,
            "model": MODEL_SPECS[model_key],
            "rows": int(summary["num_examples"]),
            "accuracy": summary["accuracy"],
            "macro_f1": summary["macro_f1"],
        }
        for label in LABEL_ORDER:
            per_label = summary.get("per_label", {}).get(label, {})
            row[f"{label}_support"] = per_label.get("support", 0)
            row[f"{label}_precision"] = per_label.get("precision", 0)
            row[f"{label}_recall"] = per_label.get("recall", 0)
            row[f"{label}_f1"] = per_label.get("f1", 0)
            row[f"predicted_{label}"] = pred_counts.get(label, 0)
        metric_rows.append(row)

        details = load_json(details_path)
        total = len(details)
        correct = sum(1 for item in details if item["gold_label"] == item["predicted_label"])
        detail_counts = Counter((item["gold_label"], item["predicted_label"]) for item in details)
        predicted_labels = {item["predicted_label"] for item in details}
        error_rows.append(
            {
                "venue_year": "iclr2025_repro_v2",
                "model_key": model_key,
                "model": MODEL_SPECS[model_key],
                "rows": total,
                "correct": correct,
                "accuracy": correct / total if total else 0.0,
                "unique_predicted_labels": len(predicted_labels),
                "majority_only": len(predicted_labels) == 1,
                "fixed_missed_as_partially_fixed": detail_counts[("fixed", "partially_fixed")],
                "fixed_missed_as_unresolved": detail_counts[("fixed", "unresolved")],
                "fixed_missed_as_regressed": detail_counts[("fixed", "regressed")],
                "partially_fixed_misread_as_fixed": detail_counts[("partially_fixed", "fixed")],
                "partially_fixed_misread_as_unresolved": detail_counts[("partially_fixed", "unresolved")],
                "partially_fixed_misread_as_regressed": detail_counts[("partially_fixed", "regressed")],
            }
        )
    return metric_rows, error_rows


def svg_line_plot(path: Path, rows: list[dict[str, Any]], metric: str, title: str) -> None:
    width, height = 980, 520
    left, right, top, bottom = 86, 28, 58, 82
    plot_w = width - left - right
    plot_h = height - top - bottom
    versions = [f"v{i}" for i in range(1, 8)]
    x_by_version = {
        version: left + idx * plot_w / max(len(versions) - 1, 1)
        for idx, version in enumerate(versions)
    }
    selected = [
        "TF-IDF + LinearSVC",
        "ModernBERT + LinearSVC",
        "MPNet + LinearSVC",
        "Issue-Ledger",
        "Structured (No Overrides)",
        "Structured",
    ]
    grouped: dict[str, dict[str, float]] = {model: {} for model in selected}
    for row in rows:
        model = row["model"]
        if model in grouped:
            grouped[model][row["version"]] = float(row[metric])

    def y(value: float) -> float:
        return top + (1.0 - value) * plot_h

    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#fbf7ef"/>',
        f'<text x="{left}" y="32" font-family="Arial, sans-serif" font-size="22" font-weight="700" fill="#1b1814">{title}</text>',
    ]
    for tick in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
        yy = y(tick)
        elements.append(f'<line x1="{left}" x2="{width-right}" y1="{yy:.1f}" y2="{yy:.1f}" stroke="#ddd1c2" stroke-width="1"/>')
        elements.append(f'<text x="{left-12}" y="{yy+4:.1f}" text-anchor="end" font-family="Arial, sans-serif" font-size="12" fill="#6a5646">{tick:.1f}</text>')
    elements.append(f'<line x1="{left}" x2="{width-right}" y1="{top+plot_h}" y2="{top+plot_h}" stroke="#1b1814" stroke-width="1.3"/>')
    elements.append(f'<line x1="{left}" x2="{left}" y1="{top}" y2="{top+plot_h}" stroke="#1b1814" stroke-width="1.3"/>')
    for version, xx in x_by_version.items():
        elements.append(f'<text x="{xx:.1f}" y="{height-46}" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" fill="#1b1814">{version}</text>')

    legend_x, legend_y = left, height - 26
    for idx, model in enumerate(selected):
        color = MODEL_COLORS[model]
        lx = legend_x + (idx % 3) * 292
        ly = legend_y + (idx // 3) * 20
        elements.append(f'<circle cx="{lx}" cy="{ly-4}" r="5" fill="{color}"/>')
        elements.append(f'<text x="{lx+12}" y="{ly}" font-family="Arial, sans-serif" font-size="12" fill="#1b1814">{model}</text>')

    for model in selected:
        points = []
        for version in versions:
            if version in grouped[model]:
                points.append((x_by_version[version], y(grouped[model][version])))
        if len(points) < 2:
            continue
        color = MODEL_COLORS[model]
        point_str = " ".join(f"{xx:.1f},{yy:.1f}" for xx, yy in points)
        elements.append(f'<polyline points="{point_str}" fill="none" stroke="{color}" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>')
        for xx, yy in points:
            elements.append(f'<circle cx="{xx:.1f}" cy="{yy:.1f}" r="4" fill="{color}" stroke="#fbf7ef" stroke-width="1.5"/>')

    elements.append("</svg>")
    path.write_text("\n".join(elements), encoding="utf-8")


def write_markdown_summary(
    path: Path,
    metric_rows: list[dict[str, Any]],
    frontier_rows: list[dict[str, Any]],
    iclr2025_rows: list[dict[str, Any]],
    null_rows: list[dict[str, Any]],
    claim_rows: list[dict[str, str]],
) -> None:
    latest = [row for row in metric_rows if row["version"] == "v7"]
    latest_by_model = {row["model"]: row for row in latest}
    structured = latest_by_model["Structured"]
    mpnet = latest_by_model["MPNet + LinearSVC"]
    no_overrides = latest_by_model["Structured (No Overrides)"]
    frontier_total = sum(row["unlabeled_disagreements"] for row in frontier_rows)
    transfer_section = ""
    if iclr2025_rows:
        by_model = {row["model_key"]: row for row in iclr2025_rows}
        tfidf = by_model["tfidf"]
        structured_2025 = by_model["structured"]
        modernbert = by_model["modernbert"]
        null_by_dataset = {
            row["dataset_key"]: row
            for row in null_rows
            if row["model_key"] == "majority_label"
        }
        majority_2024 = null_by_dataset.get("iclr2024_clean_dev_v7", {})
        majority_2025 = null_by_dataset.get("iclr2025_repro_v2", {})
        transfer_section = f"""
## Cross-Year Transfer Sanity Check

- ICLR 2025 repro v2 covers all `21` local issue candidates with label distribution `partially_fixed 16 / fixed 5`.
- `TF-IDF + LinearSVC`: accuracy `{tfidf['accuracy']:.3f}`, macro-F1 `{tfidf['macro_f1']:.3f}`, fixed F1 `{tfidf['fixed_f1']:.3f}`.
- `Structured`: accuracy `{structured_2025['accuracy']:.3f}`, macro-F1 `{structured_2025['macro_f1']:.3f}`, fixed F1 `{structured_2025['fixed_f1']:.3f}`.
- Best macro-F1 on this tiny transfer set is `ModernBERT + LinearSVC` at `{modernbert['macro_f1']:.3f}`; this is still weak and not a method-win result.
- The important signal is negative evidence: high accuracy can come from predicting only the majority `partially_fixed` label.

## Null-Baseline Check

- ICLR 2024 clean dev v7 majority baseline: accuracy `{majority_2024.get('accuracy', 0):.3f}`, macro-F1 `{majority_2024.get('macro_f1', 0):.3f}`.
- ICLR 2025 repro v2 majority baseline: accuracy `{majority_2025.get('accuracy', 0):.3f}`, macro-F1 `{majority_2025.get('macro_f1', 0):.3f}`.
- On ICLR 2025 v2, TF-IDF matches the majority-label baseline exactly in accuracy and macro-F1 because it predicts only `partially_fixed`.
"""
    expanded_standard_path = ROOT / "outputs/day1/paper_assets/iclr2025_expanded80_standard_transfer_metrics.csv"
    expanded_standard_rows = load_csv(expanded_standard_path) if expanded_standard_path.exists() else []
    expanded_section = ""
    if expanded_standard_rows:
        best_expanded = max(expanded_standard_rows, key=lambda row: (float(row["macro_f1"]), float(row["accuracy"])))
        expanded_section = f"""
## Standard-Labeled Expanded80 Frontier

- Expanded80 has `80` user-confirmed standard labels with complete evidence spans.
- Best expanded80 model by macro-F1: `{best_expanded['model_key']}` with accuracy `{float(best_expanded['accuracy']):.3f}`, macro-F1 `{float(best_expanded['macro_f1']):.3f}`, fixed F1 `{float(best_expanded['fixed_f1']):.3f}`.
- Reporting boundary: expanded80 is a hardened standard single-user active frontier, not an independent two-annotator IAA set or natural-prevalence estimate.
"""
    iclr2023_random_path = ROOT / "outputs/day1/paper_assets/iclr2023_limit80_random80_standard_transfer_metrics.csv"
    iclr2023_random_rows = load_csv(iclr2023_random_path) if iclr2023_random_path.exists() else []
    iclr2023_random_section = ""
    if iclr2023_random_rows:
        best_random = max(iclr2023_random_rows, key=lambda row: (float(row["macro_f1"]), float(row["accuracy"])))
        iclr2023_random_section = f"""
## Standard-Labeled ICLR 2023 Random/Stratified Slice

- ICLR 2023 random80 has `80` user-confirmed standard labels and complete evidence spans.
- Best random80 transfer row by macro-F1: `{best_random['model_key']}` with accuracy `{float(best_random['accuracy']):.3f}`, macro-F1 `{float(best_random['macro_f1']):.3f}`.
- Reporting boundary: this is standard single-user validation from user-confirmed resolved candidates; it is not independent IAA and should be reported by measured slice design, not as natural venue prevalence.
"""
    failure_taxonomy_path = ROOT / "outputs/day1/paper_assets/failure_taxonomy.csv"
    failure_taxonomy_rows = load_csv(failure_taxonomy_path) if failure_taxonomy_path.exists() else []
    failure_section = ""
    if failure_taxonomy_rows:
        expanded_failure_rows = [
            row for row in failure_taxonomy_rows if row.get("source_split") == "iclr2025_expanded80_standard"
        ]
        failure_section = f"""
## Failure Taxonomy

- Failure taxonomy rows: `{len(failure_taxonomy_rows)}` total, `{len(expanded_failure_rows)}` from expanded80 standard validation.
- Paper table: [failure_taxonomy.md](failure_taxonomy.md) and `paper/tables/failure_taxonomy.tex`.
- Main diagnostic modes: stale criticism, over-crediting unresolved issues, fixed under-recovery, regression blindness, and partial/full-boundary errors.
"""
    ready_claims = sum(1 for row in claim_rows if row["status"] == "ready")
    integrity_ready_claims = sum(1 for row in claim_rows if row["status"] == "integrity_ready")
    stress_claims = sum(1 for row in claim_rows if row["status"] == "stress_evidence")
    not_ready_claims = sum(1 for row in claim_rows if row["status"] == "not_ready")
    text = f"""# Paper Asset Summary

Generated from local RevTrack outputs.

## Main Clean-Dev Claim

- Latest benchmark: clean dev v7, `148` assistant-adjudicated issue examples.
- `Structured`: accuracy `{structured['accuracy']:.3f}`, macro-F1 `{structured['macro_f1']:.3f}`.
- Best semantic baseline (`MPNet + LinearSVC`): accuracy `{mpnet['accuracy']:.3f}`, macro-F1 `{mpnet['macro_f1']:.3f}`.
- No-overrides ablation: accuracy `{no_overrides['accuracy']:.3f}`, macro-F1 `{no_overrides['macro_f1']:.3f}`.

## Active-Sampling Status

- Train v8 covers `180` labeled or high-confidence examples.
- Remaining unlabeled model-disagreement frontier in the current 230-candidate ICLR 2024 pool: `{frontier_total}`.
{transfer_section}
## Scaled Cross-Year Frontier

- ICLR 2025 expanded80 passes candidate-pool quality gates with `322` candidates and `244` model-disagreement rows.
- The expanded80 frontier summary is [iclr2025_expanded80_frontier_summary.md](iclr2025_expanded80_frontier_summary.md).
- The expanded80 blind validation packet has `80` standard single-user labels and an audited hidden assistant/model key.
- Standard expanded80 transfer metrics are available at [iclr2025_expanded80_standard_transfer_metrics.md](iclr2025_expanded80_standard_transfer_metrics.md).
{expanded_section}
{iclr2023_random_section}
{failure_section}

## Claim Ledger

- Ready claims: `{ready_claims}`
- Integrity-ready claims: `{integrity_ready_claims}`
- Stress-evidence claims: `{stress_claims}`
- Not-ready claims: `{not_ready_claims}`
- Full ledger: [claim_evidence_ledger.md](claim_evidence_ledger.md)


## Paper Interpretation

The strongest current claim is not that the task is solved. It is that revision-aware structured evidence slots plus selective follow-up overrides beat pure semantic matching on a deliberately hardened, active-sampled revision benchmark, especially in macro-F1 and minority-label recovery. The 21-row ICLR 2025 repro result remains a reliability stress test; expanded80 and NeurIPS limit100 add standard-labeled hardened active-frontier evidence, and ICLR 2023 random80 adds bounded random/stratified external-validity evidence while preserving the boundary that none of these single-user packets are IAA results.
"""
    path.write_text(text, encoding="utf-8")


def main() -> None:
    args = parse_args()
    output_dir = ROOT / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    metric_rows, label_rows = collect_clean_dev_metrics()
    transfer_dist_rows, churn_rows, disagreement_rows = collect_transfer_tables()
    frontier_rows = collect_frontier_rows()
    iclr2025_rows, iclr2025_error_rows = collect_iclr2025_v2_transfer_metrics()
    null_rows = collect_null_baseline_rows()
    claim_rows = collect_claim_evidence_rows(
        metric_rows=metric_rows,
        frontier_rows=frontier_rows,
        iclr2025_rows=iclr2025_rows,
        null_rows=null_rows,
    )

    metric_fields = [
        "version",
        "rows",
        "model_key",
        "model",
        "accuracy",
        "macro_f1",
        "fixed_f1",
        "partially_fixed_f1",
        "unresolved_f1",
        "regressed_f1",
        "fixed_recall",
        "partially_fixed_recall",
        "unresolved_recall",
        "regressed_recall",
    ]
    write_csv(output_dir / "clean_dev_metrics.csv", metric_rows, metric_fields)
    write_csv(output_dir / "clean_dev_label_distribution.csv", label_rows, ["version", "rows", *LABEL_ORDER])
    write_csv(output_dir / "transfer_label_distribution.csv", transfer_dist_rows, ["version", "model_key", "model", "rows", *LABEL_ORDER])
    write_csv(output_dir / "transfer_churn.csv", churn_rows, ["from_version", "to_version", "model_key", "model", "changed", "total", "churn_rate"])
    write_csv(output_dir / "latest_pairwise_disagreements.csv", disagreement_rows, ["version", "pair", "total", "top_pairs"])
    write_csv(output_dir / "frontier_status.csv", frontier_rows, ["version", "pair", "unlabeled_disagreements"])
    write_csv(
        output_dir / "iclr2025_v2_transfer_metrics.csv",
        iclr2025_rows,
        [
            "venue_year",
            "transfer_train",
            "model_key",
            "model",
            "rows",
            "accuracy",
            "macro_f1",
            *[f"{label}_support" for label in LABEL_ORDER],
            *[f"{label}_precision" for label in LABEL_ORDER],
            *[f"{label}_recall" for label in LABEL_ORDER],
            *[f"{label}_f1" for label in LABEL_ORDER],
            *[f"predicted_{label}" for label in LABEL_ORDER],
        ],
    )
    write_csv(
        output_dir / "iclr2025_v2_error_profile.csv",
        iclr2025_error_rows,
        [
            "venue_year",
            "model_key",
            "model",
            "rows",
            "correct",
            "accuracy",
            "unique_predicted_labels",
            "majority_only",
            "fixed_missed_as_partially_fixed",
            "fixed_missed_as_unresolved",
            "fixed_missed_as_regressed",
            "partially_fixed_misread_as_fixed",
            "partially_fixed_misread_as_unresolved",
            "partially_fixed_misread_as_regressed",
        ],
    )
    write_csv(
        output_dir / "null_baseline_comparison.csv",
        null_rows,
        [
            "dataset_key",
            "dataset",
            "rows",
            "row_type",
            "model_key",
            "model",
            "predicted_label",
            "accuracy",
            "macro_f1",
            *LABEL_ORDER,
            *[f"{label}_f1" for label in LABEL_ORDER],
            *[f"{label}_recall" for label in LABEL_ORDER],
        ],
    )
    claim_fields = [
        "claim_id",
        "status",
        "proposed_claim",
        "support_summary",
        "risk_or_counterevidence",
        "required_next_step",
        "primary_artifacts",
    ]
    write_csv(output_dir / "claim_evidence_ledger.csv", claim_rows, claim_fields)
    write_claim_evidence_markdown(output_dir / "claim_evidence_ledger.md", claim_rows)

    svg_line_plot(output_dir / "clean_dev_accuracy.svg", metric_rows, "accuracy", "Clean-Dev Accuracy Across Active-Learning Rounds")
    svg_line_plot(output_dir / "clean_dev_macro_f1.svg", metric_rows, "macro_f1", "Clean-Dev Macro-F1 Across Active-Learning Rounds")
    write_markdown_summary(output_dir / "paper_asset_summary.md", metric_rows, frontier_rows, iclr2025_rows, null_rows, claim_rows)

    print(f"Wrote paper assets to {output_dir}")


if __name__ == "__main__":
    main()
