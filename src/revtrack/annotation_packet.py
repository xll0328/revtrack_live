from __future__ import annotations

import csv
import html
from collections import Counter
from pathlib import Path
from typing import Any

from revtrack.schema import LABELS

MODEL_FIELDS = (
    ("heuristic_label", "heuristic"),
    ("tfidf_label", "tfidf"),
    ("modernbert_label", "modernbert"),
    ("mpnet_label", "mpnet"),
    ("issue_ledger_label", "issue-ledger"),
    ("structured_label", "structured"),
)

LABEL_CLASS = {
    "fixed": "fixed",
    "partially_fixed": "partially-fixed",
    "unresolved": "unresolved",
    "regressed": "regressed",
    "missing": "missing",
}

TEXT_FIELDS = (
    "review_excerpt",
    "top_response_excerpt",
    "aligned_response_excerpt",
    "revision_summary",
    "silver_comment",
    "evidence_span",
    "notes",
    "suggestion_note",
)


def load_sheet_rows(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def normalize_label(value: str | None) -> str:
    if not value:
        return ""
    return str(value).strip().lower()


def label_css_class(label: str | None) -> str:
    return LABEL_CLASS.get(normalize_label(label), "missing")


def format_label(label: str | None) -> str:
    label = normalize_label(label)
    if not label:
        return "missing"
    return label.replace("_", " ")


def render_text_block(text: str) -> str:
    return html.escape(text or "")


def unique_model_labels(row: dict[str, str]) -> list[str]:
    labels = []
    for field, _ in MODEL_FIELDS:
        label = normalize_label(row.get(field, ""))
        if label:
            labels.append(label)
    return sorted(set(labels))


def disagreement_count(row: dict[str, str]) -> int:
    unique = unique_model_labels(row)
    return max(0, len(unique) - 1)


def high_conflict(row: dict[str, str]) -> bool:
    labels = set(unique_model_labels(row))
    if len(labels) >= 3:
        return True
    return "fixed" in labels and "regressed" in labels


def build_search_blob(row: dict[str, str]) -> str:
    parts = [
        row.get("issue_id", ""),
        row.get("paper_title", ""),
        row.get("suggested_label", ""),
        row.get("silver_label", ""),
        row.get("gold_label", ""),
        row.get("suggestion_source", ""),
        row.get("suggestion_note", ""),
    ]
    parts.extend(row.get(field, "") for field in TEXT_FIELDS)
    return " ".join(part for part in parts if part).lower()


def summarize_rows(rows: list[dict[str, str]]) -> dict[str, Any]:
    suggested = Counter()
    gold = Counter()
    conflict = Counter()
    suggestion_sources = Counter()
    silver_present = 0
    labeled = 0
    high_conflict_count = 0

    for row in rows:
        suggested_label = normalize_label(row.get("suggested_label", ""))
        if suggested_label:
            suggested[suggested_label] += 1

        gold_label = normalize_label(row.get("gold_label", ""))
        if gold_label:
            gold[gold_label] += 1
            labeled += 1

        if normalize_label(row.get("silver_label", "")):
            silver_present += 1

        conflict[disagreement_count(row)] += 1
        suggestion_source = row.get("suggestion_source", "").strip() or "unknown"
        suggestion_sources[suggestion_source] += 1

        if high_conflict(row):
            high_conflict_count += 1

    return {
        "rows": len(rows),
        "labeled": labeled,
        "unlabeled": len(rows) - labeled,
        "silver_present": silver_present,
        "high_conflict": high_conflict_count,
        "suggested": suggested,
        "gold": gold,
        "conflict": conflict,
        "suggestion_sources": suggestion_sources,
    }


def render_label_chip(prefix: str, label: str | None) -> str:
    label_text = format_label(label)
    safe_prefix = html.escape(prefix)
    return (
        f'<span class="pill pill-{label_css_class(label)}">'
        f"<span class=\"pill-key\">{safe_prefix}</span>"
        f"<span>{html.escape(label_text)}</span>"
        "</span>"
    )


def render_counter_group(title: str, counter: Counter[str]) -> str:
    if not counter:
        return (
            f'<div class="stat-group"><div class="stat-title">{html.escape(title)}</div>'
            '<div class="stat-empty">none</div></div>'
        )
    chips = []
    for key, count in sorted(counter.items(), key=lambda item: (-item[1], item[0])):
        cls = label_css_class(key)
        chips.append(
            f'<span class="count-chip count-{cls}">'
            f"<strong>{count}</strong> {html.escape(format_label(key))}"
            "</span>"
        )
    return (
        f'<div class="stat-group"><div class="stat-title">{html.escape(title)}</div>'
        f"<div class=\"count-strip\">{''.join(chips)}</div></div>"
    )


def render_row_card(row: dict[str, str]) -> str:
    issue_id = row.get("issue_id", "")
    paper_title = row.get("paper_title", "")
    priority_score = row.get("priority_score", "")
    review_rating = row.get("review_rating", "")
    review_confidence = row.get("review_confidence", "")
    suggested_label = normalize_label(row.get("suggested_label", ""))
    silver_label = normalize_label(row.get("silver_label", ""))
    gold_label = normalize_label(row.get("gold_label", ""))
    suggestion_source = row.get("suggestion_source", "")
    suggestion_note = row.get("suggestion_note", "")
    conflict_size = len(unique_model_labels(row))
    disagreement = disagreement_count(row)
    high_conflict_flag = "1" if high_conflict(row) else "0"
    has_silver = "1" if silver_label else "0"
    has_gold = "1" if gold_label else "0"
    search_blob = build_search_blob(row)

    model_chips = "".join(
        render_label_chip(name, row.get(field, "")) for field, name in MODEL_FIELDS
    )

    sections = [
        ("Review Concern", row.get("review_excerpt", ""), True),
        ("Top Response Chunk", row.get("top_response_excerpt", ""), True),
        ("Aligned Response Context", row.get("aligned_response_excerpt", ""), False),
        ("Revision Summary", row.get("revision_summary", ""), False),
        ("Silver Follow-up Comment", row.get("silver_comment", ""), False),
        ("Evidence Span", row.get("evidence_span", ""), False),
        ("Notes", row.get("notes", ""), False),
    ]

    section_html = []
    for title, text, open_by_default in sections:
        if not text:
            continue
        open_attr = " open" if open_by_default else ""
        section_html.append(
            f'<details class="detail-block"{open_attr}>'
            f"<summary>{html.escape(title)}</summary>"
            f"<pre>{render_text_block(text)}</pre>"
            "</details>"
        )

    badge_strip = "".join(
        [
            render_label_chip("suggested", suggested_label),
            render_label_chip("silver", silver_label),
            render_label_chip("gold", gold_label),
        ]
    )

    return (
        f'<article class="issue-card" '
        f'data-suggested="{html.escape(suggested_label)}" '
        f'data-gold="{html.escape(gold_label)}" '
        f'data-silver="{has_silver}" '
        f'data-unlabeled="{str(has_gold == "0").lower()}" '
        f'data-conflict="{conflict_size}" '
        f'data-disagreement="{disagreement}" '
        f'data-high-conflict="{high_conflict_flag}" '
        f'data-search="{html.escape(search_blob)}">'
        '<div class="card-topline">'
        f"<span>{html.escape(issue_id)}</span>"
        f"<span>priority {html.escape(priority_score or '?')}</span>"
        f"<span>{conflict_size}-label spread</span>"
        f"<span>{disagreement} disagreement step{'s' if disagreement != 1 else ''}</span>"
        "</div>"
        f"<h2>{html.escape(paper_title)}</h2>"
        '<div class="meta-row">'
        f"<span>{html.escape(review_rating)}</span>"
        f"<span>{html.escape(review_confidence)}</span>"
        "</div>"
        f'<div class="badge-strip">{badge_strip}</div>'
        '<div class="prediction-panel">'
        '<div class="prediction-title">Model snapshot</div>'
        f'<div class="badge-strip badge-strip-models">{model_chips}</div>'
        "</div>"
        '<div class="reason-box">'
        f"<div><strong>suggestion source</strong> {html.escape(suggestion_source or 'none')}</div>"
        f"<div><strong>hint</strong> {html.escape(suggestion_note or 'none')}</div>"
        "</div>"
        f"{''.join(section_html)}"
        "</article>"
    )


def render_annotation_packet(
    rows: list[dict[str, str]],
    *,
    title: str,
    sheet_name: str,
) -> str:
    summary = summarize_rows(rows)
    summary_html = "".join(
        [
            render_counter_group("Suggested Labels", summary["suggested"]),
            render_counter_group("Gold Labels", summary["gold"]),
            render_counter_group("Suggestion Sources", summary["suggestion_sources"]),
            render_counter_group(
                "Conflict Spread",
                Counter({f"{key} labels": value for key, value in summary["conflict"].items()}),
            ),
        ]
    )

    cards_html = "".join(render_row_card(row) for row in rows)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    :root {{
      --bg: #f6efe2;
      --panel: rgba(255, 251, 244, 0.88);
      --panel-strong: #fffaf2;
      --ink: #1d1a17;
      --muted: #685c4c;
      --line: rgba(40, 28, 10, 0.14);
      --accent: #0b6e4f;
      --accent-2: #c16200;
      --fixed: #1f8f59;
      --partially-fixed: #2d6cdf;
      --unresolved: #c76a12;
      --regressed: #b0283a;
      --missing: #8c8071;
      --shadow: 0 18px 60px rgba(44, 30, 10, 0.12);
      --radius: 22px;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "IBM Plex Sans", "Segoe UI", sans-serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(11, 110, 79, 0.12), transparent 28%),
        radial-gradient(circle at 85% 10%, rgba(193, 98, 0, 0.12), transparent 25%),
        linear-gradient(180deg, #fbf5ea 0%, #f3ead8 100%);
    }}
    .page {{
      width: min(1500px, calc(100vw - 32px));
      margin: 24px auto 48px;
    }}
    .hero {{
      background: linear-gradient(135deg, rgba(255,255,255,0.92), rgba(250,241,225,0.82));
      border: 1px solid var(--line);
      border-radius: 30px;
      padding: 28px 30px;
      box-shadow: var(--shadow);
      position: relative;
      overflow: hidden;
    }}
    .hero::after {{
      content: "";
      position: absolute;
      inset: auto -80px -120px auto;
      width: 280px;
      height: 280px;
      background: radial-gradient(circle, rgba(11, 110, 79, 0.16), transparent 70%);
      pointer-events: none;
    }}
    .eyebrow {{
      text-transform: uppercase;
      letter-spacing: 0.14em;
      font-size: 12px;
      color: var(--accent-2);
      margin-bottom: 10px;
    }}
    h1 {{
      margin: 0;
      font-family: "IBM Plex Serif", "Georgia", serif;
      font-size: clamp(30px, 4.6vw, 54px);
      line-height: 0.98;
      max-width: 900px;
    }}
    .hero p {{
      margin: 14px 0 0;
      max-width: 980px;
      color: var(--muted);
      font-size: 16px;
      line-height: 1.55;
    }}
    .hero-grid {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 14px;
      margin-top: 20px;
    }}
    .hero-stat {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 14px 16px;
      backdrop-filter: blur(8px);
    }}
    .hero-stat strong {{
      display: block;
      font-size: 28px;
      line-height: 1;
      margin-bottom: 6px;
    }}
    .layout {{
      display: grid;
      grid-template-columns: 340px minmax(0, 1fr);
      gap: 18px;
      margin-top: 18px;
      align-items: start;
    }}
    .sidebar {{
      position: sticky;
      top: 18px;
      display: grid;
      gap: 14px;
    }}
    .panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: var(--radius);
      padding: 18px;
      box-shadow: var(--shadow);
      backdrop-filter: blur(8px);
    }}
    .panel h3 {{
      margin: 0 0 12px;
      font-size: 15px;
      letter-spacing: 0.02em;
      text-transform: uppercase;
      color: var(--muted);
    }}
    .panel p {{
      margin: 0;
      color: var(--muted);
      line-height: 1.5;
      font-size: 14px;
    }}
    label {{
      display: block;
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--muted);
      margin: 12px 0 8px;
    }}
    input, select {{
      width: 100%;
      padding: 11px 12px;
      border-radius: 12px;
      border: 1px solid var(--line);
      background: var(--panel-strong);
      font: inherit;
      color: var(--ink);
    }}
    .check {{
      display: flex;
      gap: 10px;
      align-items: center;
      margin-top: 12px;
      font-size: 14px;
      color: var(--ink);
      text-transform: none;
      letter-spacing: 0;
    }}
    .check input {{
      width: auto;
      margin: 0;
    }}
    .results-line {{
      color: var(--muted);
      font-size: 14px;
      margin-top: 10px;
    }}
    .stat-group + .stat-group {{
      margin-top: 14px;
      padding-top: 14px;
      border-top: 1px dashed var(--line);
    }}
    .stat-title {{
      margin-bottom: 10px;
      font-size: 13px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--muted);
    }}
    .count-strip, .badge-strip {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }}
    .count-chip, .pill {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 7px 10px;
      border-radius: 999px;
      border: 1px solid transparent;
      font-size: 13px;
      line-height: 1;
      background: rgba(255,255,255,0.68);
    }}
    .pill-key {{
      text-transform: uppercase;
      letter-spacing: 0.08em;
      font-size: 10px;
      opacity: 0.72;
    }}
    .pill-fixed, .count-fixed {{
      border-color: rgba(31, 143, 89, 0.24);
      color: var(--fixed);
      background: rgba(31, 143, 89, 0.1);
    }}
    .pill-partially-fixed, .count-partially-fixed {{
      border-color: rgba(45, 108, 223, 0.24);
      color: var(--partially-fixed);
      background: rgba(45, 108, 223, 0.1);
    }}
    .pill-unresolved, .count-unresolved {{
      border-color: rgba(199, 106, 18, 0.24);
      color: var(--unresolved);
      background: rgba(199, 106, 18, 0.1);
    }}
    .pill-regressed, .count-regressed {{
      border-color: rgba(176, 40, 58, 0.24);
      color: var(--regressed);
      background: rgba(176, 40, 58, 0.1);
    }}
    .pill-missing, .count-missing {{
      border-color: rgba(140, 128, 113, 0.18);
      color: var(--missing);
      background: rgba(140, 128, 113, 0.1);
    }}
    .cards {{
      display: grid;
      gap: 14px;
    }}
    .issue-card {{
      background: linear-gradient(180deg, rgba(255,255,255,0.9), rgba(255,249,240,0.82));
      border: 1px solid var(--line);
      border-radius: 24px;
      padding: 20px 20px 16px;
      box-shadow: var(--shadow);
    }}
    .issue-card[data-high-conflict="1"] {{
      box-shadow: 0 18px 60px rgba(193, 98, 0, 0.12);
      border-color: rgba(193, 98, 0, 0.32);
    }}
    .card-topline, .meta-row {{
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      color: var(--muted);
      font-size: 13px;
    }}
    .card-topline {{
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-bottom: 10px;
    }}
    .issue-card h2 {{
      margin: 0;
      font-size: clamp(20px, 2.4vw, 28px);
      line-height: 1.1;
      font-family: "IBM Plex Serif", "Georgia", serif;
    }}
    .meta-row {{
      margin: 10px 0 14px;
    }}
    .prediction-panel, .reason-box {{
      margin-top: 14px;
      padding: 14px;
      border-radius: 18px;
      border: 1px solid var(--line);
      background: rgba(255,255,255,0.58);
    }}
    .prediction-title {{
      margin-bottom: 10px;
      font-size: 13px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--muted);
    }}
    .badge-strip-models .pill {{
      background: rgba(248, 244, 238, 0.86);
    }}
    .reason-box {{
      display: grid;
      gap: 8px;
      color: var(--muted);
      font-size: 14px;
    }}
    .reason-box strong {{
      color: var(--ink);
      text-transform: uppercase;
      letter-spacing: 0.08em;
      font-size: 11px;
      margin-right: 6px;
    }}
    .detail-block {{
      margin-top: 12px;
      border: 1px solid var(--line);
      border-radius: 16px;
      background: rgba(255,255,255,0.56);
      overflow: hidden;
    }}
    .detail-block summary {{
      cursor: pointer;
      list-style: none;
      padding: 14px 16px;
      font-weight: 600;
    }}
    .detail-block summary::-webkit-details-marker {{
      display: none;
    }}
    .detail-block pre {{
      margin: 0;
      padding: 0 16px 16px;
      white-space: pre-wrap;
      word-break: break-word;
      font-family: "IBM Plex Mono", "SFMono-Regular", monospace;
      font-size: 12.5px;
      line-height: 1.6;
      color: #3e352c;
    }}
    .hidden {{
      display: none !important;
    }}
    @media (max-width: 1100px) {{
      .layout {{
        grid-template-columns: 1fr;
      }}
      .sidebar {{
        position: static;
      }}
    }}
    @media (max-width: 720px) {{
      .page {{
        width: min(100vw - 18px, 100%);
        margin: 10px auto 24px;
      }}
      .hero {{
        padding: 20px;
        border-radius: 24px;
      }}
      .hero-grid {{
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }}
      .panel, .issue-card {{
        border-radius: 18px;
      }}
    }}
  </style>
