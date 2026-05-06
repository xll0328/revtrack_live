from __future__ import annotations

import argparse
import json
from collections import Counter
from itertools import combinations
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

LABEL_ORDER = ["fixed", "partially_fixed", "unresolved", "regressed"]
LABEL_COLORS = {
    "fixed": "#157f5b",
    "partially_fixed": "#d58617",
    "unresolved": "#b33a2f",
    "regressed": "#8e2f75",
}
MODEL_COLORS = {
    "Heuristic": "#8d5f2b",
    "TF-IDF + LinearSVC": "#286dc9",
    "ModernBERT + LinearSVC": "#7b63d6",
    "MPNet + LinearSVC": "#0f7b77",
    "Issue-Ledger Calibrator": "#c14f1a",
    "Structured Calibrator (No Overrides)": "#8060c9",
    "Structured Calibrator": "#ad2e49",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a dynamic RevTrack progress dashboard.")
    parser.add_argument("--output", required=True)
    parser.add_argument("--title", default="RevTrack Progress Dashboard")
    return parser.parse_args()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def load_label_distribution(path: Path) -> dict[str, int]:
    rows = load_jsonl(path)
    counter = Counter(row["gold_label"] for row in rows)
    return {label: int(counter.get(label, 0)) for label in LABEL_ORDER}


def load_metric_summary(path: Path) -> dict[str, float]:
    payload = load_json(path)["summary"]
    return {
        "accuracy": float(payload["accuracy"]),
        "macro_f1": float(payload["macro_f1"]),
    }


def load_prediction_distribution(path: Path) -> dict[str, int]:
    rows = load_jsonl(path)
    counter = Counter(row["predicted_label"] for row in rows)
    return {label: int(counter.get(label, 0)) for label in LABEL_ORDER}


def compute_disagreement(path_a: Path, path_b: Path) -> tuple[int, dict[str, int]]:
    rows_a = {row["id"]: row["predicted_label"] for row in load_jsonl(path_a)}
    rows_b = {row["id"]: row["predicted_label"] for row in load_jsonl(path_b)}
    ids = sorted(set(rows_a) & set(rows_b))
    counter = Counter(
        f"{rows_a[item]} -> {rows_b[item]}"
        for item in ids
        if rows_a[item] != rows_b[item]
    )
    return sum(counter.values()), dict(counter.most_common(8))


def build_payload() -> dict:
    dev_versions = [
        {
            "id": "v1",
            "label": "Clean Dev v1",
            "data": ROOT / "data/processed/iclr2024_clean_dev_assistant_v1.jsonl",
        },
        {
            "id": "v2",
            "label": "Clean Dev v2",
            "data": ROOT / "data/processed/iclr2024_clean_dev_assistant_v2.jsonl",
        },
        {
            "id": "v3",
            "label": "Clean Dev v3",
            "data": ROOT / "data/processed/iclr2024_clean_dev_assistant_v3.jsonl",
        },
        {
            "id": "v4",
            "label": "Clean Dev v4",
            "data": ROOT / "data/processed/iclr2024_clean_dev_assistant_v4.jsonl",
        },
        {
            "id": "v5",
            "label": "Clean Dev v5",
            "data": ROOT / "data/processed/iclr2024_clean_dev_assistant_v5.jsonl",
        },
        {
            "id": "v6",
            "label": "Clean Dev v6",
            "data": ROOT / "data/processed/iclr2024_clean_dev_assistant_v6.jsonl",
        },
        {
            "id": "v7",
            "label": "Clean Dev v7",
            "data": ROOT / "data/processed/iclr2024_clean_dev_assistant_v7.jsonl",
        },
    ]

    for item in dev_versions:
        item["labels"] = load_label_distribution(item["data"])
        item["rows"] = sum(item["labels"].values())
        item.pop("data", None)

    metric_paths = {
        "Heuristic": {
            "v1": ROOT / "outputs/day1/iclr2024_clean_dev_assistant_heuristic_metrics.json",
            "v2": ROOT / "outputs/day1/iclr2024_clean_dev_assistant_v2_heuristic_metrics.json",
            "v3": ROOT / "outputs/day1/iclr2024_clean_dev_assistant_v3_heuristic_metrics.json",
            "v4": ROOT / "outputs/day1/iclr2024_clean_dev_assistant_v4_heuristic_metrics.json",
            "v5": ROOT / "outputs/day1/iclr2024_clean_dev_assistant_v5_heuristic_metrics.json",
            "v6": ROOT / "outputs/day1/iclr2024_clean_dev_assistant_v6_heuristic_metrics.json",
            "v7": ROOT / "outputs/day1/iclr2024_clean_dev_assistant_v7_heuristic_metrics.json",
        },
        "TF-IDF + LinearSVC": {
            "v1": ROOT / "outputs/day1/iclr2024_clean_dev_assistant_tfidf_metrics.json",
            "v2": ROOT / "outputs/day1/iclr2024_clean_dev_assistant_v2_tfidf_metrics.json",
            "v3": ROOT / "outputs/day1/iclr2024_clean_dev_assistant_v3_tfidf_metrics.json",
            "v4": ROOT / "outputs/day1/iclr2024_clean_dev_assistant_v4_tfidf_metrics.json",
            "v5": ROOT / "outputs/day1/iclr2024_clean_dev_assistant_v5_tfidf_metrics.json",
            "v6": ROOT / "outputs/day1/iclr2024_clean_dev_assistant_v6_tfidf_metrics.json",
            "v7": ROOT / "outputs/day1/iclr2024_clean_dev_assistant_v7_tfidf_metrics.json",
        },
        "ModernBERT + LinearSVC": {
            "v1": ROOT / "outputs/day1/iclr2024_clean_dev_assistant_modernbert_metrics.json",
            "v2": ROOT / "outputs/day1/iclr2024_clean_dev_assistant_v2_modernbert_metrics.json",
            "v3": ROOT / "outputs/day1/iclr2024_clean_dev_assistant_v3_modernbert_metrics.json",
            "v4": ROOT / "outputs/day1/iclr2024_clean_dev_assistant_v4_modernbert_metrics.json",
            "v5": ROOT / "outputs/day1/iclr2024_clean_dev_assistant_v5_modernbert_metrics.json",
            "v6": ROOT / "outputs/day1/iclr2024_clean_dev_assistant_v6_modernbert_metrics.json",
            "v7": ROOT / "outputs/day1/iclr2024_clean_dev_assistant_v7_modernbert_metrics.json",
        },
        "MPNet + LinearSVC": {
            "v1": ROOT / "outputs/day1/iclr2024_clean_dev_assistant_mpnet_metrics.json",
            "v2": ROOT / "outputs/day1/iclr2024_clean_dev_assistant_v2_mpnet_metrics.json",
            "v3": ROOT / "outputs/day1/iclr2024_clean_dev_assistant_v3_mpnet_metrics.json",
            "v4": ROOT / "outputs/day1/iclr2024_clean_dev_assistant_v4_mpnet_metrics.json",
            "v5": ROOT / "outputs/day1/iclr2024_clean_dev_assistant_v5_mpnet_metrics.json",
            "v6": ROOT / "outputs/day1/iclr2024_clean_dev_assistant_v6_mpnet_metrics.json",
            "v7": ROOT / "outputs/day1/iclr2024_clean_dev_assistant_v7_mpnet_metrics.json",
        },
        "Issue-Ledger Calibrator": {
            "v1": ROOT / "outputs/day1/iclr2024_clean_dev_assistant_issue_ledger_metrics.json",
            "v2": ROOT / "outputs/day1/iclr2024_clean_dev_assistant_v2_issue_ledger_refreshed_metrics.json",
            "v3": ROOT / "outputs/day1/iclr2024_clean_dev_assistant_v3_issue_ledger_metrics.json",
            "v4": ROOT / "outputs/day1/iclr2024_clean_dev_assistant_v4_issue_ledger_metrics.json",
            "v5": ROOT / "outputs/day1/iclr2024_clean_dev_assistant_v5_issue_ledger_metrics.json",
            "v6": ROOT / "outputs/day1/iclr2024_clean_dev_assistant_v6_issue_ledger_metrics.json",
            "v7": ROOT / "outputs/day1/iclr2024_clean_dev_assistant_v7_issue_ledger_metrics.json",
        },
        "Structured Calibrator (No Overrides)": {
            "v3": ROOT / "outputs/day1/iclr2024_clean_dev_assistant_v3_structured_no_overrides_metrics.json",
            "v4": ROOT / "outputs/day1/iclr2024_clean_dev_assistant_v4_structured_no_overrides_metrics.json",
            "v5": ROOT / "outputs/day1/iclr2024_clean_dev_assistant_v5_structured_no_overrides_metrics.json",
            "v6": ROOT / "outputs/day1/iclr2024_clean_dev_assistant_v6_structured_no_overrides_metrics.json",
            "v7": ROOT / "outputs/day1/iclr2024_clean_dev_assistant_v7_structured_no_overrides_metrics.json",
        },
        "Structured Calibrator": {
            "v3": ROOT / "outputs/day1/iclr2024_clean_dev_assistant_v3_structured_metrics.json",
            "v4": ROOT / "outputs/day1/iclr2024_clean_dev_assistant_v4_structured_metrics.json",
            "v5": ROOT / "outputs/day1/iclr2024_clean_dev_assistant_v5_structured_metrics.json",
            "v6": ROOT / "outputs/day1/iclr2024_clean_dev_assistant_v6_structured_metrics.json",
            "v7": ROOT / "outputs/day1/iclr2024_clean_dev_assistant_v7_structured_metrics.json",
        },
    }

    metric_rows = []
    for model_name, versions in metric_paths.items():
        points = []
        for version in dev_versions:
            path = versions.get(version["id"])
            if path and path.exists():
                summary = load_metric_summary(path)
                points.append({"version": version["id"], **summary})
        if points:
            metric_rows.append(
                {
                    "model": model_name,
                    "color": MODEL_COLORS.get(model_name, "#444"),
                    "points": points,
                }
            )

    transfer_specs = {
        "v3": {
            "tfidf": ROOT / "outputs/day1/iclr2024_candidates_tfidf_train_v3_transfer_predictions.jsonl",
            "modernbert": ROOT / "outputs/day1/iclr2024_candidates_modernbert_train_v3_transfer_predictions.jsonl",
            "mpnet": ROOT / "outputs/day1/iclr2024_candidates_mpnet_train_v3_transfer_predictions.jsonl",
            "issue_ledger": ROOT / "outputs/day1/iclr2024_candidates_issue_ledger_train_v3_transfer_predictions.jsonl",
            "structured": ROOT / "outputs/day1/iclr2024_candidates_structured_train_v3_transfer_predictions.jsonl",
        },
        "v4": {
            "tfidf": ROOT / "outputs/day1/iclr2024_candidates_tfidf_train_v4_transfer_predictions.jsonl",
            "modernbert": ROOT / "outputs/day1/iclr2024_candidates_modernbert_train_v4_transfer_predictions.jsonl",
            "mpnet": ROOT / "outputs/day1/iclr2024_candidates_mpnet_train_v4_transfer_predictions.jsonl",
            "issue_ledger": ROOT / "outputs/day1/iclr2024_candidates_issue_ledger_train_v4_transfer_predictions.jsonl",
            "structured": ROOT / "outputs/day1/iclr2024_candidates_structured_train_v4_transfer_predictions.jsonl",
        },
        "v5": {
            "tfidf": ROOT / "outputs/day1/iclr2024_candidates_tfidf_train_v5_transfer_predictions.jsonl",
            "modernbert": ROOT / "outputs/day1/iclr2024_candidates_modernbert_train_v5_transfer_predictions.jsonl",
            "mpnet": ROOT / "outputs/day1/iclr2024_candidates_mpnet_train_v5_transfer_predictions.jsonl",
            "issue_ledger": ROOT / "outputs/day1/iclr2024_candidates_issue_ledger_train_v5_transfer_predictions.jsonl",
            "structured": ROOT / "outputs/day1/iclr2024_candidates_structured_train_v5_transfer_predictions.jsonl",
        },
        "v6": {
            "tfidf": ROOT / "outputs/day1/iclr2024_candidates_tfidf_train_v6_transfer_predictions.jsonl",
            "modernbert": ROOT / "outputs/day1/iclr2024_candidates_modernbert_train_v6_transfer_predictions.jsonl",
            "mpnet": ROOT / "outputs/day1/iclr2024_candidates_mpnet_train_v6_transfer_predictions.jsonl",
            "issue_ledger": ROOT / "outputs/day1/iclr2024_candidates_issue_ledger_train_v6_transfer_predictions.jsonl",
            "structured": ROOT / "outputs/day1/iclr2024_candidates_structured_train_v6_transfer_predictions.jsonl",
        },
        "v7": {
            "tfidf": ROOT / "outputs/day1/iclr2024_candidates_tfidf_train_v7_transfer_predictions.jsonl",
            "modernbert": ROOT / "outputs/day1/iclr2024_candidates_modernbert_train_v7_transfer_predictions.jsonl",
            "mpnet": ROOT / "outputs/day1/iclr2024_candidates_mpnet_train_v7_transfer_predictions.jsonl",
            "issue_ledger": ROOT / "outputs/day1/iclr2024_candidates_issue_ledger_train_v7_transfer_predictions.jsonl",
            "structured": ROOT / "outputs/day1/iclr2024_candidates_structured_train_v7_transfer_predictions.jsonl",
        },
        "v8": {
            "tfidf": ROOT / "outputs/day1/iclr2024_candidates_tfidf_train_v8_transfer_predictions.jsonl",
            "modernbert": ROOT / "outputs/day1/iclr2024_candidates_modernbert_train_v8_transfer_predictions.jsonl",
            "mpnet": ROOT / "outputs/day1/iclr2024_candidates_mpnet_train_v8_transfer_predictions.jsonl",
            "issue_ledger": ROOT / "outputs/day1/iclr2024_candidates_issue_ledger_train_v8_transfer_predictions.jsonl",
            "structured": ROOT / "outputs/day1/iclr2024_candidates_structured_train_v8_transfer_predictions.jsonl",
        },
    }

    transfer_rows = {}
    for version, models in transfer_specs.items():
        transfer_rows[version] = {}
        for model_name, path in models.items():
            transfer_rows[version][model_name] = load_prediction_distribution(path)

    latest_paths = transfer_specs["v8"]
    disagreement_rows = []
    for a, b in [("structured", "tfidf"), ("structured", "mpnet"), ("structured", "issue_ledger")]:
        total, top_pairs = compute_disagreement(latest_paths[a], latest_paths[b])
        disagreement_rows.append(
            {
                "pair": f"{a} vs {b}",
                "total": total,
                "top_pairs": top_pairs,
            }
        )

    best_latest = load_metric_summary(metric_paths["Structured Calibrator"]["v7"])
    return {
        "label_order": LABEL_ORDER,
        "label_colors": LABEL_COLORS,
        "dev_versions": dev_versions,
        "metric_rows": metric_rows,
        "transfer_rows": transfer_rows,
        "disagreements": disagreement_rows,
        "hero": {
            "dev_versions": len(dev_versions),
            "latest_rows": dev_versions[-1]["rows"],
            "best_accuracy": round(best_latest["accuracy"], 3),
            "best_macro_f1": round(best_latest["macro_f1"], 3),
            "candidate_count": 230,
        },
    }


def build_html(title: str, payload: dict) -> str:
    data = json.dumps(payload, ensure_ascii=False)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    :root {{
      --bg: #f5ebdc;
      --ink: #1b1814;
      --muted: #6a5646;
      --line: rgba(27, 24, 20, 0.12);
      --panel: rgba(255, 249, 241, 0.86);
      --panel-strong: rgba(255, 255, 255, 0.94);
      --shadow: 0 26px 70px rgba(46, 28, 10, 0.14);
      --gold: #c56c16;
      --teal: #0d7765;
      --blue: #2e61cf;
      --rose: #b23256;
      --sand: #f0e0c9;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      color: var(--ink);
      font-family: "IBM Plex Sans", "Segoe UI", sans-serif;
      background:
        radial-gradient(circle at 8% 10%, rgba(13,119,101,0.16), transparent 24%),
        radial-gradient(circle at 92% 12%, rgba(197,108,22,0.18), transparent 24%),
        linear-gradient(180deg, #f8f2e9 0%, #efe2d0 54%, #f7f3ee 100%);
    }}
    .page {{
      width: min(1540px, calc(100vw - 28px));
      margin: 18px auto 40px;
    }}
    .hero {{
      position: relative;
      overflow: hidden;
      padding: 28px 30px 26px;
      border: 1px solid var(--line);
      border-radius: 34px;
      background: linear-gradient(135deg, rgba(255,255,255,0.96), rgba(251,241,224,0.88));
      box-shadow: var(--shadow);
    }}
    .hero::after {{
      content: "";
      position: absolute;
      right: -80px;
      bottom: -100px;
      width: 320px;
      height: 320px;
      background: radial-gradient(circle, rgba(46,97,207,0.18), transparent 70%);
      pointer-events: none;
    }}
    .eyebrow {{
      text-transform: uppercase;
      letter-spacing: 0.16em;
      font-size: 12px;
      color: var(--gold);
      margin-bottom: 10px;
    }}
    h1 {{
      margin: 0;
      font-family: "Space Grotesk", "IBM Plex Sans", sans-serif;
      font-size: clamp(34px, 5vw, 64px);
      line-height: 0.95;
      letter-spacing: -0.05em;
      max-width: 980px;
    }}
    .sub {{
      max-width: 980px;
      margin-top: 14px;
      font-size: 16px;
      line-height: 1.55;
      color: var(--muted);
    }}
    .hero-grid {{
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 14px;
      margin-top: 22px;
    }}
    .hero-card {{
      padding: 14px 16px;
      border-radius: 18px;
      background: rgba(255,255,255,0.72);
      border: 1px solid var(--line);
      backdrop-filter: blur(8px);
    }}
    .hero-card strong {{
      display: block;
      font-size: 30px;
      line-height: 1;
      margin-bottom: 6px;
      font-family: "IBM Plex Serif", Georgia, serif;
    }}
    .hero-card span {{
      font-size: 12px;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.12em;
    }}
    .layout {{
      display: grid;
      grid-template-columns: 1.18fr 0.82fr;
      gap: 18px;
      margin-top: 18px;
      align-items: start;
    }}
    .stack {{
      display: grid;
      gap: 18px;
    }}
    .panel {{
      border: 1px solid var(--line);
      border-radius: 28px;
      background: var(--panel);
      box-shadow: var(--shadow);
      padding: 20px;
    }}
    .panel h2 {{
      margin: 0 0 12px;
      font-family: "IBM Plex Serif", Georgia, serif;
      font-size: 25px;
    }}
    .kicker {{
      margin-bottom: 12px;
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.12em;
      color: var(--muted);
    }}
    .note {{
      font-size: 14px;
      line-height: 1.5;
      color: var(--muted);
      margin-bottom: 16px;
    }}
    .toggle-row {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin-bottom: 16px;
    }}
    .toggle {{
      border: 1px solid var(--line);
      background: rgba(255,255,255,0.75);
      color: var(--ink);
      padding: 9px 12px;
      border-radius: 999px;
      font: inherit;
      cursor: pointer;
      transition: transform 140ms ease, background 140ms ease, color 140ms ease;
    }}
    .toggle.active {{
      background: linear-gradient(135deg, rgba(13,119,101,0.14), rgba(197,108,22,0.15));
      color: var(--teal);
      transform: translateY(-1px);
    }}
    .line-shell {{
      position: relative;
      border-radius: 24px;
      background: var(--panel-strong);
      border: 1px solid var(--line);
      padding: 16px;
    }}
    svg {{
      display: block;
      width: 100%;
      height: auto;
    }}
    .legend {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
      margin-top: 14px;
    }}
    .legend-item {{
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 10px 12px;
      border: 1px solid var(--line);
      border-radius: 16px;
      background: rgba(255,255,255,0.72);
      font-size: 14px;
    }}
    .swatch {{
      width: 12px;
      height: 12px;
      border-radius: 50%;
      flex: 0 0 auto;
    }}
    .mix-grid {{
      display: grid;
      gap: 12px;
    }}
    .mix-card {{
      border: 1px solid var(--line);
      border-radius: 20px;
      background: var(--panel-strong);
      padding: 14px;
    }}
    .mix-head {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: baseline;
      margin-bottom: 10px;
    }}
    .mix-head strong {{
      font-size: 18px;
      font-family: "IBM Plex Serif", Georgia, serif;
    }}
    .mix-head span {{
      font-size: 12px;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.12em;
    }}
    .stacked {{
      display: flex;
      width: 100%;
      height: 18px;
      overflow: hidden;
      border-radius: 999px;
      background: rgba(27,24,20,0.06);
    }}
    .seg {{
      width: 0;
      transition: width 800ms cubic-bezier(.2,.8,.2,1);
    }}
    .mix-labels {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 8px 14px;
      margin-top: 12px;
      font-size: 13px;
    }}
    .mix-label {{
      display: flex;
      align-items: center;
      gap: 8px;
      color: var(--muted);
    }}
    .mix-dot {{
      width: 10px;
      height: 10px;
      border-radius: 50%;
      flex: 0 0 auto;
    }}
    .transfer-tabs {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin-bottom: 16px;
    }}
    .transfer-tab {{
      cursor: pointer;
      padding: 9px 12px;
      border-radius: 999px;
      border: 1px solid var(--line);
      background: rgba(255,255,255,0.78);
      font: inherit;
    }}
    .transfer-tab.active {{
      background: linear-gradient(135deg, rgba(46,97,207,0.12), rgba(173,50,86,0.12));
      color: var(--rose);
    }}
    .transfer-grid {{
      display: grid;
      gap: 12px;
    }}
    .transfer-card {{
      border: 1px solid var(--line);
      border-radius: 20px;
      background: var(--panel-strong);
      padding: 14px;
    }}
    .mini-note {{
      color: var(--muted);
      font-size: 13px;
      margin-top: 12px;
      line-height: 1.45;
    }}
    .disagreement-grid {{
      display: grid;
      gap: 12px;
    }}
    .dis-card {{
      border: 1px solid var(--line);
      border-radius: 20px;
      background: linear-gradient(135deg, rgba(255,255,255,0.94), rgba(251,241,226,0.88));
      padding: 16px;
    }}
    .dis-top {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: baseline;
      margin-bottom: 12px;
    }}
    .dis-top strong {{
      font-size: 20px;
      font-family: "IBM Plex Serif", Georgia, serif;
    }}
    .dis-total {{
      color: var(--rose);
      font-weight: 800;
      font-size: 18px;
    }}
    .pair-list {{
      display: grid;
      gap: 8px;
    }}
    .pair-row {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
      padding: 8px 10px;
      border-radius: 12px;
      background: rgba(255,255,255,0.72);
      font-size: 13px;
    }}
    .foot {{
      margin-top: 18px;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.5;
    }}
    @media (max-width: 1080px) {{
      .layout {{
        grid-template-columns: 1fr;
      }}
      .hero-grid {{
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }}
      .legend {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <div class="page">
    <section class="hero">
      <div class="eyebrow">RevTrack Flight Deck</div>
      <h1>{title}</h1>
      <div class="sub">
        A dynamic progress view for the EMNLP 2026 revision-aware judgment project. This panel tracks how the clean-dev benchmark hardens over time, how model rankings shift under stricter evaluation, and how the full-candidate frontier shrinks as supervision grows.
      </div>
      <div class="hero-grid" id="hero-grid"></div>
    </section>

    <div class="layout">
      <div class="stack">
        <section class="panel">
          <div class="kicker">Metric Progression</div>
          <h2>Clean-Dev Trajectories</h2>
          <div class="note">
            Toggle between accuracy and macro-F1. The key story is not just the peak score, but which models stay stable as the benchmark shifts from `v1` to the much harder `v4`.
          </div>
          <div class="toggle-row">
            <button class="toggle active" data-metric="accuracy">Accuracy</button>
            <button class="toggle" data-metric="macro_f1">Macro-F1</button>
          </div>
          <div class="line-shell">
            <svg id="metric-chart" viewBox="0 0 980 420" aria-label="metric progression chart"></svg>
          </div>
          <div class="legend" id="metric-legend"></div>
        </section>

        <section class="panel">
          <div class="kicker">Benchmark Growth</div>
          <h2>Label Mix By Dev Version</h2>
          <div class="note">
            The benchmark is getting larger and more adversarial in the `fixed <-> partially_fixed` region. That pressure is exactly why the semantic baselines fall from `v3` to `v4`.
          </div>
          <div class="mix-grid" id="mix-grid"></div>
        </section>
      </div>

      <div class="stack">
        <section class="panel">
          <div class="kicker">Transfer Drift</div>
          <h2>Full-Candidate Label Distributions</h2>
          <div class="note">
            Switch models to see how the `230` public issue candidates move from `train_v3` to `train_v5`. This is where the project’s active-learning frontier becomes visible.
          </div>
          <div class="transfer-tabs" id="transfer-tabs"></div>
          <div class="transfer-grid" id="transfer-grid"></div>
          <div class="mini-note">
            `structured` and `mpnet` are now almost converged globally, while `structured vs tfidf` still carries the most reviewer-relevant `fixed <-> partially_fixed` disagreements.
          </div>
        </section>

        <section class="panel">
          <div class="kicker">Latest Frontier</div>
          <h2>Disagreement Surface At Train V5</h2>
          <div class="note">
            These cards summarize the latest label-level fault lines. They are the best direct input for the next annotation tranche and for the “why structure helps” section of the paper.
          </div>
          <div class="disagreement-grid" id="disagreement-grid"></div>
        </section>
      </div>
    </div>

    <div class="foot">
      `v4` clean-dev metrics use strict `LOO-feature` evaluation for `issue-ledger` and `structured`.
      Earlier optimistic passes that injected full-train transfer labels into the clean-dev sheet are not shown here.
    </div>
  </div>

  <script>
    const payload = {data};
    const labelOrder = payload.label_order;
    const labelColors = payload.label_colors;
    const devVersions = payload.dev_versions;
    const metricRows = payload.metric_rows;
    const transferRows = payload.transfer_rows;
    const disagreements = payload.disagreements;
    const hero = payload.hero;

    function pct(value) {{
      return `${{(value * 100).toFixed(1)}}%`;
    }}

    function makeHero() {{
      const stats = [
        ['Versions', hero.dev_versions],
        ['Latest Rows', hero.latest_rows],
        ['Best Acc.', hero.best_accuracy.toFixed(3)],
        ['Best Macro-F1', hero.best_macro_f1.toFixed(3)],
        ['Candidates', hero.candidate_count],
      ];
      const grid = document.getElementById('hero-grid');
      stats.forEach(([label, value]) => {{
        const card = document.createElement('div');
        card.className = 'hero-card';
        card.innerHTML = `<strong>${{value}}</strong><span>${{label}}</span>`;
        grid.appendChild(card);
      }});
    }}

    let currentMetric = 'accuracy';

    function renderMetricChart() {{
      const svg = document.getElementById('metric-chart');
      svg.innerHTML = '';
      const width = 980;
      const height = 420;
      const pad = {{ top: 28, right: 26, bottom: 58, left: 70 }};
      const innerW = width - pad.left - pad.right;
      const innerH = height - pad.top - pad.bottom;

      const versions = devVersions.map(item => item.id);
      const xFor = (version, index) => pad.left + (innerW / Math.max(1, versions.length - 1)) * index;
      const yFor = value => pad.top + innerH - value * innerH;

      for (let i = 0; i <= 5; i += 1) {{
        const value = i / 5;
        const y = yFor(value);
        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('x1', String(pad.left));
        line.setAttribute('x2', String(width - pad.right));
        line.setAttribute('y1', String(y));
        line.setAttribute('y2', String(y));
        line.setAttribute('stroke', 'rgba(27,24,20,0.12)');
        line.setAttribute('stroke-dasharray', '4 6');
        svg.appendChild(line);

        const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        label.setAttribute('x', String(pad.left - 14));
        label.setAttribute('y', String(y + 4));
        label.setAttribute('text-anchor', 'end');
        label.setAttribute('fill', '#6a5646');
        label.setAttribute('font-size', '12');
        label.textContent = value.toFixed(1);
        svg.appendChild(label);
      }}

      versions.forEach((version, index) => {{
        const x = xFor(version, index);
        const tick = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        tick.setAttribute('x', String(x));
        tick.setAttribute('y', String(height - 20));
        tick.setAttribute('text-anchor', 'middle');
        tick.setAttribute('fill', '#6a5646');
        tick.setAttribute('font-size', '13');
        tick.textContent = version.toUpperCase();
        svg.appendChild(tick);
      }});

      metricRows.forEach((row, index) => {{
        const points = row.points.map(point => {{
          const versionIndex = versions.indexOf(point.version);
          return [xFor(point.version, versionIndex), yFor(point[currentMetric])];
        }});
        const polyline = document.createElementNS('http://www.w3.org/2000/svg', 'polyline');
        polyline.setAttribute('fill', 'none');
        polyline.setAttribute('stroke', row.color);
        polyline.setAttribute('stroke-width', '4');
        polyline.setAttribute('stroke-linecap', 'round');
        polyline.setAttribute('stroke-linejoin', 'round');
        polyline.setAttribute('points', points.map(point => point.join(',')).join(' '));
        polyline.style.opacity = '0.92';
        polyline.style.strokeDasharray = '1400';
        polyline.style.strokeDashoffset = '1400';
        polyline.style.animation = `dash 1.2s ease forwards ${{index * 90}}ms`;
        svg.appendChild(polyline);

        row.points.forEach((point, pointIndex) => {{
          const versionIndex = versions.indexOf(point.version);
          const cx = xFor(point.version, versionIndex);
          const cy = yFor(point[currentMetric]);
          const group = document.createElementNS('http://www.w3.org/2000/svg', 'g');
          const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
          circle.setAttribute('cx', String(cx));
          circle.setAttribute('cy', String(cy));
          circle.setAttribute('r', '6');
          circle.setAttribute('fill', row.color);
          circle.setAttribute('stroke', '#fff');
          circle.setAttribute('stroke-width', '2.5');
          group.appendChild(circle);

          const title = document.createElementNS('http://www.w3.org/2000/svg', 'title');
          title.textContent = `${{row.model}} | ${{point.version.toUpperCase()}} | ${{currentMetric}}=${{point[currentMetric].toFixed(3)}}`;
          group.appendChild(title);
          group.style.animation = `rise 600ms ease both ${{index * 90 + pointIndex * 40}}ms`;
          svg.appendChild(group);
        }});
      }});
    }}

    function renderLegend() {{
      const legend = document.getElementById('metric-legend');
      legend.innerHTML = '';
      metricRows.forEach(row => {{
        const item = document.createElement('div');
        item.className = 'legend-item';
        item.innerHTML = `<span class="swatch" style="background:${{row.color}}"></span><span>${{row.model}}</span>`;
        legend.appendChild(item);
      }});
    }}

    function renderMix() {{
      const mix = document.getElementById('mix-grid');
      mix.innerHTML = '';
      devVersions.forEach(version => {{
        const card = document.createElement('div');
        card.className = 'mix-card';
        const total = version.rows;
        const labels = labelOrder.map(label => {{
          const count = version.labels[label] || 0;
          const width = total ? (count / total) * 100 : 0;
          return `<div class="seg" style="background:${{labelColors[label]}}; width:${{width}}%"></div>`;
        }}).join('');
        const labelRows = labelOrder.map(label => {{
          const count = version.labels[label] || 0;
          return `<div class="mix-label"><span class="mix-dot" style="background:${{labelColors[label]}}"></span><span>${{label.replace('_', ' ')}}: <strong>${{count}}</strong></span></div>`;
        }}).join('');
        card.innerHTML = `
          <div class="mix-head">
            <strong>${{version.label}}</strong>
            <span>${{version.rows}} rows</span>
          </div>
          <div class="stacked">${{labels}}</div>
          <div class="mix-labels">${{labelRows}}</div>
        `;
        mix.appendChild(card);
      }});
    }}

    const transferModelOrder = ['structured', 'mpnet', 'tfidf', 'modernbert', 'issue_ledger'];
    let currentTransferModel = 'structured';

    function renderTransferTabs() {{
      const tabs = document.getElementById('transfer-tabs');
      tabs.innerHTML = '';
      transferModelOrder.forEach(model => {{
        const btn = document.createElement('button');
        btn.className = 'transfer-tab' + (model === currentTransferModel ? ' active' : '');
        btn.textContent = model.replace('_', ' ');
        btn.onclick = () => {{
          currentTransferModel = model;
          renderTransferTabs();
          renderTransferGrid();
        }};
        tabs.appendChild(btn);
      }});
    }}

    function renderTransferGrid() {{
      const grid = document.getElementById('transfer-grid');
      grid.innerHTML = '';
      Object.entries(transferRows).forEach(([version, models]) => {{
        const counts = models[currentTransferModel];
        const total = labelOrder.reduce((acc, label) => acc + (counts[label] || 0), 0);
        const labels = labelOrder.map(label => {{
          const count = counts[label] || 0;
          const width = total ? (count / total) * 100 : 0;
          return `<div class="seg" style="background:${{labelColors[label]}}; width:${{width}}%"></div>`;
        }}).join('');
        const labelsDetail = labelOrder.map(label => `${{label.replace('_', ' ')}} ${{counts[label] || 0}}`).join(' · ');
        const card = document.createElement('div');
        card.className = 'transfer-card';
        card.innerHTML = `
          <div class="mix-head">
            <strong>Train ${{version.toUpperCase()}}</strong>
            <span>${{currentTransferModel.replace('_', ' ')}}</span>
          </div>
          <div class="stacked">${{labels}}</div>
          <div class="mini-note">${{labelsDetail}}</div>
        `;
        grid.appendChild(card);
      }});
    }}

    function renderDisagreements() {{
      const grid = document.getElementById('disagreement-grid');
      grid.innerHTML = '';
      disagreements.forEach(row => {{
        const pairs = Object.entries(row.top_pairs).map(([pair, count]) => `
          <div class="pair-row">
            <span>${{pair}}</span>
            <strong>${{count}}</strong>
          </div>
        `).join('');
        const card = document.createElement('div');
        card.className = 'dis-card';
        card.innerHTML = `
          <div class="dis-top">
            <strong>${{row.pair}}</strong>
            <div class="dis-total">${{row.total}}</div>
          </div>
          <div class="pair-list">${{pairs}}</div>
        `;
        grid.appendChild(card);
      }});
    }}

    document.querySelectorAll('.toggle').forEach(button => {{
      button.addEventListener('click', () => {{
        document.querySelectorAll('.toggle').forEach(item => item.classList.remove('active'));
        button.classList.add('active');
        currentMetric = button.dataset.metric;
        renderMetricChart();
      }});
    }});

    makeHero();
    renderLegend();
    renderMetricChart();
    renderMix();
    renderTransferTabs();
    renderTransferGrid();
    renderDisagreements();
  </script>
  <style>
    @keyframes dash {{
      to {{
        stroke-dashoffset: 0;
      }}
    }}
    @keyframes rise {{
      from {{
        opacity: 0;
        transform: translateY(10px) scale(0.98);
      }}
      to {{
        opacity: 1;
        transform: translateY(0) scale(1);
      }}
    }}
  </style>
</body>
</html>"""


def main() -> None:
    args = parse_args()
    payload = build_payload()
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(build_html(args.title, payload), encoding="utf-8")
    print(f"Wrote progress dashboard to {output_path}")


if __name__ == "__main__":
    main()
