from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "export_oral_evidence_panel.py"
SPEC = importlib.util.spec_from_file_location("export_oral_evidence_panel", SCRIPT)
assert SPEC is not None
assert SPEC.loader is not None
export_oral_evidence_panel = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(export_oral_evidence_panel)


def test_build_panel_returns_expected_axes() -> None:
    rows = export_oral_evidence_panel.build_panel()
    axes = {row["axis"] for row in rows}
    assert "In-domain gain" in axes
    assert "Accuracy trap" in axes
    assert "IAA boundary-packet reliability" in axes
    assert "Readiness gate" in axes
    assert len(rows) >= 7
