from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "export_human_validation_queue.py"
SPEC = importlib.util.spec_from_file_location("export_human_validation_queue", SCRIPT)
assert SPEC is not None
assert SPEC.loader is not None
export_human_validation_queue = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(export_human_validation_queue)


def write_tsv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def make_packet(tmp_path: Path, name: str = "packet"):
    blind = tmp_path / "blind.tsv"
    key = tmp_path / "key.tsv"
    audit = tmp_path / "audit.tsv"
    metrics = tmp_path / "pending_metrics.json"
    packet = tmp_path / "packet.html"
    packet.write_text("<html></html>", encoding="utf-8")
    write_tsv(
        blind,
        [
            {
                "issue_id": "low",
                "paper_title": "Low",
                "review_rating": "6",
                "review_confidence": "3",
                "human_label": "",
            },
            {
                "issue_id": "high",
                "paper_title": "High",
                "review_rating": "8",
                "review_confidence": "4",
                "human_label": "",
            },
            {
                "issue_id": "done",
                "paper_title": "Done",
                "review_rating": "7",
                "review_confidence": "3",
                "human_label": "fixed",
            },
        ],
        ["issue_id", "paper_title", "review_rating", "review_confidence", "human_label"],
    )
    write_tsv(
        key,
        [
            {"issue_id": "low", "assistant_label": "partially_fixed", "suggested_label": "partially_fixed"},
            {"issue_id": "high", "assistant_label": "unresolved", "suggested_label": "unresolved"},
            {"issue_id": "done", "assistant_label": "fixed", "suggested_label": "fixed"},
        ],
        ["issue_id", "assistant_label", "suggested_label"],
    )
    write_tsv(
        audit,
        [
            {
                "issue_id": "low",
                "audit_rank": "2",
                "audit_score": "10.0",
                "priority_score": "1.0",
                "audit_bucket": "label_stratum",
                "assistant_label": "partially_fixed",
            },
            {
                "issue_id": "high",
                "audit_rank": "1",
                "audit_score": "20.0",
                "priority_score": "2.0",
                "audit_bucket": "minority_unresolved",
                "assistant_label": "unresolved",
            },
            {
                "issue_id": "done",
                "audit_rank": "3",
                "audit_score": "30.0",
                "priority_score": "3.0",
                "audit_bucket": "minority_regressed",
                "assistant_label": "fixed",
            },
        ],
        [
            "issue_id",
            "audit_rank",
            "audit_score",
            "priority_score",
            "audit_bucket",
            "assistant_label",
        ],
    )
    metrics.write_text(
        json.dumps({"rows": 3, "labeled_rows": 1, "unlabeled_rows": 2}),
        encoding="utf-8",
    )
    return export_human_validation_queue.PacketSpec(
        name=name,
        blind=blind,
        key=key,
        audit=audit,
        pending_metrics=metrics,
        blind_packet=packet,
    )


def test_build_queue_prioritizes_pending_high_risk_rows(tmp_path: Path) -> None:
    packet = make_packet(tmp_path)

    rows = export_human_validation_queue.build_queue([packet])

    assert [row["issue_id"] for row in rows] == ["high", "low", "done"]
    assert [row["queue_rank"] for row in rows] == ["1", "2", "3"]
    assert rows[0]["priority_reason"] == "minority_unresolved; assistant=unresolved; audit_score=20.000"
    assert rows[2]["status"] == "done"


def test_write_outputs_include_boundary_and_counts(tmp_path: Path) -> None:
    packet = make_packet(tmp_path)
    rows = export_human_validation_queue.build_queue([packet])
    summaries = export_human_validation_queue.packet_summary([packet])
    csv_path = tmp_path / "queue.csv"
    md_path = tmp_path / "queue.md"

    export_human_validation_queue.write_csv(csv_path, rows)
    export_human_validation_queue.write_markdown(md_path, rows, summaries)

    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        csv_rows = list(csv.DictReader(handle))
    assert len(csv_rows) == 3
    assert csv_rows[0]["issue_id"] == "high"

    markdown = md_path.read_text(encoding="utf-8")
    assert "validation claims must come from completed blind sheets" in markdown
    assert "Total rows: `3`" in markdown
    assert "Unlabeled rows: `2`" in markdown
