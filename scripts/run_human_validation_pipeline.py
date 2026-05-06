from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def load_script_module(name: str) -> Any:
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot import {name} from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


audit_paper_readiness = load_script_module("audit_paper_readiness")
evaluate_human_validation = load_script_module("evaluate_human_validation")
export_human_validation_batches = load_script_module("export_human_validation_batches")
export_human_validation_queue = load_script_module("export_human_validation_queue")
merge_human_validation_batches = load_script_module("merge_human_validation_batches")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the human-validation ingest, evaluation, queue, batch, and readiness pipeline."
    )
    parser.add_argument(
        "--packet",
        action="append",
        default=None,
        help=(
            "Packet spec as name:blind:key:audit:pending_metrics:blind_packet. "
            "May be repeated. Defaults to active ICLR 2024 v1, ICLR 2025 repro v2, and ICLR 2025 expanded80 v1 packets."
        ),
    )
    parser.add_argument("--queue-csv", default="outputs/day1/paper_assets/human_validation_work_queue.csv")
    parser.add_argument("--queue-md", default="outputs/day1/paper_assets/human_validation_work_queue.md")
    parser.add_argument("--batch-dir", default="outputs/day1/human_validation_batches")
    parser.add_argument("--batch-prefix", default="human_validation_priority")
    parser.add_argument("--batch-size", type=int, default=10)
    parser.add_argument("--ingest-output-dir", default="outputs/day1/human_validation_batch_ingest")
    parser.add_argument(
        "--ingest-json",
        default="outputs/day1/paper_assets/human_validation_batch_ingest_report.json",
    )
    parser.add_argument(
        "--ingest-md",
        default="outputs/day1/paper_assets/human_validation_batch_ingest_report.md",
    )
    parser.add_argument("--preview-eval-dir", default="outputs/day1/human_validation_batch_ingest/evaluation")
    parser.add_argument(
        "--pipeline-json",
        default="outputs/day1/paper_assets/human_validation_pipeline_report.json",
    )
    parser.add_argument(
        "--pipeline-md",
        default="outputs/day1/paper_assets/human_validation_pipeline_report.md",
    )
    parser.add_argument("--readiness-json", default="outputs/day1/paper_assets/paper_readiness_audit.json")
    parser.add_argument("--readiness-md", default="outputs/day1/paper_assets/paper_readiness_audit.md")
    parser.add_argument("--write-canonical", action="store_true")
    parser.add_argument("--allow-overwrite", action="store_true")
    parser.add_argument("--skip-readiness", action="store_true")
    parser.add_argument("--fail-on-error", action="store_true")
    return parser.parse_args()


def resolve_path(path: str | Path) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else ROOT / candidate


def relpath(path: str | Path) -> str:
    resolved = Path(path)
    try:
        return str(resolved.relative_to(ROOT))
    except ValueError:
        return str(resolved)


def parse_packet_specs(values: list[str] | None) -> list[Any]:
    return [
        export_human_validation_queue.parse_packet_spec(value)
        for value in (values or export_human_validation_queue.DEFAULT_PACKETS)
    ]


def mismatch_path_for(metrics_path: str | Path) -> Path:
    path = Path(metrics_path)
    name = path.name
    if name.endswith("_pending_metrics.json"):
        return path.with_name(name.replace("_pending_metrics.json", "_pending_mismatches.tsv"))
    if name.endswith("_metrics.json"):
        return path.with_name(name.replace("_metrics.json", "_mismatches.tsv"))
    return path.with_suffix(".mismatches.tsv")


def write_json(path: str | Path, payload: dict[str, Any]) -> None:
    output_path = resolve_path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_queue(packet_specs: list[Any], *, output_csv: str | Path, output_md: str | Path) -> list[dict[str, str]]:
    rows = export_human_validation_queue.build_queue(packet_specs)
    summaries = export_human_validation_queue.packet_summary(packet_specs, rows)
    export_human_validation_queue.write_csv(output_csv, rows)
    export_human_validation_queue.write_markdown(output_md, rows, summaries)
    return rows


