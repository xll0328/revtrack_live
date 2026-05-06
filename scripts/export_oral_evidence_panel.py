from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

DEFAULT_NULL_BASELINES = ROOT / "outputs/day1/paper_assets/null_baseline_comparison.csv"
DEFAULT_EXPANDED80 = ROOT / "outputs/day1/paper_assets/iclr2025_expanded80_standard_transfer_metrics.csv"
DEFAULT_NEURIPS = ROOT / "outputs/day1/paper_assets/neurips2024_limit100_standard_transfer_metrics.csv"
DEFAULT_PROMPTED_SIG = ROOT / "outputs/day1/paper_assets/prompted_llm_significance.csv"
DEFAULT_IAA_METRICS = ROOT / "outputs/day1/paper_assets/iaa_second_annotator_boundary160_v1_metrics.json"
DEFAULT_READINESS = ROOT / "outputs/day1/paper_assets/paper_readiness_audit.json"

DEFAULT_OUTPUT_CSV = ROOT / "outputs/day1/paper_assets/oral_evidence_panel.csv"
DEFAULT_OUTPUT_MD = ROOT / "outputs/day1/paper_assets/oral_evidence_panel.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs/day1/paper_assets/oral_evidence_panel.json"
DEFAULT_OUTPUT_TEX = ROOT / "paper/tables/oral_evidence_panel.tex"


def read_csv(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def to_float(value: str | None) -> float:
    return float(value or 0.0)


def pick_row(rows: list[dict[str, str]], **conditions: str) -> dict[str, str]:
    for row in rows:
        if all((row.get(key, "") == value) for key, value in conditions.items()):
            return row
    raise ValueError(f"Missing row for conditions={conditions}")


def fmt3(value: float) -> str:
    return f"{value:.3f}"


def build_panel() -> list[dict[str, str]]:
    null_rows = read_csv(DEFAULT_NULL_BASELINES)
    expanded_rows = read_csv(DEFAULT_EXPANDED80)
    neurips_rows = read_csv(DEFAULT_NEURIPS)
    prompted_rows = read_csv(DEFAULT_PROMPTED_SIG)
    iaa = json.loads(DEFAULT_IAA_METRICS.read_text(encoding="utf-8"))
    readiness = json.loads(DEFAULT_READINESS.read_text(encoding="utf-8"))

    iclr24_structured = pick_row(
        null_rows,
        dataset_key="iclr2024_clean_dev_v7",
        row_type="model",
        model_key="structured",
    )
    iclr24_mpnet = pick_row(
        null_rows,
        dataset_key="iclr2024_clean_dev_v7",
        row_type="model",
        model_key="mpnet",
    )
    iclr25_majority = pick_row(
        null_rows,
        dataset_key="iclr2025_repro_v2",
        row_type="null_baseline",
        model_key="majority_label",
    )
    iclr25_tfidf = pick_row(
        null_rows,
        dataset_key="iclr2025_repro_v2",
        row_type="model",
        model_key="tfidf",
    )

    expanded_issue = pick_row(expanded_rows, model_key="issue_ledger")
    expanded_structured = pick_row(expanded_rows, model_key="structured")

    neurips_mpnet = pick_row(neurips_rows, model_key="mpnet")
    neurips_tfidf = pick_row(neurips_rows, model_key="tfidf")

    p_iclr25_vote = pick_row(prompted_rows, dataset="ICLR25", method="Vote-3 (+U+F-cal)")
    p_iclr25_majority = pick_row(prompted_rows, dataset="ICLR25", method="Majority")
    p_neurips_vote = pick_row(prompted_rows, dataset="NeurIPS24", method="Vote-3 (+U+F-cal)")
    p_neurips_majority = pick_row(prompted_rows, dataset="NeurIPS24", method="Majority")

    structured_macro = to_float(iclr24_structured["macro_f1"])
    mpnet_macro = to_float(iclr24_mpnet["macro_f1"])
    gap = structured_macro - mpnet_macro

    panel = [
        {
            "axis": "In-domain gain",
            "checkpoint": (
                f"ICLR24 structured macro-F1={fmt3(structured_macro)} vs MPNet={fmt3(mpnet_macro)} "
                f"(delta={fmt3(gap)})"
            ),
            "boundary": "Clean-dev v7 only; transfer claims are separate.",
        },
        {
            "axis": "Accuracy trap",
            "checkpoint": (
                f"ICLR25 repro TF-IDF acc={fmt3(to_float(iclr25_tfidf['accuracy']))} equals majority "
                f"acc={fmt3(to_float(iclr25_majority['accuracy']))}; fixed F1 stays {fmt3(to_float(iclr25_tfidf['fixed_f1']))}"
            ),
            "boundary": "Stress-set diagnostic, not prevalence estimate.",
        },
        {
            "axis": "Transfer frontier (ICLR25 expanded80)",
            "checkpoint": (
                f"Best macro-F1 is issue-ledger {fmt3(to_float(expanded_issue['macro_f1']))}; structured macro-F1 "
                f"{fmt3(to_float(expanded_structured['macro_f1']))} with unresolved F1 {fmt3(to_float(expanded_structured['unresolved_f1']))}"
            ),
            "boundary": "Active disagreement frontier; no natural-prevalence claim.",
        },
        {
            "axis": "Cross-venue frontier (NeurIPS24)",
            "checkpoint": (
                f"Best macro-F1 is MPNet {fmt3(to_float(neurips_mpnet['macro_f1']))}; TF-IDF unresolved F1 "
                f"{fmt3(to_float(neurips_tfidf['unresolved_f1']))}"
            ),
            "boundary": "Single-user standard frontier; fixed/regressed labels absent in this split.",
        },
        {
            "axis": "Prompted significance",
            "checkpoint": (
                f"ICLR25 Vote-3(+U+F-cal) macro-F1 {fmt3(to_float(p_iclr25_vote['macro_f1']))} vs majority "
                f"{fmt3(to_float(p_iclr25_majority['macro_f1']))}; NeurIPS24 vote {fmt3(to_float(p_neurips_vote['macro_f1']))} "
                f"vs majority {fmt3(to_float(p_neurips_majority['macro_f1']))}"
            ),
            "boundary": "Bootstrap deltas quantify split uncertainty only.",
        },
        {
            "axis": "IAA boundary-packet reliability",
            "checkpoint": (
                f"boundary160 labeled={iaa.get('labeled_rows')} agreement={fmt3(float(iaa.get('agreement') or 0.0))} "
                f"kappa={fmt3(float(iaa.get('cohen_kappa') or 0.0))} mismatches={iaa.get('mismatches')}"
            ),
            "boundary": "User-confirmed prelabel-assisted packet; bounded support, not blind-independent full two-annotator coverage.",
        },
        {
            "axis": "Readiness gate",
            "checkpoint": (
                f"overall_status={readiness.get('overall_status')} ready_claims={readiness.get('claim_status_counts', {}).get('ready', 0)} "
                f"blockers={len(readiness.get('blockers', []))}"
            ),
            "boundary": "Submission gate is satisfied for current scoped claims.",
        },
    ]
    return panel


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["axis", "checkpoint", "boundary"])
        writer.writeheader()
        writer.writerows(rows)


