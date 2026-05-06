from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any, NamedTuple


ROOT = Path(__file__).resolve().parents[1]
VALID_LABELS = {"fixed", "partially_fixed", "unresolved", "regressed"}
BUCKET_PRIORITY = {
    "minority_regressed": 0,
    "minority_unresolved": 1,
    "structured_error": 2,
    "model_high_conflict": 3,
    "model_disagreement": 4,
    "label_stratum": 5,
}
DEFAULT_PACKETS = [
    "ICLR 2024 v1:"
    "experiments/day1/iclr2024_human_validation_v1_blind.tsv:"
    "experiments/day1/iclr2024_human_validation_v1_key.tsv:"
    "experiments/day1/iclr2024_human_validation_v1_audit.tsv:"
    "outputs/day1/iclr2024_human_validation_v1_pending_metrics.json:"
    "outputs/day1/iclr2024_human_validation_v1_blind_packet.html",
    "ICLR 2025 repro v2:"
    "experiments/day1/iclr2025_repro_human_validation_v2_blind.tsv:"
    "experiments/day1/iclr2025_repro_human_validation_v2_key.tsv:"
    "experiments/day1/iclr2025_repro_human_validation_v2_audit.tsv:"
    "outputs/day1/iclr2025_repro_human_validation_v2_pending_metrics.json:"
    "outputs/day1/iclr2025_repro_human_validation_v2_blind_packet.html",
    "ICLR 2025 expanded80 v1:"
    "experiments/day1/iclr2025_expanded80_human_validation_v1_blind.tsv:"
    "experiments/day1/iclr2025_expanded80_human_validation_v1_key.tsv:"
    "experiments/day1/iclr2025_expanded80_human_validation_v1_audit.tsv:"
    "outputs/day1/iclr2025_expanded80_human_validation_v1_standard_metrics.json:"
    "outputs/day1/iclr2025_expanded80_human_validation_v1_blind_packet.html",
    "NeurIPS 2024 limit100 v1:"
    "experiments/day1/neurips2024_limit100_human_validation_v1_blind.tsv:"
    "experiments/day1/neurips2024_limit100_human_validation_v1_key.tsv:"
    "experiments/day1/neurips2024_limit100_human_validation_v1_audit.tsv:"
    "outputs/day1/neurips2024_limit100_human_validation_v1_pending_metrics.json:"
    "outputs/day1/neurips2024_limit100_human_validation_v1_blind_packet.html",
    "ICLR 2023 random80 v1:"
    "experiments/day1/iclr2023_limit80_random80_human_validation_v1_blind.tsv:"
    "experiments/day1/iclr2023_limit80_random80_human_validation_v1_key.tsv:"
    "experiments/day1/iclr2023_limit80_random80_human_validation_v1_audit.tsv:"
    "outputs/day1/iclr2023_limit80_random80_human_validation_v1_standard_metrics.json:"
    "outputs/day1/iclr2023_limit80_random80_human_validation_v1_blind_packet.html",
]
QUEUE_FIELDS = [
    "queue_rank",
    "packet",
    "status",
    "issue_id",
    "paper_title",
    "audit_bucket",
    "audit_score",
    "priority_score",
    "audit_rank",
    "assistant_label",
    "suggested_label",
    "human_label_present",
    "current_human_label",
    "review_rating",
    "review_confidence",
    "priority_reason",
    "next_action",
    "blind_sheet",
    "blind_packet",
]


class PacketSpec(NamedTuple):
    name: str
    blind: Path
    key: Path
    audit: Path
    pending_metrics: Path
    blind_packet: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export a prioritized queue for independent human validation."
    )
    parser.add_argument(
        "--packet",
        action="append",
        default=None,
        help=(
            "Packet spec as name:blind:key:audit:pending_metrics:blind_packet. "
            "May be repeated. Defaults to all active standard human-validation packets."
        ),
    )
    parser.add_argument(
        "--output-csv",
        default="outputs/day1/paper_assets/human_validation_work_queue.csv",
    )
    parser.add_argument(
        "--output-md",
        default="outputs/day1/paper_assets/human_validation_work_queue.md",
    )
    return parser.parse_args()


def resolve_path(path: str | Path) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else ROOT / candidate


def parse_packet_spec(value: str) -> PacketSpec:
    parts = value.split(":", 5)
    if len(parts) != 6:
        raise ValueError(
            "Packet spec must have 6 colon-separated fields: "
            "name:blind:key:audit:pending_metrics:blind_packet"
        )
    name, blind, key, audit, pending_metrics, blind_packet = parts
    return PacketSpec(
        name=name,
        blind=resolve_path(blind),
        key=resolve_path(key),
        audit=resolve_path(audit),
        pending_metrics=resolve_path(pending_metrics),
        blind_packet=resolve_path(blind_packet),
    )


