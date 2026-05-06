from __future__ import annotations

from typing import Any

from revtrack.openreview_tasks import normalize_text


FIXED_CUES = (
    "addressed my main concern",
    "addressed my concerns",
    "addresses my concerns",
    "address my concerns",
    "adequately addresses my concerns",
    "addressing my questions",
    "responses to my questions were satisfactory",
    "i am satisfied",
    "increased my score",
    "increase my score",
    "raise my score",
    "raise my rating",
    "updated my rating",
    "more certain now",
    "concerns are solved",
    "solved my concerns",
    "sufficient details",
    "i will keep my score",
    "maintaining my score",
    "keep my current scoring",
)

PARTIAL_CUES = (
    "partially addressed",
    "most of my concerns are solved",
    "minor issue",
    "not without flaws",
    "would appreciate seeing",
    "one more question",
    "additional clarification questions",
    "however",
)

UNRESOLVED_CUES = (
    "still have some doubts",
    "i still think",
    "not increase my score",
    "not convinced",
    "questionable",
    "remain concerned",
    "still necessary",
    "not addressed",
    "fails to",
    "inhibiting practicality",
)

REGRESSED_CUES = (
    "worse",
    "new issue",
    "regression",
    "decrease my score",
    "reduced my score",
)


def infer_silver_label_from_comment(comment_text: str) -> dict[str, Any] | None:
    text = normalize_text(comment_text).lower()
    if not text:
        return None

    has_fixed = any(cue in text for cue in FIXED_CUES)
    has_partial = any(cue in text for cue in PARTIAL_CUES)
    has_unresolved = any(cue in text for cue in UNRESOLVED_CUES)
    has_regressed = any(cue in text for cue in REGRESSED_CUES)
    has_mixed = any(token in text for token in (" however ", " but ", " still "))

    if has_regressed:
        return {"label": "regressed", "confidence": 0.9, "rule": "regressed_cue"}
    if "partially addressed" in text:
        return {"label": "partially_fixed", "confidence": 0.9, "rule": "explicit_partial"}
    if "most of my concerns are solved" in text:
        return {"label": "partially_fixed", "confidence": 0.82, "rule": "mostly_solved"}
    if ("keep my score" in text or "keep my rating" in text) and ("solid" in text or "address" in text):
        return {"label": "fixed", "confidence": 0.74, "rule": "keep_score_positive"}
    if has_fixed and not (has_partial or has_unresolved or has_mixed):
        return {"label": "fixed", "confidence": 0.86, "rule": "strong_positive"}
    if has_fixed and (has_partial or has_unresolved or has_mixed):
        return {"label": "partially_fixed", "confidence": 0.76, "rule": "positive_but_mixed"}
    if has_unresolved:
        return {"label": "unresolved", "confidence": 0.82, "rule": "negative_signal"}
    if "maintain my score" in text or "keep my score" in text:
        if "address" in text or "appreciate" in text:
            return {"label": "partially_fixed", "confidence": 0.68, "rule": "maintain_with_positive"}
    return None


def collect_followup_comments(submission: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    reviews = [reply for reply in submission.get("replies", []) if reply.get("type") == "official_review"]
    comments = [reply for reply in submission.get("replies", []) if reply.get("type") == "official_comment"]

    matched: dict[str, list[dict[str, Any]]] = {}
    for review in reviews:
        review_id = review.get("id", "")
        review_signatures = set(review.get("signatures", []))
        matched_comments = []
        for comment in comments:
            if review_signatures & set(comment.get("signatures", [])):
                matched_comments.append(comment)
        matched[review_id] = matched_comments
    return matched