def write_md(path: Path, rows: list[dict[str, str]]) -> None:
    lines = [
        "# Oral Evidence Panel",
        "",
        "Reviewer-facing high-signal checkpoints for oral/rebuttal sprint.",
        "",
        "| Axis | Quantitative checkpoint | Claim boundary |",
        "| --- | --- | --- |",
    ]
    for row in rows:
        lines.append(f"| {row['axis']} | {row['checkpoint']} | {row['boundary']} |")
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
    lines = [
        r"\begin{table*}[t]",
        r"\centering",
        r"\scriptsize",
        r"\setlength{\tabcolsep}{3pt}",
        r"\begin{tabular}{p{0.19\textwidth}p{0.47\textwidth}p{0.28\textwidth}}",
        r"\toprule",
        r"Axis & Quantitative checkpoint & Claim boundary \\",
        r"\midrule",
    ]
    for row in rows:
        lines.append(
            f"{latex_escape(row['axis'])} & {latex_escape(row['checkpoint'])} & {latex_escape(row['boundary'])} \\\\"
        )
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}",
            r"\caption{Oral/rebuttal evidence panel built from current auditable artifacts.}",
            r"\label{tab:oral-evidence-panel}",
            r"\end{table*}",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    rows = build_panel()
    write_csv(DEFAULT_OUTPUT_CSV, rows)
    write_md(DEFAULT_OUTPUT_MD, rows)
    DEFAULT_OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_OUTPUT_JSON.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_tex(DEFAULT_OUTPUT_TEX, rows)
    print(f"Wrote {len(rows)} oral-evidence rows.")


if __name__ == "__main__":
    main()
