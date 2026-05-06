from __future__ import annotations

import argparse
import csv
import html
import re
import textwrap
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SIGNOFF = ROOT / "outputs/day1/ai_assisted_validation_signoff/ai_assisted_validation_signoff.tsv"
DEFAULT_OUTPUT = ROOT / "outputs/day1/paper_assets/figure1_revision_tracking.svg"
DEFAULT_ISSUE_ID = "w7P92BEsb2__r01"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render Figure 1 schematic for RevTrack.")
    parser.add_argument("--signoff", default=str(DEFAULT_SIGNOFF))
    parser.add_argument("--issue-id", default=DEFAULT_ISSUE_ID)
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    return parser.parse_args()


def compact(value: str | None) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def load_row(path: str | Path, issue_id: str) -> dict[str, str]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        if row.get("issue_id") == issue_id:
            return row
    raise KeyError(f"issue_id not found: {issue_id}")


def label_text(text: str, width: int) -> list[str]:
    return textwrap.wrap(compact(text), width=width, break_long_words=False, break_on_hyphens=False)


def tspan_lines(lines: list[str], *, x: int, y: int, size: int = 15, line_gap: int = 22) -> str:
    parts = []
    for index, line in enumerate(lines):
        parts.append(
            f'<text x="{x}" y="{y + index * line_gap}" '
            f'font-family="Source Sans 3, Helvetica Neue, Arial, sans-serif" font-size="{size}" fill="#17202a">'
            f"{html.escape(line)}</text>"
        )
    return "\n".join(parts)


def card(
    *,
    x: int,
    y: int,
    w: int,
    h: int,
    title: str,
    subtitle: str,
    body: str,
    accent: str,
    fill: str = "#ffffff",
    body_size: int = 15,
) -> str:
    wrap_width = max(24, int((w - 36) / 7.0))
    lines = label_text(body, wrap_width)
    return "\n".join(
        [
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{fill}" stroke="#c7d0da" stroke-width="1.4"/>',
            f'<rect x="{x}" y="{y}" width="{w}" height="7" rx="3.5" fill="{accent}"/>',
            f'<text x="{x + 18}" y="{y + 34}" font-family="Source Sans 3, Helvetica Neue, Arial, sans-serif" font-size="17" font-weight="800" fill="#111827">{html.escape(title)}</text>',
            f'<text x="{x + 18}" y="{y + 60}" font-family="Source Sans 3, Helvetica Neue, Arial, sans-serif" font-size="12" font-weight="800" letter-spacing="1.2" fill="{accent}">{html.escape(subtitle.upper())}</text>',
            tspan_lines(lines, x=x + 18, y=y + 88, size=body_size, line_gap=22),
        ]
    )


def arrow(x1: int, y1: int, x2: int, y2: int, color: str = "#435466") -> str:
    return "\n".join(
        [
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="2.5" marker-end="url(#arrow)"/>',
        ]
    )


def badge(x: int, y: int, text: str, fill: str, fg: str = "#ffffff") -> str:
    return (
        f'<rect x="{x}" y="{y}" width="{len(text) * 8 + 34}" height="28" rx="14" fill="{fill}"/>'
        f'<text x="{x + 17}" y="{y + 19}" font-family="Source Sans 3, Helvetica Neue, Arial, sans-serif" '
        f'font-size="13" font-weight="800" fill="{fg}">{html.escape(text)}</text>'
    )


def pipeline_step(x: int, y: int, number: str, title: str, note: str, accent: str) -> str:
    lines = label_text(note, 24)
    return "\n".join(
        [
            f'<circle cx="{x + 24}" cy="{y + 24}" r="22" fill="{accent}"/>',
            f'<text x="{x + 24}" y="{y + 31}" text-anchor="middle" font-family="Source Sans 3, Helvetica Neue, Arial, sans-serif" font-size="18" font-weight="900" fill="#ffffff">{html.escape(number)}</text>',
            f'<text x="{x + 58}" y="{y + 21}" font-family="Source Sans 3, Helvetica Neue, Arial, sans-serif" font-size="15" font-weight="800" fill="#111827">{html.escape(title)}</text>',
            tspan_lines(lines[:2], x=x + 58, y=y + 45, size=12, line_gap=16),
        ]
    )


