from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "export_split_label_coverage.py"
SPEC = importlib.util.spec_from_file_location("export_split_label_coverage", SCRIPT)
assert SPEC is not None
assert SPEC.loader is not None
export_split_label_coverage = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(export_split_label_coverage)


def test_build_rows_captures_known_missing_labels() -> None:
    rows = export_split_label_coverage.build_rows()
    by_split = {row["split"]: row for row in rows}

    neurips = by_split["NeurIPS 2024 limit100"]
    assert neurips["fixed"] == 0
    assert neurips["regressed"] == 0
    assert "fixed" in neurips["missing_labels"]
    assert "regressed" in neurips["missing_labels"]

    random80 = by_split["ICLR 2023 random80"]
    assert random80["sample_design"] == "random_stratified"
