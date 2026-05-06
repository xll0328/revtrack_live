from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_iaa_second_annotator_pipeline.py"
SPEC = importlib.util.spec_from_file_location("run_iaa_second_annotator_pipeline", SCRIPT)
assert SPEC is not None
assert SPEC.loader is not None
pipeline = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pipeline)


def test_merge_batch_annotations_updates_rows_and_counts() -> None:
    blind_rows = [
        {"issue_id": "a", "human_label": "", "human_confidence": "", "evidence_span": "", "notes": ""},
        {"issue_id": "b", "human_label": "", "human_confidence": "", "evidence_span": "", "notes": ""},
        {"issue_id": "c", "human_label": "", "human_confidence": "", "evidence_span": "", "notes": ""},
    ]
    batch_entries = [
        (
            "batch1.tsv",
            [
                {
                    "issue_id": "a",
                    "human_label": "fixed",
                    "human_confidence": "0.8",
                    "evidence_span": "span-a",
                    "notes": "note-a",
                },
                {
                    "issue_id": "b",
                    "human_label": "",
                    "human_confidence": "",
                    "evidence_span": "",
                    "notes": "",
                },
            ],
        ),
        (
            "batch2.tsv",
            [
                {
                    "issue_id": "c",
                    "human_label": "unresolved",
                    "human_confidence": "0.7",
                    "evidence_span": "span-c",
                    "notes": "note-c",
                }
            ],
        ),
    ]

    merged_rows, summary = pipeline.merge_batch_annotations(
        blind_rows=blind_rows,
        batch_entries=batch_entries,
    )

    merged_by_id = {row["issue_id"]: row for row in merged_rows}
    assert merged_by_id["a"]["human_label"] == "fixed"
    assert merged_by_id["c"]["human_label"] == "unresolved"
    assert merged_by_id["b"]["human_label"] == ""
    assert summary["blind_rows"] == 3
    assert summary["labeled_rows"] == 2
    assert summary["unlabeled_rows"] == 1
    assert summary["missing_batch_issue_rows"] == 0


def test_merge_batch_annotations_conflicting_duplicate_raises() -> None:
    blind_rows = [
        {"issue_id": "a", "human_label": "", "human_confidence": "", "evidence_span": "", "notes": ""},
    ]
    batch_entries = [
        (
            "batch1.tsv",
            [
                {
                    "issue_id": "a",
                    "human_label": "fixed",
                    "human_confidence": "0.8",
                    "evidence_span": "span-a",
                    "notes": "note-a",
                }
            ],
        ),
        (
            "batch2.tsv",
            [
                {
                    "issue_id": "a",
                    "human_label": "unresolved",
                    "human_confidence": "0.9",
                    "evidence_span": "span-a2",
                    "notes": "note-a2",
                }
            ],
        ),
    ]

    with pytest.raises(ValueError, match="conflicting annotations"):
        pipeline.merge_batch_annotations(blind_rows=blind_rows, batch_entries=batch_entries)
