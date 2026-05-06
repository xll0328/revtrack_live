from __future__ import annotations

from revtrack.annotation_packet import disagreement_count, high_conflict, render_annotation_packet, summarize_rows


def make_row(**overrides: str) -> dict[str, str]:
    row = {
        "issue_id": "paper__r01",
        "paper_title": "A Revision Test",
        "priority_score": "6.2",
        "review_rating": "6: marginally above threshold",
        "review_confidence": "4: confident",
        "suggested_label": "partially_fixed",
        "suggestion_source": "priority_secondary_mpnet",
        "suggestion_note": "mpnet=partially_fixed; heuristic=fixed",
        "silver_label": "",
        "gold_label": "",
        "heuristic_label": "fixed",
        "tfidf_label": "fixed",
        "modernbert_label": "partially_fixed",
        "mpnet_label": "regressed",
        "review_excerpt": "Need more evidence for the claim.",
        "top_response_excerpt": "We added one ablation but not the runtime analysis.",
        "aligned_response_excerpt": "",
        "revision_summary": "Minor revisions only.",
        "silver_comment": "",
        "evidence_span": "",
        "notes": "",
    }
    row.update(overrides)
    return row


def test_disagreement_and_high_conflict() -> None:
    row = make_row()
    assert disagreement_count(row) == 2
    assert high_conflict(row) is True


def test_render_annotation_packet_contains_key_content() -> None:
    rows = [
        make_row(),
        make_row(
            issue_id="paper__r02",
            suggested_label="fixed",
            gold_label="fixed",
            mpnet_label="fixed",
            modernbert_label="fixed",
            top_response_excerpt="We added the requested runtime table.",
        ),
    ]
    summary = summarize_rows(rows)
    assert summary["rows"] == 2
    assert summary["labeled"] == 1
    assert summary["high_conflict"] == 1

    rendered = render_annotation_packet(
        rows,
        title="Demo Packet",
        sheet_name="demo.tsv",
    )

    assert "Demo Packet" in rendered
    assert "paper__r01" in rendered
    assert "Only high-conflict rows" in rendered
    assert "mpnet" in rendered
    assert "fixed" in rendered
    assert "partially fixed" in rendered

