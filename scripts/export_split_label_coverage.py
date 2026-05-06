from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LABELS = ["fixed", "partially_fixed", "unresolved", "regressed"]


DATASET_SPECS = [
    {
        "split": "ICLR 2024 clean dev v7",
        "path": "data/processed/iclr2024_clean_dev_assistant_v7.jsonl",
        "sample_design": "in_domain_standard",
        "validation_status": "standard_single_user_confirmed",
    },
    {
        "split": "ICLR 2025 repro v2",
        "path": "data/processed/iclr2025_repro_multi_frontier_structured_v2_full_assistant.jsonl",
        "sample_design": "stress_set",
        "validation_status": "standard_single_user_confirmed",
    },
    {
        "split": "ICLR 2025 expanded80",
        "path": "data/processed/iclr2025_expanded80_standard_validation_v1.jsonl",
        "sample_design": "active_frontier",
        "validation_status": "standard_single_user_confirmed",
    },
    {
        "split": "NeurIPS 2024 limit100",
        "path": "data/processed/neurips2024_limit100_standard_validation_v1.jsonl",
        "sample_design": "active_frontier",
        "validation_status": "standard_single_user_confirmed",
    },
    {
        "split": "ICLR 2023 random80",
        "path": "data/processed/iclr2023_limit80_random80_standard_validation_v1.jsonl",
        "sample_design": "random_stratified",
        "validation_status": "standard_single_user_confirmed",
    },
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export split-level label coverage diagnostics for paper-facing claim boundaries.")
    parser.add_argument("--output-csv", default="outputs/day1/paper_assets/split_label_coverage.csv")
    parser.add_argument("--output-json", default="outputs/day1/paper_assets/split_label_coverage.json")
    parser.add_argument("--output-md", default="outputs/day1/paper_assets/split_label_coverage.md")
    parser.add_argument("--output-tex", default="paper/tables/split_label_coverage.tex")
    return parser.parse_args()


def resolve(path: str | Path) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else ROOT / candidate


def load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def label_of(row: dict) -> str:
    return str(row.get("gold_label") or row.get("human_label") or "").strip().lower()


def export_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "split",
        "rows",
        "sample_design",
        "validation_status",
        "fixed",
        "partially_fixed",
        "unresolved",
        "regressed",
        "missing_labels",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def export_json(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rows, indent=2), encoding="utf-8")


def export_md(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Split Label Coverage",
        "",
        "This panel summarizes label availability for each paper-facing split.",
        "Missing labels indicate where four-way interpretation should be treated as bounded.",
        "",
        "| Split | Rows | Design | fixed | partially_fixed | unresolved | regressed | Missing labels |",
        "| --- | ---: | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row['split']} | {row['rows']} | {row['sample_design']} | {row['fixed']} | "
            f"{row['partially_fixed']} | {row['unresolved']} | {row['regressed']} | {row['missing_labels'] or '-'} |"
        )
    lines.extend(
        [
            "",
            "Boundary notes:",
            "- Active-frontier splits are disagreement-harvested hard subsets, not natural prevalence samples.",
            "- Missing-label splits should not be interpreted as full four-way coverage for prevalence claims.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def latex_escape(value: str) -> str:
    return value.replace("_", "\\_")


def export_tex(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "\\begin{table*}[t]",
        "\\centering",
        "\\scriptsize",
        "\\setlength{\\tabcolsep}{3pt}",
        "\\begin{tabular}{p{0.26\\textwidth}r p{0.16\\textwidth}rrrr p{0.18\\textwidth}}",
        "\\toprule",
        "Split & Rows & Design & fixed & partial & unresolved & regressed & Missing labels \\\\",
        "\\midrule",
    ]
    for row in rows:
        missing = row["missing_labels"] or "-"
        split = latex_escape(str(row["split"]))
        design = latex_escape(str(row["sample_design"]))
        missing_escaped = latex_escape(str(missing))
        lines.append(
            f"{split} & {row['rows']} & {design} & {row['fixed']} & "
            f"{row['partially_fixed']} & {row['unresolved']} & {row['regressed']} & {missing_escaped} \\\\"
        )
    lines.extend(
        [
            "\\bottomrule",
            "\\end{tabular}",
            "\\caption{Split-level label coverage and missing-label diagnostics for paper-facing evaluations. Missing labels mark bounded four-way interpretation.}",
            "\\label{tab:split-label-coverage}",
            "\\end{table*}",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_rows(specs: list[dict] | None = None) -> list[dict]:
    rows: list[dict] = []
    for spec in specs or DATASET_SPECS:
        payload = load_jsonl(resolve(spec["path"]))
        counter = Counter(label_of(row) for row in payload)
        missing = [label for label in LABELS if counter.get(label, 0) == 0]
        rows.append(
            {
                "split": spec["split"],
                "rows": len(payload),
                "sample_design": spec["sample_design"],
                "validation_status": spec["validation_status"],
                "fixed": counter.get("fixed", 0),
                "partially_fixed": counter.get("partially_fixed", 0),
                "unresolved": counter.get("unresolved", 0),
                "regressed": counter.get("regressed", 0),
                "missing_labels": ",".join(missing),
            }
        )
    return rows


def main() -> None:
    args = parse_args()
    rows = build_rows()
    export_csv(resolve(args.output_csv), rows)
    export_json(resolve(args.output_json), rows)
    export_md(resolve(args.output_md), rows)
    export_tex(resolve(args.output_tex), rows)
    print(f"Wrote split-label coverage panel for {len(rows)} splits.")


if __name__ == "__main__":
    main()
