from __future__ import annotations

import csv
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "merge_human_validation_batches.py"
SPEC = importlib.util.spec_from_file_location("merge_human_validation_batches", SCRIPT)
assert SPEC is not None
assert SPEC.loader is not None
merge_human_validation_batches = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(merge_human_validation_batches)


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_tsv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def blind_row(issue_id: str, human_label: str = "") -> dict[str, str]:
    return {
        "issue_id": issue_id,
        "paper_title": f"Paper {issue_id}",
        "review_rating": "6",
        "review_confidence": "3",
        "review_excerpt": "Concern.",
        "top_response_excerpt": "Response.",
        "aligned_response_excerpt": "Context.",
        "revision_summary": "Revision.",
        "human_label": human_label,
        "human_confidence": "",
        "evidence_span": "",
        "notes": "",
    }


def test_ingest_batches_writes_merged_copy_without_overwriting_canonical(tmp_path: Path) -> None:
    blind = tmp_path / "blind.tsv"
    queue = tmp_path / "queue.csv"
    batch_dir = tmp_path / "batches"
    output_dir = tmp_path / "ingest"
    fields = [
        "issue_id",
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
    write_tsv(blind, [blind_row("a"), blind_row("b")], fields)
    write_csv(
        queue,
        [
            {"packet": "P1", "issue_id": "a", "blind_sheet": str(blind)},
            {"packet": "P1", "issue_id": "b", "blind_sheet": str(blind)},
        ],
        ["packet", "issue_id", "blind_sheet"],
    )
    write_tsv(
        batch_dir / "batch_01_blind.tsv",
        [
            {
                "batch_rank": "1",
                "global_queue_rank": "1",
                "source_packet": "P1",
                **blind_row("a", human_label="Fixed"),
                "human_confidence": "4",
                "evidence_span": "Added ablation table.",
                "notes": "Resolved.",
            },
            {
                "batch_rank": "2",
                "global_queue_rank": "2",
                "source_packet": "P1",
                **blind_row("b"),
            },
        ],
        ["batch_rank", "global_queue_rank", "source_packet", *fields],
    )

    report = merge_human_validation_batches.ingest_batches(
        queue_path=queue,
        batch_dir=batch_dir,
        output_dir=output_dir,
    )

    assert report["status"] == "ok"
    assert report["completed_batch_rows"] == 1
    assert report["blank_batch_rows"] == 1
    assert read_tsv(blind)[0]["human_label"] == ""
    merged = read_tsv(output_dir / "sheets" / "blind.tsv")
    assert merged[0]["human_label"] == "fixed"
    assert merged[0]["evidence_span"] == "Added ablation table."
    assert report["sheets"][0]["labeled_rows"] == 1


def test_ingest_batches_reports_invalid_labels_and_forbidden_fields(tmp_path: Path) -> None:
    blind = tmp_path / "blind.tsv"
    queue = tmp_path / "queue.csv"
    batch_dir = tmp_path / "batches"
    fields = [
        "issue_id",
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
    write_tsv(blind, [blind_row("a")], fields)
    write_csv(
        queue,
        [{"packet": "P1", "issue_id": "a", "blind_sheet": str(blind)}],
        ["packet", "issue_id", "blind_sheet"],
    )
    write_tsv(
        batch_dir / "batch_01_blind.tsv",
        [
            {
                "batch_rank": "1",
                "global_queue_rank": "1",
                "source_packet": "P1",
                **blind_row("a", human_label="done"),
                "human_confidence": "4",
                "evidence_span": "Evidence.",
                "notes": "Notes.",
                "assistant_label": "fixed",
            }
        ],
        ["batch_rank", "global_queue_rank", "source_packet", *fields, "assistant_label"],
    )

    report = merge_human_validation_batches.ingest_batches(
        queue_path=queue,
        batch_dir=batch_dir,
        output_dir=tmp_path / "ingest",
    )

    assert report["status"] == "error"
    assert report["invalid_label_rows"][0]["human_label"] == "done"
    assert any("forbidden fields" in message for message in report["error_messages"])


def test_ingest_batches_all_done_queue_allows_empty_batch_directory(tmp_path: Path) -> None:
    blind = tmp_path / "blind.tsv"
    queue = tmp_path / "queue.csv"
    batch_dir = tmp_path / "batches"
    batch_dir.mkdir()
    fields = [
        "issue_id",
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
    write_tsv(
        blind,
        [
            {
                **blind_row("a", human_label="fixed"),
                "human_confidence": "4",
                "evidence_span": "Evidence.",
                "notes": "Done.",
            }
        ],
        fields,
    )
    write_csv(
        queue,
        [
            {
                "queue_rank": "1",
                "packet": "P1",
                "status": "done",
                "issue_id": "a",
                "human_label_present": "true",
                "blind_sheet": str(blind),
            }
        ],
        ["queue_rank", "packet", "status", "issue_id", "human_label_present", "blind_sheet"],
    )

    report = merge_human_validation_batches.ingest_batches(
        queue_path=queue,
        batch_dir=batch_dir,
        output_dir=tmp_path / "ingest",
    )

    assert report["status"] == "ok"
    assert report["batch_rows"] == 0
    assert report["error_count"] == 0
    assert report["sheets"][0]["labeled_rows"] == 1
