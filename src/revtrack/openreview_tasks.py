from __future__ import annotations

import re
from collections.abc import Iterable
from typing import Any

from revtrack.openreview_api import detect_reply_type


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "we",
    "with",
    "you",
}

REVISION_HINTS = (
    "revised version",
    "revision",
    "new pdf",
    "updated manuscript",
    "uploaded the revised",
    "in the new pdf",
    "in the revised manuscript",
    "we added",
    "we include",
    "section",
    "table",
    "appendix",
)


def normalize_text(text: str) -> str:
    return " ".join(text.split())


def tokenize(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]+", text.lower())
        if token not in STOPWORDS and len(token) > 1
    }


def overlap_score(query: str, candidate: str) -> float:
    query_tokens = tokenize(query)
    candidate_tokens = tokenize(candidate)
    if not query_tokens or not candidate_tokens:
        return 0.0
    shared = len(query_tokens & candidate_tokens)
    containment = shared / len(query_tokens)
    jaccard = shared / len(query_tokens | candidate_tokens)
    return 0.7 * containment + 0.3 * jaccard


def iter_text_fields(content: dict[str, Any]) -> Iterable[tuple[str, str]]:
    for key, value in content.items():
        if isinstance(value, str):
            text = normalize_text(value)
            if text:
                yield key, text


def build_review_concern(review: dict[str, Any]) -> dict[str, Any]:
    content = review.get("content", {})
    preferred_fields = []
    for key in ("weaknesses", "questions", "summary", "limitations", "main_review", "review"):
        value = content.get(key)
        if isinstance(value, str) and normalize_text(value):
            preferred_fields.append((key, normalize_text(value)))

    if not preferred_fields:
        preferred_fields = list(iter_text_fields(content))

    preferred_fields = preferred_fields[:3]
    primary = preferred_fields[0][1] if preferred_fields else ""
    combined = "\n\n".join(f"[{key}] {text}" for key, text in preferred_fields)
    return {
        "primary": primary,
        "combined": combined,
        "fields": [key for key, _ in preferred_fields],
    }


def reply_type(reply: dict[str, Any]) -> str:
    detected = detect_reply_type(reply)
    if detected != "other":
        return detected
    return str(reply.get("type", "other"))


def response_text(response: dict[str, Any]) -> str:
    content = response.get("content", {})
    for key in ("comment", "rebuttal", "response", "text"):
        text = normalize_text(str(content.get(key, "")))
        if text:
            return text
    return ""


def build_revision_summary(author_responses: list[dict[str, Any]], top_k: int = 3) -> str:
    scored: list[tuple[float, str]] = []
    for response in author_responses:
        text = response_text(response)
        if not text:
            continue
        lowered = text.lower()
        hint_hits = sum(hint in lowered for hint in REVISION_HINTS)
        if hint_hits == 0 and len(text) < 80:
            continue
        score = hint_hits + min(len(text), 1200) / 1200.0
        scored.append((score, text))

    deduped: list[str] = []
    seen = set()
    for _, text in sorted(scored, reverse=True):
        key = text[:180]
        if key in seen:
            continue
        seen.add(key)
        deduped.append(text)
        if len(deduped) >= top_k:
            break
    return "\n\n".join(deduped)


def select_top_responses(
    concern_text: str,
    author_responses: list[dict[str, Any]],
    top_k: int = 3,
) -> list[dict[str, Any]]:
    ranked: list[dict[str, Any]] = []
    for response in author_responses:
        text = response_text(response)
        if not text:
            continue
        ranked.append(
            {
                "response_id": response.get("id", ""),
                "score": overlap_score(concern_text, text),
                "text": text,
                "signatures": response.get("signatures", []),
            }
        )

    ranked.sort(key=lambda item: (item["score"], len(item["text"])), reverse=True)
    return ranked[:top_k]


def build_issue_candidates(submission: dict[str, Any], top_k_responses: int = 3) -> list[dict[str, Any]]:
    content = submission.get("content", {})
    replies = submission.get("replies", [])
    official_reviews = [reply for reply in replies if reply_type(reply) == "official_review"]
    author_responses = [reply for reply in replies if reply_type(reply) == "author_response"]
    revision_summary = build_revision_summary(author_responses)

    candidates: list[dict[str, Any]] = []
    for index, review in enumerate(official_reviews, start=1):
        concern = build_review_concern(review)
        if not concern["combined"]:
            continue
        responses = select_top_responses(concern["combined"], author_responses, top_k=top_k_responses)
        aligned_response_excerpt = "\n\n".join(item["text"] for item in responses)
        review_content = review.get("content", {})
        candidate = {
            "issue_id": f"{submission.get('id', '')}__r{index:02d}",
            "source": "openreview",
            "venue": content.get("venueid", "") or submission.get("venueid", ""),
            "submission_id": submission.get("id", ""),
            "forum": submission.get("forum", ""),
            "paper_title": content.get("title", ""),
            "abstract": content.get("abstract", ""),
            "submission_version": submission.get("version", 1),
            "review_id": review.get("id", ""),
            "review_rating": review_content.get("rating", ""),
            "review_confidence": review_content.get("confidence", ""),
            "review_fields": concern["fields"],
            "review_excerpt": concern["combined"],
            "concern_text": concern["primary"],
            "aligned_response_excerpt": aligned_response_excerpt,
            "revision_summary": revision_summary,
            "response_candidates": responses,
        }
        candidates.append(candidate)
    return candidates
