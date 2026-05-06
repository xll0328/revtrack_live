from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    src = ROOT / "outputs/day1/prompted_llm_baselines/postprocess_rule_search.json"
    payload = json.loads(src.read_text(encoding="utf-8"))
    rules = payload["rules"]

    lines = [
        r"\begin{table*}[t]",
        r"\centering",
        r"\scriptsize",
        r"\setlength{\tabcolsep}{3pt}",
        r"\begin{tabular}{p{0.28\textwidth}rrrrr}",
        r"\toprule",
        r"Rule & Mean F1 & ICLR24 F1 & ICLR25 F1 & NeurIPS24 F1 & ICLR25 U Recall \\",
        r"\midrule",
    ]

    for item in rules:
        by_ds = {row["dataset_key"]: row for row in item["datasets"]}
        rule_name = item["rule"].replace("_", r"\_")
        mean_f1 = float(item["mean_macro_f1"])
        iclr24 = float(by_ds["iclr2024_clean_dev_v7"]["macro_f1"])
        iclr25 = float(by_ds["iclr2025_expanded80"]["macro_f1"])
        neu24 = float(by_ds["neurips2024_limit100_resolved_candidate"]["macro_f1"])
        iclr25_u = float(by_ds["iclr2025_expanded80"]["unresolved_recall"])
        lines.append(
            f"{rule_name} & {mean_f1:.3f} & {iclr24:.3f} & {iclr25:.3f} & {neu24:.3f} & {iclr25_u:.3f} \\\\"
        )

    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}",
            r"\caption{Offline post-processing rule search on top of a three-model prompted vote (GPT-5.5(v2), GPT-4.1-mini, Qwen2.5-72B). The best rule combines unresolved guarding with fixed-disagreement suppression.}",
            r"\label{tab:prompted-llm-postprocess-rules}",
            r"\end{table*}",
            "",
        ]
    )

    out = ROOT / "paper/tables/prompted_llm_postprocess_rules.tex"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