</head>
<body>
  <main class="page">
    <section class="hero">
      <div class="eyebrow">RevTrack Annotation Packet</div>
      <h1>{html.escape(title)}</h1>
      <p>
        This browser packet is optimized for fast issue adjudication. Keep it open next to
        <code>{html.escape(sheet_name)}</code>, filter for high-conflict cases, and use the
        suggestion and silver signals as references rather than ground truth.
      </p>
      <div class="hero-grid">
        <div class="hero-stat"><strong>{summary["rows"]}</strong><span>rows in packet</span></div>
        <div class="hero-stat"><strong>{summary["unlabeled"]}</strong><span>still unlabeled</span></div>
        <div class="hero-stat"><strong>{summary["silver_present"]}</strong><span>with silver clue</span></div>
        <div class="hero-stat"><strong>{summary["high_conflict"]}</strong><span>high-conflict cards</span></div>
      </div>
    </section>

    <section class="layout">
      <aside class="sidebar">
        <div class="panel">
          <h3>Filters</h3>
          <label for="search">Search</label>
          <input id="search" type="search" placeholder="issue id, paper title, quote, label">

          <label for="suggested">Suggested label</label>
          <select id="suggested">
            <option value="">All suggested labels</option>
            <option value="fixed">fixed</option>
            <option value="partially_fixed">partially fixed</option>
            <option value="unresolved">unresolved</option>
            <option value="regressed">regressed</option>
          </select>

          <label for="gold">Gold label</label>
          <select id="gold">
            <option value="">All gold states</option>
            <option value="missing">missing</option>
            <option value="fixed">fixed</option>
            <option value="partially_fixed">partially fixed</option>
            <option value="unresolved">unresolved</option>
            <option value="regressed">regressed</option>
          </select>

          <label for="conflict">Conflict spread</label>
          <select id="conflict">
            <option value="">Any model spread</option>
            <option value="1">1 label only</option>
            <option value="2">2 labels</option>
            <option value="3">3 labels</option>
            <option value="4">4 labels</option>
          </select>

          <label class="check"><input id="silverOnly" type="checkbox">Only rows with silver clue</label>
          <label class="check"><input id="unlabeledOnly" type="checkbox">Only unlabeled rows</label>
          <label class="check"><input id="highConflictOnly" type="checkbox">Only high-conflict rows</label>
          <div class="results-line" id="resultsLine"></div>
        </div>

        <div class="panel">
          <h3>How To Use</h3>
          <p>
            Start with the review concern and top response chunk. Use the broader revision summary only
            to resolve ambiguity. The fastest paper-worthy cases are usually ones where a naive heuristic
            says <code>fixed</code> but the stronger encoder says <code>partially_fixed</code>,
            <code>unresolved</code>, or <code>regressed</code>.
          </p>
        </div>

        <div class="panel">
          <h3>Packet Summary</h3>
          {summary_html}
        </div>
      </aside>

      <section class="cards" id="cards">
        {cards_html}
      </section>
    </section>
  </main>

  <script>
    const searchInput = document.getElementById("search");
    const suggestedSelect = document.getElementById("suggested");
    const goldSelect = document.getElementById("gold");
    const conflictSelect = document.getElementById("conflict");
    const silverOnly = document.getElementById("silverOnly");
    const unlabeledOnly = document.getElementById("unlabeledOnly");
    const highConflictOnly = document.getElementById("highConflictOnly");
    const resultsLine = document.getElementById("resultsLine");
    const cards = Array.from(document.querySelectorAll(".issue-card"));

    function matches(card) {{
      const search = searchInput.value.trim().toLowerCase();
      const suggested = suggestedSelect.value;
      const gold = goldSelect.value;
      const conflict = conflictSelect.value;

      if (search && !card.dataset.search.includes(search)) {{
        return false;
      }}
      if (suggested && card.dataset.suggested !== suggested) {{
        return false;
      }}
      if (gold) {{
        const goldValue = card.dataset.gold || "missing";
        if (goldValue !== gold) {{
          return false;
        }}
      }}
      if (conflict && card.dataset.conflict !== conflict) {{
        return false;
      }}
      if (silverOnly.checked && card.dataset.silver !== "1") {{
        return false;
      }}
      if (unlabeledOnly.checked && card.dataset.unlabeled !== "true") {{
        return false;
      }}
      if (highConflictOnly.checked && card.dataset.highConflict !== "1") {{
        return false;
      }}
      return true;
    }}

    function applyFilters() {{
      let visible = 0;
      for (const card of cards) {{
        const ok = matches(card);
        card.classList.toggle("hidden", !ok);
        if (ok) {{
          visible += 1;
        }}
      }}
      resultsLine.textContent = `${{visible}} / ${{cards.length}} rows visible`;
    }}

    [searchInput, suggestedSelect, goldSelect, conflictSelect, silverOnly, unlabeledOnly, highConflictOnly]
      .forEach((node) => node.addEventListener("input", applyFilters));

    applyFilters();
  </script>
</body>
</html>
"""
