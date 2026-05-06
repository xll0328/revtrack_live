from __future__ import annotations

import csv
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "export_human_validation_batches.py"
SPEC = importlib.util.spec_from_file_location("export_human_validation_batches", SCRIPT)
assert SPEC is not None
assert SPEC.loader is not None
export_human_validation_batches = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(export_human_validation_batches)


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_tsv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def test_export_batches_splits_pending_rows_and_omits_queue_labels(tmp_path: Path) -> None:
    blind = tmp_path / "blind.tsv"
    queue = tmp_path / "queue.csv"
    out = tmp_path / "batches"
    write_tsv(
        blind,
        [
            {
                "issue_id": "a",
                "paper_title": "Paper A",
                "review_rating": "6",
                "review_confidence": "3",
                "review_excerpt": "Need ablation.",
                "top_response_excerpt": "We added Table 2.",
                "aligned_response_excerpt": "Context A.",
                "revision_summary": "Added experiments.",
                "human_label": "",
                "human_confidence": "",
                "evidence_span": "",
                "notes": "",
            },
            {
                "issue_id": "b",
                "paper_title": "Paper B",
                "review_rating": "7",
                "review_confidence": "4",
                "review_excerpt": "Need clarity.",
                "top_response_excerpt": "We rewrote Section 3.",
                "aligned_response_excerpt": "Context B.",
                "revision_summary": "Rewrote text.",
                "human_label": "",
                "human_confidence": "",
                "evidence_span": "",
                "notes": "",
            },
            {
                "issue_id": "c",
                "paper_title": "Paper C",
                "review_rating": "8",
                "review_confidence": "5",
                "review_excerpt": "Need proof.",
                "top_response_excerpt": "Proof is unchanged.",
                "aligned_response_excerpt": "Context C.",
                "revision_summary": "No proof change.",
                "human_label": "fixed",
                "human_confidence": "5",
                "evidence_span": "done",
                "notes": "complete",
            },
        ],
        export_human_validation_batches.BLIND_FIELDS,
    )
    write_csv(
        queue,
        [
            {
                "queue_rank": "1",
                "packet": "P1",
                "status": "pending",
                "issue_id": "a",
                "assistant_label": "secret_label",
                "audit_bucket": "secret_bucket",
                "human_label_present": "false",
                "blind_sheet": str(blind),
            },
            {
                "queue_rank": "2",
                "packet": "P1",
                "status": "pending",
                "issue_id": "b",
                "assistant_label": "secret_label",
                "audit_bucket": "secret_bucket",
                "human_label_present": "false",
                "blind_sheet": str(blind),
            },
            {
                "queue_rank": "3",
                "packet": "P1",
                "status": "done",
                "issue_id": "c",
                "assistant_label": "secret_label",
                "audit_bucket": "secret_bucket",
                "human_label_present": "true",
                "blind_sheet": str(blind),
            },
        ],
        [
            "queue_rank",
            "packet",
            "status",
            "issue_id",
            "assistant_label",
            "audit_bucket",
            "human_label_present",
            "blind_sheet",
        ],
    )

    manifest = export_human_validation_batches.export_batches(
        queue_path=queue,
        output_dir=out,
        prefix="priority",
        batch_size=1,
    )

    assert [row["batch_id"] for row in manifest] == ["priority_batch_01", "priority_batch_02"]
    first_tsv = out / "priority_batch_01_blind.tsv"
    first_html = out / "priority_batch_01_packet.html"
    with first_tsv.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    assert rows[0]["issue_id"] == "a"
    assert "assistant_label" not in rows[0]
    assert "audit_bucket" not in rows[0]
    assert "secret_label" not in first_html.read_text(encoding="utf-8")
    assert "secret_bucket" not in first_html.read_text(encoding="utf-8")


def test_pending_queue_rows_sorts_by_numeric_queue_rank() -> None:
    rows = export_human_validation_batches.pending_queue_rows(
        [
            {"queue_rank": "10", "status": "pending", "human_label_present": "false"},
            {"queue_rank": "2", "status": "pending", "human_label_present": "false"},
            {"queue_rank": "1", "status": "done", "human_label_present": "true"},
        ]
    )

    assert [row["queue_rank"] for row in rows] == ["2", "10"]


def test_export_batches_removes_stale_generated_batch_files(tmp_path: Path) -> None:
    blind = tmp_path / "blind.tsv"
    queue = tmp_path / "queue.csv"
    out = tmp_path / "batches"
    out.mkdir()
    stale_tsv = out / "priority_batch_99_blind.tsv"
    stale_html = out / "priority_batch_99_packet.html"
    unrelated = out / "other_batch_99_blind.tsv"
    stale_tsv.write_text("stale", encoding="utf-8")
    stale_html.write_text("stale", encoding="utf-8")
    unrelated.write_text("keep", encoding="utf-8")
    write_tsv(
        blind,
        [
            {
                "issue_id": "a",
                "paper_title": "Paper A",
                "review_rating": "6",
                "review_confidence": "3",
                "review_excerpt": "Need ablation.",
                "top_response_excerpt": "We added Table 2.",
                "aligned_response_excerpt": "Context A.",
                "revision_summary": "Added experiments.",
                "human_label": "",
                "human_confidence": "",
                "evidence_span": "",
                "notes": "",
            }
        ],
        export_human_validation_batches.BLIND_FIELDS,
    )
    write_csv(
        queue,
        [
            {
                "queue_rank": "1",
                "packet": "P1",
                "status": "pending",
                "issue_id": "a",
                "human_label_present": "false",
                "blind_sheet": str(blind),
            }
        ],
        ["queue_rank", "packet", "status", "issue_id", "human_label_present", "blind_sheet"],
    )

    export_human_validation_batches.export_batches(
        queue_path=queue,
        output_dir=out,
        prefix="priority",
        batch_size=10,
    )

    assert not stale_tsv.exists()
    assert not stale_html.exists()
    assert unrelated.exists()
