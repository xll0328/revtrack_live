from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "export_failure_taxonomy.py"
SPEC = importlib.util.spec_from_file_location("export_failure_taxonomy", SCRIPT)
assert SPEC is not None
assert SPEC.loader is not None
export_failure_taxonomy = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(export_failure_taxonomy)


def test_failure_taxonomy_includes_accuracy_trap_from_fixed_miss() -> None:
    signoff_rows = [
        {
            "issue_id": "w7P92BEsb2__r01",
            "paper_title": "PIED",
            "assistant_label": "fixed",
            "review_excerpt": "Need computational cost.",
            "assistant_evidence_span": "Figure 6 compares cost.",
        },
        {
            "issue_id": "My7lkRNnL9__r01",
            "paper_title": "Forward Learning",
            "assistant_label": "unresolved",
            "review_excerpt": "Theory is shallow.",
            "assistant_evidence_span": "Theory remains limited.",
        },
        {
            "issue_id": "9k0krNzvlV__r02",
            "paper_title": "Watermarks",
            "assistant_label": "partially_fixed",
            "review_excerpt": "Contribution unclear.",
            "assistant_evidence_span": "Added experiments.",
        },
        {
            "issue_id": "kmn0BhQk7p__r04",
            "paper_title": "Privacy",
            "assistant_label": "fixed",
            "review_excerpt": "Need cross-labeling.",
            "assistant_evidence_span": "Cross-labeled 25%.",
        },
    ]
    tfidf_details = [
        {
            "id": "w7P92BEsb2__r01",
            "paper_title": "PIED",
            "gold_label": "fixed",
            "predicted_label": "partially_fixed",
        }
    ]
    structured_details = [
        {
            "id": "w7P92BEsb2__r01",
            "paper_title": "PIED",
            "gold_label": "fixed",
            "predicted_label": "fixed",
        }
    ]

    rows = export_failure_taxonomy.build_rows(
        signoff_rows=signoff_rows,
        tfidf_details=tfidf_details,
        structured_details=structured_details,
    )

    modes = {row["failure_mode"] for row in rows}
    assert "stale_criticism" in modes
    assert "accuracy_trap_fixed_cases" in modes
    accuracy_row = next(row for row in rows if row["failure_mode"] == "accuracy_trap_fixed_cases")
    assert accuracy_row["tfidf_prediction"] == "partially_fixed"


def test_failure_taxonomy_adds_expanded80_aggregate_modes() -> None:
    signoff_rows = [
        {
            "issue_id": "w7P92BEsb2__r01",
            "paper_title": "PIED",
            "assistant_label": "fixed",
            "review_excerpt": "Need computational cost.",
            "assistant_evidence_span": "Figure 6 compares cost.",
        },
        {
            "issue_id": "My7lkRNnL9__r01",
            "paper_title": "Forward Learning",
            "assistant_label": "unresolved",
            "review_excerpt": "Theory is shallow.",
            "assistant_evidence_span": "Theory remains limited.",
        },
        {
            "issue_id": "9k0krNzvlV__r02",
            "paper_title": "Watermarks",
            "assistant_label": "partially_fixed",
            "review_excerpt": "Contribution unclear.",
            "assistant_evidence_span": "Added experiments.",
        },
        {
            "issue_id": "kmn0BhQk7p__r04",
            "paper_title": "Privacy",
            "assistant_label": "fixed",
            "review_excerpt": "Need cross-labeling.",
            "assistant_evidence_span": "Cross-labeled 25%.",
        },
    ]
    expanded_human = [
        {
            "issue_id": "u1",
            "paper_title": "Paper U",
            "review_excerpt": "Need a stronger baseline.",
            "evidence_span": "Only a partial comparison was added.",
        },
        {
            "issue_id": "r1",
            "paper_title": "Paper R",
            "review_excerpt": "New result contradicts the claim.",
            "evidence_span": "Revision introduces a worse setting.",
        },
    ]
    rows = export_failure_taxonomy.build_rows(
        signoff_rows=signoff_rows,
        tfidf_details=[],
        structured_details=[],
        expanded_human_rows=expanded_human,
        expanded_details_by_model={
            "structured": [
                {
                    "id": "u1",
                    "paper_title": "Paper U",
                    "gold_label": "unresolved",
                    "predicted_label": "fixed",
                }
            ],
            "tfidf": [
                {
                    "id": "r1",
                    "paper_title": "Paper R",
                    "gold_label": "regressed",
                    "predicted_label": "partially_fixed",
                }
            ],
        },
    )

    by_mode = {row["failure_mode"]: row for row in rows}
    assert by_mode["over_crediting_unresolved"]["source_split"] == "iclr2025_expanded80_standard"
    assert by_mode["over_crediting_unresolved"]["support_count"] == "1"
    assert by_mode["regression_blindness"]["model_key"] == "tfidf"
