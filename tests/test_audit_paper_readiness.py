from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_paper_readiness.py"
SPEC = importlib.util.spec_from_file_location("audit_paper_readiness", SCRIPT)
assert SPEC is not None
assert SPEC.loader is not None
audit_paper_readiness = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit_paper_readiness)


def claim(claim_id: str, status: str) -> dict[str, str]:
    return {"claim_id": claim_id, "status": status}


def gate(ok: bool, rows: int = 200, disagreements: int = 40) -> dict[str, object]:
    return {
        "ok": ok,
        "rows": rows,
        "complete_rate": 1.0,
        "disagreement": {"disagreement_rows": disagreements},
    }


def human(rows: int, labeled_rows: int) -> dict[str, int]:
    return {"rows": rows, "labeled_rows": labeled_rows}


def test_readiness_blocks_when_human_validation_pending() -> None:
    report = audit_paper_readiness.audit_readiness(
        claim_rows=[
            claim("C1", "ready"),
            claim("C2", "ready"),
            claim("C3", "ready"),
            claim("C4", "stress_evidence"),
            claim("C5", "not_ready"),
        ],
        iclr2024_gate=gate(True),
        iclr2025_gate=gate(False, rows=21, disagreements=16),
        iclr2024_human=human(40, 0),
        iclr2025_human=human(21, 0),
        packet_audits=[{"ok": True}, {"ok": True}],
        label_evidence_audits=[{"rows": 61, "evidence_issue_count": 0}],
    )

    assert report["overall_status"] == "blocked"
    assert any(check["check_id"] == "human_validation_completed" for check in report["blockers"])
    assert any(check["check_id"] == "iclr2025_pool_quality" for check in report["warnings"])


def test_readiness_is_provisional_when_only_cross_year_warning_remains() -> None:
    report = audit_paper_readiness.audit_readiness(
        claim_rows=[
            claim("C1", "ready"),
            claim("C2", "ready"),
            claim("C3", "ready"),
            claim("C4", "stress_evidence"),
        ],
        iclr2024_gate=gate(True),
        iclr2025_gate=gate(False, rows=21, disagreements=16),
        iclr2024_human=human(40, 10),
        iclr2025_human=human(21, 0),
        packet_audits=[{"ok": True}, {"ok": True}],
        label_evidence_audits=[{"rows": 61, "evidence_issue_count": 0}],
    )

    assert report["overall_status"] == "provisional"
    assert report["blockers"] == []
    assert any(check["check_id"] == "iclr2025_pool_quality" for check in report["warnings"])


def test_readiness_records_human_validation_provenance() -> None:
    report = audit_paper_readiness.audit_readiness(
        claim_rows=[
            claim("C1", "ready"),
            claim("C2", "ready"),
            claim("C3", "ready"),
        ],
        iclr2024_gate=gate(True),
        iclr2025_gate=gate(True),
        iclr2024_human=human(40, 40),
        iclr2025_human=human(21, 21),
        packet_audits=[{"ok": True}],
        label_evidence_audits=[{"rows": 61, "evidence_issue_count": 0}],
        human_validation_provenance={"status": "ok", "promoted_rows": 61},
    )

    validation_check = next(
        check for check in report["checks"] if check["check_id"] == "human_validation_completed"
    )
    assert validation_check["status"] == "pass"
    assert "promoted_rows=61" in validation_check["evidence"]
    assert "standard human-validation signoff" in validation_check["evidence"]


def test_readiness_warns_on_missing_label_evidence() -> None:
    report = audit_paper_readiness.audit_readiness(
        claim_rows=[
            claim("C1", "ready"),
            claim("C2", "ready"),
            claim("C3", "ready"),
        ],
        iclr2024_gate=gate(True),
        iclr2025_gate=gate(True),
        iclr2024_human=human(40, 10),
        iclr2025_human=human(21, 1),
        packet_audits=[{"ok": True}],
        label_evidence_audits=[{"rows": 100, "evidence_issue_count": 3}],
    )

    assert report["overall_status"] == "provisional"
    assert any(check["check_id"] == "label_evidence_complete" for check in report["warnings"])


