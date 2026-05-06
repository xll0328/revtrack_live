from __future__ import annotations

import argparse
import csv
import json
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
VALID_LABELS = {"fixed", "partially_fixed", "unresolved", "regressed"}
FIX_CUES = {
    "we added",
    "we have added",
    "we add",
    "we include",
    "we included",
    "we will include",
    "we implemented",
    "we ran",
    "we report",
    "we provide",
    "we clarify",
    "we clarified",
    "additional experiment",
    "additional experiments",
    "new experiment",
    "new experiments",
    "new baseline",
    "new baselines",
    "new table",
    "table",
    "figure",
    "appendix",
}
OPEN_CUES = {
    "beyond scope",
    "future work",
    "not central",
    "not include",
    "not included",
    "do not",
    "did not",
    "cannot",
    "unable",
    "limitation",
    "limitations",
    "leave",
}
STRICT_REGRESSION_CUES = {
    "revision introduced",
    "introduced an error",
    "introduced a mistake",
    "worse than before",
    "decreased performance",
    "performance decreased",
    "degraded performance",
    "removed the",
    "contradicts",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Resolve an active-frontier assistant adjudication draft into conservative label candidates."
    )
    parser.add_argument(
        "--dataset-name",
        default="Active frontier",
        help="Dataset label used in report titles and boundaries.",
    )
    parser.add_argument("--adjudication", required=True)
    parser.add_argument("--output-tsv", required=True)
    parser.add_argument("--candidate-blind", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--report-md", required=True)
    return parser.parse_args()


def compact(value: str | None) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def clip(value: str | None, max_chars: int = 420) -> str:
    text = compact(value)
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(" ", 1)[0] + "..."


def load_tsv(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def model_counts(row: dict[str, str]) -> Counter[str]:
    return Counter(compact(row.get(field)).lower() for field in MODEL_FIELDS if compact(row.get(field)))


def model_support(row: dict[str, str], label: str) -> int:
    return sum(1 for field in MODEL_FIELDS if compact(row.get(field)).lower() == label)


def context_text(row: dict[str, str]) -> str:
    return compact(" ".join([row.get("aligned_response_excerpt", ""), row.get("revision_summary", "")]))


def cue_hits(text: str, cues: set[str]) -> list[str]:
    lower = text.lower()
    return sorted(cue for cue in cues if cue in lower)


def resolved_confidence(label: str, support: int, fix_hits: list[str], open_hits: list[str]) -> str:
    if support >= 3 and fix_hits and not open_hits:
        return "4"
    if support >= 2 or fix_hits:
        return "3"
    if label == "unresolved":
        return "3"
    return "2"


def resolve_row(row: dict[str, str]) -> dict[str, str]:
    draft_label = compact(row.get("assistant_label")).lower()
    counts = model_counts(row)
    support = model_support(row, draft_label)
    text = context_text(row)
    fix_hits = cue_hits(text, FIX_CUES)
    open_hits = cue_hits(text, OPEN_CUES)
    strict_regression_hits = cue_hits(text, STRICT_REGRESSION_CUES)

    resolved = draft_label
    action = "keep"
    reason = "Draft label has sufficient support for review-stage use."
    review_required = "true"

    if draft_label == "regressed":
        regressed_support = counts.get("regressed", 0)
        if regressed_support >= 2 and strict_regression_hits:
            resolved = "regressed"
            action = "keep_regressed_candidate"
            reason = (
                "At least two models support regressed and strict response/revision regression cues are present; "
                "requires final same-axis confirmation."
            )
        else:
            resolved = "partially_fixed" if fix_hits else "unresolved"
            action = "downgrade_regressed"
            reason = (
                "Draft regressed lacks strict same-axis negative-change evidence; use conservative non-regression label."
            )
    elif draft_label == "unresolved" and support <= 1:
        fixed_or_partial_support = counts.get("fixed", 0) + counts.get("partially_fixed", 0)
        if fix_hits and fixed_or_partial_support >= 3:
            if counts.get("fixed", 0) >= 3 and not open_hits:
                resolved = "fixed"
                action = "upgrade_weak_unresolved_to_fixed"
                reason = "Weak unresolved draft conflicts with multiple fixed predictions and concrete fix cues."
            else:
                resolved = "partially_fixed"
                action = "upgrade_weak_unresolved_to_partial"
                reason = (
                    "Weak unresolved draft conflicts with fixed/partial model support and concrete response/revision evidence; "
                    "open-scope cues keep this conservative."
                )
        else:
            resolved = "unresolved"
            action = "keep_weak_unresolved"
            reason = "Weak unresolved draft has insufficient concrete fix evidence for promotion."

    if resolved not in VALID_LABELS:
        resolved = "unresolved"
        action = "fallback_unresolved"
        reason = "Invalid resolved label fallback."

    evidence = compact(row.get("evidence_span")) or clip(text)
    return {
        **row,
        "draft_label": draft_label,
        "resolved_label": resolved,
        "resolved_confidence": resolved_confidence(
            resolved,
            model_support(row, resolved),
            fix_hits,
            open_hits,
        ),
        "resolved_evidence_span": evidence,
        "resolution_action": action,
        "resolution_reason": reason,
        "model_support_for_draft": str(support),
        "model_support_for_resolved": str(model_support(row, resolved)),
        "model_label_counts": json.dumps(dict(sorted(counts.items())), sort_keys=True),
        "fix_cues": ";".join(fix_hits),
        "open_cues": ";".join(open_hits),
        "strict_regression_cues": ";".join(strict_regression_hits),
        "review_required": review_required,
        "resolution_provenance": "assistant_resolved_candidate_not_human_validation",
    }


def resolve_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [resolve_row(row) for row in rows]


def write_tsv(path: str | Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t")
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fields} for row in rows)


def write_resolved_tsv(path: str | Path, rows: list[dict[str, str]]) -> None:
    fields = [
        "issue_id",
        "paper_title",
        "draft_label",
        "resolved_label",
        "resolved_confidence",
        "resolution_action",
        "resolution_reason",
        "model_support_for_draft",
        "model_support_for_resolved",
        "model_label_counts",
        "fix_cues",
        "open_cues",
        "strict_regression_cues",
        "review_required",
        "resolution_provenance",
        "resolved_evidence_span",
        "review_excerpt",
        "aligned_response_excerpt",
        "revision_summary",
        "tfidf_label",
        "modernbert_label",
        "mpnet_label",
        "issue_ledger_label",
        "structured_label",
    ]
    write_tsv(path, rows, fields)


def write_candidate_blind(path: str | Path, rows: list[dict[str, str]]) -> None:
    fields = [
        "issue_id",
        "paper_title",
        "review_rating",
        "review_confidence",
        "review_excerpt",
        "top_response_excerpt",
        "aligned_response_excerpt",
        "revision_summary",
        "human_label",
        "human_confidence",
        "evidence_span",
        "notes",
    ]
    candidate_rows: list[dict[str, str]] = []
    for row in rows:
        note = (
            "Assistant-resolved standard-label candidate; not human validation. "
            f"draft={row['draft_label']}; action={row['resolution_action']}; "
            f"reason={row['resolution_reason']}"
        )
        candidate_rows.append(
            {
                "issue_id": row.get("issue_id", ""),
                "paper_title": row.get("paper_title", ""),
                "review_rating": row.get("review_rating", ""),
                "review_confidence": row.get("review_confidence", ""),
                "review_excerpt": row.get("review_excerpt", ""),
                "top_response_excerpt": row.get("top_response_excerpt", ""),
                "aligned_response_excerpt": row.get("aligned_response_excerpt", ""),
                "revision_summary": row.get("revision_summary", ""),
                "human_label": row["resolved_label"],
                "human_confidence": row["resolved_confidence"],
                "evidence_span": row["resolved_evidence_span"],
                "notes": note,
            }
        )
    write_tsv(path, candidate_rows, fields)


def write_manifest(path: str | Path, rows: list[dict[str, str]], *, output_tsv: str | Path, candidate_blind: str | Path) -> None:
    payload: dict[str, Any] = {
        "status": "assistant_resolved_candidate",
        "human_validation_status": "not_human_validated",
        "rows": len(rows),
        "draft_distribution": dict(sorted(Counter(row["draft_label"] for row in rows).items())),
        "resolved_distribution": dict(sorted(Counter(row["resolved_label"] for row in rows).items())),
        "action_distribution": dict(sorted(Counter(row["resolution_action"] for row in rows).items())),
        "review_required_rows": sum(row["review_required"] == "true" for row in rows),
        "output_tsv": str(output_tsv),
        "candidate_blind": str(candidate_blind),
        "claim_boundary": (
            "Use as an assistant-resolved candidate sheet only; do not report as standard human validation, "
            "IAA, or benchmark transfer performance until user-confirmed labels are written to the canonical blind sheet."
        ),
    }
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_report_md(
    path: str | Path,
    rows: list[dict[str, str]],
    *,
    dataset_name: str,
    output_tsv: str | Path,
    candidate_blind: str | Path,
) -> None:
    lines = [
        f"# {dataset_name} Resolved Label Candidate",
        "",
        "Status: `assistant_resolved_candidate_not_human_validation`",
        "",
        "This resolves the assistant draft into conservative label candidates. It does not create standard human-validation labels.",
        "",
        "## Summary",
        "",
        "- Rows: `" + str(len(rows)) + "`",
        "- Draft labels: " + ", ".join(f"`{k}`={v}" for k, v in sorted(Counter(row["draft_label"] for row in rows).items())),
        "- Resolved labels: "
        + ", ".join(f"`{k}`={v}" for k, v in sorted(Counter(row["resolved_label"] for row in rows).items())),
        "- Actions: "
        + ", ".join(f"`{k}`={v}" for k, v in sorted(Counter(row["resolution_action"] for row in rows).items())),
        "",
        "## Outputs",
        "",
        f"- Resolved TSV: `{output_tsv}`",
        f"- Candidate blind sheet: `{candidate_blind}`",
        "",
        "## Highest-Impact Changes",
        "",
        "| issue | draft | resolved | action | reason |",
        "| --- | --- | --- | --- | --- |",
    ]
    changed = [row for row in rows if row["draft_label"] != row["resolved_label"]]
    if not changed:
        lines.append("| _none_ |  |  |  |  |")
    for row in changed:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{row['issue_id']}`",
                    row["draft_label"],
                    row["resolved_label"],
                    row["resolution_action"],
                    row["resolution_reason"],
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            f"- The canonical {dataset_name} blind validation sheet remains untouched.",
            "- Promote only after user confirmation.",
            "- Do not report these labels as independent human validation or IAA.",
        ]
    )
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    rows = resolve_rows(load_tsv(args.adjudication))
    write_resolved_tsv(args.output_tsv, rows)
    write_candidate_blind(args.candidate_blind, rows)
    write_manifest(args.manifest, rows, output_tsv=args.output_tsv, candidate_blind=args.candidate_blind)
    write_report_md(
        args.report_md,
        rows,
        dataset_name=args.dataset_name,
        output_tsv=args.output_tsv,
        candidate_blind=args.candidate_blind,
    )
    print(f"Wrote {len(rows)} resolved candidate rows to {args.output_tsv}")


if __name__ == "__main__":
    main()
