from __future__ import annotations

import argparse
import csv
import html
import math
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
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
BATCH_FIELDS = ["batch_rank", "global_queue_rank", "source_packet", *BLIND_FIELDS]
MANIFEST_FIELDS = [
    "batch_id",
    "rows",
    "queue_rank_start",
    "queue_rank_end",
    "source_packets",
    "blind_sheet",
    "packet_html",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Split the active human-validation queue into small blind review batches."
    )
    parser.add_argument(
        "--queue",
        default="outputs/day1/paper_assets/human_validation_work_queue.csv",
        help="CSV queue exported by export_human_validation_queue.py.",
    )
    parser.add_argument("--output-dir", default="outputs/day1/human_validation_batches")
    parser.add_argument("--prefix", default="human_validation_priority")
    parser.add_argument("--batch-size", type=int, default=10)
    parser.add_argument(
        "--max-batches",
        type=int,
        help="Optional cap for exporting only the first N priority batches.",
    )
    return parser.parse_args()


def resolve_path(path: str | Path) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else ROOT / candidate


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
        writer.writerows(rows)


def write_csv(path: str | Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def integer(value: str | int | None, default: int = 999999) -> int:
    if value in (None, ""):
        return default
    try:
        return int(value)
    except ValueError:
        return default


def relpath(path: str | Path) -> str:
    resolved = Path(path)
    try:
        return str(resolved.relative_to(ROOT))
    except ValueError:
        return str(resolved)


def pending_queue_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    pending = [
        row
        for row in rows
        if row.get("status", "").strip().lower() == "pending"
        and row.get("human_label_present", "").strip().lower() != "true"
    ]
    return sorted(pending, key=lambda row: integer(row.get("queue_rank")))


def chunk_rows(rows: list[dict[str, str]], batch_size: int, max_batches: int | None = None) -> list[list[dict[str, str]]]:
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    batches = [rows[index : index + batch_size] for index in range(0, len(rows), batch_size)]
    return batches[:max_batches] if max_batches is not None else batches


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


def as_batch_row(
    *,
    batch_rank: int,
    queue_row: dict[str, str],
    blind_row: dict[str, str],
) -> dict[str, str]:
    output = {
        "batch_rank": str(batch_rank),
        "global_queue_rank": queue_row.get("queue_rank", ""),
        "source_packet": queue_row.get("packet", ""),
    }
    for field in BLIND_FIELDS:
        if field in {"human_label", "human_confidence", "evidence_span", "notes"}:
            output[field] = blind_row.get(field, "")
        else:
            output[field] = blind_row.get(field, "")
    return output


def build_batch_rows(
    batch_queue_rows: list[dict[str, str]],
    blind_index: dict[tuple[str, str], dict[str, str]],
) -> list[dict[str, str]]:
    batch_rows: list[dict[str, str]] = []
    for batch_rank, queue_row in enumerate(batch_queue_rows, start=1):
        blind_sheet = queue_row.get("blind_sheet", "").strip()
        issue_id = queue_row.get("issue_id", "").strip()
        blind_row = blind_index.get((blind_sheet, issue_id))
        if blind_row is None:
            raise KeyError(f"Missing blind row for issue_id={issue_id!r} in {blind_sheet!r}")
        batch_rows.append(
            as_batch_row(
                batch_rank=batch_rank,
                queue_row=queue_row,
                blind_row=blind_row,
            )
        )
    return batch_rows


def text_block(title: str, value: str) -> str:
    if not value:
        return ""
    return (
        '<section class="text-block">'
        f"<h3>{html.escape(title)}</h3>"
        f"<pre>{html.escape(value)}</pre>"
        "</section>"
    )


def render_batch_html(rows: list[dict[str, str]], *, title: str, sheet_name: str) -> str:
    cards = []
    for row in rows:
        cards.append(
            '<article class="item">'
            '<div class="meta">'
            f"<span>Batch {html.escape(row.get('batch_rank', ''))}</span>"
            f"<span>Queue {html.escape(row.get('global_queue_rank', ''))}</span>"
            f"<span>{html.escape(row.get('issue_id', ''))}</span>"
            "</div>"
            f"<h2>{html.escape(row.get('paper_title', ''))}</h2>"
            '<div class="review-meta">'
            f"<span>{html.escape(row.get('review_rating', ''))}</span>"
            f"<span>{html.escape(row.get('review_confidence', ''))}</span>"
            "</div>"
            + text_block("Review Concern", row.get("review_excerpt", ""))
            + text_block("Top Response Chunk", row.get("top_response_excerpt", ""))
            + text_block("Aligned Response Context", row.get("aligned_response_excerpt", ""))
            + text_block("Revision Summary", row.get("revision_summary", ""))
            + '<div class="fill-box">'
            "<strong>Fields to complete in the TSV:</strong> human_label, human_confidence, evidence_span, notes."
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
      --accent: #136f63;
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
    .item {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 18px;
      margin: 16px 0;
    }}
    .meta, .review-meta {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      color: var(--muted);
      font-size: 13px;
    }}
    .meta span, .review-meta span {{
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
      background: #eef7f4;
      color: var(--ink);
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <h1>{html.escape(title)}</h1>
      <div class="sub">Sheet: {html.escape(sheet_name)}. This packet is blind: it omits assistant labels, model labels, audit buckets, and hidden keys.</div>
    </header>
    {''.join(cards)}
  </main>
</body>
</html>
"""


def batch_id(prefix: str, index: int) -> str:
    return f"{prefix}_batch_{index:02d}"


def build_manifest_row(
    *,
    batch_name: str,
    batch_rows: list[dict[str, str]],
    blind_sheet: Path,
    packet_html: Path,
) -> dict[str, str]:
    ranks = [integer(row.get("global_queue_rank")) for row in batch_rows]
    packets = sorted({row.get("source_packet", "") for row in batch_rows if row.get("source_packet", "")})
    return {
        "batch_id": batch_name,
        "rows": str(len(batch_rows)),
        "queue_rank_start": str(min(ranks)),
        "queue_rank_end": str(max(ranks)),
        "source_packets": "; ".join(packets),
        "blind_sheet": relpath(blind_sheet),
        "packet_html": relpath(packet_html),
    }


def write_manifest_md(path: str | Path, manifest_rows: list[dict[str, str]], *, total_pending: int) -> None:
    lines = [
        "# Human Validation Batch Manifest",
        "",
        "These are blind priority batches derived from the assistant-generated work queue. They do not contain assistant labels, model predictions, audit buckets, or hidden keys.",
        "",
        f"- Pending queue rows covered by exported batches: `{sum(int(row['rows']) for row in manifest_rows)}`",
        f"- Total pending rows in queue: `{total_pending}`",
        f"- Batches: `{len(manifest_rows)}`",
        "",
        "| batch | rows | queue ranks | source packets | blind sheet | packet |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in manifest_rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    row["batch_id"],
                    row["rows"],
                    f"{row['queue_rank_start']}-{row['queue_rank_end']}",
                    row["source_packets"],
                    f"[tsv]({Path(row['blind_sheet']).name})",
                    f"[html]({Path(row['packet_html']).name})",
                ]
            )
            + " |"
        )
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def remove_stale_batch_files(output_root: Path, prefix: str) -> None:
    output_root.mkdir(parents=True, exist_ok=True)
    for pattern in [
        f"{prefix}_batch_*_blind.tsv",
        f"{prefix}_batch_*_packet.html",
    ]:
        for path in output_root.glob(pattern):
            if path.is_file():
                path.unlink()


def export_batches(
    *,
    queue_path: str | Path,
    output_dir: str | Path,
    prefix: str,
    batch_size: int,
    max_batches: int | None = None,
) -> list[dict[str, str]]:
    queue_rows = pending_queue_rows(load_csv(resolve_path(queue_path)))
    batches = chunk_rows(queue_rows, batch_size=batch_size, max_batches=max_batches)
    blind_index = load_blind_index(queue_rows)
    output_root = resolve_path(output_dir)
    remove_stale_batch_files(output_root, prefix)
    manifest_rows: list[dict[str, str]] = []

    for index, batch_queue_rows in enumerate(batches, start=1):
        name = batch_id(prefix, index)
        rows = build_batch_rows(batch_queue_rows, blind_index)
        blind_sheet = output_root / f"{name}_blind.tsv"
        packet_html = output_root / f"{name}_packet.html"
        write_tsv(blind_sheet, rows, BATCH_FIELDS)
        packet_html.write_text(
            render_batch_html(
                rows,
                title=f"{name} blind packet",
                sheet_name=blind_sheet.name,
            ),
            encoding="utf-8",
        )
        manifest_rows.append(
            build_manifest_row(
                batch_name=name,
                batch_rows=rows,
                blind_sheet=blind_sheet,
                packet_html=packet_html,
            )
        )

    write_csv(output_root / f"{prefix}_manifest.csv", manifest_rows, MANIFEST_FIELDS)
    write_manifest_md(output_root / f"{prefix}_manifest.md", manifest_rows, total_pending=len(queue_rows))
    return manifest_rows


def main() -> None:
    args = parse_args()
    manifest_rows = export_batches(
        queue_path=args.queue,
        output_dir=args.output_dir,
        prefix=args.prefix,
        batch_size=args.batch_size,
        max_batches=args.max_batches,
    )
    total = sum(int(row["rows"]) for row in manifest_rows)
    batch_size = args.batch_size if args.batch_size > 0 else 1
    expected_batches = math.ceil(total / batch_size) if total else 0
    print(f"Wrote {total} blind validation rows across {len(manifest_rows)} batches")
    if args.max_batches is not None and len(manifest_rows) < expected_batches:
        print(f"Export capped at {args.max_batches} batches")


if __name__ == "__main__":
    main()
