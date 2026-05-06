from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from revtrack.io import load_examples, load_predictions


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a standalone animated issue timeline.")
    parser.add_argument("--data", required=True)
    parser.add_argument("--predictions", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--limit", type=int, default=8)
    return parser.parse_args()


def build_html(rows: list[dict]) -> str:
    payload = json.dumps(rows, ensure_ascii=False)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>RevTrack Issue Timeline</title>
  <style>
    :root {{
      --bg: #f6f0e8;
      --ink: #1e1a18;
      --panel: rgba(255,255,255,0.72);
      --line: rgba(30,26,24,0.12);
      --fixed: #297d4e;
      --partial: #d68c1d;
      --unresolved: #a2372b;
      --regressed: #a2216b;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "IBM Plex Sans", "Segoe UI", sans-serif;
      color: var(--ink);
      background:
        radial-gradient(circle at 20% 20%, rgba(223, 189, 135, 0.35), transparent 26%),
        radial-gradient(circle at 80% 10%, rgba(109, 141, 190, 0.24), transparent 24%),
        linear-gradient(180deg, #f7f2ea, #ece3d3 54%, #f8f4ee);
    }}
    .wrap {{
      max-width: 1240px;
      margin: 0 auto;
      padding: 40px 24px 64px;
    }}
    h1 {{
      margin: 0 0 10px;
      font-family: "Space Grotesk", "Segoe UI", sans-serif;
      font-size: clamp(32px, 4vw, 58px);
      letter-spacing: -0.04em;
    }}
    .sub {{
      max-width: 780px;
      font-size: 17px;
      line-height: 1.5;
      opacity: 0.8;
      margin-bottom: 28px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 18px;
    }}
    .card {{
      position: relative;
      overflow: hidden;
      border: 1px solid var(--line);
      border-radius: 22px;
      background: var(--panel);
      backdrop-filter: blur(12px);
      box-shadow: 0 20px 50px rgba(60, 41, 14, 0.08);
      padding: 18px 18px 16px;
      animation: rise 700ms cubic-bezier(.2,.7,.2,1) both;
    }}
    .card::before {{
      content: "";
      position: absolute;
      inset: 0 auto 0 0;
      width: 7px;
      background: var(--status-color);
    }}
    .top {{
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 12px;
    }}
    .badge {{
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.12em;
      padding: 5px 9px;
      border-radius: 999px;
      background: color-mix(in srgb, var(--status-color) 14%, white);
      color: var(--status-color);
      font-weight: 700;
    }}
    .paper {{
      font-size: 12px;
      opacity: 0.65;
    }}
    .title {{
      font-family: "Space Grotesk", "Segoe UI", sans-serif;
      font-size: 20px;
      line-height: 1.1;
      margin: 0 0 12px;
    }}
    .lane {{
      position: relative;
      margin: 12px 0;
      padding-left: 18px;
      border-left: 2px dashed rgba(30,26,24,0.14);
    }}
    .event {{
      position: relative;
      margin-bottom: 12px;
      padding: 10px 12px 10px 14px;
      border-radius: 14px;
      background: rgba(255,255,255,0.66);
    }}
    .event::before {{
      content: "";
      position: absolute;
      left: -24px;
      top: 14px;
      width: 10px;
      height: 10px;
      border-radius: 50%;
      background: var(--status-color);
      box-shadow: 0 0 0 5px rgba(255,255,255,0.5);
    }}
    .label {{
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.12em;
      opacity: 0.56;
      margin-bottom: 6px;
    }}
    .text {{
      font-size: 14px;
      line-height: 1.45;
    }}
    .outcome {{
      display: flex;
      justify-content: space-between;
      gap: 14px;
      border-top: 1px solid var(--line);
      margin-top: 14px;
      padding-top: 14px;
      font-size: 13px;
    }}
    .gold, .pred {{
      flex: 1;
      padding: 10px 12px;
      border-radius: 12px;
      background: rgba(255,255,255,0.75);
    }}
    .status {{
      font-weight: 800;
      color: var(--status-color);
      text-transform: uppercase;
      letter-spacing: 0.08em;
      font-size: 12px;
    }}
    @keyframes rise {{
      from {{ opacity: 0; transform: translateY(28px) scale(0.98); }}
      to {{ opacity: 1; transform: translateY(0) scale(1); }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <h1>RevTrack Issue Ledger</h1>
    <div class="sub">
      A dynamic visualization for revision-aware scientific judgment. Each card shows one review concern, the author response, the revision event, and the resulting issue status.
    </div>
    <div id="grid" class="grid"></div>
  </div>
  <script>
    const rows = {payload};
    const colorMap = {{
      fixed: "var(--fixed)",
      partially_fixed: "var(--partial)",
      unresolved: "var(--unresolved)",
      regressed: "var(--regressed)",
      missing: "#555"
    }};
    const grid = document.getElementById("grid");
    rows.forEach((row, index) => {{
      const card = document.createElement("article");
      card.className = "card";
      card.style.setProperty("--status-color", colorMap[row.predicted_label] || "#555");
      card.style.animationDelay = `${{index * 90}}ms`;
      card.innerHTML = `
        <div class="top">
          <div class="badge">${{row.predicted_label.replace("_", " ")}}</div>
          <div class="paper">${{row.venue || "demo"}}</div>
        </div>
        <div class="title">${{row.paper_title}}</div>
        <div class="lane">
          <div class="event">
            <div class="label">Review Concern</div>
            <div class="text">${{row.review_text}}</div>
          </div>
          <div class="event">
            <div class="label">Author Response</div>
            <div class="text">${{row.author_response}}</div>
          </div>
          <div class="event">
            <div class="label">Revision Event</div>
            <div class="text">${{row.revision_summary}}</div>
          </div>
        </div>
        <div class="outcome">
          <div class="gold">
            <div class="label">Gold</div>
            <div class="status">${{row.gold_label}}</div>
          </div>
          <div class="pred">
            <div class="label">Prediction</div>
            <div class="status">${{row.predicted_label}}</div>
          </div>
        </div>
      `;
      grid.appendChild(card);
    }});
  </script>
</body>
</html>"""


def main() -> None:
    args = parse_args()
    examples = load_examples(args.data)[: args.limit]
    predictions = {item.id: item for item in load_predictions(args.predictions)}

    rows = []
    for example in examples:
        prediction = predictions.get(example.id)
        rows.append(
            {
                "id": example.id,
                "venue": example.venue,
                "paper_title": example.paper_title,
                "review_text": example.review_text,
                "author_response": example.author_response,
                "revision_summary": example.revision_summary,
                "gold_label": example.gold_label,
                "predicted_label": prediction.predicted_label if prediction else "missing",
            }
        )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(build_html(rows), encoding="utf-8")
    print(f"Wrote HTML visualization to {output_path}")


if __name__ == "__main__":
    main()
