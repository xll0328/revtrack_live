from __future__ import annotations

from revtrack.schema import IssueExample


def _clip_text(text: str, max_chars: int) -> str:
    text = " ".join(text.split())
    if len(text) <= max_chars:
        return text
    head = max_chars // 2
    tail = max_chars - head - len(" ... ")
    return f"{text[:head]} ... {text[-tail:]}"


def build_prompt(example: IssueExample) -> str:
    title = _clip_text(example.paper_title, 200)
    abstract = _clip_text(example.abstract, 700)
    review_text = _clip_text(example.review_text, 1800)
    author_response = _clip_text(example.author_response, 2200)
    revision_summary = _clip_text(example.revision_summary, 1600)
    return f"""You are a strict research-review assistant.

Task:
Decide whether the original review concern was fixed after revision.

Allowed labels:
- fixed
- partially_fixed
- unresolved
- regressed

Decision rules:
- fixed: the concern is directly addressed with concrete revision evidence
- partially_fixed: some progress exists but the concern is not fully resolved
- unresolved: the response evades, defers, or fails to address the concern
- regressed: the revision introduces a new problem or weakens the paper on this issue

Paper title:
{title}

Abstract:
{abstract}

Review concern:
{review_text}

Author response:
{author_response}

Revision summary:
{revision_summary}

Return JSON with keys:
- label
- rationale

Example:
{{"label": "fixed", "rationale": "..."}}"""


def build_chat_messages(example: IssueExample) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": "You are a strict research-review assistant. Return concise JSON only.",
        },
        {
            "role": "user",
            "content": build_prompt(example),
        },
    ]
