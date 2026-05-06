from __future__ import annotations

import argparse
import csv
import re
from collections import Counter
from pathlib import Path


MODEL_FIELDS = [
    "tfidf_label",
    "modernbert_label",
    "mpnet_label",
    "issue_ledger_label",
    "structured_label",
]
REGRESSION_CUES = {
    "contradict",
    "contradicted",
    "decrease",
    "decreased",
    "degrade",
    "degraded",
    "dropped",
    "fail",
    "failure",
    "harm",
    "hurt",
    "incorrect",
    "inconsistent",
    "introduced",
    "introduces",
    "removed",
    "regress",
    "regression",
    "rushed",
    "weaker",
    "worse",
    "worsen",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export a regression-verification packet for active-frontier assistant adjudication."
    )
    parser.add_argument("--dataset-name", required=True)
    parser.add_argument("--adjudication", required=True)
    parser.add_argument("--review-queue", required=True)
    parser.add_argument("--output-csv", required=True)
    parser.add_argument("--output-md", required=True)
    parser.add_argument("--top-n", type=int, default=40)
    return parser.parse_args()


def compact(value: str | None) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def clip(value: str | None, max_chars: int = 320) -> str:
    text = compact(value)
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(" ", 1)[0] + "..."


def load_tsv(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def load_csv(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def model_labels(row: dict[str, str]) -> dict[str, str]:
    return {
        field.removesuffix("_label"): compact(row.get(field)).lower()
        for field in MODEL_FIELDS
        if compact(row.get(field))
    }


def support_models(row: dict[str, str]) -> list[str]:
    label = compact(row.get("assistant_label")).lower()
    return [name for name, value in model_labels(row).items() if value == label]


def response_revision_text(row: dict[str, str]) -> str:
    return compact(" ".join([row.get("aligned_response_excerpt", ""), row.get("revision_summary", "")]))


def cue_hits(text: str) -> list[str]:
    lower = text.lower()
    return sorted(cue for cue in REGRESSION_CUES if re.search(rf"\b{re.escape(cue)}\w*\b", lower))


def risk_tier(row: dict[str, str]) -> tuple[str, str, str]:
    label = compact(row.get("assistant_label")).lower()
    evidence_source = compact(row.get("evidence_source")).lower()
    context = response_revision_text(row)
    context_cues = cue_hits(context)
    support_count = len(support_models(row))

    if label != "regressed":
        return (
            "tier_4_not_regressed",
            "not_a_regressed_draft",
            "Review under the standard active-frontier queue rather than the regression gate.",
        )
    if evidence_source == "review_excerpt" and not context:
        return (
            "tier_1_block_regressed",
            "do_not_promote_as_regressed",
            "Do not keep regressed without response/revision evidence; relabel or fetch missing context before promotion.",
        )
    if evidence_source == "review_excerpt":
        return (
            "tier_2_old_concern_only_risk",
            "manual_same_axis_check_required",
            "Original-review evidence cannot prove regression; require response/revision evidence of a same-axis negative change.",
        )
    if not context_cues or support_count <= 1:
        return (
            "tier_3_regression_candidate_needs_confirmation",
            "manual_same_axis_check_required",
            "Confirm the cited response/revision text really worsens, removes, contradicts, or degrades the original concern.",
        )
    return (
        "tier_4_regressed_candidate",
        "candidate_keep_regressed",
        "Regression cues exist in response/revision context, but still require final standard-label confirmation.",
    )


def build_rows(
    *,
    dataset_name: str,
    adjudication_rows: list[dict[str, str]],
    review_queue_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    queue_by_id = {row["issue_id"]: row for row in review_queue_rows if row.get("issue_id")}
    rows: list[dict[str, str]] = []
    for row in adjudication_rows:
        if compact(row.get("assistant_label")).lower() != "regressed":
            continue
        queue_row = queue_by_id.get(row.get("issue_id", ""), {})
        tier, gate, action = risk_tier(row)
        context = response_revision_text(row)
        support = support_models(row)
        snapshot = model_labels(row)
        rows.append(
            {
                "verification_rank": "",
                "review_rank": queue_row.get("review_rank", ""),
                "dataset_name": dataset_name,
                "issue_id": row.get("issue_id", ""),
                "paper_title": row.get("paper_title", ""),
                "current_label": compact(row.get("assistant_label")).lower(),
                "assistant_confidence": row.get("assistant_confidence", ""),
                "evidence_source": row.get("evidence_source", ""),
                "support_count": str(len(support)),
                "support_models": ",".join(support),
                "risk_tier": tier,
                "standard_label_gate": gate,
                "response_revision_context": "present" if context else "missing",
                "response_revision_regression_cues": ",".join(cue_hits(context)),
                "model_snapshot": "; ".join(f"{name}={value}" for name, value in sorted(snapshot.items())),
                "recommended_action": action,
                "evidence_span": row.get("evidence_span", ""),
                "review_excerpt": clip(row.get("review_excerpt")),
                "aligned_response_excerpt": clip(row.get("aligned_response_excerpt")),
                "revision_summary": clip(row.get("revision_summary")),
            }
        )

    tier_order = {
        "tier_1_block_regressed": 0,
        "tier_2_old_concern_only_risk": 1,
        "tier_3_regression_candidate_needs_confirmation": 2,
        "tier_4_regressed_candidate": 3,
    }
    rows.sort(
        key=lambda item: (
            tier_order.get(item["risk_tier"], 99),
            int(item["support_count"]),
            int(item["review_rank"] or 999999),
            item["issue_id"],
        )
    )
    for rank, row in enumerate(rows, start=1):
        row["verification_rank"] = str(rank)
    return rows


def write_csv(path: str | Path, rows: list[dict[str, str]]) -> None:
    fields = [
        "verification_rank",
        "review_rank",
        "dataset_name",
        "issue_id",
        "paper_title",
        "current_label",
        "assistant_confidence",
        "evidence_source",
        "support_count",
        "support_models",
        "risk_tier",
        "standard_label_gate",
        "response_revision_context",
        "response_revision_regression_cues",
        "model_snapshot",
        "recommended_action",
        "evidence_span",
        "review_excerpt",
        "aligned_response_excerpt",
        "revision_summary",
    ]
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: str | Path, *, dataset_name: str, rows: list[dict[str, str]], top_n: int) -> None:
    tiers = Counter(row["risk_tier"] for row in rows)
    gates = Counter(row["standard_label_gate"] for row in rows)
    sources = Counter(row["evidence_source"] for row in rows)
    lines = [
        f"# {dataset_name} Regression Verification Packet",
        "",
        f"Rows: `{len(rows)}` regressed draft labels",
        "",
        "This packet verifies whether provisional `regressed` labels have enough response/revision evidence to survive standard-label review. It is a review aid, not a human-validation result.",
        "",
        "## Summary",
        "",
        "- Risk tiers: " + ", ".join(f"`{key}`={value}" for key, value in sorted(tiers.items())),
        "- Standard-label gates: " + ", ".join(f"`{key}`={value}" for key, value in sorted(gates.items())),
        "- Evidence sources: " + ", ".join(f"`{key}`={value}" for key, value in sorted(sources.items())),
        "",
        "## Highest Priority Verification Rows",
        "",
        "| rank | review rank | issue | tier | gate | evidence | support | context | action |",
        "| ---: | ---: | --- | --- | --- | --- | ---: | --- | --- |",
    ]
    for row in rows[:top_n]:
        lines.append(
            "| "
            + " | ".join(
                [
                    row["verification_rank"],
                    row["review_rank"] or "-",
                    f"`{row['issue_id']}`",
                    row["risk_tier"],
                    row["standard_label_gate"],
                    row["evidence_source"],
                    row["support_count"],
                    row["response_revision_context"],
                    row["recommended_action"],
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Promotion Rule",
            "",
            "- `tier_1_block_regressed` rows should not remain `regressed` unless missing response/revision context is recovered.",
            "- `tier_2` and `tier_3` rows require same-axis response/revision evidence before promotion.",
            "- This packet does not create standard validation labels; it narrows the review work before filling the blind sheet.",
        ]
    )
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    rows = build_rows(
        dataset_name=args.dataset_name,
        adjudication_rows=load_tsv(args.adjudication),
        review_queue_rows=load_csv(args.review_queue),
    )
    write_csv(args.output_csv, rows)
    write_markdown(args.output_md, dataset_name=args.dataset_name, rows=rows, top_n=args.top_n)
    print(f"Wrote {len(rows)} regression verification rows to {args.output_csv}")


if __name__ == "__main__":
    main()
