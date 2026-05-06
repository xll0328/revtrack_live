from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "export_active_frontier_failure_taxonomy.py"
SPEC = importlib.util.spec_from_file_location("export_active_frontier_failure_taxonomy", SCRIPT)
assert SPEC is not None
assert SPEC.loader is not None
export_taxonomy = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(export_taxonomy)


def test_active_frontier_taxonomy_groups_transfer_errors() -> None:
    label_rows = [
        {
            "issue_id": "r1",
            "paper_title": "Paper R",
            "assistant_label": "regressed",
            "evidence_span": "Revision introduces a weaker evaluation.",
            "review_excerpt": "Need reliable evaluation.",
        },
        {
            "issue_id": "u1",
            "paper_title": "Paper U",
            "assistant_label": "unresolved",
            "evidence_span": "Response acknowledges the limitation.",
            "review_excerpt": "Need broader baselines.",
        },
    ]
    details_by_model = {
        "structured": [
            {
                "id": "r1",
                "paper_title": "Paper R",
                "gold_label": "regressed",
                "predicted_label": "fixed",
            },
            {
                "id": "u1",
                "paper_title": "Paper U",
                "gold_label": "unresolved",
                "predicted_label": "partially_fixed",
            },
        ]
    }

    rows = export_taxonomy.build_rows(
        dataset_name="NeurIPS 2024 limit100",
        label_rows=label_rows,
        details_by_model=details_by_model,
        label_field="assistant_label",
        validation_status="provisional_assistant_adjudication_not_human_validation",
    )

    by_mode = {row["failure_mode"]: row for row in rows}
    assert by_mode["regression_blindness"]["support_count"] == "1"
    assert by_mode["over_crediting_unresolved"]["gold_label"] == "unresolved"
    assert by_mode["over_crediting_unresolved"]["label_consistency_note"] == "label_sheet=unresolved"
