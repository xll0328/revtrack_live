from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

DEFAULT_BLIND = ROOT / "experiments/day1/iaa_second_annotator_mini60_v1_blind.tsv"
DEFAULT_KEY = ROOT / "experiments/day1/iaa_second_annotator_mini60_v1_key.tsv"
DEFAULT_OUTPUT_DIR = ROOT / "experiments/day1"
DEFAULT_MANIFEST_JSON = ROOT / "outputs/day1/paper_assets/iaa_second_annotator_mini60_batches.json"
DEFAULT_MANIFEST_MD = ROOT / "outputs/day1/paper_assets/iaa_second_annotator_mini60_batches.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Split second-annotator IAA packet into balanced blind batches."
    )
    parser.add_argument("--blind-sheet", default=str(DEFAULT_BLIND))
    parser.add_argument("--key-sheet", default=str(DEFAULT_KEY))
    parser.add_argument("--num-batches", type=int, default=3)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--batch-prefix", default="iaa_second_annotator_mini60_v1_blind_batch")
    parser.add_argument("--manifest-json", default=str(DEFAULT_MANIFEST_JSON))
    parser.add_argument("--manifest-md", default=str(DEFAULT_MANIFEST_MD))
    return parser.parse_args()


def resolve(path: str | Path) -> Path:
    p = Path(path)
    return p if p.is_absolute() else ROOT / p


def load_tsv(path: str | Path) -> tuple[list[str], list[dict[str, str]]]:
    with resolve(path).open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        fieldnames = reader.fieldnames or []
        rows = list(reader)
    return fieldnames, rows


def write_tsv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def relpath(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def build_batches(
    blind_rows: list[dict[str, str]],
    key_rows: list[dict[str, str]],
    num_batches: int,
) -> list[list[dict[str, str]]]:
    key_by_id = {row.get("issue_id", ""): row for row in key_rows}
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in blind_rows:
        issue_id = row.get("issue_id", "")
        key = key_by_id.get(issue_id, {})
        label = (key.get("first_pass_label") or key.get("assistant_label") or "unknown").strip().lower()
        source = (row.get("source_packet") or "unknown").strip()
        grouped[(label, source)].append(row)

    # Deterministic ordering for reproducibility.
    for key in grouped:
        grouped[key].sort(key=lambda row: row.get("issue_id", ""))

    batches: list[list[dict[str, str]]] = [[] for _ in range(num_batches)]
    cursor = 0
    for group_key in sorted(grouped.keys()):
        for row in grouped[group_key]:
            batches[cursor % num_batches].append(row)
            cursor += 1

    # Keep stable row order in each batch.
    for batch in batches:
        batch.sort(key=lambda row: row.get("issue_id", ""))
    return batches


def summarize_batch(batch: list[dict[str, str]], key_by_id: dict[str, dict[str, str]]) -> dict[str, Any]:
    label_counts: Counter[str] = Counter()
    source_counts: Counter[str] = Counter()
    for row in batch:
        issue_id = row.get("issue_id", "")
        key = key_by_id.get(issue_id, {})
        label = (key.get("first_pass_label") or key.get("assistant_label") or "unknown").strip().lower()
        source = (row.get("source_packet") or "unknown").strip()
        label_counts[label] += 1
        source_counts[source] += 1
    return {
        "rows": len(batch),
        "label_distribution": dict(sorted(label_counts.items())),
        "source_distribution": dict(sorted(source_counts.items())),
    }


def write_manifest_md(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# IAA Second Annotator Batch Plan",
        "",
        f"- total rows: `{payload['total_rows']}`",
        f"- batches: `{len(payload['batches'])}`",
        "",
        "## Batch Summary",
        "",
        "| batch | rows | labels | sources | file |",
        "| --- | ---: | --- | --- | --- |",
    ]
    for batch in payload["batches"]:
        labels = ", ".join(f"{k}:{v}" for k, v in batch["label_distribution"].items())
        sources = ", ".join(f"{k}:{v}" for k, v in batch["source_distribution"].items())
        lines.append(
            f"| {batch['batch_id']} | {batch['rows']} | {labels} | {sources} | `{batch['file']}` |"
        )
    lines.extend(
        [
            "",
            "## Aggregation After Batch Labeling",
            "",
            "1. Merge batch files back into `experiments/day1/iaa_second_annotator_mini60_v1_blind.tsv`.",
            "2. Run:",
            "",
            "```bash",
            "python scripts/evaluate_human_validation.py \\",
            "  --human-sheet experiments/day1/iaa_second_annotator_mini60_v1_blind.tsv \\",
            "  --key experiments/day1/iaa_second_annotator_mini60_v1_key.tsv \\",
            "  --output-json outputs/day1/paper_assets/iaa_second_annotator_mini60_v1_metrics.json \\",
            "  --mismatch-output outputs/day1/paper_assets/iaa_second_annotator_mini60_v1_mismatches.tsv",
            "```",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    if args.num_batches <= 1:
        raise SystemExit("--num-batches must be >= 2")

    blind_fields, blind_rows = load_tsv(args.blind_sheet)
    _, key_rows = load_tsv(args.key_sheet)
    key_by_id = {row.get("issue_id", ""): row for row in key_rows}

    batches = build_batches(blind_rows, key_rows, args.num_batches)
    output_dir = resolve(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    batch_payloads: list[dict[str, Any]] = []
    for idx, rows in enumerate(batches, start=1):
        out_path = output_dir / f"{args.batch_prefix}{idx}.tsv"
        write_tsv(out_path, blind_fields, rows)
        summary = summarize_batch(rows, key_by_id)
        batch_payloads.append(
            {
                "batch_id": idx,
                "file": relpath(out_path),
                **summary,
            }
        )

    payload = {
        "total_rows": len(blind_rows),
        "num_batches": args.num_batches,
        "batches": batch_payloads,
    }
    manifest_json = resolve(args.manifest_json)
    manifest_json.parent.mkdir(parents=True, exist_ok=True)
    manifest_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_manifest_md(resolve(args.manifest_md), payload)
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
