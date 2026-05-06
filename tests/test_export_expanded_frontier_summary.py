from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "export_expanded_frontier_summary.py"
SPEC = importlib.util.spec_from_file_location("export_expanded_frontier_summary", SCRIPT)
assert SPEC is not None
assert SPEC.loader is not None
summary = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(summary)


def test_build_summary_marks_frontier_as_not_standard_validated_without_metrics() -> None:
    rows = summary.build_summary_rows(
        candidates=[
            {"issue_id": "a", "submission_id": "s1"},
            {"issue_id": "b", "submission_id": "s2"},
        ],
        gate={
            "ok": True,
            "rows": 2,
            "complete_rate": 1.0,
            "disagreement": {"disagreement_rows": 1, "high_disagreement_rows": 1},
        },
        frontier_rows=[
            {"issue_id": "a", "suggested_label": "unresolved", "structured_label": "fixed"},
            {"issue_id": "b", "suggested_label": "fixed", "structured_label": "fixed"},
        ],
        packet_audit={
            "ok": True,
            "blind_rows": 2,
            "audit_rows": 2,
            "assistant_distribution": {"fixed": 1, "unresolved": 1},
        },
        predictions={
            "structured": [
                {"id": "a", "predicted_label": "fixed"},
                {"id": "b", "predicted_label": "fixed"},
            ]
        },
    )

    by_metric = {row["metric"]: row for row in rows}
    assert by_metric["submissions"]["value"] == "2"
    assert by_metric["quality_gate_ok"]["value"] == "True"
    assert by_metric["claim_status"]["value"] == "construction_ready"
    assert by_metric["claim_boundary"]["value"] == "not_standard_validated"
    assert "unresolved=1" in by_metric["hidden_assistant_distribution"]["value"]


def test_build_summary_marks_standard_labeled_active_frontier() -> None:
    rows = summary.build_summary_rows(
        candidates=[
            {"issue_id": "a", "submission_id": "s1"},
            {"issue_id": "b", "submission_id": "s2"},
        ],
        gate={
            "ok": True,
            "rows": 2,
            "complete_rate": 1.0,
            "disagreement": {"disagreement_rows": 1, "high_disagreement_rows": 1},
        },
        frontier_rows=[
            {"issue_id": "a", "suggested_label": "unresolved", "structured_label": "fixed"},
            {"issue_id": "b", "suggested_label": "fixed", "structured_label": "fixed"},
        ],
        packet_audit={
            "ok": True,
            "blind_rows": 2,
            "audit_rows": 2,
            "assistant_distribution": {"fixed": 1, "unresolved": 1},
        },
        predictions={
            "structured": [
                {"id": "a", "predicted_label": "fixed"},
                {"id": "b", "predicted_label": "fixed"},
            ]
        },
        standard_metrics={
            "labeled_rows": 2,
            "unlabeled_rows": 0,
            "invalid_rows": [],
            "human_distribution": {"fixed": 1, "unresolved": 1},
            "agreement": 1.0,
        },
    )

    by_metric = {row["metric"]: row for row in rows}
    assert by_metric["claim_status"]["value"] == "standard_labeled_active_frontier"
    assert by_metric["claim_boundary"]["value"] == "active_frontier_not_iaa_or_prevalence"
    assert by_metric["labeled_rows"]["value"] == "2"
    assert by_metric["agreement_against_promoted_key"]["value"] == "1.000"