def test_readiness_tracks_human_validation_queue_readiness() -> None:
    report = audit_paper_readiness.audit_readiness(
        claim_rows=[
            claim("C1", "ready"),
            claim("C2", "ready"),
            claim("C3", "ready"),
        ],
        iclr2024_gate=gate(True),
        iclr2025_gate=gate(True),
        iclr2024_human=human(2, 0),
        iclr2025_human=human(1, 0),
        packet_audits=[{"ok": True}],
        label_evidence_audits=[{"rows": 3, "evidence_issue_count": 0}],
        human_validation_queue_rows=[
            {"status": "pending", "packet": "ICLR 2024 v1"},
            {"status": "pending", "packet": "ICLR 2024 v1"},
            {"status": "pending", "packet": "ICLR 2025 repro v2"},
        ],
    )

    queue_check = next(
        check for check in report["checks"] if check["check_id"] == "human_validation_queue_ready"
    )
    assert queue_check["status"] == "pass"
    assert "queue_rows=3" in queue_check["evidence"]


def test_readiness_tracks_human_validation_batch_coverage() -> None:
    report = audit_paper_readiness.audit_readiness(
        claim_rows=[
            claim("C1", "ready"),
            claim("C2", "ready"),
            claim("C3", "ready"),
        ],
        iclr2024_gate=gate(True),
        iclr2025_gate=gate(True),
        iclr2024_human=human(2, 0),
        iclr2025_human=human(1, 0),
        packet_audits=[{"ok": True}],
        label_evidence_audits=[{"rows": 3, "evidence_issue_count": 0}],
        human_validation_batch_rows=[
            {"batch_id": "b1", "rows": "2"},
            {"batch_id": "b2", "rows": "1"},
        ],
    )

    batch_check = next(
        check for check in report["checks"] if check["check_id"] == "human_validation_batches_ready"
    )
    assert batch_check["status"] == "pass"
    assert "batch_rows=3" in batch_check["evidence"]


def test_readiness_accepts_empty_batch_manifest_when_no_pending_rows() -> None:
    report = audit_paper_readiness.audit_readiness(
        claim_rows=[
            claim("C1", "ready"),
            claim("C2", "ready"),
            claim("C3", "ready"),
        ],
        iclr2024_gate=gate(True),
        iclr2025_gate=gate(True),
        iclr2024_human=human(2, 2),
        iclr2025_human=human(1, 1),
        packet_audits=[{"ok": True}],
        label_evidence_audits=[{"rows": 3, "evidence_issue_count": 0}],
        human_validation_batch_rows=[],
    )

    batch_check = next(
        check for check in report["checks"] if check["check_id"] == "human_validation_batches_ready"
    )
    assert batch_check["status"] == "pass"
    assert "expected_pending_rows=0" in batch_check["evidence"]


def test_readiness_tracks_human_validation_batch_ingest() -> None:
    report = audit_paper_readiness.audit_readiness(
        claim_rows=[
            claim("C1", "ready"),
            claim("C2", "ready"),
            claim("C3", "ready"),
        ],
        iclr2024_gate=gate(True),
        iclr2025_gate=gate(True),
        iclr2024_human=human(2, 0),
        iclr2025_human=human(1, 0),
        packet_audits=[{"ok": True}],
        label_evidence_audits=[{"rows": 3, "evidence_issue_count": 0}],
        human_validation_batch_ingest={
            "status": "ok",
            "batch_rows": 3,
            "completed_batch_rows": 0,
            "merged_rows": 0,
            "error_count": 0,
        },
    )

    ingest_check = next(
        check for check in report["checks"] if check["check_id"] == "human_validation_batch_ingest_ready"
    )
    assert ingest_check["status"] == "pass"
    assert "completed_batch_rows=0" in ingest_check["evidence"]


