from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SIGNOFF = ROOT / "outputs/day1/ai_assisted_validation_signoff/ai_assisted_validation_signoff.tsv"
DEFAULT_TFIDF_DETAILS = ROOT / "outputs/day1/iclr2025_repro_v2_full_tfidf_details.json"
DEFAULT_STRUCTURED_DETAILS = ROOT / "outputs/day1/iclr2025_repro_v2_full_structured_details.json"
DEFAULT_EXPANDED_HUMAN = ROOT / "experiments/day1/iclr2025_expanded80_human_validation_v1_blind.tsv"
DEFAULT_EXPANDED_DETAILS_DIR = ROOT / "outputs/day1/iclr2025_expanded80_standard_transfer"
DEFAULT_OUTPUT_CSV = ROOT / "outputs/day1/paper_assets/failure_taxonomy.csv"
DEFAULT_OUTPUT_MD = ROOT / "outputs/day1/paper_assets/failure_taxonomy.md"
DEFAULT_OUTPUT_TEX = ROOT / "paper/tables/failure_taxonomy.tex"

MODEL_DISPLAY = {
    "issue_ledger": "Issue ledger",
    "structured": "Structured",
    "tfidf": "TF-IDF",
    "modernbert": "ModernBERT",
    "mpnet": "MPNet",
}


