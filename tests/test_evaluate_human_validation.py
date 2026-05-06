from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "evaluate_human_validation.py"
SPEC = importlib.util.spec_from_file_location("evaluate_human_validation", SCRIPT)
assert SPEC is not None
assert SPEC.loader is not None
evaluate_human_validation = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(evaluate_human_validation)


def test_evaluate_human_validation_agreement_and_mismatches() -> None:
    human_rows = [
        {"issue_id": "a", "human_label": "fixed", "evidence_span": "ok", "notes": ""},
        {"issue_id": "b", "human_label": "unresolved", "evidence_span": "", "notes": "still vague"},
        {"issue_id": "c", "human_label": "", "evidence_span": "", "notes": ""},
    ]
    key_rows = [
        {"issue_id": "a", "assistant_label": "fixed", "audit_bucket": "label_stratum"},
        {"issue_id": "b", "assistant_label": "partially_fixed", "audit_bucket": "structured_error"},
        {"issue_id": "c", "assistant_label": "regressed", "audit_bucket": "minority_regressed"},
    ]

    summary, mismatches = evaluate_human_validation.evaluate(human_rows, key_rows)

    assert summary["rows"] == 3
    assert summary["labeled_rows"] == 2
    assert summary["agreement"] == 0.5
    assert summary["mismatches"] == 1
    assert mismatches[0]["issue_id"] == "b"
    assert summary["confusion_assistant_to_human"]["fixed"]["fixed"] == 1
    assert summary["confusion_assistant_to_human"]["partially_fixed"]["unresolved"] == 1
