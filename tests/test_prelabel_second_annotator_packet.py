from __future__ import annotations

import csv
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "prelabel_second_annotator_packet.py"
SPEC = importlib.util.spec_from_file_location("prelabel_second_annotator_packet", SCRIPT)
assert SPEC is not None
assert SPEC.loader is not None
prelabel_second_annotator_packet = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(prelabel_second_annotator_packet)


def write_tsv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def test_prelabel_fills_blank_human_fields(tmp_path: Path) -> None:
    blind = tmp_path / "blind.tsv"
    key = tmp_path / "key.tsv"
    report_json = tmp_path / "report.json"
    report_md = tmp_path / "report.md"

    blind_fields = ["issue_id", "human_label", "human_confidence", "evidence_span", "notes"]
    key_fields = [
        "issue_id",
        "assistant_label",
        "first_pass_label",
        "first_pass_confidence",
        "first_pass_evidence_span",
        "assistant_evidence_span",
    ]

    write_tsv(
        blind,
        [{"issue_id": "i1", "human_label": "", "human_confidence": "", "evidence_span": "", "notes": ""}],
        blind_fields,
    )
    write_tsv(
        key,
        [
            {
                "issue_id": "i1",
                "assistant_label": "unresolved",
                "first_pass_label": "unresolved",
                "first_pass_confidence": "4",
                "first_pass_evidence_span": "evidence text",
                "assistant_evidence_span": "",
            }
        ],
        key_fields,
    )

    report = prelabel_second_annotator_packet.prelabel(
        blind_sheet=blind,
        key_sheet=key,
        report_json=report_json,
        report_md=report_md,
        label_source="assistant_first",
        default_confidence="3",
        allow_overwrite=False,
        write=True,
    )

    assert report["status"] == "ok"
    assert report["prefilled_rows"] == 1
    rows = read_tsv(blind)
    assert rows[0]["human_label"] == "unresolved"
    assert rows[0]["human_confidence"] == "4"
    assert rows[0]["evidence_span"] == "evidence text"
    assert "AI prelabel draft" in rows[0]["notes"]


def test_prelabel_skips_existing_without_overwrite(tmp_path: Path) -> None:
    blind = tmp_path / "blind.tsv"
    key = tmp_path / "key.tsv"
    report_json = tmp_path / "report.json"
    report_md = tmp_path / "report.md"

    blind_fields = ["issue_id", "human_label", "human_confidence", "evidence_span", "notes"]
    key_fields = ["issue_id", "assistant_label", "first_pass_label"]

    write_tsv(
        blind,
        [
            {
                "issue_id": "i1",
                "human_label": "fixed",
                "human_confidence": "4",
                "evidence_span": "old",
                "notes": "existing",
            }
        ],
        blind_fields,
    )
    write_tsv(
        key,
        [{"issue_id": "i1", "assistant_label": "unresolved", "first_pass_label": "unresolved"}],
        key_fields,
    )

    report = prelabel_second_annotator_packet.prelabel(
        blind_sheet=blind,
        key_sheet=key,
        report_json=report_json,
        report_md=report_md,
        label_source="assistant_first",
        default_confidence="3",
        allow_overwrite=False,
        write=True,
    )

    assert report["prefilled_rows"] == 0
    assert report["skipped_existing_rows"] == 1
    rows = read_tsv(blind)
    assert rows[0]["human_label"] == "fixed"
    assert rows[0]["notes"] == "existing"