TAXONOMY_SEEDS = [
    {
        "failure_mode": "stale_criticism",
        "issue_id": "w7P92BEsb2__r01",
        "paper_section": "Figure 1 / task motivation",
        "claim": "A static critique can preserve an old concern even after revision evidence directly fixes it.",
        "model_risk": "predicts partially_fixed or unresolved because the original concern remains semantically plausible",
    },
    {
        "failure_mode": "over_crediting_long_response",
        "issue_id": "My7lkRNnL9__r01",
        "paper_section": "Failure taxonomy",
        "claim": "A long response can acknowledge a limitation without resolving it.",
        "model_risk": "predicts fixed because the response is detailed and polite",
    },
    {
        "failure_mode": "partial_fix_ambiguity",
        "issue_id": "9k0krNzvlV__r02",
        "paper_section": "Label rubric",
        "claim": "Some revisions add experiments and framing but leave part of the value proposition unresolved.",
        "model_risk": "collapses partially_fixed into fixed",
    },
    {
        "failure_mode": "evidence_quality_fix",
        "issue_id": "kmn0BhQk7p__r04",
        "paper_section": "Dataset validation example",
        "claim": "Concrete added evidence, such as cross-labeling, can fully resolve a reviewer concern.",
        "model_risk": "misses concise factual fixes when the surrounding review is long",
    },
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export RevTrack qualitative failure taxonomy.")
    parser.add_argument("--signoff", default=str(DEFAULT_SIGNOFF))
    parser.add_argument("--tfidf-details", default=str(DEFAULT_TFIDF_DETAILS))
    parser.add_argument("--structured-details", default=str(DEFAULT_STRUCTURED_DETAILS))
    parser.add_argument("--expanded-human", default=str(DEFAULT_EXPANDED_HUMAN))
    parser.add_argument("--expanded-details-dir", default=str(DEFAULT_EXPANDED_DETAILS_DIR))
    parser.add_argument("--output-csv", default=str(DEFAULT_OUTPUT_CSV))
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--output-tex", default=str(DEFAULT_OUTPUT_TEX))
    return parser.parse_args()


def compact(value: str | None) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def clip(value: str | None, max_chars: int = 260) -> str:
    text = compact(value)
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(" ", 1)[0] + "..."


def load_tsv(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def by_id(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row["issue_id"]: row for row in rows if row.get("issue_id")}


def prediction_lookup(details: list[dict[str, str]]) -> dict[str, str]:
    return {row["id"]: row["predicted_label"] for row in details}


def row_template(
    *,
    failure_mode: str,
    issue_id: str,
    paper_title: str = "",
    gold_label: str = "",
    tfidf_prediction: str = "",
    structured_prediction: str = "",
    paper_section: str = "",
    claim: str = "",
    model_risk: str = "",
    review_concern: str = "",
    revision_evidence: str = "",
    why_it_matters: str = "",
    source_split: str = "iclr2024_signoff",
    model_key: str = "",
    support_count: str = "",
) -> dict[str, str]:
    return {
        "failure_mode": failure_mode,
        "issue_id": issue_id,
        "paper_title": paper_title,
        "gold_label": gold_label,
        "tfidf_prediction": tfidf_prediction,
        "structured_prediction": structured_prediction,
        "paper_section": paper_section,
        "claim": claim,
        "model_risk": model_risk,
        "review_concern": review_concern,
        "revision_evidence": revision_evidence,
        "why_it_matters": why_it_matters,
        "source_split": source_split,
        "model_key": model_key,
        "support_count": support_count,
    }


def matching_errors(
    details: list[dict[str, str]],
    *,
    gold: str,
    predicted: set[str],
) -> list[dict[str, str]]:
    return [
        row
        for row in details
        if row.get("gold_label") == gold and row.get("predicted_label") in predicted
    ]


def build_expanded80_rows(
    *,
    human_rows: list[dict[str, str]],
    details_by_model: dict[str, list[dict[str, str]]],
) -> list[dict[str, str]]:
    human = by_id(human_rows)
    tfidf = prediction_lookup(details_by_model.get("tfidf", []))
    structured = prediction_lookup(details_by_model.get("structured", []))
    specs = [
        {
            "failure_mode": "over_crediting_unresolved",
            "model_key": "structured",
            "gold": "unresolved",
            "predicted": {"fixed", "partially_fixed"},
            "claim": "Transfer models often treat a response or local edit as resolution even when the original concern remains open.",
            "model_risk": "over-credits unresolved concerns as fixed or partially fixed",
            "why_it_matters": "This is the practical stale-assistant failure: the model would stop tracking an unresolved concern.",
        },
        {
            "failure_mode": "fixed_under_recovery",
            "model_key": "tfidf",
            "gold": "fixed",
            "predicted": {"partially_fixed", "unresolved", "regressed"},
            "claim": "Semantic baselines can miss direct fixes when the old criticism remains lexically salient.",
            "model_risk": "keeps a fixed concern alive as partially fixed or unresolved",
            "why_it_matters": "This motivates fixed-case F1 rather than accuracy-only reporting.",
        },
        {
            "failure_mode": "regression_blindness",
            "model_key": "tfidf",
            "gold": "regressed",
            "predicted": {"fixed", "partially_fixed", "unresolved"},
            "claim": "Regression cases are rare but high-risk: several baselines smooth them into non-regression labels.",
            "model_risk": "misses cases where the revision introduces or worsens a problem",
            "why_it_matters": "This justifies keeping the regressed label while avoiding strong regression-performance claims.",
        },
        {
            "failure_mode": "partial_vs_fixed_boundary",
            "model_key": "issue_ledger",
            "gold": "partially_fixed",
            "predicted": {"fixed"},
            "claim": "Even the best expanded80 model sometimes upgrades partial evidence into a full fix.",
            "model_risk": "collapses partial resolution into fixed",
            "why_it_matters": "This is the central label-boundary risk for benchmark reliability.",
        },
    ]

    rows: list[dict[str, str]] = []
    for spec in specs:
        model_key = spec["model_key"]
        matches = matching_errors(
            details_by_model.get(model_key, []),
            gold=spec["gold"],
            predicted=spec["predicted"],
        )
        if not matches:
            continue
        example = matches[0]
        issue_id = example["id"]
        human_row = human.get(issue_id, {})
        rows.append(
            row_template(
                failure_mode=spec["failure_mode"],
                issue_id=issue_id,
                paper_title=example.get("paper_title", human_row.get("paper_title", "")),
                gold_label=example.get("gold_label", ""),
                tfidf_prediction=tfidf.get(issue_id, ""),
                structured_prediction=structured.get(issue_id, ""),
                paper_section="Expanded80 failure taxonomy",
                claim=f"{spec['claim']} Observed {len(matches)} times for {MODEL_DISPLAY.get(model_key, model_key)} on expanded80.",
                model_risk=spec["model_risk"],
                review_concern=clip(human_row.get("review_excerpt")),
                revision_evidence=clip(human_row.get("evidence_span")),
                why_it_matters=spec["why_it_matters"],
                source_split="iclr2025_expanded80_standard",
                model_key=model_key,
                support_count=str(len(matches)),
            )
        )
    return rows


def build_rows(
    *,
    signoff_rows: list[dict[str, str]],
    tfidf_details: list[dict[str, str]],
    structured_details: list[dict[str, str]],
    expanded_human_rows: list[dict[str, str]] | None = None,
    expanded_details_by_model: dict[str, list[dict[str, str]]] | None = None,
) -> list[dict[str, str]]:
    signoff = by_id(signoff_rows)
    tfidf = prediction_lookup(tfidf_details)
    structured = prediction_lookup(structured_details)
    rows: list[dict[str, str]] = []

    for seed in TAXONOMY_SEEDS:
        row = signoff[seed["issue_id"]]
        rows.append(
            row_template(
                failure_mode=seed["failure_mode"],
                issue_id=seed["issue_id"],
                paper_title=row.get("paper_title", ""),
                gold_label=row.get("assistant_label", ""),
                tfidf_prediction=tfidf.get(seed["issue_id"], ""),
                structured_prediction=structured.get(seed["issue_id"], ""),
                paper_section=seed["paper_section"],
                claim=seed["claim"],
                model_risk=seed["model_risk"],
                review_concern=clip(row.get("review_excerpt")),
                revision_evidence=clip(row.get("assistant_evidence_span")),
                why_it_matters="This example separates revision-aware judgment from static semantic plausibility.",
                source_split="iclr2024_signoff",
            )
        )

    fixed_misses = [
        row
        for row in tfidf_details
        if row.get("gold_label") == "fixed" and row.get("predicted_label") != "fixed"
    ]
    if fixed_misses:
        example = fixed_misses[0]
        signoff_row = signoff.get(example["id"], {})
        rows.append(
            row_template(
                failure_mode="accuracy_trap_fixed_cases",
                issue_id=example["id"],
                paper_title=example.get("paper_title", ""),
                gold_label=example.get("gold_label", ""),
                tfidf_prediction=example.get("predicted_label", ""),
                structured_prediction=structured.get(example["id"], ""),
                paper_section="Results / accuracy trap",
                claim="A majority-like model can score well by predicting partially_fixed while missing fixed cases.",
                model_risk="high accuracy, low fixed-label recovery",
                review_concern=clip(signoff_row.get("review_excerpt")),
                revision_evidence=clip(signoff_row.get("assistant_evidence_span")),
                why_it_matters="This is the core reason the paper reports macro-F1 and per-label recovery.",
                source_split="iclr2025_repro_v2",
                model_key="tfidf",
                support_count=str(len(fixed_misses)),
            )
        )
    if expanded_human_rows and expanded_details_by_model:
        rows.extend(
            build_expanded80_rows(
                human_rows=expanded_human_rows,
                details_by_model=expanded_details_by_model,
            )
        )
    return rows


def write_csv(path: str | Path, rows: list[dict[str, str]]) -> None:
    fields = [
        "failure_mode",
        "source_split",
        "model_key",
        "support_count",
        "issue_id",
        "paper_title",
        "gold_label",
        "tfidf_prediction",
        "structured_prediction",
        "paper_section",
        "claim",
        "model_risk",
        "review_concern",
        "revision_evidence",
        "why_it_matters",
    ]
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: str | Path, rows: list[dict[str, str]]) -> None:
    lines = [
        "# RevTrack Failure Taxonomy v0",
        "",
        "This table is a paper-facing qualitative analysis seed. It turns model errors and label-boundary examples into reusable claims for Figure 1, the task definition, and the results analysis. Expanded80 rows use user-confirmed standard validation, not independent IAA.",
        "",
        "| failure mode | split | model | n | issue | gold | TF-IDF | structured | paper use | claim |",
        "| --- | --- | --- | ---: | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    row["failure_mode"],
                    row["source_split"],
                    MODEL_DISPLAY.get(row["model_key"], row["model_key"]) or "-",
                    row["support_count"] or "-",
                    f"`{row['issue_id']}`",
                    row["gold_label"],
                    row["tfidf_prediction"] or "-",
                    row["structured_prediction"] or "-",
                    row["paper_section"],
                    row["claim"],
                ]
            )
            + " |"
        )
    lines.append("")
    lines.append("## Writing Use")
    lines.append("")
    lines.append("- Use `stale_criticism` for Figure 1 and the opening paragraph.")
    lines.append("- Use `over_crediting_long_response` to show why response length is not resolution evidence.")
    lines.append("- Use `partial_fix_ambiguity` to justify the four-label rubric.")
    lines.append("- Use `accuracy_trap_fixed_cases` to motivate macro-F1 and per-label recovery.")
    lines.append("- Use expanded80 aggregate rows for the RQ3/RQ4 bridge: transfer brittleness is mostly over-crediting unresolved issues, fixed under-recovery, and regression blindness.")
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def latex_escape(value: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in value)


