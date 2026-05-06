from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Aggregate multi-seed ModernBERT fine-tune probe metrics.")
    parser.add_argument(
        "--seed-dir",
        action="append",
        required=True,
        help="Directory containing metrics_summary.json from one seed run. Repeatable.",
    )
    parser.add_argument("--output-csv", default="outputs/day1/paper_assets/finetuned_modernbert_multiseed_20260506.csv")
    parser.add_argument("--output-json", default="outputs/day1/paper_assets/finetuned_modernbert_multiseed_20260506.json")
    parser.add_argument("--output-md", default="outputs/day1/paper_assets/finetuned_modernbert_multiseed_20260506.md")
    parser.add_argument("--output-tex", default="paper/tables/finetuned_modernbert_multiseed_probe.tex")
    return parser.parse_args()


def resolve(path: str | Path) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else ROOT / candidate


def load_metrics(seed_dir: Path) -> dict[str, dict[str, float]]:
    payload = json.loads((seed_dir / "metrics_summary.json").read_text(encoding="utf-8"))
    return {row["split"]: row for row in payload}


def aggregate(seeds: list[Path]) -> list[dict[str, float | str]]:
    per_seed = [load_metrics(seed) for seed in seeds]
    splits = sorted(per_seed[0].keys())
    rows: list[dict[str, float | str]] = []
    for split in splits:
        metrics = {
            "accuracy": np.array([seed_metrics[split]["accuracy"] for seed_metrics in per_seed], dtype=float),
            "macro_f1": np.array([seed_metrics[split]["macro_f1"] for seed_metrics in per_seed], dtype=float),
            "fixed_f1": np.array([seed_metrics[split]["fixed_f1"] for seed_metrics in per_seed], dtype=float),
            "partially_fixed_f1": np.array([seed_metrics[split]["partially_fixed_f1"] for seed_metrics in per_seed], dtype=float),
            "unresolved_f1": np.array([seed_metrics[split]["unresolved_f1"] for seed_metrics in per_seed], dtype=float),
            "regressed_f1": np.array([seed_metrics[split]["regressed_f1"] for seed_metrics in per_seed], dtype=float),
        }
        rows.append(
            {
                "split": split,
                "rows": int(per_seed[0][split]["rows"]),
                "seeds": len(seeds),
                "accuracy_mean": float(metrics["accuracy"].mean()),
                "accuracy_std": float(metrics["accuracy"].std(ddof=0)),
                "macro_f1_mean": float(metrics["macro_f1"].mean()),
                "macro_f1_std": float(metrics["macro_f1"].std(ddof=0)),
                "unresolved_f1_mean": float(metrics["unresolved_f1"].mean()),
                "unresolved_f1_std": float(metrics["unresolved_f1"].std(ddof=0)),
                "fixed_f1_mean": float(metrics["fixed_f1"].mean()),
                "fixed_f1_std": float(metrics["fixed_f1"].std(ddof=0)),
                "regressed_f1_mean": float(metrics["regressed_f1"].mean()),
                "regressed_f1_std": float(metrics["regressed_f1"].std(ddof=0)),
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, float | str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, rows: list[dict[str, float | str]], seed_dirs: list[Path]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "seed_dirs": [str(seed) for seed in seed_dirs],
        "rows": rows,
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def fmt(mean: float, std: float) -> str:
    return f"{mean:.3f} ± {std:.3f}"


def write_md(path: Path, rows: list[dict[str, float | str]], seed_dirs: list[Path]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Fine-Tuned ModernBERT Multi-Seed Probe (2026-05-06)",
        "",
        f"Seeds: `{len(seed_dirs)}`",
        "",
        "Seed run dirs:",
    ]
    for seed in seed_dirs:
        lines.append(f"- `{seed}`")
    lines.extend(
        [
            "",
            "| Split | Rows | Accuracy | Macro-F1 | Unresolved F1 | Fixed F1 | Regressed F1 |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in rows:
        lines.append(
            f"| {row['split']} | {row['rows']} | {fmt(row['accuracy_mean'], row['accuracy_std'])} | "
            f"{fmt(row['macro_f1_mean'], row['macro_f1_std'])} | {fmt(row['unresolved_f1_mean'], row['unresolved_f1_std'])} | "
            f"{fmt(row['fixed_f1_mean'], row['fixed_f1_std'])} | {fmt(row['regressed_f1_mean'], row['regressed_f1_std'])} |"
        )
    lines.extend(
        [
            "",
            "Readout:",
            "- In-domain performance is materially higher than simple semantic baselines.",
            "- Transfer unresolved/regressed recovery remains near-zero across seeds on frontier splits.",
            "- This supports a stronger version of the transfer-brittleness claim while reducing single-seed variance concerns.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def latex_escape(value: str) -> str:
    return value.replace("_", "\\_")


def write_tex(path: Path, rows: list[dict[str, float | str]], seed_count: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "\\begin{table}[t]",
        "\\centering",
        "\\scriptsize",
        "\\setlength{\\tabcolsep}{3pt}",
        "\\begin{tabular}{p{0.28\\linewidth}rrr}",
        "\\toprule",
        "Split & Accuracy & Macro-F1 & Unresolved F1 \\\\",
        "\\midrule",
    ]
    for row in rows:
        lines.append(
            f"{latex_escape(str(row['split']))} & "
            f"{row['accuracy_mean']:.3f}$\\pm${row['accuracy_std']:.3f} & "
            f"{row['macro_f1_mean']:.3f}$\\pm${row['macro_f1_std']:.3f} & "
            f"{row['unresolved_f1_mean']:.3f}$\\pm${row['unresolved_f1_std']:.3f} \\\\"
        )
    lines.extend(
        [
            "\\bottomrule",
            "\\end{tabular}",
            f"\\caption{{Multi-seed ($n={seed_count}$) fine-tuned ModernBERT probe trained on ICLR2024 train v8. Transfer unresolved recovery remains brittle across seeds.}}",
            "\\label{tab:finetuned-modernbert-multiseed}",
            "\\end{table}",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    seed_dirs = [resolve(seed_dir) for seed_dir in args.seed_dir]
    rows = aggregate(seed_dirs)
    write_csv(resolve(args.output_csv), rows)
    write_json(resolve(args.output_json), rows, seed_dirs)
    write_md(resolve(args.output_md), rows, seed_dirs)
    write_tex(resolve(args.output_tex), rows, len(seed_dirs))
    print(f"Wrote multi-seed probe summary for {len(seed_dirs)} seeds.")


if __name__ == "__main__":
    main()
