from __future__ import annotations

import csv
from pathlib import Path

from revtrack.schema import LABELS, Prediction

VALID_LABELS = set(LABELS)

STRONG_REGRESSED_CUES = (
    "performance is worse",
    "size of the coreset is comparable to that of the full data",
    "no particular need to apply the coreset method",
    "weaken",
    "worse than",
)

STRONG_FIXED_SILVER_CUES = (
    "adequately addresses my concerns",
    "addressed my main concern",
    "more certain now that this work should be accepted",
    "initial concerns addressed",
    "sufficient details on the experiments",
    "having seen the new draft had my initial concerns addressed",
    "raise my score accordingly",
)

STRONG_PARTIAL_SILVER_CUES = (
    "partially addressed",
    "most of my concerns are solved. however",
    "request the authors to reword the contributions and claims",
    "not increase my score",
    "not increased my score significantly",
    "still think it is necessary",
    "simple solution is to add one extra baseline",
)

RESPONSE_EVIDENCE_CUES = (
    "we added",
    "we included",
    "we conducted",
    "we present",
    "we provided",
    "we have updated",
    "we have revised",
    "we uploaded the revised manuscript",
    "table ",
    "figure ",
    "appendix",
    "ablation",
    "visualization",
    "cross-labeled",
    "new domains",
    "unseen scenarios",
    "communication rounds",
    "runtime",
    "severity level",
)

ARGUMENTATIVE_CUES = (
    "we argue",
    "we believe",
    "we cannot agree",
    "we hope",
    "we would like to clarify",
    "our contribution",
)

PARTIAL_CUES = (
    "limitation",
    "needs to be further studied",
)

REQUEST_BROAD_GENERALIZATION_CUES = (
    "different severity levels",
    "broader range of severity levels",
    "other domains",
    "commonsense reasoning",
    "symbolic reasoning",
    "single mathematical domain",
    "single domain",
    "larger scale",
    "broader array of experiments",
    "generality",
    "generalizability",
    "ood",
    "unseen",
)

RESPONSE_BROAD_GENERALIZATION_CUES = (
    "under unbiased reliability conditions",
    "severity level 3",
    "two new domains",
    "legal domain",
    "customer review domain",
    "unseen scenarios",
    "larger scale",
)

REQUEST_CLARITY_CUES = (
    "clarify",
    "unclear",
    "not clear",
    "hard to read",
    "presentation",
    "notation",
    "typo",
    "grammar",
    "figures",
    "examples",
    "follow",
)

REQUEST_NOVELTY_CUES = (
    "novelty",
    "novel ideas",
    "incremental",
    "similar to",
    "derived from previous work",
    "limited technical contribution",
    "contribution is limited",
)

RESPONSE_PARTIAL_UPGRADE_CUES = (
    "two new domains",
    "new domains",
    "rewritten introduction",
    "more clarity and focus",
    "theoretical support",
    "evaluation of factual knowledge",
)


def normalize_label(value: str | None) -> str:
    if not value:
        return ""
    value = str(value).strip().lower()
    return value if value in VALID_LABELS else ""


def normalize_text(*parts: str | None) -> str:
    return " ".join((part or "").strip().lower() for part in parts if part)


def contains_any(text: str, cues: tuple[str, ...]) -> bool:
    return any(cue in text for cue in cues)


def load_sheet_rows(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def calibrate_issue_label(row: dict[str, str], *, base_field: str = "mpnet_label") -> tuple[str, str]:
    silver_label = normalize_label(row.get("silver_label", ""))
    base_label = normalize_label(row.get(base_field, ""))
    review = normalize_text(row.get("review_excerpt", ""))
    response = normalize_text(
        row.get("top_response_excerpt", ""),
        row.get("aligned_response_excerpt", ""),
        row.get("revision_summary", ""),
    )
    silver_comment = normalize_text(row.get("silver_comment", ""))
    combined = normalize_text(response, silver_comment)

    if contains_any(silver_comment, STRONG_REGRESSED_CUES):
        return "regressed", "silver_comment_regressed"

    if contains_any(silver_comment, STRONG_FIXED_SILVER_CUES) and not contains_any(
        silver_comment,
        STRONG_PARTIAL_SILVER_CUES,
    ):
        return "fixed", "silver_comment_fixed"

    if contains_any(silver_comment, STRONG_PARTIAL_SILVER_CUES):
        return "partially_fixed", "silver_comment_partial"

    if silver_label:
        return silver_label, "silver_label_override"

    review_broad = contains_any(review, REQUEST_BROAD_GENERALIZATION_CUES)
    response_broad = contains_any(combined, RESPONSE_BROAD_GENERALIZATION_CUES)
    added_evidence = contains_any(combined, RESPONSE_EVIDENCE_CUES)
    argumentative_only = contains_any(combined, ARGUMENTATIVE_CUES) and not added_evidence
    request_clarity = contains_any(review, REQUEST_CLARITY_CUES)
    request_novelty = contains_any(review, REQUEST_NOVELTY_CUES)

    if base_label == "regressed":
        if added_evidence and not contains_any(combined, STRONG_REGRESSED_CUES):
            return "partially_fixed", "base_regressed_softened_by_new_evidence"
        return "regressed", "base_regressed_kept"

    if base_label == "fixed" and review_broad and response_broad:
        return "partially_fixed", "base_fixed_broad_request_only_partially_closed"

    if base_label == "unresolved":
        if review_broad and response_broad:
            return "partially_fixed", "base_unresolved_broad_request_partially_closed"
        if request_clarity and contains_any(combined, RESPONSE_PARTIAL_UPGRADE_CUES):
            return "partially_fixed", "base_unresolved_upgraded_by_new_scope_and_clarity"

    if review_broad:
        if not response_broad and added_evidence:
            return "unresolved", "local_patch_not_enough_for_broad_request"
        return "unresolved", "broad_request_without_new_evidence"

    if request_novelty:
        if argumentative_only:
            return "unresolved", "novelty_argument_without_evidence"
        if added_evidence and not request_clarity:
            return "partially_fixed", "novelty_reframed_with_some_new_evidence"

    if argumentative_only:
        return "unresolved", "argument_without_new_evidence"

    if base_label:
        return base_label, "base_label_kept"

    return "partially_fixed", "default_partial"


def sheet_row_to_prediction(row: dict[str, str], *, base_field: str = "mpnet_label") -> Prediction:
    label, rule = calibrate_issue_label(row, base_field=base_field)
    return Prediction(
        id=row["issue_id"],
        predicted_label=label,
        raw_output=rule,
        metadata={"backend": "issue_ledger", "base_field": base_field, "rule": rule},
    )
