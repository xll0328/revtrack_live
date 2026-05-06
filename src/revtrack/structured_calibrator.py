from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression

from revtrack.issue_ledger import (
    REQUEST_BROAD_GENERALIZATION_CUES,
    REQUEST_CLARITY_CUES,
    REQUEST_NOVELTY_CUES,
    RESPONSE_BROAD_GENERALIZATION_CUES,
    RESPONSE_EVIDENCE_CUES,
    RESPONSE_PARTIAL_UPGRADE_CUES,
    STRONG_FIXED_SILVER_CUES,
    STRONG_PARTIAL_SILVER_CUES,
    STRONG_REGRESSED_CUES,
    calibrate_issue_label,
    contains_any,
    load_sheet_rows,
    normalize_label,
    normalize_text,
)
from revtrack.schema import LABELS

VALID_LABELS = set(LABELS)

LABEL_FIELDS = (
    "tfidf_label",
    "modernbert_label",
    "mpnet_label",
)

REQUEST_EXPERIMENT_CUES = (
    "experiment",
    "benchmark",
    "ablation",
    "baseline",
    "compare",
    "comparison",
    "qualitative",
    "human evaluation",
    "error bars",
    "sample size",
    "runtime",
    "complexity",
    "dataset",
)

REQUEST_THEORY_CUES = (
    "theory",
    "theoretical",
    "proof",
    "equation",
    "derivation",
    "notation",
    "define",
    "definition",
)

REQUEST_CODE_CUES = (
    "code",
    "source code",
    "release",
    "implementation",
)

CUSTOM_BROAD_REVIEW_CUES = (
    "broader experiments",
    "more datasets",
    "more model evaluation",
    "larger evaluation",
)

RESPONSE_EXPERIMENT_CUES = (
    "we added",
    "we included",
    "we conducted",
    "we evaluated",
    "we expanded",
    "we supplemented",
    "new results",
    "new datasets",
    "ablation",
    "appendix",
    "table ",
    "figure ",
)

RESPONSE_THEORY_CUES = (
    "we define",
    "we clarified",
    "we derive",
    "we proved",
    "derivation",
    "appendix a",
    "appendix b",
    "equation",
    "notation",
)

RESPONSE_FUTURE_WORK_CUES = (
    "future work",
    "we will",
    "plan to",
    "camera-ready",
    "beyond the scope",
    "beyond scope",
    "time constraints",
    "unable to",
)

RESPONSE_CODE_PROMISE_CUES = (
    "working on releasing",
    "will provide a link",
    "next few days",
    "anonymized version of our code",
)


def count_cues(text: str, cues: tuple[str, ...]) -> int:
    return sum(1 for cue in cues if cue in text)


def word_count(text: str) -> int:
    return len(text.split())


def positive_number_count(text: str) -> int:
    return sum(char.isdigit() for char in text)


def _label_or_missing(row: dict[str, str], field: str) -> str:
    label = normalize_label(row.get(field, ""))
    return label or "missing"


