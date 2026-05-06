from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_human_validation_pipeline.py"
SPEC = importlib.util.spec_from_file_location("run_human_validation_pipeline", SCRIPT)
assert SPEC is not None
assert SPEC.loader is not None
run_human_validation_pipeline = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(run_human_validation_pipeline)


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


def write_tsv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


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


def make_packet(tmp_path: Path) -> tuple[str, dict[str, Path]]:
    blind = tmp_path / "blind.tsv"
    key = tmp_path / "key.tsv"
    audit = tmp_path / "audit.tsv"
    metrics = tmp_path / "metrics.json"
    blind_packet = tmp_path / "blind_packet.html"
    write_tsv(blind, [blind_row("a"), blind_row("b")], BLIND_FIELDS)
    write_tsv(
        key,
        [
            {"issue_id": "a", "assistant_label": "fixed", "audit_bucket": "label_stratum"},
            {"issue_id": "b", "assistant_label": "unresolved", "audit_bucket": "minority_unresolved"},
        ],
        ["issue_id", "assistant_label", "audit_bucket"],
    )
    write_tsv(
        audit,
        [
            {"issue_id": "a", "audit_bucket": "label_stratum", "audit_score": "1", "priority_score": "1"},
            {"issue_id": "b", "audit_bucket": "minority_unresolved", "audit_score": "2", "priority_score": "2"},
        ],
        ["issue_id", "audit_bucket", "audit_score", "priority_score"],
    )
    metrics.write_text(
        json.dumps({"rows": 2, "labeled_rows": 0, "unlabeled_rows": 2}) + "\n",
        encoding="utf-8",
    )
    blind_packet.write_text("<html></html>", encoding="utf-8")
    spec = f"P1:{blind}:{key}:{audit}:{metrics}:{blind_packet}"
    return spec, {
        "blind": blind,
        "key": key,
        "audit": audit,
        "metrics": metrics,
        "blind_packet": blind_packet,
    }


def write_completed_batch(batch_dir: Path) -> None:
    write_tsv(
        batch_dir / "priority_batch_01_blind.tsv",
        [
            {
                "batch_rank": "1",
                "global_queue_rank": "1",
                "source_packet": "P1",
                **blind_row("a", human_label="fixed"),
                "human_confidence": "4",
                "evidence_span": "The revision added the requested table.",
                "notes": "Looks fixed.",
            },
            {
                "batch_rank": "2",
                "global_queue_rank": "2",
                "source_packet": "P1",
                **blind_row("b"),
            },
        ],
        ["batch_rank", "global_queue_rank", "source_packet", *BLIND_FIELDS],
    )


def test_pipeline_dry_run_previews_metrics_without_overwriting_canonical(tmp_path: Path) -> None:
    spec, paths = make_packet(tmp_path)
    batch_dir = tmp_path / "batches"
    write_completed_batch(batch_dir)

    report = run_human_validation_pipeline.run_pipeline(
        packet_values=[spec],
        queue_csv=tmp_path / "queue.csv",
        queue_md=tmp_path / "queue.md",
        batch_dir=batch_dir,
        batch_prefix="priority",
        ingest_output_dir=tmp_path / "ingest",
        ingest_json=tmp_path / "ingest.json",
        ingest_md=tmp_path / "ingest.md",
        preview_eval_dir=tmp_path / "preview",
        pipeline_json=tmp_path / "pipeline.json",
        pipeline_md=tmp_path / "pipeline.md",
        write_canonical=False,
        run_readiness=False,
    )

    assert report["status"] == "ok"
    assert report["evaluations"][0]["labeled_rows"] == 1
    assert read_tsv(paths["blind"])[0]["human_label"] == ""
    preview_metrics = json.loads((tmp_path / "preview" / "metrics.json").read_text(encoding="utf-8"))
    assert preview_metrics["labeled_rows"] == 1
    official_metrics = json.loads(paths["metrics"].read_text(encoding="utf-8"))
    assert official_metrics["labeled_rows"] == 0


def test_pipeline_canonical_write_refreshes_official_metrics_and_pending_batches(tmp_path: Path) -> None:
    spec, paths = make_packet(tmp_path)
    batch_dir = tmp_path / "batches"
    write_completed_batch(batch_dir)

    report = run_human_validation_pipeline.run_pipeline(
        packet_values=[spec],
        queue_csv=tmp_path / "queue.csv",
        queue_md=tmp_path / "queue.md",
        batch_dir=batch_dir,
        batch_prefix="priority",
        batch_size=10,
        ingest_output_dir=tmp_path / "ingest",
        ingest_json=tmp_path / "ingest.json",
        ingest_md=tmp_path / "ingest.md",
        preview_eval_dir=tmp_path / "preview",
        pipeline_json=tmp_path / "pipeline.json",
        pipeline_md=tmp_path / "pipeline.md",
        write_canonical=True,
        run_readiness=False,
    )

    assert report["status"] == "ok"
    assert read_tsv(paths["blind"])[0]["human_label"] == "fixed"
    official_metrics = json.loads(paths["metrics"].read_text(encoding="utf-8"))
    assert official_metrics["labeled_rows"] == 1
    manifest = list(csv.DictReader((batch_dir / "priority_manifest.csv").open("r", encoding="utf-8")))
    assert manifest[0]["rows"] == "1"
    batch_rows = read_tsv(batch_dir / "priority_batch_01_blind.tsv")
    assert [row["issue_id"] for row in batch_rows] == ["b"]
