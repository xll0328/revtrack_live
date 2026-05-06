from __future__ import annotations

import argparse
import csv
import html
import re
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
VALID_LABELS = {"fixed", "partially_fixed", "unresolved", "regressed"}
MODEL_FIELDS = [
    "heuristic_label",
    "tfidf_label",
    "modernbert_label",
    "mpnet_label",
    "issue_ledger_label",
    "structured_label",
]
SIGNOFF_FIELDS = [
    "signoff_rank",
    "queue_rank",
    "packet",
    "issue_id",
    "paper_title",
    "review_rating",
    "review_confidence",
    "review_excerpt",
    "top_response_excerpt",
    "aligned_response_excerpt",
    "revision_summary",
    "assistant_label",
    "assistant_evidence_span",
    "assistant_notes",
    "suggested_label",
    "audit_bucket",
    "audit_score",
    "priority_score",
    "model_snapshot",
    "reviewer_decision",
    "reviewer_final_label",
    "reviewer_confidence",
    "reviewer_evidence_span",
    "reviewer_notes",
    "signoff_status",
]
MANIFEST_FIELDS = [
    "artifact",
    "rows",
    "needs_human_review",
    "key_evidence_rows",
    "context_fallback_evidence_rows",
    "assistant_distribution",
    "audit_bucket_distribution",
    "signoff_sheet",
    "signoff_packet",
]
DEFAULT_PACKET_KEYS = {
    "ICLR 2024 v1": "experiments/day1/iclr2024_human_validation_v1_key.tsv",
    "ICLR 2025 repro v2": "experiments/day1/iclr2025_repro_human_validation_v2_key.tsv",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export a non-blind AI-assisted validation signoff sheet for final human review."
    )
    parser.add_argument(
        "--queue",
        default="outputs/day1/paper_assets/human_validation_work_queue.csv",
        help="CSV queue exported by export_human_validation_queue.py.",
    )
    parser.add_argument(
        "--packet-key",
        action="append",
        default=None,
        help="Mapping as packet_name:key_tsv. May be repeated. Defaults to active packets.",
    )
    parser.add_argument("--output-dir", default="outputs/day1/ai_assisted_validation_signoff")
    parser.add_argument("--prefix", default="ai_assisted_validation_signoff")
    parser.add_argument("--include-done", action="store_true")
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


def load_csv(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def load_tsv(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: str | Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fieldnames} for row in rows)


def write_csv(path: str | Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fieldnames} for row in rows)


def integer(value: str | int | None, default: int = 999999) -> int:
    if value in (None, ""):
        return default
    try:
        return int(value)
    except ValueError:
        return default


def normalize_label(value: str | None) -> str:
    return (value or "").strip().lower()


def parse_packet_keys(values: list[str] | None) -> dict[str, Path]:
    if values is None:
        return {name: resolve_path(path) for name, path in DEFAULT_PACKET_KEYS.items()}
    packet_keys: dict[str, Path] = {}
    for value in values:
        if ":" not in value:
            raise ValueError("packet-key must be packet_name:key_tsv")
        name, path = value.split(":", 1)
        packet_keys[name] = resolve_path(path)
    return packet_keys


