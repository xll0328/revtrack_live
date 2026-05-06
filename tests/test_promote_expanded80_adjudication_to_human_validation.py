from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "promote_expanded80_adjudication_to_human_validation.py"
SPEC = importlib.util.spec_from_file_location("promote_expanded80", SCRIPT)
assert SPEC is not None
assert SPEC.loader is not None
promote_expanded80 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(promote_expanded80)


def write_tsv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def test_promotes_user_confirmed_expanded80_rows(tmp_path: Path) -> None:
    adjudication = tmp_path / "adjudication.tsv"
    blind = tmp_path / "blind.tsv"
    report = tmp_path / "report.json"
    write_tsv(
        adjudication,
        [
            {
                "issue_id": "a",
                "assistant_label": "fixed",
                "assistant_confidence": "medium",
                "evidence_source": "aligned_response_excerpt",
                "evidence_span": "The revision adds a new ablation.",
                "notes": '{"audit_bucket": "minority_fixed"}',
            }
        ],
        ["issue_id", "assistant_label", "assistant_confidence", "evidence_source", "evidence_span", "notes"],
    )
    write_tsv(
        blind,
        [{"issue_id": "a", "paper_title": "Paper A", "human_label": "", "human_confidence": "", "evidence_span": "", "notes": ""}],
        ["issue_id", "paper_title", "human_label", "human_confidence", "evidence_span", "notes"],
    )

    result = promote_expanded80.promote(
        adjudication_path=adjudication,
        blind_sheet_path=blind,
        report_json=report,
        write=True,
    )

    rows = read_tsv(blind)
    payload = json.loads(report.read_text(encoding="utf-8"))
    assert result["status"] == "ok"
    assert payload["promoted_rows"] == 1
    assert rows[0]["human_label"] == "fixed"
    assert rows[0]["human_confidence"] == "4"
    assert rows[0]["evidence_span"] == "The revision adds a new ablation."
    assert "User-confirmed standard expanded80 validation" in rows[0]["notes"]