def test_readiness_tracks_paper_citation_audit() -> None:
    report = audit_paper_readiness.audit_readiness(
        claim_rows=[
            claim("C1", "ready"),
            claim("C2", "ready"),
            claim("C3", "ready"),
        ],
        iclr2024_gate=gate(True),
        iclr2025_gate=gate(True),
        iclr2024_human=human(2, 2),
        iclr2025_human=human(1, 1),
        packet_audits=[{"ok": True}],
        label_evidence_audits=[{"rows": 3, "evidence_issue_count": 0}],
        citation_audit={
            "ok": True,
            "status": "pass",
            "cited_key_count": 9,
            "bib_entry_count": 9,
            "missing_bib_keys": [],
            "unused_bib_keys": [],
            "duplicate_bib_keys": [],
            "missing_required_fields": [],
            "log_problems": [],
        },
    )

    citation_check = next(check for check in report["checks"] if check["check_id"] == "paper_citations_ready")
    assert citation_check["status"] == "pass"
    assert "cited_keys=9" in citation_check["evidence"]


def test_readiness_blocks_on_citation_audit_blocker() -> None:
    report = audit_paper_readiness.audit_readiness(
        claim_rows=[
            claim("C1", "ready"),
            claim("C2", "ready"),
            claim("C3", "ready"),
        ],
        iclr2024_gate=gate(True),
        iclr2025_gate=gate(True),
        iclr2024_human=human(2, 2),
        iclr2025_human=human(1, 1),
        packet_audits=[{"ok": True}],
        label_evidence_audits=[{"rows": 3, "evidence_issue_count": 0}],
        citation_audit={
            "ok": False,
            "status": "blocker",
            "cited_key_count": 2,
            "bib_entry_count": 1,
            "missing_bib_keys": ["missing"],
            "unused_bib_keys": [],
            "duplicate_bib_keys": [],
            "missing_required_fields": [],
            "log_problems": [],
        },
    )

    assert report["overall_status"] == "blocked"
    assert any(check["check_id"] == "paper_citations_ready" for check in report["blockers"])


def test_readiness_tracks_second_annotator_packet_status() -> None:
    report = audit_paper_readiness.audit_readiness(
        claim_rows=[
            claim("C1", "ready"),
            claim("C2", "ready"),
            claim("C3", "ready"),
        ],
        iclr2024_gate=gate(True),
        iclr2025_gate=gate(True),
        iclr2024_human=human(2, 2),
        iclr2025_human=human(1, 1),
        packet_audits=[{"ok": True}],
        label_evidence_audits=[{"rows": 3, "evidence_issue_count": 0}],
        iaa_second_annotator_manifest={"selected_rows": 60},
        iaa_second_annotator_blind_rows=[
            {"issue_id": "a", "human_label": ""},
            {"issue_id": "b", "human_label": "fixed"},
        ],
        iaa_second_annotator_metrics={"labeled_rows": 1, "agreement": 1.0, "cohen_kappa": 1.0},
    )

    iaa_check = next(check for check in report["checks"] if check["check_id"] == "iaa_second_annotator_packet")
    assert iaa_check["status"] == "warning"
    assert "target_rows=60" in iaa_check["evidence"]
    assert "labeled_rows=1" in iaa_check["evidence"]


def test_readiness_marks_second_annotator_packet_complete() -> None:
    report = audit_paper_readiness.audit_readiness(
        claim_rows=[
            claim("C1", "ready"),
            claim("C2", "ready"),
            claim("C3", "ready"),
        ],
        iclr2024_gate=gate(True),
        iclr2025_gate=gate(True),
        iclr2024_human=human(2, 2),
        iclr2025_human=human(1, 1),
        packet_audits=[{"ok": True}],
        label_evidence_audits=[{"rows": 3, "evidence_issue_count": 0}],
        iaa_second_annotator_manifest={"selected_rows": 2},
        iaa_second_annotator_blind_rows=[
            {"issue_id": "a", "human_label": "fixed"},
            {"issue_id": "b", "human_label": "unresolved"},
        ],
        iaa_second_annotator_metrics={"labeled_rows": 2, "agreement": 1.0, "cohen_kappa": 1.0},
    )

    iaa_check = next(check for check in report["checks"] if check["check_id"] == "iaa_second_annotator_packet")
    assert iaa_check["status"] == "pass"
    assert "agreement=1.0" in iaa_check["evidence"]
    assert "Second-annotator packet metrics are complete" in iaa_check["next_action"]
