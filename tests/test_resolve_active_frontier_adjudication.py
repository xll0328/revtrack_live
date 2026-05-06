from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "resolve_active_frontier_adjudication.py"
SPEC = importlib.util.spec_from_file_location("resolve_active_frontier_adjudication", SCRIPT)
assert SPEC is not None
assert SPEC.loader is not None
resolver = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(resolver)


def test_resolver_downgrades_unsupported_regressed_label() -> None:
    row = {
        "issue_id": "r1",
        "assistant_label": "regressed",
        "tfidf_label": "partially_fixed",
        "modernbert_label": "fixed",
        "mpnet_label": "regressed",
        "issue_ledger_label": "partially_fixed",
        "structured_label": "fixed",
        "aligned_response_excerpt": "We added runtime benchmarks and a clearer limitation discussion.",
        "revision_summary": "We added runtime benchmarks.",
        "evidence_span": "We added runtime benchmarks.",
    }

    resolved = resolver.resolve_row(row)

    assert resolved["resolved_label"] == "partially_fixed"
    assert resolved["resolution_action"] == "downgrade_regressed"
    assert resolved["resolution_provenance"] == "assistant_resolved_candidate_not_human_validation"


def test_resolver_upgrades_weak_unresolved_with_concrete_fix_evidence() -> None:
    row = {
        "issue_id": "u1",
        "assistant_label": "unresolved",
        "tfidf_label": "partially_fixed",
        "modernbert_label": "fixed",
        "mpnet_label": "fixed",
        "issue_ledger_label": "unresolved",
        "structured_label": "fixed",
        "aligned_response_excerpt": "We added a new experiment and report it in Table 3.",
        "revision_summary": "We added a new experiment in Table 3.",
        "evidence_span": "We added a new experiment in Table 3.",
    }

    resolved = resolver.resolve_row(row)

    assert resolved["resolved_label"] == "fixed"
    assert resolved["resolution_action"] == "upgrade_weak_unresolved_to_fixed"


def test_resolver_keeps_weak_unresolved_without_fix_evidence() -> None:
    row = {
        "issue_id": "u2",
        "assistant_label": "unresolved",
        "tfidf_label": "partially_fixed",
        "modernbert_label": "fixed",
        "mpnet_label": "fixed",
        "issue_ledger_label": "unresolved",
        "structured_label": "fixed",
        "aligned_response_excerpt": "This experiment is beyond scope and left for future work.",
        "revision_summary": "This experiment is beyond scope.",
        "evidence_span": "This experiment is beyond scope.",
    }

    resolved = resolver.resolve_row(row)

    assert resolved["resolved_label"] == "unresolved"
    assert resolved["resolution_action"] == "keep_weak_unresolved"


def test_report_lists_all_changed_rows(tmp_path: Path) -> None:
    rows = [
        {
            "issue_id": f"row{i:02d}",
            "draft_label": "unresolved",
            "resolved_label": "partially_fixed",
            "resolution_action": "upgrade_weak_unresolved_to_partial",
            "resolution_reason": "Concrete fix evidence.",
        }
        for i in range(35)
    ]
    report = tmp_path / "report.md"

    resolver.write_report_md(
        report,
        rows,
        output_tsv="resolved.tsv",
        candidate_blind="candidate.tsv",
    )

    text = report.read_text(encoding="utf-8")
    assert "`row00`" in text
    assert "`row34`" in text
