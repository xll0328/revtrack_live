from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

LABELS = ("fixed", "partially_fixed", "unresolved", "regressed")


@dataclass
class IssueExample:
    id: str
    source: str
    venue: str
    paper_title: str
    review_text: str
    author_response: str
    revision_summary: str
    gold_label: str
    abstract: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "IssueExample":
        return cls(
            id=data["id"],
            source=data.get("source", ""),
            venue=data.get("venue", ""),
            paper_title=data.get("paper_title", ""),
            review_text=data.get("review_text", ""),
            author_response=data.get("author_response", ""),
            revision_summary=data.get("revision_summary", ""),
            gold_label=data.get("gold_label", ""),
            abstract=data.get("abstract", ""),
            metadata=data.get("metadata", {}),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "source": self.source,
            "venue": self.venue,
            "paper_title": self.paper_title,
            "abstract": self.abstract,
            "review_text": self.review_text,
            "author_response": self.author_response,
            "revision_summary": self.revision_summary,
            "gold_label": self.gold_label,
            "metadata": self.metadata,
        }


@dataclass
class Prediction:
    id: str
    predicted_label: str
    raw_output: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Prediction":
        return cls(
            id=data["id"],
            predicted_label=data["predicted_label"],
            raw_output=data.get("raw_output", ""),
            metadata=data.get("metadata", {}),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "predicted_label": self.predicted_label,
            "raw_output": self.raw_output,
            "metadata": self.metadata,
        }
