from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "promote_ai_signoff_to_human_validation.py"
SPEC = importlib.util.spec_from_file_location("promote_ai_signoff_to_human_validation", SCRIPT)
assert SPEC is not None
assert SPEC.loader is not None
promote_ai_signoff_to_human_validation = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(promote_ai_signoff_to_human_validation)


BLIND_FIELDS = [
    "issue_id",
    "paper_title",
    "review_rating",
    "review_confidence",
    "review_excerpt",
    "top_response_excerpt",
    "aligned_response_excerpt",
    "revision_summary",
    "human_label",
    "human_confidence",
    "evidence_span",
    "notes",
]

SIGNOFF_FIELDS = [
    "packet",
    "issue_id",
    "assistant_label",
    "assistant_evidence_span",
    "assistant_notes",
    "reviewer_decision",
    "reviewer_final_label",
    "reviewer_confidence",
    "reviewer_evidence_span",
    "reviewer_notes",
]


def write_tsv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_clean_audit(path: Path) -> None:
    path.write_text(
        json.dumps({"overall_status": "pass", "error_count": 0, "warning_count": 0}) + "\n",
        encoding="utf-8",
    )


def blind_row(issue_id: str, human_label: str = "") -> dict[str, str]:
    return {
        "issue_id": issue_id,
        "paper_title": f"Paper {issue_id}",
        "review_rating": "6",
        "review_confidence": "3",
        "review_excerpt": "Concern.",
        "top_response_excerpt": "Response.",
        "aligned_response_excerpt": "Context.",
        "revision_summary": "Revision.",
        "human_label": human_label,
        "human_confidence": "",
        "evidence_span": "",
        "notes": "",
    }


def test_promotes_user_reviewed_signoff_into_human_validation_sheet(tmp_path: Path) -> None:
    signoff = tmp_path / "signoff.tsv"
    audit = tmp_path / "audit.json"
    blind = tmp_path / "blind.tsv"
    report_path = tmp_path / "report.json"
    write_clean_audit(audit)
    write_tsv(blind, [blind_row("a"), blind_row("b")], BLIND_FIELDS)
    write_tsv(
        signoff,
        [
            {
                "packet": "P1",
                "issue_id": "a",
                "assistant_label": "fixed",
                "assistant_evidence_span": "Added the ablation.",
                "assistant_notes": "Concern addressed.",
                "reviewer_decision": "",
                "reviewer_final_label": "",
                "reviewer_confidence": "",
                "reviewer_evidence_span": "",
                "reviewer_notes": "",
            },
            {
                "packet": "P1",
                "issue_id": "b",
                "assistant_label": "fixed",
                "assistant_evidence_span": "Original evidence.",
                "assistant_notes": "",
                "reviewer_decision": "revise",
                "reviewer_final_label": "partially_fixed",
                "reviewer_confidence": "5",
                "reviewer_evidence_span": "Only the main clarity concern was addressed.",
                "reviewer_notes": "Keep as partial.",
            },
        ],
        SIGNOFF_FIELDS,
    )

    report = promote_ai_signoff_to_human_validation.promote_signoff(
        signoff_path=signoff,
        signoff_audit_path=audit,
        packet_sheets={"P1": blind},
        report_json=report_path,
        write=True,
    )

    rows = read_tsv(blind)
    assert report["status"] == "ok"
    assert report["promoted_rows"] == 2
    assert rows[0]["human_label"] == "fixed"
    assert rows[0]["human_confidence"] == "4"
    assert rows[0]["evidence_span"] == "Added the ablation."
    assert "standard human-validation signoff" in rows[0]["notes"]
    assert rows[1]["human_label"] == "partially_fixed"
    assert rows[1]["human_confidence"] == "5"
    assert rows[1]["evidence_span"] == "Only the main clarity concern was addressed."
    assert json.loads(report_path.read_text(encoding="utf-8"))["write"] is True


def test_refuses_to_promote_when_signoff_audit_is_not_clean(tmp_path: Path) -> None:
    signoff = tmp_path / "signoff.tsv"
    audit = tmp_path / "audit.json"
    blind = tmp_path / "blind.tsv"
    audit.write_text(
        json.dumps({"overall_status": "warning", "error_count": 0, "warning_count": 1}) + "\n",
        encoding="utf-8",
    )
    write_tsv(blind, [blind_row("a")], BLIND_FIELDS)
    write_tsv(
        signoff,
        [
            {
                "packet": "P1",
                "issue_id": "a",
                "assistant_label": "fixed",
                "assistant_evidence_span": "Evidence.",
            }
        ],
        SIGNOFF_FIELDS,
    )

    report = promote_ai_signoff_to_human_validation.promote_signoff(
        signoff_path=signoff,
        signoff_audit_path=audit,
        packet_sheets={"P1": blind},
        report_json=tmp_path / "report.json",
        write=True,
    )

    assert report["status"] == "error"
    assert any("signoff audit has 1 warnings" in message for message in report["errors"])
    assert read_tsv(blind)[0]["human_label"] == ""