def write_latex(path: str | Path, rows: list[dict[str, str]]) -> None:
    preferred = [
        "stale_criticism",
        "over_crediting_unresolved",
        "fixed_under_recovery",
        "regression_blindness",
        "partial_vs_fixed_boundary",
    ]
    by_mode = {row["failure_mode"]: row for row in rows}
    selected = [by_mode[mode] for mode in preferred if mode in by_mode]
    mode_names = {
        "stale_criticism": "Stale criticism",
        "over_crediting_unresolved": "Over-crediting",
        "fixed_under_recovery": "Fixed under-recovery",
        "regression_blindness": "Regression blindness",
        "partial_vs_fixed_boundary": "Partial/full boundary",
    }
    lines = [
        r"\begin{table}[t]",
        r"\centering",
        r"\scriptsize",
        r"\setlength{\tabcolsep}{3pt}",
        r"\begin{tabular}{p{0.22\linewidth}p{0.31\linewidth}p{0.35\linewidth}}",
        r"\toprule",
        r"Failure mode & Pattern & Evidence use \\",
        r"\midrule",
    ]
    for row in selected:
        support = f" ({row['support_count']} expanded80 errors)" if row["support_count"] else ""
        pattern = row["model_risk"] + support
        lines.append(
            f"{latex_escape(mode_names.get(row['failure_mode'], row['failure_mode']))} & "
            f"{latex_escape(pattern)} & "
            f"{latex_escape(row['why_it_matters'])} \\\\"
        )
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}",
            r"\caption{Qualitative failure taxonomy used to interpret RevTrack errors. Expanded80 counts are from the user-confirmed standard active frontier and should not be read as natural prevalence.}",
            r"\label{tab:failure-taxonomy}",
            r"\end{table}",
        ]
    )
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def load_expanded_details(path: str | Path) -> dict[str, list[dict[str, str]]]:
    root = Path(path)
    details: dict[str, list[dict[str, str]]] = {}
    for model_key in MODEL_DISPLAY:
        detail_path = root / f"{model_key}_details.json"
        if detail_path.exists():
            details[model_key] = load_json(detail_path)
    return details


def main() -> None:
    args = parse_args()
    expanded_human = Path(args.expanded_human)
    expanded_details = load_expanded_details(args.expanded_details_dir)
    rows = build_rows(
        signoff_rows=load_tsv(args.signoff),
        tfidf_details=load_json(args.tfidf_details),
        structured_details=load_json(args.structured_details),
        expanded_human_rows=load_tsv(expanded_human) if expanded_human.exists() else None,
        expanded_details_by_model=expanded_details,
    )
    write_csv(args.output_csv, rows)
    write_markdown(args.output_md, rows)
    write_latex(args.output_tex, rows)
    print(f"Wrote {len(rows)} taxonomy rows to {args.output_csv}")


if __name__ == "__main__":
    main()
