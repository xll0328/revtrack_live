from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, NamedTuple


ROOT = Path(__file__).resolve().parents[1]
VALID_LABELS = {"fixed", "partially_fixed", "unresolved", "regressed"}
LABEL_ORDER = ["regressed", "fixed", "unresolved", "partially_fixed"]
MODEL_FIELDS = [
    "heuristic_label",
    "tfidf_label",
    "modernbert_label",
    "mpnet_label",
    "issue_ledger_label",
    "structured_label",
]
DEFAULT_PACKETS = [
    "ICLR 2024 v1:"
    "experiments/day1/iclr2024_human_validation_v1_blind.tsv:"
    "experiments/day1/iclr2024_human_validation_v1_key.tsv:"
    "experiments/day1/iclr2024_human_validation_v1_audit.tsv",
    "ICLR 2025 repro v2:"
    "experiments/day1/iclr2025_repro_human_validation_v2_blind.tsv:"
    "experiments/day1/iclr2025_repro_human_validation_v2_key.tsv:"
    "experiments/day1/iclr2025_repro_human_validation_v2_audit.tsv",
    "ICLR 2025 expanded80 v1:"
    "experiments/day1/iclr2025_expanded80_human_validation_v1_blind.tsv:"
    "experiments/day1/iclr2025_expanded80_human_validation_v1_key.tsv:"
    "experiments/day1/iclr2025_expanded80_human_validation_v1_audit.tsv",
    "NeurIPS 2024 limit100 v1:"
    "experiments/day1/neurips2024_limit100_human_validation_v1_blind.tsv:"
    "experiments/day1/neurips2024_limit100_human_validation_v1_key.tsv:"
    "experiments/day1/neurips2024_limit100_human_validation_v1_audit.tsv",
    "ICLR 2023 random80 v1:"
    "experiments/day1/iclr2023_limit80_random80_human_validation_v1_blind.tsv:"
    "experiments/day1/iclr2023_limit80_random80_human_validation_v1_key.tsv:"
    "experiments/day1/iclr2023_limit80_random80_human_validation_v1_audit.tsv",
]

DEFAULT_QUOTAS = {
    "regressed": 6,
    "fixed": 12,
    "unresolved": 20,
    "partially_fixed": 12,
}

BLIND_FIELDS = [
    "issue_id",
    "source_packet",
    "paper_title",
    "review_rating",
    "review_confidence",
    "review_excerpt",
    "top_response_excerpt",
    "aligned_response_excerpt",
    "revision_summary",
    "human_label",
    "human_confidence",
    "evidence_span",
    "notes",
]

KEY_FIELDS = [
    "issue_id",
    "source_packet",
    "assistant_label",
    "first_pass_label",
    "first_pass_confidence",
    "first_pass_evidence_span",
    "first_pass_notes",
    "selection_score",
    "selection_reason",
    "audit_bucket",
    "audit_score",
    "priority_score",
    "original_assistant_label",
    "suggested_label",
    "silver_label",
    *MODEL_FIELDS,
    "assistant_evidence_span",
    "assistant_notes",
]


class PacketSpec(NamedTuple):
    name: str
    blind: Path
    key: Path
    audit: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Export a second-annotator IAA mini-slice from existing standard "
            "human-validation packets."
        )
    )
    parser.add_argument(
        "--packet",
        action="append",
        default=None,
        help=(
            "Packet spec as name:blind:key:audit. May be repeated. "
            "Defaults to all current standard packets."
        ),
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        default=60,
        help="Number of rows to sample for the second-annotator packet.",
    )
    parser.add_argument(
        "--min-per-packet",
        type=int,
        default=8,
        help="Minimum rows from each packet before label-quota fill. Set 0 to disable.",
    )
    parser.add_argument(
        "--max-per-packet",
        type=int,
        default=20,
        help="Maximum rows from any packet. Set 0 to disable.",
    )
    parser.add_argument(
        "--label-quota",
        action="append",
        default=None,
        help=(
            "Per-label target in the form label=count. "
            "Repeatable. Defaults: regressed=6,fixed=12,unresolved=20,partially_fixed=12."
        ),
    )
    parser.add_argument(
        "--blind-output",
        default="experiments/day1/iaa_second_annotator_mini60_v1_blind.tsv",
    )
    parser.add_argument(
        "--key-output",
        default="experiments/day1/iaa_second_annotator_mini60_v1_key.tsv",
    )
    parser.add_argument(
        "--manifest-json",
        default="outputs/day1/paper_assets/iaa_second_annotator_mini60_v1_manifest.json",
    )
    parser.add_argument(
        "--manifest-md",
        default="outputs/day1/paper_assets/iaa_second_annotator_mini60_v1_manifest.md",
    )
    return parser.parse_args()