def by_issue_id(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {
        row["issue_id"].strip(): row
        for row in rows
        if row.get("issue_id", "").strip()
    }


def load_key_index(packet_keys: dict[str, Path]) -> dict[tuple[str, str], dict[str, str]]:
    index: dict[tuple[str, str], dict[str, str]] = {}
    for packet, path in packet_keys.items():
        for issue_id, row in by_issue_id(load_tsv(path)).items():
            index[(packet, issue_id)] = row
    return index


def load_blind_index(queue_rows: list[dict[str, str]]) -> dict[tuple[str, str], dict[str, str]]:
    rows_by_sheet: dict[str, list[dict[str, str]]] = {}
    for queue_row in queue_rows:
        blind_sheet = queue_row.get("blind_sheet", "").strip()
        if blind_sheet and blind_sheet not in rows_by_sheet:
            rows_by_sheet[blind_sheet] = load_tsv(resolve_path(blind_sheet))

    index: dict[tuple[str, str], dict[str, str]] = {}
    for blind_sheet, rows in rows_by_sheet.items():
        for row in rows:
            issue_id = row.get("issue_id", "").strip()
            if issue_id:
                index[(blind_sheet, issue_id)] = row
    return index


def model_snapshot(row: dict[str, str]) -> str:
    parts = []
    for field in MODEL_FIELDS:
        value = normalize_label(row.get(field))
        if value:
            parts.append(f"{field.removesuffix('_label')}={value}")
    return "; ".join(parts)


def compact_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def clip_text(value: str, max_chars: int = 360) -> str:
    text = compact_text(value)
    if len(text) <= max_chars:
        return text
    clipped = text[:max_chars].rsplit(" ", 1)[0]
    return f"{clipped}..."


def assistant_evidence_span(key: dict[str, str], blind: dict[str, str]) -> str:
    existing = compact_text(key.get("assistant_evidence_span", ""))
    if existing:
        return existing
    fallback_sources = [
        ("aligned response context", blind.get("aligned_response_excerpt") or key.get("aligned_response_excerpt", "")),
        ("top response chunk", blind.get("top_response_excerpt") or key.get("top_response_excerpt", "")),
        ("revision summary", blind.get("revision_summary") or key.get("revision_summary", "")),
        ("assistant note", key.get("assistant_notes", "")),
    ]
    for source_name, value in fallback_sources:
        clipped = clip_text(value)
        if clipped:
            return f"Context fallback from {source_name}: {clipped}"
    return ""


def signoff_status(row: dict[str, str]) -> str:
    decision = row.get("reviewer_decision", "").strip().lower()
    final_label = normalize_label(row.get("reviewer_final_label"))
    if decision in {"accept", "revise", "defer"} and (decision == "defer" or final_label in VALID_LABELS):
        return "reviewed"
    return "needs_human_review"


def queue_rows_for_signoff(rows: list[dict[str, str]], *, include_done: bool) -> list[dict[str, str]]:
    selected = [
        row
        for row in rows
        if include_done or row.get("status", "").strip().lower() == "pending"
    ]
    return sorted(selected, key=lambda row: integer(row.get("queue_rank")))


def build_signoff_rows(
    *,
    queue_rows: list[dict[str, str]],
    key_index: dict[tuple[str, str], dict[str, str]],
    blind_index: dict[tuple[str, str], dict[str, str]] | None = None,
    include_done: bool = False,
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    blind_index = blind_index or {}
    for signoff_rank, queue_row in enumerate(queue_rows_for_signoff(queue_rows, include_done=include_done), start=1):
        packet = queue_row.get("packet", "").strip()
        issue_id = queue_row.get("issue_id", "").strip()
        key = key_index.get((packet, issue_id), {})
        blind = blind_index.get((queue_row.get("blind_sheet", "").strip(), issue_id), {})
        assistant = normalize_label(key.get("assistant_label") or queue_row.get("assistant_label"))
        row = {
            "signoff_rank": str(signoff_rank),
            "queue_rank": queue_row.get("queue_rank", ""),
            "packet": packet,
            "issue_id": issue_id,
            "paper_title": queue_row.get("paper_title", ""),
            "review_rating": queue_row.get("review_rating", ""),
            "review_confidence": queue_row.get("review_confidence", ""),
            "review_excerpt": blind.get("review_excerpt") or key.get("review_excerpt", ""),
            "top_response_excerpt": blind.get("top_response_excerpt") or key.get("top_response_excerpt", ""),
            "aligned_response_excerpt": blind.get("aligned_response_excerpt") or key.get("aligned_response_excerpt", ""),
            "revision_summary": blind.get("revision_summary") or key.get("revision_summary", ""),
            "assistant_label": assistant,
            "assistant_evidence_span": assistant_evidence_span(key, blind),
            "assistant_notes": key.get("assistant_notes", ""),
            "suggested_label": normalize_label(key.get("suggested_label") or queue_row.get("suggested_label")),
            "audit_bucket": key.get("audit_bucket") or queue_row.get("audit_bucket", ""),
            "audit_score": key.get("audit_score") or queue_row.get("audit_score", ""),
            "priority_score": key.get("priority_score") or queue_row.get("priority_score", ""),
            "model_snapshot": model_snapshot(key),
            "reviewer_decision": "",
            "reviewer_final_label": "",
            "reviewer_confidence": "",
            "reviewer_evidence_span": "",
            "reviewer_notes": "",
            "signoff_status": "needs_human_review",
        }
        rows.append(row)
    return rows


def text_block(title: str, value: str) -> str:
    if not value:
        return ""
    return (
        '<section class="text-block">'
        f"<h3>{html.escape(title)}</h3>"
        f"<pre>{html.escape(value)}</pre>"
        "</section>"
    )


def render_html(rows: list[dict[str, str]], *, title: str, sheet_name: str) -> str:
    cards = []
    for row in rows:
        cards.append(
            '<article class="item">'
            '<div class="meta">'
            f"<span>Signoff {html.escape(row.get('signoff_rank', ''))}</span>"
            f"<span>Queue {html.escape(row.get('queue_rank', ''))}</span>"
            f"<span>{html.escape(row.get('packet', ''))}</span>"
            f"<span>{html.escape(row.get('issue_id', ''))}</span>"
            "</div>"
            f"<h2>{html.escape(row.get('paper_title', ''))}</h2>"
            '<div class="label-row">'
            f"<span>assistant: {html.escape(row.get('assistant_label', ''))}</span>"
            f"<span>suggested: {html.escape(row.get('suggested_label', ''))}</span>"
            f"<span>{html.escape(row.get('audit_bucket', ''))}</span>"
            "</div>"
            + text_block("Review Concern", row.get("review_excerpt", ""))
            + text_block("Top Response Chunk", row.get("top_response_excerpt", ""))
            + text_block("Aligned Response Context", row.get("aligned_response_excerpt", ""))
            + text_block("Revision Summary", row.get("revision_summary", ""))
            + text_block("Assistant Evidence Span", row.get("assistant_evidence_span", ""))
            + text_block("Assistant Notes", row.get("assistant_notes", ""))
            + text_block("Model Snapshot", row.get("model_snapshot", ""))
            + '<div class="fill-box">'
            "<strong>Human signoff fields:</strong> reviewer_decision, reviewer_final_label, reviewer_confidence, reviewer_evidence_span, reviewer_notes."
            "</div>"
            "</article>"
        )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    :root {{
      --bg: #f7f7f4;
      --panel: #ffffff;
      --ink: #1d2430;
      --muted: #596273;
      --line: #d8dde6;
      --accent: #8a4b10;
      --warn: #fff1dc;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Arial, Helvetica, sans-serif;
      color: var(--ink);
      background: var(--bg);
    }}
    main {{
      width: min(1180px, calc(100vw - 32px));
      margin: 24px auto 48px;
    }}
    header {{
      border-bottom: 2px solid var(--accent);
      padding-bottom: 16px;
      margin-bottom: 18px;
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: 30px;
      letter-spacing: 0;
    }}
    .sub {{
      color: var(--muted);
      line-height: 1.45;
    }}
    .warning {{
      margin-top: 12px;
      padding: 10px 12px;
      border-left: 4px solid var(--accent);
      background: var(--warn);
    }}
    .item {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 18px;
      margin: 16px 0;
    }}
    .meta, .label-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      color: var(--muted);
      font-size: 13px;
    }}
    .meta span, .label-row span {{
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 4px 8px;
      background: #fafafa;
    }}
    h2 {{
      margin: 12px 0;
      font-size: 20px;
      letter-spacing: 0;
    }}
    h3 {{
      margin: 0 0 6px;
      font-size: 14px;
      color: var(--accent);
      letter-spacing: 0;
    }}
    pre {{
      margin: 0;
      white-space: pre-wrap;
      word-break: break-word;
      font-family: Arial, Helvetica, sans-serif;
      line-height: 1.45;
    }}
    .text-block {{
      border-top: 1px solid var(--line);
      padding-top: 12px;
      margin-top: 12px;
    }}
    .fill-box {{
      margin-top: 14px;
      padding: 10px 12px;
      border-left: 4px solid var(--accent);
      background: var(--warn);
      color: var(--ink);
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <h1>{html.escape(title)}</h1>
      <div class="sub">Sheet: {html.escape(sheet_name)}.</div>
      <div class="warning">This is a non-blind AI-assisted signoff artifact. It exposes assistant labels and must not be reported as independent human validation.</div>
    </header>
    {''.join(cards)}
  </main>
</body>
</html>
"""


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def write_manifest_md(path: str | Path, manifest: dict[str, str]) -> None:
    lines = [
        "# AI-Assisted Validation Signoff Manifest",
        "",
        "This artifact is for final human review of assistant-generated judgments. It is non-blind, exposes assistant/model evidence, and must not be reported as independent human validation.",
        "",
        f"- Rows: `{manifest['rows']}`",
        f"- Needs human review: `{manifest['needs_human_review']}`",
        f"- Key evidence rows: `{manifest['key_evidence_rows']}`",
        f"- Context fallback evidence rows: `{manifest['context_fallback_evidence_rows']}`",
        f"- Signoff sheet: [{Path(manifest['signoff_sheet']).name}]({manifest['signoff_sheet']})",
        f"- Signoff packet: [{Path(manifest['signoff_packet']).name}]({manifest['signoff_packet']})",
        "",
        "## Distributions",
        "",
        markdown_table(
            ["field", "distribution"],
            [
                ["assistant labels", manifest["assistant_distribution"]],
                ["audit buckets", manifest["audit_bucket_distribution"]],
            ],
        ),
        "",
        "## Required Human Action",
        "",
        "For each row, fill `reviewer_decision` as `accept`, `revise`, or `defer`. Fill `reviewer_final_label`, `reviewer_confidence`, `reviewer_evidence_span`, and `reviewer_notes` for accepted or revised rows.",
    ]
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def distribution_text(counter: Counter[str]) -> str:
    return " / ".join(f"{key} {count}" for key, count in sorted(counter.items())) or "none"


def build_manifest(
    *,
    rows: list[dict[str, str]],
    signoff_sheet: Path,
    signoff_packet: Path,
) -> dict[str, str]:
    return {
        "artifact": "ai_assisted_validation_signoff",
        "rows": str(len(rows)),
        "needs_human_review": str(sum(1 for row in rows if row.get("signoff_status") == "needs_human_review")),
        "key_evidence_rows": str(
            sum(
                1
                for row in rows
                if row.get("assistant_evidence_span", "")
                and not row.get("assistant_evidence_span", "").startswith("Context fallback from ")
            )
        ),
        "context_fallback_evidence_rows": str(
            sum(
                1
                for row in rows
                if row.get("assistant_evidence_span", "").startswith("Context fallback from ")
            )
        ),
        "assistant_distribution": distribution_text(Counter(row.get("assistant_label", "") for row in rows)),
        "audit_bucket_distribution": distribution_text(Counter(row.get("audit_bucket", "") for row in rows)),
        "signoff_sheet": relpath(signoff_sheet),
        "signoff_packet": relpath(signoff_packet),
    }


def export_signoff(
    *,
    queue_path: str | Path,
    packet_keys: dict[str, Path],
    output_dir: str | Path,
    prefix: str,
    include_done: bool = False,
) -> dict[str, str]:
    queue_rows = load_csv(resolve_path(queue_path))
    key_index = load_key_index(packet_keys)
    blind_index = load_blind_index(queue_rows)
    rows = build_signoff_rows(
        queue_rows=queue_rows,
        key_index=key_index,
        blind_index=blind_index,
        include_done=include_done,
    )
    output_root = resolve_path(output_dir)
    signoff_sheet = output_root / f"{prefix}.tsv"
    signoff_packet = output_root / f"{prefix}.html"
    manifest_csv = output_root / f"{prefix}_manifest.csv"
    manifest_md = output_root / f"{prefix}_manifest.md"
    write_tsv(signoff_sheet, rows, SIGNOFF_FIELDS)
    signoff_packet.parent.mkdir(parents=True, exist_ok=True)
    signoff_packet.write_text(
        render_html(rows, title="AI-assisted validation signoff", sheet_name=signoff_sheet.name),
        encoding="utf-8",
    )
    manifest = build_manifest(rows=rows, signoff_sheet=signoff_sheet, signoff_packet=signoff_packet)
    write_csv(manifest_csv, [manifest], MANIFEST_FIELDS)
    write_manifest_md(manifest_md, manifest)
    return manifest


def main() -> None:
    args = parse_args()
    manifest = export_signoff(
        queue_path=args.queue,
        packet_keys=parse_packet_keys(args.packet_key),
        output_dir=args.output_dir,
        prefix=args.prefix,
        include_done=args.include_done,
    )
    print(
        f"Wrote {manifest['rows']} AI-assisted signoff rows to "
        f"{manifest['signoff_sheet']}"
    )


if __name__ == "__main__":
    main()
