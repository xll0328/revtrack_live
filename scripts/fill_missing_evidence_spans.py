from __future__ import annotations

import argparse
import csv
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create an assistant evidence-filled copy of a labeled TSV sheet without overwriting the source sheet."
    )
    parser.add_argument("--sheet", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--max-followup-chars", type=int, default=260)
    return parser.parse_args()


def clip(text: str, max_chars: int) -> str:
    text = " ".join(str(text or "").split())
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3].rstrip() + "..."


def is_model_snapshot(text: str) -> bool:
    text = " ".join(str(text or "").split())
    if not text:
        return False
    return "=" in text and len(text) < 140


def synthesize_evidence(row: dict[str, str], *, max_followup_chars: int = 260) -> str:
    notes = " ".join(row.get("notes", "").split())
    suggestion_note = " ".join(row.get("suggestion_note", "").split())
    suggestion_source = row.get("suggestion_source", "").strip()

    if suggestion_source == "silver_followup_comment" and suggestion_note:
        return f"Assistant evidence from reviewer follow-up: {clip(suggestion_note, max_followup_chars)}"
    if notes:
        return f"Assistant evidence from adjudication note: {notes}"
    if suggestion_note and not is_model_snapshot(suggestion_note):
        return f"Assistant evidence from suggestion note: {clip(suggestion_note, max_followup_chars)}"
    return "Assistant evidence pending: original row had no evidence_span or usable note."


def fill_rows(rows: list[dict[str, str]], *, max_followup_chars: int = 260) -> tuple[list[dict[str, str]], int]:
    filled = 0
    output_rows: list[dict[str, str]] = []
    for row in rows:
        row = dict(row)
        if not row.get("evidence_span", "").strip():
            row["evidence_span"] = synthesize_evidence(row, max_followup_chars=max_followup_chars)
            filled += 1
        output_rows.append(row)
    return output_rows, filled


def load_tsv(path: str | Path) -> tuple[list[str], list[dict[str, str]]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return list(reader.fieldnames or []), list(reader)


def write_tsv(path: str | Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = parse_args()
    fieldnames, rows = load_tsv(args.sheet)
    filled_rows, filled_count = fill_rows(rows, max_followup_chars=args.max_followup_chars)
    write_tsv(args.output, filled_rows, fieldnames)
    print(f"Wrote {len(filled_rows)} rows to {args.output}; filled {filled_count} missing evidence spans")


if __name__ == "__main__":
    main()