def extract_row_features(row: dict[str, str]) -> dict[str, Any]:
    review = normalize_text(row.get("review_excerpt", ""))
    response = normalize_text(
        row.get("top_response_excerpt", ""),
        row.get("aligned_response_excerpt", ""),
        row.get("revision_summary", ""),
    )
    silver_comment = normalize_text(row.get("silver_comment", ""))
    combined = normalize_text(response, silver_comment)

    review_words = word_count(review)
    response_words = word_count(response)
    silver_words = word_count(silver_comment)

    review_broad = contains_any(review, REQUEST_BROAD_GENERALIZATION_CUES) or contains_any(review, CUSTOM_BROAD_REVIEW_CUES)
    review_clarity = contains_any(review, REQUEST_CLARITY_CUES)
    review_novelty = contains_any(review, REQUEST_NOVELTY_CUES)
    review_experiment = contains_any(review, REQUEST_EXPERIMENT_CUES)
    review_theory = contains_any(review, REQUEST_THEORY_CUES)
    review_code = contains_any(review, REQUEST_CODE_CUES)

    response_added = contains_any(combined, RESPONSE_EVIDENCE_CUES)
    response_broad = contains_any(combined, RESPONSE_BROAD_GENERALIZATION_CUES)
    response_partial_upgrade = contains_any(combined, RESPONSE_PARTIAL_UPGRADE_CUES)
    response_experiment = contains_any(combined, RESPONSE_EXPERIMENT_CUES)
    response_theory = contains_any(combined, RESPONSE_THEORY_CUES)
    response_future = contains_any(combined, RESPONSE_FUTURE_WORK_CUES)
    response_code_promise = contains_any(combined, RESPONSE_CODE_PROMISE_CUES)

    silver_label = normalize_label(row.get("silver_label", ""))
    silver_fixed = contains_any(silver_comment, STRONG_FIXED_SILVER_CUES)
    silver_partial = contains_any(silver_comment, STRONG_PARTIAL_SILVER_CUES)
    silver_regressed = contains_any(silver_comment, STRONG_REGRESSED_CUES)

    ledger_label, ledger_rule = calibrate_issue_label(row, base_field="mpnet_label")

    features: dict[str, Any] = {
        "review_words_bucket": min(review_words // 100, 20),
        "response_words_bucket": min(response_words // 120, 20),
        "silver_words_bucket": min(silver_words // 80, 20),
        "response_digit_count_bucket": min(positive_number_count(response) // 4, 20),
        "silver_digit_count_bucket": min(positive_number_count(silver_comment) // 4, 20),
        "review_broad": int(review_broad),
        "review_clarity": int(review_clarity),
        "review_novelty": int(review_novelty),
        "review_experiment": int(review_experiment),
        "review_theory": int(review_theory),
        "review_code": int(review_code),
        "response_added_evidence": int(response_added),
        "response_broad_evidence": int(response_broad),
        "response_partial_upgrade": int(response_partial_upgrade),
        "response_experiment": int(response_experiment),
        "response_theory": int(response_theory),
        "response_future": int(response_future),
        "response_code_promise": int(response_code_promise),
        "silver_has_label": int(bool(silver_label)),
        "silver_fixed_cue": int(silver_fixed),
        "silver_partial_cue": int(silver_partial),
        "silver_regressed_cue": int(silver_regressed),
        "review_request_cue_count": count_cues(review, REQUEST_EXPERIMENT_CUES + REQUEST_THEORY_CUES),
        "response_evidence_cue_count": count_cues(combined, RESPONSE_EVIDENCE_CUES + RESPONSE_EXPERIMENT_CUES),
        "response_future_cue_count": count_cues(combined, RESPONSE_FUTURE_WORK_CUES),
        "response_argumentative_only": int(
            any(cue in combined for cue in ("we argue", "we believe", "our contribution"))
            and not response_added
        ),
        "request_experiment_answered": int(review_experiment and response_experiment),
        "request_theory_answered": int(review_theory and response_theory),
        "request_code_answered": int(review_code and response_code_promise),
        "broad_request_partially_closed": int(review_broad and response_broad),
        "future_work_without_evidence": int(response_future and not response_added),
        "ledger_rule": ledger_rule,
        "ledger_label": ledger_label,
        "silver_label": silver_label or "missing",
    }

    labels = {_label_or_missing(row, field) for field in LABEL_FIELDS}
    features["base_unique_labels"] = len(labels)
    features["base_any_unresolved"] = int(any(_label_or_missing(row, field) == "unresolved" for field in LABEL_FIELDS))
    features["base_any_regressed"] = int(any(_label_or_missing(row, field) == "regressed" for field in LABEL_FIELDS))

    for field in LABEL_FIELDS:
        features[field] = _label_or_missing(row, field)

    for first, second in (("tfidf_label", "modernbert_label"), ("tfidf_label", "mpnet_label"), ("modernbert_label", "mpnet_label")):
        features[f"agree:{first}:{second}"] = int(_label_or_missing(row, first) == _label_or_missing(row, second))

    return features


def prepare_labeled_rows(rows: list[dict[str, str]]) -> tuple[list[str], list[dict[str, Any]]]:
    labels: list[str] = []
    features: list[dict[str, Any]] = []
    for row in rows:
        gold = normalize_label(row.get("gold_label", ""))
        if gold not in VALID_LABELS:
            continue
        labels.append(gold)
        features.append(extract_row_features(row))
    return labels, features


def hard_override_label(row: dict[str, str]) -> tuple[str, str] | None:
    silver_label = normalize_label(row.get("silver_label", ""))
    silver_comment = normalize_text(row.get("silver_comment", ""))

    if contains_any(silver_comment, STRONG_REGRESSED_CUES):
        return "regressed", "hard_override_regressed_silver_comment"

    if contains_any(silver_comment, STRONG_FIXED_SILVER_CUES) and not contains_any(
        silver_comment,
        STRONG_PARTIAL_SILVER_CUES,
    ):
        return "fixed", "hard_override_fixed_silver_comment"

    if contains_any(silver_comment, STRONG_PARTIAL_SILVER_CUES):
        return "partially_fixed", "hard_override_partial_silver_comment"

    if silver_label:
        return silver_label, "hard_override_silver_label"

    return None


def make_classifier() -> LogisticRegression:
    return LogisticRegression(
        class_weight="balanced",
        max_iter=5000,
        solver="liblinear",
    )


def load_sheet_lookup(path: str | Path) -> dict[str, dict[str, str]]:
    return {row["issue_id"]: row for row in load_sheet_rows(path)}


def raw_output_from_model(model: LogisticRegression, vectorizer: DictVectorizer, feature_row: dict[str, Any]) -> str:
    matrix = vectorizer.transform([feature_row])
    scores = model.decision_function(matrix)
    if hasattr(scores, "tolist"):
        score_payload = scores.tolist()
    else:
        score_payload = list(scores)
    return json.dumps(
        {
            "label": str(model.predict(matrix)[0]),
            "scores": score_payload,
            "classes": list(model.classes_),
        },
        ensure_ascii=False,
    )
