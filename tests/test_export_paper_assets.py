from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "export_paper_assets.py"
SPEC = importlib.util.spec_from_file_location("export_paper_assets", SCRIPT)
assert SPEC is not None
assert SPEC.loader is not None
export_paper_assets = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(export_paper_assets)


def test_constant_prediction_summary_exposes_accuracy_trap() -> None:
    labels = ["partially_fixed"] * 16 + ["fixed"] * 5

    summary = export_paper_assets.constant_prediction_summary(labels, "partially_fixed")

    assert summary["accuracy"] == 16 / 21
    assert summary["per_label"]["fixed"]["f1"] == 0
    assert round(summary["macro_f1"], 12) == round((32 / 37) / 4, 12)


def test_majority_label_uses_label_order_for_ties() -> None:
    labels = ["fixed", "partially_fixed"]

    assert export_paper_assets.majority_label(labels) == "fixed"


def test_claim_row_preserves_claim_fields() -> None:
    row = export_paper_assets.claim_row(
        claim_id="C_test",
        status="ready",
        proposed_claim="A claim.",
        support_summary="Evidence.",
        risk_or_counterevidence="Risk.",
        required_next_step="Next.",
        primary_artifacts="artifact.csv",
    )

    assert row["claim_id"] == "C_test"
    assert row["status"] == "ready"
    assert row["primary_artifacts"] == "artifact.csv"
