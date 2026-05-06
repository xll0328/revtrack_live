from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_label_evidence.py"
SPEC = importlib.util.spec_from_file_location("audit_label_evidence", SCRIPT)
assert SPEC is not None
assert SPEC.loader is not None
audit_label_evidence = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit_label_evidence)


def test_label_evidence_audit_passes_complete_rows() -> None:
    report = audit_label_evidence.audit_sheet(
        [
            {
                "issue_id": "a",
                "gold_label": "fixed",
                "evidence_span": "Added a new ablation table with all requested settings.",
                "notes": "The requested experiment is directly added.",
            }
        ]
    )

    assert report["ok"] is True
    assert report["label_counts"] == {"fixed": 1}
    assert report["evidence_issue_count"] == 0


def test_label_evidence_audit_flags_missing_and_invalid_fields() -> None:
    report = audit_label_evidence.audit_sheet(
        [
            {
                "issue_id": "a",
                "gold_label": "fixed",
                "evidence_span": "",
                "notes": "clear enough",
            },
            {
                "issue_id": "a",
                "gold_label": "maybe",
                "evidence_span": "tiny",
                "notes": "",
            },
        ]
    )

    assert report["ok"] is False
    assert report["structural_ok"] is False
    assert report["evidence_ok"] is False
    assert report["problem_counts"]["missing_evidence"] == 1
    assert report["problem_counts"]["short_evidence"] == 1
    assert report["problem_counts"]["missing_notes"] == 1
    assert any("duplicate" in error for error in report["structural_errors"])
    assert any("invalid labels" in error for error in report["structural_errors"])
