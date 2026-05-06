from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "export_modernbert_multiseed_probe.py"
SPEC = importlib.util.spec_from_file_location("export_modernbert_multiseed_probe", SCRIPT)
assert SPEC is not None
assert SPEC.loader is not None
export_modernbert_multiseed_probe = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(export_modernbert_multiseed_probe)


def test_aggregate_computes_mean_std(tmp_path: Path) -> None:
    split = "iclr2024_clean_dev_v7"
    seed_dirs = []
    values = [0.5, 0.6, 0.7]
    for idx, macro_f1 in enumerate(values):
        seed_dir = tmp_path / f"seed{idx}"
        seed_dir.mkdir(parents=True, exist_ok=True)
        payload = [
            {
                "split": split,
                "rows": 100.0,
                "accuracy": 0.8,
                "macro_f1": macro_f1,
                "fixed_f1": 0.4,
                "partially_fixed_f1": 0.5,
                "unresolved_f1": 0.3,
                "regressed_f1": 0.0,
            }
        ]
        (seed_dir / "metrics_summary.json").write_text(json.dumps(payload), encoding="utf-8")
        seed_dirs.append(seed_dir)

    rows = export_modernbert_multiseed_probe.aggregate(seed_dirs)
    assert len(rows) == 1
    row = rows[0]
    assert row["split"] == split
    assert abs(float(row["macro_f1_mean"]) - 0.6) < 1e-9
    assert float(row["macro_f1_std"]) > 0
