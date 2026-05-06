from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "export_oral_casebook.py"
SPEC = importlib.util.spec_from_file_location("export_oral_casebook", SCRIPT)
assert SPEC is not None
assert SPEC.loader is not None
export_oral_casebook = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(export_oral_casebook)


def test_build_casebook_rows_keeps_priority_modes() -> None:
    sample = [
        {"failure_mode": "over_crediting_unresolved", "issue_id": "b", "source_split": "s2"},
        {"failure_mode": "stale_criticism", "issue_id": "a", "source_split": "s1"},
        {"failure_mode": "partial_vs_fixed_boundary", "issue_id": "c", "source_split": "s3"},
    ]
    rows = export_oral_casebook.build_casebook_rows(sample)
    assert rows[0]["failure_mode"] == "stale_criticism"
    assert any(row["failure_mode"] == "over_crediting_unresolved" for row in rows)
    assert any(row["failure_mode"] == "partial_vs_fixed_boundary" for row in rows)

