from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CANDIDATES = ROOT / "data/processed/iclr2025_expanded80_issue_candidates.jsonl"
DEFAULT_GATE = ROOT / "outputs/day1/iclr2025_expanded80_candidate_pool_quality_gate.json"
DEFAULT_FRONTIER = ROOT / "experiments/day1/iclr2025_expanded80_multi_frontier_structured_prefilled.tsv"
DEFAULT_PACKET_AUDIT = ROOT / "outputs/day1/iclr2025_expanded80_human_validation_v1_packet_audit.json"
DEFAULT_STANDARD_METRICS = ROOT / "outputs/day1/iclr2025_expanded80_human_validation_v1_standard_metrics.json"
DEFAULT_OUTPUT_CSV = ROOT / "outputs/day1/paper_assets/iclr2025_expanded80_frontier_summary.csv"
DEFAULT_OUTPUT_MD = ROOT / "outputs/day1/paper_assets/iclr2025_expanded80_frontier_summary.md"

DEFAULT_PREDICTIONS = {
    "tfidf": ROOT / "outputs/day1/iclr2025_expanded80_candidates_tfidf_train_iclr2024_v8_transfer_predictions.jsonl",
    "modernbert": ROOT
    / "outputs/day1/iclr2025_expanded80_candidates_modernbert_train_iclr2024_v8_transfer_predictions.jsonl",
    "mpnet": ROOT / "outputs/day1/iclr2025_expanded80_candidates_mpnet_train_iclr2024_v8_transfer_predictions.jsonl",
    "issue_ledger": ROOT
    / "outputs/day1/iclr2025_expanded80_candidates_issue_ledger_train_iclr2024_v8_transfer_predictions.jsonl",
    "structured": ROOT
    / "outputs/day1/iclr2025_expanded80_candidates_structured_train_iclr2024_v8_transfer_predictions.jsonl",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export paper-facing summary for the scaled ICLR 2025 frontier.")
    parser.add_argument("--candidates", default=str(DEFAULT_CANDIDATES))
    parser.add_argument("--gate", default=str(DEFAULT_GATE))
    parser.add_argument("--frontier", default=str(DEFAULT_FRONTIER))
    parser.add_argument("--packet-audit", default=str(DEFAULT_PACKET_AUDIT))
    parser.add_argument("--standard-metrics", default=str(DEFAULT_STANDARD_METRICS))
    parser.add_argument("--prediction", action="append", default=[])
    parser.add_argument("--output-csv", default=str(DEFAULT_OUTPUT_CSV))
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    return parser.parse_args()


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def load_tsv(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def parse_prediction_arg(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise ValueError("Prediction inputs must use NAME=PATH")
    name, path = value.split("=", 1)
    return name.strip(), Path(path)


def label_distribution(rows: list[dict[str, Any]], field: str) -> str:
    counts = Counter(str(row.get(field, "") or "missing") for row in rows)
    return "; ".join(f"{label}={count}" for label, count in sorted(counts.items()))


def add_row(rows: list[dict[str, str]], section: str, metric: str, value: Any, notes: str = "") -> None:
    rows.append(
        {
            "section": section,
            "metric": metric,
            "value": str(value),
            "notes": notes,
        }
    )


def build_summary_rows(
    *,
    candidates: list[dict[str, Any]],
    gate: dict[str, Any],
    frontier_rows: list[dict[str, str]],
    packet_audit: dict[str, Any],
    predictions: dict[str, list[dict[str, Any]]],
    standard_metrics: dict[str, Any] | None = None,
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    submissions = {
        str(row.get("submission_id") or row.get("forum") or "")
        for row in candidates
        if row.get("submission_id") or row.get("forum")
    }
    disagreement = gate.get("disagreement", {})

    add_row(rows, "candidate_pool", "submissions", len(submissions), "OpenReview submissions collected")
    add_row(rows, "candidate_pool", "candidates", gate.get("rows", len(candidates)), "issue-level candidates")
    add_row(rows, "candidate_pool", "complete_rate", f"{float(gate.get('complete_rate', 0.0)):.3f}")
    add_row(rows, "candidate_pool", "disagreement_rows", disagreement.get("disagreement_rows", 0))
    add_row(rows, "candidate_pool", "high_disagreement_rows", disagreement.get("high_disagreement_rows", 0))
    add_row(rows, "candidate_pool", "quality_gate_ok", gate.get("ok", False))

    for name, prediction_rows in sorted(predictions.items()):
        add_row(
            rows,
            "model_predictions",
            f"{name}_label_distribution",
            label_distribution(prediction_rows, "predicted_label"),
            f"{len(prediction_rows)} predictions",
        )

    add_row(rows, "frontier", "frontier_rows", len(frontier_rows), "multi-model structured frontier")
    add_row(rows, "frontier", "suggested_label_distribution", label_distribution(frontier_rows, "suggested_label"))
    add_row(rows, "frontier", "structured_label_distribution", label_distribution(frontier_rows, "structured_label"))

    add_row(rows, "blind_packet", "packet_ok", packet_audit.get("ok", False))
    add_row(rows, "blind_packet", "blind_rows", packet_audit.get("blind_rows", 0))
    add_row(rows, "blind_packet", "audit_rows", packet_audit.get("audit_rows", 0))
    add_row(
        rows,
        "blind_packet",
        "hidden_assistant_distribution",
        "; ".join(
            f"{label}={count}"
            for label, count in sorted(packet_audit.get("assistant_distribution", {}).items())
        ),
        "assistant/model key only; not human labels",
    )

    standard_ready = bool(
        standard_metrics
        and int(standard_metrics.get("labeled_rows", 0)) == int(packet_audit.get("blind_rows", 0))
        and int(standard_metrics.get("unlabeled_rows", 0)) == 0
        and not standard_metrics.get("invalid_rows", [])
    )
    if standard_metrics:
        add_row(
            rows,
            "standard_validation",
            "labeled_rows",
            standard_metrics.get("labeled_rows", 0),
            "user-confirmed standard validation",
        )
        add_row(rows, "standard_validation", "unlabeled_rows", standard_metrics.get("unlabeled_rows", 0))
        add_row(
            rows,
            "standard_validation",
            "human_distribution",
            "; ".join(
                f"{label}={count}"
                for label, count in sorted(standard_metrics.get("human_distribution", {}).items())
            ),
        )
        add_row(
            rows,
            "standard_validation",
            "agreement_against_promoted_key",
            f"{float(standard_metrics.get('agreement', 0.0)):.3f}",
            "agreement is by construction after user-confirmed promotion",
        )

    add_row(
        rows,
        "interpretation",
        "claim_status",
        "standard_labeled_active_frontier" if standard_ready else "construction_ready",
    )
    add_row(
        rows,
        "interpretation",
        "claim_boundary",
        "active_frontier_not_iaa_or_prevalence" if standard_ready else "not_standard_validated",
        (
            "Use as hardened cross-year active-frontier evidence; do not report as independent IAA or natural label prevalence."
            if standard_ready
            else "Use as scaled frontier evidence until standard labels are completed."
        ),
    )
    return rows


def write_csv(path: str | Path, rows: list[dict[str, str]]) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["section", "metric", "value", "notes"])
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: str | Path, rows: list[dict[str, str]]) -> None:
    by_metric = {row["metric"]: row for row in rows}
    standard_ready = by_metric.get("claim_status", {}).get("value") == "standard_labeled_active_frontier"
    intro = (
        "This is a standard-labeled cross-year active-frontier summary. It is user-confirmed single-pass validation, not an independent two-annotator IAA result or a natural-prevalence estimate."
        if standard_ready
        else "This is a construction-ready cross-year frontier summary. It is not a standard-labeled benchmark result yet."
    )
    paper_use = (
        [
            "- Use this to show that the cross-year scale blocker has been removed.",
            "- Report expanded80 as a hardened active-frontier result with explicit provenance.",
            "- Pair this table with the 21-row validated ICLR 2025 stress result, and avoid IAA or natural-prevalence claims.",
        ]
        if standard_ready
        else [
            "- Use this to show that the cross-year scale blocker has been removed.",
            "- Do not report expanded80 model performance as benchmark performance until the blind packet is standard-labeled.",
            "- Pair this table with the 21-row validated ICLR 2025 stress result to separate evidence of brittleness from benchmark generalization.",
        ]
    )
    lines = [
        "# ICLR 2025 Expanded80 Frontier Summary",
        "",
        intro,
        "",
        "| section | metric | value | notes |",
        "| --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(f"| {row['section']} | {row['metric']} | {row['value']} | {row['notes']} |")
    lines.extend(
        [
            "",
            "## Paper Use",
            "",
            *paper_use,
        ]
    )
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    prediction_paths = dict(DEFAULT_PREDICTIONS)
    for value in args.prediction:
        name, path = parse_prediction_arg(value)
        prediction_paths[name] = path

    rows = build_summary_rows(
        candidates=load_jsonl(args.candidates),
        gate=load_json(args.gate),
        frontier_rows=load_tsv(args.frontier),
        packet_audit=load_json(args.packet_audit),
        standard_metrics=load_json(args.standard_metrics) if Path(args.standard_metrics).exists() else None,
        predictions={name: load_jsonl(path) for name, path in prediction_paths.items()},
    )
    write_csv(args.output_csv, rows)
    write_markdown(args.output_md, rows)
    print(f"Wrote expanded frontier summary to {args.output_csv}")


if __name__ == "__main__":
    main()