def merged_sheet_path(ingest_output_dir: str | Path, canonical_sheet: str | Path) -> Path:
    return resolve_path(ingest_output_dir) / "sheets" / Path(canonical_sheet).name


def evaluate_packets(
    packet_specs: list[Any],
    *,
    use_canonical: bool,
    ingest_output_dir: str | Path,
    preview_eval_dir: str | Path,
) -> list[dict[str, Any]]:
    reports: list[dict[str, Any]] = []
    for packet in packet_specs:
        human_sheet = packet.blind if use_canonical else merged_sheet_path(ingest_output_dir, packet.blind)
        metrics_path = packet.pending_metrics if use_canonical else resolve_path(preview_eval_dir) / packet.pending_metrics.name
        mismatch_path = mismatch_path_for(metrics_path)
        summary, mismatches = evaluate_human_validation.evaluate(
            evaluate_human_validation.load_tsv(human_sheet),
            evaluate_human_validation.load_tsv(packet.key),
        )
        write_json(metrics_path, summary)
        evaluate_human_validation.write_tsv(
            mismatch_path,
            mismatches,
            [
                "issue_id",
                "assistant_label",
                "human_label",
                "audit_bucket",
                "assistant_evidence_span",
                "human_evidence_span",
                "human_notes",
            ],
        )
        reports.append(
            {
                "packet": packet.name,
                "human_sheet": relpath(human_sheet),
                "key": relpath(packet.key),
                "metrics": relpath(metrics_path),
                "mismatches": relpath(mismatch_path),
                "rows": summary["rows"],
                "labeled_rows": summary["labeled_rows"],
                "unlabeled_rows": summary["unlabeled_rows"],
                "agreement": summary["agreement"],
                "cohen_kappa": summary["cohen_kappa"],
                "mismatch_count": len(mismatches),
            }
        )
    return reports


def run_readiness_audit(*, output_json: str | Path, output_md: str | Path) -> dict[str, Any]:
    defaults = audit_paper_readiness.DEFAULTS
    report = audit_paper_readiness.audit_readiness(
        claim_rows=audit_paper_readiness.load_claim_rows(defaults["claim_ledger"]),
        iclr2024_gate=audit_paper_readiness.load_json(defaults["iclr2024_gate"]),
        iclr2025_gate=audit_paper_readiness.load_json(defaults["iclr2025_gate"]),
        iclr2024_human=audit_paper_readiness.load_json(defaults["iclr2024_human_metrics"]),
        iclr2025_human=audit_paper_readiness.load_json(defaults["iclr2025_human_metrics"]),
        iclr2025_expanded80_human=audit_paper_readiness.load_json(defaults["iclr2025_expanded80_human_metrics"])
        if Path(defaults["iclr2025_expanded80_human_metrics"]).exists()
        else None,
        neurips2024_standard=audit_paper_readiness.load_json(defaults["neurips2024_standard_manifest"])
        if Path(defaults["neurips2024_standard_manifest"]).exists()
        else None,
        iclr2023_random80_human=audit_paper_readiness.load_json(defaults["iclr2023_random80_human_metrics"])
        if Path(defaults["iclr2023_random80_human_metrics"]).exists()
        else None,
        iclr2023_random80_standard=audit_paper_readiness.load_json(
            defaults["iclr2023_random80_standard_manifest"]
        )
        if Path(defaults["iclr2023_random80_standard_manifest"]).exists()
        else None,
        packet_audits=[audit_paper_readiness.load_json(path) for path in defaults["packet_audits"]],
        label_evidence_audits=[
            audit_paper_readiness.load_json(path)
            for path in defaults["label_evidence_audits"]
            if Path(path).exists()
        ],
        human_validation_queue_rows=audit_paper_readiness.load_csv_rows(defaults["human_validation_queue"])
        if Path(defaults["human_validation_queue"]).exists()
        else None,
        human_validation_batch_rows=audit_paper_readiness.load_csv_rows(defaults["human_validation_batch_manifest"])
        if Path(defaults["human_validation_batch_manifest"]).exists()
        else None,
        human_validation_batch_ingest=audit_paper_readiness.load_json(defaults["human_validation_batch_ingest"])
        if Path(defaults["human_validation_batch_ingest"]).exists()
        else None,
        human_validation_provenance=audit_paper_readiness.load_json(defaults["human_validation_provenance"])
        if Path(defaults["human_validation_provenance"]).exists()
        else None,
        expanded80_human_validation_provenance=audit_paper_readiness.load_json(
            defaults["expanded80_human_validation_provenance"]
        )
        if Path(defaults["expanded80_human_validation_provenance"]).exists()
        else None,
        neurips2024_human_validation_provenance=audit_paper_readiness.load_json(
            defaults["neurips2024_human_validation_provenance"]
        )
        if Path(defaults["neurips2024_human_validation_provenance"]).exists()
        else None,
        iclr2023_random80_human_validation_provenance=audit_paper_readiness.load_json(
            defaults["iclr2023_random80_human_validation_provenance"]
        )
        if Path(defaults["iclr2023_random80_human_validation_provenance"]).exists()
        else None,
    )
    write_json(output_json, report)
    audit_paper_readiness.write_markdown(output_md, report)
    return report


