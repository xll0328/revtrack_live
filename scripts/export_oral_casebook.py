from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

DEFAULT_INPUT_CSV = ROOT / "outputs/day1/paper_assets/failure_taxonomy.csv"
DEFAULT_OUTPUT_CSV = ROOT / "outputs/day1/paper_assets/oral_casebook.csv"
DEFAULT_OUTPUT_MD = ROOT / "outputs/day1/paper_assets/oral_casebook.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs/day1/paper_assets/oral_casebook.json"
DEFAULT_OUTPUT_TEX = ROOT / "paper/tables/oral_casebook_summary.tex"

MODE_ORDER = [
    "stale_criticism",
    "accuracy_trap_fixed_cases",
    "over_crediting_unresolved",
    "fixed_under_recovery",
    "regression_blindness",
    "partial_vs_fixed_boundary",
]

SPLIT_SHORT = {
    "iclr2024_signoff": "ICLR24 signoff",
    "iclr2025_repro_v2": "ICLR25 repro",
    "iclr2025_expanded80_standard": "ICLR25 exp80",
}

MODEL_SHORT = {
    "-": "-",
    "tfidf": "TF-IDF",
    "structured": "Structured",
    "issue_ledger": "Ledger",
}

LABEL_SHORT = {
    "fixed": "F",
    "partially_fixed": "P",
    "unresolved": "U",
    "regressed": "R",
}


def compact(value: str | None) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def clip(value: str | None, max_chars: int = 240) -> str:
    text = compact(value)
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(" ", 1)[0] + "..."


def read_csv(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def prediction_snapshot(row: dict[str, str]) -> str:
    tfidf = (row.get("tfidf_prediction") or "").strip()
    structured = (row.get("structured_prediction") or "").strip()
    parts = []
    if tfidf:
        parts.append(f"tfidf={tfidf}")
    if structured:
        parts.append(f"structured={structured}")
    return ", ".join(parts) if parts else "n/a"


def mode_sort_key(row: dict[str, str]) -> tuple[int, str]:
    mode = row.get("failure_mode", "")
    try:
        return (MODE_ORDER.index(mode), mode)
    except ValueError:
        return (len(MODE_ORDER), mode)


def build_casebook_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    # Keep the first record per failure mode for stable speaking examples.
    first_by_mode: dict[str, dict[str, str]] = {}
    for row in sorted(rows, key=mode_sort_key):
        mode = row.get("failure_mode", "")
        if mode and mode not in first_by_mode:
            first_by_mode[mode] = row

    ordered_modes = [mode for mode in MODE_ORDER if mode in first_by_mode]
    for mode in sorted(m for m in first_by_mode if m not in MODE_ORDER):
        ordered_modes.append(mode)

    output: list[dict[str, str]] = []
    for idx, mode in enumerate(ordered_modes, start=1):
        row = first_by_mode[mode]
        output.append(
            {
                "rank": str(idx),
                "failure_mode": mode,
                "source_split": row.get("source_split", ""),
                "model_key": row.get("model_key", "") or "-",
                "support_count": row.get("support_count", "") or "-",
                "issue_id": row.get("issue_id", ""),
                "paper_title": row.get("paper_title", ""),
                "gold_label": row.get("gold_label", ""),
                "prediction_snapshot": prediction_snapshot(row),
                "claim": compact(row.get("claim")),
                "model_risk": compact(row.get("model_risk")),
                "review_concern_excerpt": clip(row.get("review_concern"), 260),
                "revision_evidence_excerpt": clip(row.get("revision_evidence"), 260),
                "why_it_matters": compact(row.get("why_it_matters")),
            }
        )
    return output


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "rank",
        "failure_mode",
        "source_split",
        "model_key",
        "support_count",
        "issue_id",
        "paper_title",
        "gold_label",
        "prediction_snapshot",
        "claim",
        "model_risk",
        "review_concern_excerpt",
        "revision_evidence_excerpt",
        "why_it_matters",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_md(path: Path, rows: list[dict[str, str]]) -> None:
    lines = [
        "# Oral Casebook",
        "",
        "Representative failure cases for oral Q&A and rebuttal discussion.",
        "",
        "| # | Failure mode | Split | Model | Support | Gold | Predictions | Issue |",
        "| --- | --- | --- | --- | ---: | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row['rank']} | {row['failure_mode']} | {row['source_split']} | {row['model_key']} | "
            f"{row['support_count']} | {row['gold_label']} | {row['prediction_snapshot']} | `{row['issue_id']}` |"
        )

    for row in rows:
        lines.extend(
            [
                "",
                f"## Case {row['rank']}: {row['failure_mode']}",
                "",
                f"- issue: `{row['issue_id']}`",
                f"- split/model: `{row['source_split']}` / `{row['model_key']}`",
                f"- claim: {row['claim']}",
                f"- model risk: {row['model_risk']}",
                f"- why it matters: {row['why_it_matters']}",
                f"- review concern excerpt: {row['review_concern_excerpt']}",
                f"- revision evidence excerpt: {row['revision_evidence_excerpt']}",
            ]
        )
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def latex_escape(text: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "_": r"\_",
        "%": r"\%",
        "&": r"\&",
        "#": r"\#",
        "{": r"\{",
        "}": r"\}",
    }
    out = text
    for src, dst in replacements.items():
        out = out.replace(src, dst)
    return out


def write_tex(path: Path, rows: list[dict[str, str]]) -> None:
    def short_label(label: str) -> str:
        return LABEL_SHORT.get(label, label)

    def short_snapshot(snapshot: str) -> str:
        text = snapshot.strip()
        if not text or text == "n/a":
            return "n/a"
        parts = []
        for item in text.split(","):
            item = item.strip()
            if "=" not in item:
                continue
            key, value = item.split("=", 1)
            key = key.strip().lower()
            value = value.strip().lower()
            prefix = "T" if key == "tfidf" else ("S" if key == "structured" else key[:1].upper())
            parts.append(f"{prefix}:{short_label(value)}")
        return ", ".join(parts) if parts else text

    lines = [
        r"\begin{table*}[t]",
        r"\centering",
        r"\scriptsize",
        r"\setlength{\tabcolsep}{3pt}",
        r"\begin{tabular}{p{0.18\textwidth}p{0.16\textwidth}p{0.13\textwidth}p{0.44\textwidth}}",
        r"\toprule",
        r"Failure mode & Split / model & Gold / prediction & Why it matters \\",
        r"\midrule",
    ]
    for row in rows[:6]:
        split = SPLIT_SHORT.get(row["source_split"], row["source_split"])
        model = MODEL_SHORT.get(row["model_key"], row["model_key"])
        split_model = f"{split} / {model}"
        gold_pred = f"{short_label(row['gold_label'])} / {short_snapshot(row['prediction_snapshot'])}"
        why = row["why_it_matters"] or row["claim"]
        lines.append(
            f"{latex_escape(row['failure_mode'])} & {latex_escape(split_model)} & {latex_escape(gold_pred)} & "
            f"{latex_escape(clip(why, 170))} \\\\"
        )
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}",
            r"\caption{Representative failure cases used for oral/rebuttal discussion.}",
            r"\label{tab:oral-casebook-summary}",
            r"\end{table*}",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    rows = build_casebook_rows(read_csv(DEFAULT_INPUT_CSV))
    write_csv(DEFAULT_OUTPUT_CSV, rows)
    write_md(DEFAULT_OUTPUT_MD, rows)
    DEFAULT_OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_OUTPUT_JSON.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_tex(DEFAULT_OUTPUT_TEX, rows)
    print(f"Wrote {len(rows)} casebook rows.")


if __name__ == "__main__":
    main()
