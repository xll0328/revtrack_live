from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "export_second_annotator_packet.py"
SPEC = importlib.util.spec_from_file_location("export_second_annotator_packet", SCRIPT)
assert SPEC is not None
assert SPEC.loader is not None
export_second_annotator_packet = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(export_second_annotator_packet)


def write_tsv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def make_packet(tmp_path: Path) -> export_second_annotator_packet.PacketSpec:
    blind = tmp_path / "blind.tsv"
    key = tmp_path / "key.tsv"
    audit = tmp_path / "audit.tsv"

    write_tsv(
        blind,
        [
            {"issue_id": "r1", "human_label": "regressed", "paper_title": "R1"},
            {"issue_id": "f1", "human_label": "fixed", "paper_title": "F1"},
            {"issue_id": "u1", "human_label": "unresolved", "paper_title": "U1"},
            {"issue_id": "p1", "human_label": "partially_fixed", "paper_title": "P1"},
            {"issue_id": "f2", "human_label": "fixed", "paper_title": "F2"},
        ],
        ["issue_id", "human_label", "paper_title"],
    )
    write_tsv(
        key,
        [
            {
                "issue_id": "r1",
                "assistant_label": "regressed",
                "suggested_label": "regressed",
                "heuristic_label": "regressed",
                "tfidf_label": "fixed",
                "modernbert_label": "regressed",
            },
            {
                "issue_id": "f1",
                "assistant_label": "fixed",
                "suggested_label": "fixed",
                "heuristic_label": "fixed",
                "tfidf_label": "fixed",
                "modernbert_label": "fixed",
            },
            {
                "issue_id": "u1",
                "assistant_label": "unresolved",
                "suggested_label": "unresolved",
                "heuristic_label": "unresolved",
                "tfidf_label": "partially_fixed",
                "modernbert_label": "unresolved",
            },
            {
                "issue_id": "p1",
                "assistant_label": "partially_fixed",
                "suggested_label": "partially_fixed",
                "heuristic_label": "partially_fixed",
                "tfidf_label": "partially_fixed",
                "modernbert_label": "partially_fixed",
            },
            {
                "issue_id": "f2",
                "assistant_label": "fixed",
                "suggested_label": "fixed",
                "heuristic_label": "fixed",
                "tfidf_label": "unresolved",
                "modernbert_label": "fixed",
            },
        ],
        [
            "issue_id",
            "assistant_label",
            "suggested_label",
            "heuristic_label",
            "tfidf_label",
            "modernbert_label",
        ],
    )
    write_tsv(
        audit,
        [
            {"issue_id": "r1", "audit_bucket": "minority_regressed", "audit_score": "30", "priority_score": "5"},
            {"issue_id": "f1", "audit_bucket": "label_stratum", "audit_score": "12", "priority_score": "1"},
            {"issue_id": "u1", "audit_bucket": "minority_unresolved", "audit_score": "20", "priority_score": "3"},
            {"issue_id": "p1", "audit_bucket": "label_stratum", "audit_score": "5", "priority_score": "1"},
            {"issue_id": "f2", "audit_bucket": "model_disagreement", "audit_score": "15", "priority_score": "3"},
        ],
        ["issue_id", "audit_bucket", "audit_score", "priority_score"],
    )

    return export_second_annotator_packet.PacketSpec(
        name="mock",
        blind=blind,
        key=key,
        audit=audit,
    )


def test_select_candidates_respects_quotas_and_fills_remaining(tmp_path: Path) -> None:
    packet = make_packet(tmp_path)
    candidates = export_second_annotator_packet.build_candidates([packet])

    selected = export_second_annotator_packet.select_candidates(
        candidates,
        sample_size=4,
        label_quotas={
            "regressed": 1,
            "fixed": 1,
            "unresolved": 1,
            "partially_fixed": 0,
        },
    )

    selected_ids = [row["issue_id"] for row in selected]
    assert {"r1", "f1", "u1"}.issubset(set(selected_ids))
    assert len(selected_ids) == 4
    assert "f2" in selected_ids


def test_write_outputs_and_manifest(tmp_path: Path) -> None:
    packet = make_packet(tmp_path)
    candidates = export_second_annotator_packet.build_candidates([packet])
    selected = export_second_annotator_packet.select_candidates(
        candidates,
        sample_size=3,
        label_quotas={"regressed": 1, "fixed": 1, "unresolved": 1, "partially_fixed": 0},
    )

    blind_path = tmp_path / "second_blind.tsv"
    key_path = tmp_path / "second_key.tsv"
    json_path = tmp_path / "manifest.json"
    md_path = tmp_path / "manifest.md"

    export_second_annotator_packet.write_tsv(
        blind_path,
        [export_second_annotator_packet.as_blind_row(row) for row in selected],
        export_second_annotator_packet.BLIND_FIELDS,
    )
    export_second_annotator_packet.write_tsv(
        key_path,
        [export_second_annotator_packet.as_key_row(row) for row in selected],
        export_second_annotator_packet.KEY_FIELDS,
    )
    report = export_second_annotator_packet.build_report(
        selected,
        candidates,
        sample_size=3,
        label_quotas={"regressed": 1, "fixed": 1, "unresolved": 1, "partially_fixed": 0},
        blind_output=blind_path,
        key_output=key_path,
        packet_specs=[packet],
    )
    export_second_annotator_packet.write_json(json_path, report)
    export_second_annotator_packet.write_manifest_md(md_path, report)

    with blind_path.open("r", encoding="utf-8", newline="") as handle:
        blind_rows = list(csv.DictReader(handle, delimiter="\t"))
    with key_path.open("r", encoding="utf-8", newline="") as handle:
        key_rows = list(csv.DictReader(handle, delimiter="\t"))

    assert len(blind_rows) == 3
    assert len(key_rows) == 3
    assert all(row["human_label"] == "" for row in blind_rows)
    assert all(row["assistant_label"] == row["first_pass_label"] for row in key_rows)

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["selected_rows"] == 3
    assert payload["blind_output"].endswith("second_blind.tsv")
    assert "independent second-pass agreement measurement only" in md_path.read_text(encoding="utf-8")
