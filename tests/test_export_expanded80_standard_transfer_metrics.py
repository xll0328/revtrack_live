from __future__ import annotations

import csv
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "export_expanded80_standard_transfer_metrics.py"
SPEC = importlib.util.spec_from_file_location("export_expanded80_standard_transfer_metrics", SCRIPT)
assert SPEC is not None
assert SPEC.loader is not None
export_standard = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(export_standard)


def write_tsv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def test_examples_from_human_rows_require_evidence(tmp_path: Path) -> None:
    human = [
        {
            "issue_id": "a",
            "paper_title": "Paper A",
            "review_excerpt": "Need ablation.",
            "aligned_response_excerpt": "We added the ablation.",
            "revision_summary": "Added ablation.",
            "human_label": "fixed",
            "human_confidence": "4",
            "evidence_span": "We added the ablation.",
            "notes": "user confirmed",
        }
    ]

    examples = export_standard.examples_from_human_rows(human_rows=human, candidate_rows=[{"issue_id": "a"}])

    assert len(examples) == 1
    assert examples[0].gold_label == "fixed"
    assert examples[0].metadata["provenance"] == "user_confirmed_standard_expanded80_validation"