def write_ingest_report(report: dict[str, Any], *, output_json: str | Path, output_md: str | Path) -> None:
    write_json(output_json, report)
    merge_human_validation_batches.write_report_md(output_md, report)


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def write_pipeline_report_md(path: str | Path, report: dict[str, Any]) -> None:
    eval_rows = [
        [
            item["packet"],
            str(item["labeled_rows"]),
            str(item["unlabeled_rows"]),
            "NA" if item["agreement"] is None else f"{item['agreement']:.3f}",
            "NA" if item["cohen_kappa"] is None else f"{item['cohen_kappa']:.3f}",
            f"[metrics]({item['metrics']})",
        ]
        for item in report["evaluations"]
    ]
    lines = [
        "# Human Validation Pipeline Report",
        "",
        f"Status: `{report['status']}`",
        f"Mode: `{'canonical-write' if report['write_canonical'] else 'dry-run'}`",
        "",
        "## Summary",
        "",
        f"- Ingest status: `{report['ingest']['status']}`",
        f"- Ingest errors: `{report['ingest']['error_count']}`",
        f"- Completed batch rows: `{report['ingest']['completed_batch_rows']}`",
        f"- Merged rows: `{report['ingest']['merged_rows']}`",
        f"- Queue rows before ingest: `{report['queue_rows_before']}`",
        f"- Queue rows after pipeline: `{report['queue_rows_after']}`",
        "",
        "## Evaluation Outputs",
        "",
        markdown_table(["packet", "labeled", "unlabeled", "agreement", "kappa", "metrics"], eval_rows),
        "",
    ]
    if report.get("readiness"):
        lines.extend(
            [
                "## Readiness",
                "",
                f"- Overall status: `{report['readiness']['overall_status']}`",
                f"- Blockers: `{len(report['readiness']['blockers'])}`",
                f"- Warnings: `{len(report['readiness']['warnings'])}`",
                "",
            ]
        )
    if report.get("error_messages"):
        lines.extend(["## Errors", ""])
        for message in report["error_messages"]:
            lines.append(f"- {message}")
        lines.append("")
    lines.extend(["## Next Step", ""])
    if report["status"] != "ok":
        lines.append("Fix the ingest errors, then rerun the pipeline.")
    elif not report["write_canonical"]:
        lines.append(
            "Dry run complete. Inspect preview metrics and the merged sheet copies; rerun with `--write-canonical` only after the batch annotations are approved."
        )
    else:
        lines.append(
            "Canonical sheets and official validation metrics are refreshed. Continue filling any remaining pending batches before final agreement claims."
        )

    output_path = resolve_path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_pipeline(
    *,
    packet_values: list[str] | None = None,
    queue_csv: str | Path = "outputs/day1/paper_assets/human_validation_work_queue.csv",
    queue_md: str | Path = "outputs/day1/paper_assets/human_validation_work_queue.md",
    batch_dir: str | Path = "outputs/day1/human_validation_batches",
    batch_prefix: str = "human_validation_priority",
    batch_size: int = 10,
    ingest_output_dir: str | Path = "outputs/day1/human_validation_batch_ingest",
    ingest_json: str | Path = "outputs/day1/paper_assets/human_validation_batch_ingest_report.json",
    ingest_md: str | Path = "outputs/day1/paper_assets/human_validation_batch_ingest_report.md",
    preview_eval_dir: str | Path = "outputs/day1/human_validation_batch_ingest/evaluation",
    pipeline_json: str | Path = "outputs/day1/paper_assets/human_validation_pipeline_report.json",
    pipeline_md: str | Path = "outputs/day1/paper_assets/human_validation_pipeline_report.md",
    readiness_json: str | Path = "outputs/day1/paper_assets/paper_readiness_audit.json",
    readiness_md: str | Path = "outputs/day1/paper_assets/paper_readiness_audit.md",
    write_canonical: bool = False,
    allow_overwrite: bool = False,
    run_readiness: bool = True,
) -> dict[str, Any]:
    packet_specs = parse_packet_specs(packet_values)
    queue_before = write_queue(packet_specs, output_csv=queue_csv, output_md=queue_md)

    ingest_report = merge_human_validation_batches.ingest_batches(
        queue_path=queue_csv,
        batch_dir=batch_dir,
        output_dir=ingest_output_dir,
        write_canonical=write_canonical,
        allow_overwrite=allow_overwrite,
    )
    write_ingest_report(ingest_report, output_json=ingest_json, output_md=ingest_md)

    error_messages = list(ingest_report.get("error_messages", []))
    evaluations: list[dict[str, Any]] = []
    queue_after = queue_before
    readiness_report: dict[str, Any] | None = None

    if not error_messages:
        evaluations = evaluate_packets(
            packet_specs,
            use_canonical=write_canonical,
            ingest_output_dir=ingest_output_dir,
            preview_eval_dir=preview_eval_dir,
        )
        if write_canonical:
            queue_after = write_queue(packet_specs, output_csv=queue_csv, output_md=queue_md)
            export_human_validation_batches.export_batches(
                queue_path=queue_csv,
                output_dir=batch_dir,
                prefix=batch_prefix,
                batch_size=batch_size,
            )
            current_ingest = merge_human_validation_batches.ingest_batches(
                queue_path=queue_csv,
                batch_dir=batch_dir,
                output_dir=ingest_output_dir,
                write_canonical=False,
                allow_overwrite=allow_overwrite,
            )
            write_ingest_report(current_ingest, output_json=ingest_json, output_md=ingest_md)
        if run_readiness:
            readiness_report = run_readiness_audit(output_json=readiness_json, output_md=readiness_md)

    report = {
        "status": "ok" if not error_messages else "error",
        "write_canonical": write_canonical,
        "queue_rows_before": len(queue_before),
        "queue_rows_after": len(queue_after),
        "ingest": ingest_report,
        "evaluations": evaluations,
        "readiness": readiness_report,
        "error_messages": error_messages,
    }
    write_json(pipeline_json, report)
    write_pipeline_report_md(pipeline_md, report)
    return report


def main() -> None:
    args = parse_args()
    report = run_pipeline(
        packet_values=args.packet,
        queue_csv=args.queue_csv,
        queue_md=args.queue_md,
        batch_dir=args.batch_dir,
        batch_prefix=args.batch_prefix,
        batch_size=args.batch_size,
        ingest_output_dir=args.ingest_output_dir,
        ingest_json=args.ingest_json,
        ingest_md=args.ingest_md,
        preview_eval_dir=args.preview_eval_dir,
        pipeline_json=args.pipeline_json,
        pipeline_md=args.pipeline_md,
        readiness_json=args.readiness_json,
        readiness_md=args.readiness_md,
        write_canonical=args.write_canonical,
        allow_overwrite=args.allow_overwrite,
        run_readiness=not args.skip_readiness,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    if args.fail_on_error and report["status"] != "ok":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