def resolve_path(path: str | Path) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else ROOT / candidate


def relpath(path: str | Path) -> str:
    resolved = resolve_path(path)
    try:
        return str(resolved.relative_to(ROOT))
    except ValueError:
        return str(resolved)


def parse_packet_spec(value: str) -> PacketSpec:
    parts = value.split(":", 3)
    if len(parts) != 4:
        raise ValueError("Packet spec must be name:blind:key:audit")
    name, blind, key, audit = parts
    return PacketSpec(
        name=name,
        blind=resolve_path(blind),
        key=resolve_path(key),
        audit=resolve_path(audit),
    )


def load_tsv(path: str | Path) -> list[dict[str, str]]:
    with resolve_path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: str | Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    output_path = resolve_path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: str | Path, payload: dict[str, Any]) -> None:
    output_path = resolve_path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def normalize_label(value: str | None) -> str:
    return (value or "").strip().lower()


def numeric(value: str | int | float | None, default: float = 0.0) -> float:
    if value in (None, ""):
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def by_issue_id(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    output: dict[str, dict[str, str]] = {}
    for row in rows:
        issue_id = (row.get("issue_id") or "").strip()
        if issue_id:
            output[issue_id] = row
    return output


def disagreement_count(key_row: dict[str, str]) -> int:
    labels = {
        normalize_label(key_row.get(field))
        for field in MODEL_FIELDS
        if normalize_label(key_row.get(field))
    }
    return max(0, len(labels) - 1)


def label_bonus(label: str) -> float:
    if label == "regressed":
        return 10.0
    if label == "fixed":
        return 5.0
    if label == "unresolved":
        return 4.0
    return 1.0


def bucket_bonus(bucket: str) -> float:
    bucket = (bucket or "").strip()
    if bucket == "minority_regressed":
        return 4.0
    if bucket == "minority_unresolved":
        return 3.0
    if bucket == "structured_error":
        return 2.0
    if bucket == "model_high_conflict":
        return 1.5
    if bucket == "model_disagreement":
        return 1.0
    return 0.0


def selection_score(
    label: str,
    *,
    audit_score: float,
    priority_score: float,
    disagreement: int,
    bucket: str,
) -> float:
    return (
        audit_score
        + (0.2 * priority_score)
        + (2.0 * float(disagreement))
        + label_bonus(label)
        + bucket_bonus(bucket)
    )


def parse_label_quotas(items: list[str] | None) -> dict[str, int]:
    if not items:
        return dict(DEFAULT_QUOTAS)
    quotas = dict(DEFAULT_QUOTAS)
    for item in items:
        label, sep, count = item.partition("=")
        if not sep:
            raise ValueError(f"Invalid --label-quota value: {item}")
        key = normalize_label(label)
        if key not in VALID_LABELS:
            raise ValueError(f"Unknown label for --label-quota: {label}")
        quotas[key] = max(0, int(count))
    return quotas


def build_candidates(packet_specs: list[PacketSpec]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for packet in packet_specs:
        blind_rows = load_tsv(packet.blind)
        key_by_id = by_issue_id(load_tsv(packet.key))
        audit_by_id = by_issue_id(load_tsv(packet.audit))
        for blind in blind_rows:
            issue_id = (blind.get("issue_id") or "").strip()
            if not issue_id:
                continue
            label = normalize_label(blind.get("human_label") or blind.get("gold_label"))
            if label not in VALID_LABELS:
                continue
            key_row = key_by_id.get(issue_id, {})
            audit_row = audit_by_id.get(issue_id, {})
            disagreement = disagreement_count(key_row)
            audit_score = numeric(audit_row.get("audit_score"))
            priority_score = numeric(audit_row.get("priority_score"))
            bucket = audit_row.get("audit_bucket", "")
            score = selection_score(
                label,
                audit_score=audit_score,
                priority_score=priority_score,
                disagreement=disagreement,
                bucket=bucket,
            )
            reasons = [
                f"label={label}",
                f"bucket={bucket or 'unknown'}",
                f"disagreement={disagreement}",
                f"audit_score={audit_score:.3f}",
            ]
            candidates.append(
                {
                    "issue_id": issue_id,
                    "source_packet": packet.name,
                    "blind": blind,
                    "key": key_row,
                    "audit": audit_row,
                    "first_pass_label": label,
                    "selection_score": score,
                    "selection_reason": "; ".join(reasons),
                }
            )
    return candidates


def sort_key(candidate: dict[str, Any]) -> tuple[float, str]:
    return (-float(candidate["selection_score"]), str(candidate["issue_id"]))


def select_candidates(
    candidates: list[dict[str, Any]],
    *,
    sample_size: int,
    label_quotas: dict[str, int],
    min_per_packet: int = 0,
    max_per_packet: int = 0,
) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in candidates:
        grouped[row["first_pass_label"]].append(row)
    for label in grouped:
        grouped[label].sort(key=sort_key)

    selected: list[dict[str, Any]] = []
    selected_ids: set[str] = set()
    source_counts: Counter[str] = Counter()
    label_counts: Counter[str] = Counter()

    def can_take(row: dict[str, Any]) -> bool:
        if row["issue_id"] in selected_ids:
            return False
        if max_per_packet > 0 and source_counts[row["source_packet"]] >= max_per_packet:
            return False
        return True

    def take(row: dict[str, Any]) -> None:
        selected.append(row)
        selected_ids.add(row["issue_id"])
        source_counts[row["source_packet"]] += 1
        label_counts[row["first_pass_label"]] += 1

    if min_per_packet > 0:
        by_source: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in candidates:
            by_source[row["source_packet"]].append(row)
        for source in by_source:
            by_source[source].sort(key=sort_key)
        for source, rows in sorted(by_source.items()):
            for row in rows:
                if len(selected) >= sample_size:
                    break
                if source_counts[source] >= min_per_packet:
                    break
                if not can_take(row):
                    continue
                take(row)

    for label in LABEL_ORDER:
        target = max(0, label_quotas.get(label, 0))
        for row in grouped.get(label, []):
            if len(selected) >= sample_size:
                break
            if label_counts[label] >= target:
                break
            if not can_take(row):
                continue
            take(row)

    remaining = sorted(
        [row for row in candidates if row["issue_id"] not in selected_ids],
        key=sort_key,
    )
    for row in remaining:
        if len(selected) >= sample_size:
            break
        if not can_take(row):
            continue
        take(row)

    return sorted(selected, key=sort_key)


def as_blind_row(candidate: dict[str, Any]) -> dict[str, str]:
    blind = candidate["blind"]
    return {
        "issue_id": candidate["issue_id"],
        "source_packet": candidate["source_packet"],
        "paper_title": blind.get("paper_title", ""),
        "review_rating": blind.get("review_rating", ""),
        "review_confidence": blind.get("review_confidence", ""),
        "review_excerpt": blind.get("review_excerpt", ""),
        "top_response_excerpt": blind.get("top_response_excerpt", ""),
        "aligned_response_excerpt": blind.get("aligned_response_excerpt", ""),
        "revision_summary": blind.get("revision_summary", ""),
        "human_label": "",
        "human_confidence": "",
        "evidence_span": "",
        "notes": "",
    }


def as_key_row(candidate: dict[str, Any]) -> dict[str, str]:
    blind = candidate["blind"]
    key = candidate["key"]
    audit = candidate["audit"]
    first_pass_label = candidate["first_pass_label"]
    return {
        "issue_id": candidate["issue_id"],
        "source_packet": candidate["source_packet"],
        "assistant_label": first_pass_label,
        "first_pass_label": first_pass_label,
        "first_pass_confidence": blind.get("human_confidence", ""),
        "first_pass_evidence_span": blind.get("evidence_span", ""),
        "first_pass_notes": blind.get("notes", ""),
        "selection_score": f"{float(candidate['selection_score']):.3f}",
        "selection_reason": candidate["selection_reason"],
        "audit_bucket": audit.get("audit_bucket", ""),
        "audit_score": audit.get("audit_score", ""),
        "priority_score": audit.get("priority_score", ""),
        "original_assistant_label": normalize_label(key.get("assistant_label")),
        "suggested_label": normalize_label(key.get("suggested_label")),
        "silver_label": normalize_label(key.get("silver_label")),
        **{field: normalize_label(key.get(field)) for field in MODEL_FIELDS},
        "assistant_evidence_span": key.get("assistant_evidence_span", ""),
        "assistant_notes": key.get("assistant_notes", ""),
    }


def summarize_counts(rows: list[dict[str, Any]], label_field: str) -> dict[str, int]:
    counter = Counter(row[label_field] for row in rows)
    return {label: int(counter.get(label, 0)) for label in LABEL_ORDER}


def summarize_sources(rows: list[dict[str, Any]]) -> dict[str, int]:
    counter = Counter(row["source_packet"] for row in rows)
    return dict(sorted(counter.items(), key=lambda item: (-item[1], item[0])))


def write_manifest_md(path: str | Path, report: dict[str, Any]) -> None:
    output_path = resolve_path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Second Annotator IAA Mini-Slice Manifest",
        "",
        f"- sample size target: `{report['sample_size_target']}`",
        f"- per-packet minimum: `{report['min_per_packet']}`",
        f"- per-packet maximum: `{report['max_per_packet']}`",
        f"- selected rows: `{report['selected_rows']}`",
        f"- blind sheet: `{report['blind_output']}`",
        f"- key sheet: `{report['key_output']}`",
        "",
        "## Label Distribution",
        "",
        "| label | selected | candidate_pool |",
        "| --- | ---: | ---: |",
    ]
    for label in LABEL_ORDER:
        lines.append(
            f"| {label} | {report['selected_label_distribution'].get(label, 0)} | "
            f"{report['candidate_label_distribution'].get(label, 0)} |"
        )
    lines.extend(
        [
            "",
            "## Source Distribution",
            "",
            "| source packet | selected |",
            "| --- | ---: |",
        ]
    )
    for source, count in report["selected_source_distribution"].items():
        lines.append(f"| {source} | {count} |")
    lines.extend(
        [
            "",
            "## Evaluation Command After Second-Pass Labeling",
            "",
            "```bash",
            "python scripts/evaluate_human_validation.py \\",
            f"  --human-sheet {report['blind_output']} \\",
            f"  --key {report['key_output']} \\",
            "  --output-json outputs/day1/paper_assets/iaa_second_annotator_mini60_v1_metrics.json \\",
            "  --mismatch-output outputs/day1/paper_assets/iaa_second_annotator_mini60_v1_mismatches.tsv",
            "```",
            "",
            "Boundary: this packet is for independent second-pass agreement measurement only. "
            "Do not overwrite canonical first-pass standard labels.",
            "",
        ]
    )
    output_path.write_text("\n".join(lines), encoding="utf-8")


def build_report(
    selected: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
    *,
    sample_size: int,
    label_quotas: dict[str, int],
    min_per_packet: int,
    max_per_packet: int,
    blind_output: str | Path,
    key_output: str | Path,
    packet_specs: list[PacketSpec],
) -> dict[str, Any]:
    return {
        "sample_size_target": sample_size,
        "min_per_packet": min_per_packet,
        "max_per_packet": max_per_packet,
        "selected_rows": len(selected),
        "label_quotas": label_quotas,
        "blind_output": relpath(blind_output),
        "key_output": relpath(key_output),
        "packets": [
            {
                "name": packet.name,
                "blind": relpath(packet.blind),
                "key": relpath(packet.key),
                "audit": relpath(packet.audit),
            }
            for packet in packet_specs
        ],
        "candidate_rows": len(candidates),
        "candidate_label_distribution": summarize_counts(candidates, "first_pass_label"),
        "selected_label_distribution": summarize_counts(selected, "first_pass_label"),
        "selected_source_distribution": summarize_sources(selected),
    }


def main() -> None:
    args = parse_args()
    packet_specs = [parse_packet_spec(spec) for spec in (args.packet or DEFAULT_PACKETS)]
    label_quotas = parse_label_quotas(args.label_quota)

    candidates = build_candidates(packet_specs)
    selected = select_candidates(
        candidates,
        sample_size=max(1, args.sample_size),
        label_quotas=label_quotas,
        min_per_packet=max(0, args.min_per_packet),
        max_per_packet=max(0, args.max_per_packet),
    )

    write_tsv(args.blind_output, [as_blind_row(row) for row in selected], BLIND_FIELDS)
    write_tsv(args.key_output, [as_key_row(row) for row in selected], KEY_FIELDS)

    report = build_report(
        selected,
        candidates,
        sample_size=max(1, args.sample_size),
        label_quotas=label_quotas,
        min_per_packet=max(0, args.min_per_packet),
        max_per_packet=max(0, args.max_per_packet),
        blind_output=args.blind_output,
        key_output=args.key_output,
        packet_specs=packet_specs,
    )
    write_json(args.manifest_json, report)
    write_manifest_md(args.manifest_md, report)

    print(
        f"Wrote second-annotator packet with {len(selected)} rows to {resolve_path(args.blind_output)}"
    )
    print(f"Wrote packet key to {resolve_path(args.key_output)}")
    print(f"Wrote manifest to {resolve_path(args.manifest_json)}")


if __name__ == "__main__":
    main()
