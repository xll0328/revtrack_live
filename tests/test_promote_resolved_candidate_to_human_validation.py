from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "promote_resolved_candidate_to_human_validation.py"
SPEC = importlib.util.spec_from_file_location("promote_resolved_candidate_to_human_validation", SCRIPT)
assert SPEC is not None
assert SPEC.loader is not None
promoter = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(promoter)


RESOLVED_FIELDS = [
    "issue_id",
    "paper_title",
    "draft_label",
    "resolved_label",
    "resolved_confidence",
    "resolution_action",
    "resolution_reason",
    "review_required",
    "resolution_provenance",
    "resolved_evidence_span",
]

BLIND_FIELDS = [
    "issue_id",
    "paper_title",
    "human_label",
    "human_confidence",
    "evidence_span",
    "notes",
]


def write_tsv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def resolved_row(issue_id: str, label: str = "partially_fixed") -> dict[str, str]:
    return {
        "issue_id": issue_id,
        "paper_title": f"Paper {issue_id}",
        "draft_label": "unresolved",
        "resolved_label": label,
        "resolved_confidence": "3",
        "resolution_action": "upgrade_weak_unresolved_to_partial",
        "resolution_reason": "Concrete fix evidence with conservative partial label.",
        "review_required": "true",
        "resolution_provenance": "assistant_resolved_candidate_not_human_validation",
        "resolved_evidence_span": "The response adds a directly relevant experiment.",
    }


def blind_row(issue_id: str, label: str = "") -> dict[str, str]:
    return {
        "issue_id": issue_id,
        "paper_title": f"Paper {issue_id}",
        "human_label": label,
        "human_confidence": "",
        "evidence_span": "",
        "notes": "",
    }


def test_dry_run_reports_promotable_rows_without_writing(tmp_path: Path) -> None:
    resolved = tmp_path / "resolved.tsv"
    blind = tmp_path / "blind.tsv"
    report = tmp_path / "report.json"
    write_tsv(resolved, [resolved_row("a")], RESOLVED_FIELDS)
    write_tsv(blind, [blind_row("a")], BLIND_FIELDS)

    result = promoter.promote(
        resolved_candidate_path=resolved,
        blind_sheet_path=blind,
        report_json=report,
        write=False,
    )

    rows = read_tsv(blind)
    payload = json.loads(report.read_text(encoding="utf-8"))
    assert result["status"] == "ok"
    assert payload["promotable_rows"] == 1
    assert payload["promoted_rows"] == 0
    assert rows[0]["human_label"] == ""


def test_write_requires_confirmation_note(tmp_path: Path) -> None:
    resolved = tmp_path / "resolved.tsv"
    blind = tmp_path / "blind.tsv"
    report = tmp_path / "report.json"
    write_tsv(resolved, [resolved_row("a")], RESOLVED_FIELDS)
    write_tsv(blind, [blind_row("a")], BLIND_FIELDS)

    result = promoter.promote(
        resolved_candidate_path=resolved,
        blind_sheet_path=blind,
        report_json=report,
        write=True,
    )

    assert result["status"] == "error"
    assert any("--confirmation-note is required" in error for error in result["errors"])
    assert read_tsv(blind)[0]["human_label"] == ""


def test_promotes_user_confirmed_resolved_candidate(tmp_path: Path) -> None:
    resolved = tmp_path / "resolved.tsv"
    blind = tmp_path / "blind.tsv"
    report = tmp_path / "report.json"
    write_tsv(resolved, [resolved_row("a")], RESOLVED_FIELDS)
    write_tsv(blind, [blind_row("a")], BLIND_FIELDS)

    result = promoter.promote(
        resolved_candidate_path=resolved,
        blind_sheet_path=blind,
        report_json=report,
        confirmation_note="User confirmed the resolved candidate sheet on 2026-04-27.",
        write=True,
    )

    rows = read_tsv(blind)
    assert result["status"] == "ok"
    assert result["promoted_rows"] == 1
    assert rows[0]["human_label"] == "partially_fixed"
    assert rows[0]["human_confidence"] == "3"
    assert rows[0]["evidence_span"] == "The response adds a directly relevant experiment."
    assert "not an independent two-annotator IAA pass" in rows[0]["notes"]


def test_refuses_unexpected_provenance(tmp_path: Path) -> None:
    resolved = tmp_path / "resolved.tsv"
    blind = tmp_path / "blind.tsv"
    report = tmp_path / "report.json"
    bad = resolved_row("a")
    bad["resolution_provenance"] = "standard_human_validation"
    write_tsv(resolved, [bad], RESOLVED_FIELDS)
    write_tsv(blind, [blind_row("a")], BLIND_FIELDS)

    result = promoter.promote(
        resolved_candidate_path=resolved,
        blind_sheet_path=blind,
        report_json=report,
        confirmation_note="User confirmed the resolved candidate sheet on 2026-04-27.",
        write=True,
    )

    assert result["status"] == "error"
    assert any("unexpected resolution_provenance" in error for error in result["errors"])
    assert read_tsv(blind)[0]["human_label"] == ""
