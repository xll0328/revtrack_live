from __future__ import annotations

import json
from pathlib import Path

from revtrack.schema import IssueExample, Prediction


def load_examples(path: str | Path) -> list[IssueExample]:
    items: list[IssueExample] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            items.append(IssueExample.from_dict(json.loads(line)))
    return items


def save_examples(path: str | Path, examples: list[IssueExample]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        for example in examples:
            handle.write(json.dumps(example.to_dict(), ensure_ascii=False) + "\n")


def load_predictions(path: str | Path) -> list[Prediction]:
    items: list[Prediction] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            items.append(Prediction.from_dict(json.loads(line)))
    return items


def save_predictions(path: str | Path, predictions: list[Prediction]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        for prediction in predictions:
            handle.write(json.dumps(prediction.to_dict(), ensure_ascii=False) + "\n")
