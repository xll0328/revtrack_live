from __future__ import annotations

import csv
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "export_active_frontier_standard_transfer_metrics.py"
SPEC = importlib.util.spec_from_file_location("export_active_frontier_standard_transfer_metrics", SCRIPT)
assert SPEC is not None
assert SPEC.loader is not None
export_standard = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(export_standard)


def test_examples_from_standard_rows_use_configurable_provenance() -> None:
    rows = [
        {
            "issue_id": "a",
            "paper_title": "Paper A",
            "review_excerpt": "Need ablation.",
            "aligned_response_excerpt": "We added an ablation.",
            "revision_summary": "Added ablation.",
            "human_label": "fixed",
            "human_confidence": "4",
            "evidence_span": "We added an ablation.",
            "notes": "user confirmed",
        }
    ]

    examples = export_standard.examples_from_standard_rows(
        dataset_name="NeurIPS 2024 limit100",
        human_rows=rows,
        candidate_rows=[{"issue_id": "a", "venue": "NeurIPS 2024"}],
        validation_status="standard_single_user_confirmed_neurips2024",
    )

    assert len(examples) == 1
    assert examples[0].gold_label == "fixed"
    assert examples[0].metadata["dataset_name"] == "NeurIPS 2024 limit100"
    assert examples[0].metadata["provenance"] == "standard_single_user_confirmed_neurips2024"


def test_examples_from_standard_rows_reject_missing_evidence() -> None:
    rows = [
        {
            "issue_id": "a",
            "paper_title": "Paper A",
            "human_label": "fixed",
            "human_confidence": "4",
            "evidence_span": "",
        }
    ]

    try:
        export_standard.examples_from_standard_rows(
            dataset_name="frontier",
            human_rows=rows,
            candidate_rows=[{"issue_id": "a"}],
        )
    except ValueError as exc:
        assert "missing evidence_span rows" in str(exc)
    else:
        raise AssertionError("missing evidence_span should fail")


def write_tsv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)
