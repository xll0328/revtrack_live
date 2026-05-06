from __future__ import annotations

import argparse
import csv
import re
from collections import Counter
from pathlib import Path
from typing import Any


MODEL_FIELDS = [
    "tfidf_label",
    "modernbert_label",
    "mpnet_label",
    "issue_ledger_label",
    "structured_label",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export a risk-ranked review queue for an active-frontier assistant adjudication draft."
    )
    parser.add_argument("--dataset-name", required=True)
    parser.add_argument("--adjudication", required=True)
    parser.add_argument("--output-csv", required=True)
    parser.add_argument("--output-md", required=True)
    parser.add_argument(
        "--validation-status",
        default="provisional_assistant_adjudication_not_human_validation",
    )
    parser.add_argument("--top-n", type=int, default=25)
    return parser.parse_args()


def compact(value: str | None) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def clip(value: str | None, max_chars: int = 240) -> str:
    text = compact(value)
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(" ", 1)[0] + "..."


def load_tsv(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def model_labels(row: dict[str, str]) -> dict[str, str]:
    return {
        field.removesuffix("_label"): compact(row.get(field)).lower()
        for field in MODEL_FIELDS
        if compact(row.get(field))
    }


def support_models(row: dict[str, str]) -> list[str]:
    label = compact(row.get("assistant_label")).lower()
    return [name for name, value in model_labels(row).items() if value == label]


def risk_flags(row: dict[str, str]) -> list[str]:
    flags: list[str] = []
    label = compact(row.get("assistant_label")).lower()
    evidence_source = compact(row.get("evidence_source")).lower()
    confidence = compact(row.get("assistant_confidence")).lower()
    support = support_models(row)
    distinct_predictions = {value for value in model_labels(row).values() if value}

    if label == "regressed":
        flags.append("regressed_label")
    if label == "regressed" and evidence_source == "review_excerpt":
        flags.append("regressed_with_review_excerpt_evidence")
    if len(support) <= 1:
        flags.append("weak_model_support")
    if confidence == "low":
        flags.append("low_confidence")
    if len(distinct_predictions) >= 3:
        flags.append("high_model_disagreement")
    if evidence_source == "review_excerpt":
        flags.append("evidence_from_original_review")
    if not compact(row.get("aligned_response_excerpt")) and not compact(row.get("revision_summary")):
        flags.append("missing_revision_context")
    return flags


def priority_score(flags: list[str]) -> int:
    weights = {
        "regressed_with_review_excerpt_evidence": 35,
        "weak_model_support": 30,
        "regressed_label": 25,
        "evidence_from_original_review": 20,
        "low_confidence": 12,
        "high_model_disagreement": 10,
        "missing_revision_context": 8,
    }
    return sum(weights.get(flag, 0) for flag in flags)


def review_action(row: dict[str, str], flags: list[str]) -> str:
    label = compact(row.get("assistant_label")).lower()
    if label == "regressed":
        if "regressed_with_review_excerpt_evidence" in flags:
            return (
                "Verify there is response/revision evidence of a same-axis negative change; "
                "if the text only preserves the old concern, relabel as unresolved or partially_fixed."
            )
        return (
            "Verify the alleged regression is caused by the response/revision, not just an unresolved original concern."
        )
    if label == "unresolved":
        return "Check whether aligned response or revision summary contains a concrete fix that should change the label."
    if label == "partially_fixed":
        return "Check whether evidence resolves only part of the original concern or actually supports fixed."
    return "Check whether the evidence directly resolves the original issue."


def build_review_rows(
    *,
    dataset_name: str,
    adjudication_rows: list[dict[str, str]],
    validation_status: str,
) -> list[dict[str, str]]:
    output_rows: list[dict[str, str]] = []
    for row in adjudication_rows:
        flags = risk_flags(row)
        support = support_models(row)
        model_snapshot = model_labels(row)
        output_rows.append(
            {
                "review_rank": "",
                "priority_score": str(priority_score(flags)),
                "dataset_name": dataset_name,
                "validation_status": validation_status,
                "issue_id": row.get("issue_id", ""),
                "paper_title": row.get("paper_title", ""),
                "assistant_label": compact(row.get("assistant_label")).lower(),
                "assistant_confidence": row.get("assistant_confidence", ""),
                "evidence_source": row.get("evidence_source", ""),
                "support_count": str(len(support)),
                "support_models": ",".join(support),
                "model_snapshot": "; ".join(f"{name}={value}" for name, value in sorted(model_snapshot.items())),
                "risk_flags": ";".join(flags),
                "review_action": review_action(row, flags),
                "evidence_span": row.get("evidence_span", ""),
                "review_excerpt": clip(row.get("review_excerpt")),
                "aligned_response_excerpt": clip(row.get("aligned_response_excerpt")),
                "revision_summary": clip(row.get("revision_summary")),
            }
        )
    output_rows.sort(
        key=lambda item: (
            -int(item["priority_score"]),
            item["assistant_label"] != "regressed",
            int(item["support_count"]),
            item["issue_id"],
        )
    )
    for rank, row in enumerate(output_rows, start=1):
        row["review_rank"] = str(rank)
    return output_rows


def write_csv(path: str | Path, rows: list[dict[str, str]]) -> None:
    fields = [
        "review_rank",
        "priority_score",
        "dataset_name",
        "validation_status",
        "issue_id",
        "paper_title",
        "assistant_label",
        "assistant_confidence",
        "evidence_source",
        "support_count",
        "support_models",
        "model_snapshot",
        "risk_flags",
        "review_action",
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
    labels = Counter(row["assistant_label"] for row in rows)
    sources = Counter(row["evidence_source"] for row in rows)
    flags = Counter(flag for row in rows for flag in row["risk_flags"].split(";") if flag)
    support = Counter(row["support_count"] for row in rows)
    lines = [
        f"# {dataset_name} Review Queue",
        "",
        f"Rows: `{len(rows)}`",
        "",
        "This queue is for reviewing the active-frontier assistant adjudication draft. It is not a standard human-validation result until the blind sheet is explicitly confirmed and filled.",
        "",
        "## Summary",
        "",
        "- Labels: " + ", ".join(f"`{key}`={value}" for key, value in sorted(labels.items())),
        "- Evidence sources: " + ", ".join(f"`{key}`={value}" for key, value in sorted(sources.items())),
        "- Support counts: " + ", ".join(f"`{key}`={value}" for key, value in sorted(support.items())),
        "- Top risk flags: " + ", ".join(f"`{key}`={value}" for key, value in flags.most_common(8)),
        "",
        "## Highest Priority Rows",
        "",
        "| rank | score | issue | label | evidence | support | flags | action |",
        "| ---: | ---: | --- | --- | --- | ---: | --- | --- |",
    ]
    for row in rows[:top_n]:
        lines.append(
            "| "
            + " | ".join(
                [
                    row["review_rank"],
                    row["priority_score"],
                    f"`{row['issue_id']}`",
                    row["assistant_label"],
                    row["evidence_source"],
                    row["support_count"],
                    row["risk_flags"].replace(";", ", "),
                    row["review_action"],
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Promotion Rule",
            "",
            "Promote only after every row has a confirmed label, confidence, evidence span, and note in the blind validation sheet. Keep this separate from independent IAA.",
        ]
    )
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    rows = build_review_rows(
        dataset_name=args.dataset_name,
        adjudication_rows=load_tsv(args.adjudication),
        validation_status=args.validation_status,
    )
    write_csv(args.output_csv, rows)
    write_markdown(args.output_md, dataset_name=args.dataset_name, rows=rows, top_n=args.top_n)
    print(f"Wrote {len(rows)} review queue rows to {args.output_csv}")


if __name__ == "__main__":
    main()