def render(row: dict[str, str]) -> str:
    concern = (
        "The review asks for direct computational-cost evidence, not just a claim "
        "that the revised method is efficient."
    )
    response = (
        "The authors say they added a cost comparison and point to the revised "
        "experiment section."
    )
    revision = (
        "New revision evidence adds Figure 6 and Lines 510-530, comparing error "
        "and computational cost."
    )
    stale_model = (
        "A static judge can repeat the old criticism because the original concern "
        "still sounds plausible in isolation."
    )
    target = (
        "RevTrack label: fixed. The exact cost-comparison concern is retired because the "
        "new evidence directly answers it."
    )

    width, height = 1320, 760
    title = compact(row.get("paper_title", "")) or "selected OpenReview paper"
    issue_id = compact(row.get("issue_id", "")) or "selected issue"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<defs>
  <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
    <path d="M0,0 L0,6 L9,3 z" fill="#435466"/>
  </marker>
  <filter id="shadow" x="-5%" y="-5%" width="110%" height="120%">
    <feDropShadow dx="0" dy="4" stdDeviation="5" flood-color="#1f2937" flood-opacity="0.12"/>
  </filter>
</defs>
<rect width="100%" height="100%" fill="#f4f7fb"/>
<path d="M0 0 H1320 V154 C1080 132 914 120 702 144 C458 172 244 152 0 118 Z" fill="#e6eef8"/>
<text x="54" y="54" font-family="Source Sans 3, Helvetica Neue, Arial, sans-serif" font-size="29" font-weight="900" fill="#0f172a">A review concern can become stale after revision</text>
<text x="54" y="86" font-family="Source Sans 3, Helvetica Neue, Arial, sans-serif" font-size="15" fill="#475569">RevTrack evaluates whether a scientific criticism still holds after aligning the review, response, and revised evidence.</text>
<text x="54" y="112" font-family="Source Sans 3, Helvetica Neue, Arial, sans-serif" font-size="13" fill="#64748b">Example: {html.escape(title)} ({html.escape(issue_id)})</text>

<g filter="url(#shadow)">
{card(x=54, y=156, w=285, h=226, title="Original review concern", subtitle="Before revision", body=concern, accent="#2563eb", fill="#ffffff")}
{card(x=374, y=156, w=285, h=226, title="Author response", subtitle="Claimed fix", body=response, accent="#0891b2", fill="#ffffff")}
{card(x=374, y=414, w=285, h=206, title="Revised paper evidence", subtitle="Observed fix", body=revision, accent="#16a34a", fill="#ffffff")}
{card(x=704, y=156, w=255, h=226, title="Static LLM trap", subtitle="Wrong abstraction", body=stale_model, accent="#d97706", fill="#fff7ed")}
{card(x=1004, y=156, w=262, h=226, title="RevTrack target", subtitle="Issue status", body=target, accent="#15803d", fill="#f0fdf4")}
</g>

{arrow(341, 269, 372, 269)}
{arrow(660, 269, 702, 269)}
{arrow(660, 514, 1002, 281, "#15803d")}
{arrow(960, 269, 1002, 269)}

{badge(735, 338, "stale criticism", "#d97706")}
{badge(1030, 338, "fixed", "#15803d")}

<rect x="54" y="654" width="1212" height="74" rx="16" fill="#ffffff" stroke="#c7d0da" stroke-width="1.4"/>
{pipeline_step(78, 669, "1", "Extract issue", "One reviewer concern", "#2563eb")}
{pipeline_step(302, 669, "2", "Align response", "Find claimed fix", "#0891b2")}
{pipeline_step(528, 669, "3", "Check revision", "Require paper evidence", "#16a34a")}
{pipeline_step(760, 669, "4", "Assign status", "fixed / partial / unresolved / regressed", "#0f766e")}
{pipeline_step(1034, 669, "5", "Gate claims", "Only evidence-backed results", "#334155")}

<text x="704" y="430" font-family="Source Sans 3, Helvetica Neue, Arial, sans-serif" font-size="17" font-weight="900" fill="#111827">Key distinction</text>
<text x="704" y="462" font-family="Source Sans 3, Helvetica Neue, Arial, sans-serif" font-size="15" fill="#17202a">The label is not based on whether the old concern sounds reasonable.</text>
<text x="704" y="492" font-family="Source Sans 3, Helvetica Neue, Arial, sans-serif" font-size="15" fill="#17202a">It is based on whether new revision evidence resolves that exact concern.</text>
</svg>
"""


def main() -> None:
    args = parse_args()
    row = load_row(args.signoff, args.issue_id)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render(row), encoding="utf-8")
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