def load_tsv(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def normalize_label(value: str | None) -> str:
    return (value or "").strip().lower()


def numeric(value: str | int | float | None, default: float = 0.0) -> float:
    if value in (None, ""):
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def integer(value: str | int | float | None, default: int = 999999) -> int:
    if value in (None, ""):
        return default
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def by_issue_id(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {
        row["issue_id"].strip(): row
        for row in rows
        if row.get("issue_id", "").strip()
    }


def relpath(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def priority_reason(row: dict[str, str]) -> str:
    bucket = row["audit_bucket"] or "unknown"
    label = row["assistant_label"] or "unknown"
    score = row["audit_score"] or "0"
    return f"{bucket}; assistant={label}; audit_score={score}"


def next_action(status: str, blind_sheet: str) -> str:
    if status == "done":
        return "Already labeled; rerun evaluate_human_validation.py after any edits."
    return f"Fill human_label, human_confidence, evidence_span, and notes in {blind_sheet}."


def packet_queue_rows(packet: PacketSpec, packet_order: int) -> list[dict[str, str]]:
    blind_rows = load_tsv(packet.blind)
    key_by_id = by_issue_id(load_tsv(packet.key))
    audit_by_id = by_issue_id(load_tsv(packet.audit))
    blind_sheet = relpath(packet.blind)
    blind_packet = relpath(packet.blind_packet)

    queue_rows: list[dict[str, str]] = []
    for blind in blind_rows:
        issue_id = blind.get("issue_id", "").strip()
        key = key_by_id.get(issue_id, {})
        audit = audit_by_id.get(issue_id, {})
        source = {**key, **audit, **blind}
        human_label = normalize_label(blind.get("human_label") or blind.get("gold_label"))
        human_label_present = human_label in VALID_LABELS
        status = "done" if human_label_present else "pending"
        audit_score = f"{numeric(audit.get('audit_score') or key.get('audit_score')):.3f}"
        priority_score = f"{numeric(audit.get('priority_score') or key.get('priority_score')):.3f}"
        row = {
            "packet_order": str(packet_order),
            "bucket_priority": str(
                BUCKET_PRIORITY.get((audit.get("audit_bucket") or key.get("audit_bucket") or "").strip(), 99)
            ),
            "sort_audit_score": audit_score,
            "sort_priority_score": priority_score,
            "queue_rank": "",
            "packet": packet.name,
            "status": status,
            "issue_id": issue_id,
            "paper_title": source.get("paper_title", ""),
            "audit_bucket": audit.get("audit_bucket") or key.get("audit_bucket", ""),
            "audit_score": audit_score,
            "priority_score": priority_score,
            "audit_rank": audit.get("audit_rank") or key.get("audit_rank", ""),
            "assistant_label": key.get("assistant_label") or audit.get("assistant_label", ""),
            "suggested_label": key.get("suggested_label") or audit.get("suggested_label", ""),
            "human_label_present": str(human_label_present).lower(),
            "current_human_label": human_label,
            "review_rating": source.get("review_rating", ""),
            "review_confidence": source.get("review_confidence", ""),
            "priority_reason": "",
            "next_action": "",
            "blind_sheet": blind_sheet,
            "blind_packet": blind_packet,
        }
        row["priority_reason"] = priority_reason(row)
        row["next_action"] = next_action(status, blind_sheet)
        queue_rows.append(row)
    return queue_rows


def sort_queue(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    sorted_rows = sorted(
        rows,
        key=lambda row: (
            row["status"] == "done",
            integer(row["packet_order"]),
            integer(row["bucket_priority"]),
            -numeric(row["sort_audit_score"]),
            -numeric(row["sort_priority_score"]),
            integer(row["audit_rank"]),
            row["issue_id"],
        ),
    )
    for rank, row in enumerate(sorted_rows, start=1):
        row["queue_rank"] = str(rank)
    return sorted_rows


def build_queue(packet_specs: list[PacketSpec]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for packet_order, packet in enumerate(packet_specs):
        rows.extend(packet_queue_rows(packet, packet_order))
    return sort_queue(rows)


def write_csv(path: str | Path, rows: list[dict[str, str]]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=QUEUE_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in QUEUE_FIELDS})


def packet_summary(
    packet_specs: list[PacketSpec],
    rows: list[dict[str, str]] | None = None,
) -> list[dict[str, Any]]:
    row_counts: dict[str, Counter[str]] = {}
    if rows is not None:
        for row in rows:
            packet_counts = row_counts.setdefault(row["packet"], Counter())
            packet_counts["rows"] += 1
            packet_counts[row["status"]] += 1

    summaries: list[dict[str, Any]] = []
    for packet in packet_specs:
        metrics = load_json(packet.pending_metrics)
        counts = row_counts.get(packet.name, Counter())
        rows_count = int(counts.get("rows", 0)) if counts else int(metrics.get("rows", 0))
        labeled_rows = (
            int(counts.get("done", 0))
            if counts
            else int(metrics.get("labeled_rows", 0))
        )
        unlabeled_rows = (
            int(counts.get("pending", 0))
            if counts
            else int(metrics.get("unlabeled_rows", max(rows_count - labeled_rows, 0)))
        )
        summaries.append(
            {
                "packet": packet.name,
                "rows": rows_count,
                "labeled_rows": labeled_rows,
                "unlabeled_rows": unlabeled_rows,
                "blind_sheet": relpath(packet.blind),
                "blind_packet": relpath(packet.blind_packet),
                "pending_metrics": relpath(packet.pending_metrics),
            }
        )
    return summaries


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def write_markdown(
    path: str | Path,
    rows: list[dict[str, str]],
    summaries: list[dict[str, Any]],
) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    total_rows = len(rows)
    labeled_rows = sum(1 for row in rows if row["status"] == "done")
    unlabeled_rows = total_rows - labeled_rows
    bucket_counts = Counter(row["audit_bucket"] or "unknown" for row in rows)
    label_counts = Counter(row["assistant_label"] or "unknown" for row in rows)
    top_rows = [row for row in rows if row["status"] == "pending"][:25]

    packet_rows = [
        [
            summary["packet"],
            str(summary["rows"]),
            str(summary["labeled_rows"]),
            str(summary["unlabeled_rows"]),
            f"[blind sheet]({summary['blind_sheet']})",
            f"[blind packet]({summary['blind_packet']})",
        ]
        for summary in summaries
    ]
    bucket_rows = [[bucket, str(count)] for bucket, count in sorted(bucket_counts.items())]
    label_rows = [[label, str(count)] for label, count in sorted(label_counts.items())]
    top_table_rows = [
        [
            row["queue_rank"],
            row["packet"],
            row["issue_id"],
            row["audit_bucket"] or "unknown",
            row["assistant_label"] or "unknown",
            row["audit_score"],
            row["next_action"],
        ]
        for row in top_rows
    ]

    content = [
        "# Human Validation Work Queue",
        "",
        "This is an assistant-generated triage queue. Treat it as workflow metadata only; validation claims must come from completed blind sheets or explicitly promoted user-confirmed signoff records with provenance.",
        "",
        "## Summary",
        "",
        f"- Active packets: `{len(summaries)}`",
        f"- Total rows: `{total_rows}`",
        f"- Labeled rows: `{labeled_rows}`",
        f"- Unlabeled rows: `{unlabeled_rows}`",
        "",
        "## Active Packets",
        "",
        markdown_table(
            ["packet", "rows", "labeled", "unlabeled", "blind sheet", "blind packet"],
            packet_rows,
        ),
        "",
        "## Queue Policy",
        "",
        "- Pending rows are placed before completed rows.",
        "- Packet order is preserved, then rarer/high-risk audit buckets are prioritized.",
        "- Within a bucket, higher audit_score and priority_score rows are reviewed first.",
        "",
        "## Audit Bucket Distribution",
        "",
        markdown_table(["audit bucket", "rows"], bucket_rows),
        "",
        "## Assistant Label Distribution",
        "",
        markdown_table(["assistant label", "rows"], label_rows),
        "",
        "## Top Pending Rows",
        "",
        markdown_table(
            ["rank", "packet", "issue_id", "bucket", "assistant", "score", "next action"],
            top_table_rows,
        ),
        "",
    ]
    output_path.write_text("\n".join(content), encoding="utf-8")


def main() -> None:
    args = parse_args()
    packet_specs = [parse_packet_spec(value) for value in (args.packet or DEFAULT_PACKETS)]
    rows = build_queue(packet_specs)
    summaries = packet_summary(packet_specs, rows)
    write_csv(args.output_csv, rows)
    write_markdown(args.output_md, rows, summaries)
    print(f"Wrote {len(rows)} queue rows to {args.output_csv}")
    print(f"Wrote human-validation queue summary to {args.output_md}")


if __name__ == "__main__":
    main()
