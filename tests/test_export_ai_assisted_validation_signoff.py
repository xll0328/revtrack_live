from __future__ import annotations

import csv
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "export_ai_assisted_validation_signoff.py"
SPEC = importlib.util.spec_from_file_location("export_ai_assisted_validation_signoff", SCRIPT)
assert SPEC is not None
assert SPEC.loader is not None
export_ai_assisted_validation_signoff = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(export_ai_assisted_validation_signoff)


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_tsv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def test_export_signoff_sheet_exposes_assistant_context_but_requires_review(tmp_path: Path) -> None:
    queue = tmp_path / "queue.csv"
    key = tmp_path / "key.tsv"
    blind = tmp_path / "blind.tsv"
    out = tmp_path / "signoff"
    write_csv(
        queue,
        [
            {
                "queue_rank": "1",
                "packet": "P1",
                "status": "pending",
                "issue_id": "a",
                "paper_title": "Paper A",
                "assistant_label": "fixed",
                "suggested_label": "fixed",
                "audit_bucket": "label_stratum",
                "audit_score": "1.000",
                "priority_score": "2.000",
                "review_rating": "6",
                "review_confidence": "3",
                "blind_sheet": str(blind),
            }
        ],
        [
            "queue_rank",
            "packet",
            "status",
            "issue_id",
            "paper_title",
            "assistant_label",
            "suggested_label",
            "audit_bucket",
            "audit_score",
            "priority_score",
            "review_rating",
            "review_confidence",
            "blind_sheet",
        ],
    )
    write_tsv(
        blind,
        [
            {
                "issue_id": "a",
                "paper_title": "Paper A",
                "review_rating": "6",
                "review_confidence": "3",
                "review_excerpt": "Blind concern text.",
                "top_response_excerpt": "Blind response text.",
                "aligned_response_excerpt": "Blind aligned text.",
                "revision_summary": "Blind revision text.",
                "human_label": "",
                "human_confidence": "",
                "evidence_span": "",
                "notes": "",
            }
        ],
        [
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
        ],
    )
    write_tsv(
        key,
        [
            {
                "issue_id": "a",
                "assistant_label": "fixed",
                "suggested_label": "fixed",
                "audit_bucket": "label_stratum",
                "audit_score": "1.000",
                "priority_score": "2.000",
                "assistant_evidence_span": "Added the requested ablation.",
                "assistant_notes": "Exact concern is addressed.",
                "structured_label": "fixed",
                "tfidf_label": "partially_fixed",
                "review_excerpt": "Need ablation.",
                "top_response_excerpt": "We added Table 2.",
                "aligned_response_excerpt": "Table 2 reports the ablation.",
                "revision_summary": "Added Table 2.",
            }
        ],
        [
            "issue_id",
            "assistant_label",
            "suggested_label",
            "audit_bucket",
            "audit_score",
            "priority_score",
            "assistant_evidence_span",
            "assistant_notes",
            "structured_label",
            "tfidf_label",
            "review_excerpt",
            "top_response_excerpt",
            "aligned_response_excerpt",
            "revision_summary",
        ],
    )

    manifest = export_ai_assisted_validation_signoff.export_signoff(
        queue_path=queue,
        packet_keys={"P1": key},
        output_dir=out,
        prefix="signoff",
    )

    rows = read_tsv(out / "signoff.tsv")
    html = (out / "signoff.html").read_text(encoding="utf-8")
    assert manifest["rows"] == "1"
    assert manifest["needs_human_review"] == "1"
    assert manifest["key_evidence_rows"] == "1"
    assert manifest["context_fallback_evidence_rows"] == "0"
    assert rows[0]["assistant_label"] == "fixed"
    assert rows[0]["review_excerpt"] == "Blind concern text."
    assert rows[0]["top_response_excerpt"] == "Blind response text."
    assert rows[0]["assistant_evidence_span"] == "Added the requested ablation."
    assert rows[0]["reviewer_final_label"] == ""
    assert rows[0]["signoff_status"] == "needs_human_review"
    assert "must not be reported as independent human validation" in html


def test_signoff_excludes_done_rows_by_default(tmp_path: Path) -> None:
    queue = tmp_path / "queue.csv"
    key = tmp_path / "key.tsv"
    write_csv(
        queue,
        [
            {"queue_rank": "1", "packet": "P1", "status": "done", "issue_id": "a"},
            {"queue_rank": "2", "packet": "P1", "status": "pending", "issue_id": "b"},
        ],
        ["queue_rank", "packet", "status", "issue_id"],
    )
    write_tsv(
        key,
        [
            {"issue_id": "a", "assistant_label": "fixed"},
            {"issue_id": "b", "assistant_label": "unresolved"},
        ],
        ["issue_id", "assistant_label"],
    )

    rows = export_ai_assisted_validation_signoff.build_signoff_rows(
        queue_rows=export_ai_assisted_validation_signoff.load_csv(queue),
        key_index=export_ai_assisted_validation_signoff.load_key_index({"P1": key}),
    )

    assert [row["issue_id"] for row in rows] == ["b"]


def test_signoff_uses_context_fallback_when_key_evidence_is_missing(tmp_path: Path) -> None:
    queue = tmp_path / "queue.csv"
    key = tmp_path / "key.tsv"
    blind = tmp_path / "blind.tsv"
    write_csv(
        queue,
        [
            {
                "queue_rank": "1",
                "packet": "P1",
                "status": "pending",
                "issue_id": "a",
                "paper_title": "Paper A",
                "blind_sheet": str(blind),
            }
        ],
        ["queue_rank", "packet", "status", "issue_id", "paper_title", "blind_sheet"],
    )
    write_tsv(
        blind,
        [
            {
                "issue_id": "a",
                "paper_title": "Paper A",
                "review_rating": "6",
                "review_confidence": "3",
                "review_excerpt": "Need ablation.",
                "top_response_excerpt": "Top response.",
                "aligned_response_excerpt": "The revision adds Table 2 with the missing ablation.",
                "revision_summary": "Added ablation.",
                "human_label": "",
                "human_confidence": "",
                "evidence_span": "",
                "notes": "",
            }
        ],
        [
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
        ],
    )
    write_tsv(
        key,
        [
            {
                "issue_id": "a",
                "assistant_label": "fixed",
                "assistant_evidence_span": "",
                "assistant_notes": "The exact concern is addressed.",
            }
        ],
        ["issue_id", "assistant_label", "assistant_evidence_span", "assistant_notes"],
    )

    manifest = export_ai_assisted_validation_signoff.export_signoff(
        queue_path=queue,
        packet_keys={"P1": key},
        output_dir=tmp_path / "signoff",
        prefix="signoff",
    )

    rows = read_tsv(tmp_path / "signoff" / "signoff.tsv")
    manifest_md = (tmp_path / "signoff" / "signoff_manifest.md").read_text(encoding="utf-8")
    assert manifest["rows"] == "1"
    assert manifest["key_evidence_rows"] == "0"
    assert manifest["context_fallback_evidence_rows"] == "1"
    assert rows[0]["assistant_evidence_span"].startswith(
        "Context fallback from aligned response context:"
    )
    assert "missing ablation" in rows[0]["assistant_evidence_span"]
    assert "Context fallback evidence rows: `1`" in manifest_md
