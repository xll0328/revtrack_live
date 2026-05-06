from __future__ import annotations

import csv
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "split_second_annotator_packet.py"
SPEC = importlib.util.spec_from_file_location("split_second_annotator_packet", SCRIPT)
assert SPEC is not None
assert SPEC.loader is not None
split_second_annotator_packet = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(split_second_annotator_packet)


def write_tsv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def test_build_batches_balances_label_source_groups() -> None:
    blind_rows = [
        {"issue_id": f"r{i}", "source_packet": "S1"} for i in range(6)
    ] + [
        {"issue_id": f"f{i}", "source_packet": "S2"} for i in range(6)
    ]
    key_rows = [
        {"issue_id": f"r{i}", "first_pass_label": "regressed"} for i in range(6)
    ] + [
        {"issue_id": f"f{i}", "first_pass_label": "fixed"} for i in range(6)
    ]
    batches = split_second_annotator_packet.build_batches(blind_rows, key_rows, 3)

    assert len(batches) == 3
    assert all(len(batch) == 4 for batch in batches)

    key_by_id = {row["issue_id"]: row for row in key_rows}
    summaries = [split_second_annotator_packet.summarize_batch(batch, key_by_id) for batch in batches]
    for summary in summaries:
        assert summary["label_distribution"]["regressed"] == 2
        assert summary["label_distribution"]["fixed"] == 2

