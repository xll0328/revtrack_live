from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


VALID_LABELS = {"fixed", "partially_fixed", "unresolved", "regressed"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit labeled TSV sheets for label/evidence/notes completeness.")
    parser.add_argument("--sheet", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md")
    parser.add_argument("--min-evidence-chars", type=int, default=25)
    parser.add_argument("--min-notes-chars", type=int, default=20)
    return parser.parse_args()


def load_tsv(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def normalize_label(value: str | None) -> str:
    return (value or "").strip().lower()


def row_label(row: dict[str, str]) -> str:
    return normalize_label(row.get("gold_label") or row.get("human_label") or row.get("assistant_label"))


def issue_id(row: dict[str, str]) -> str:
    return row.get("issue_id", "").strip()


def audit_sheet(
    rows: list[dict[str, str]],
    *,
    min_evidence_chars: int = 25,
    min_notes_chars: int = 20,
) -> dict[str, Any]:
    ids = [issue_id(row) for row in rows]
    duplicate_ids = sorted(item for item, count in Counter(ids).items() if item and count > 1)
    missing_ids = sum(1 for item in ids if not item)
    label_counts = Counter(row_label(row) for row in rows if row_label(row) in VALID_LABELS)
    missing_labels = [issue_id(row) for row in rows if not row_label(row)]
    invalid_labels = [
        {"issue_id": issue_id(row), "label": row_label(row)}
        for row in rows
        if row_label(row) and row_label(row) not in VALID_LABELS
    ]

    evidence_issues: list[dict[str, str]] = []
    for row in rows:
        evidence = row.get("evidence_span", "").strip()
        notes = row.get("notes", "").strip()
        problems: list[str] = []
        if not evidence:
            problems.append("missing_evidence")
        elif len(evidence) < min_evidence_chars:
            problems.append("short_evidence")
        if not notes:
            problems.append("missing_notes")
        elif len(notes) < min_notes_chars:
            problems.append("short_notes")
        if problems:
            evidence_issues.append(
                {
                    "issue_id": issue_id(row),
                    "paper_title": row.get("paper_title", ""),
                    "label": row_label(row),
                    "problems": ";".join(problems),
                    "evidence_chars": str(len(evidence)),
                    "notes_chars": str(len(notes)),
                    "suggestion_source": row.get("suggestion_source", ""),
                    "suggestion_note": row.get("suggestion_note", ""),
                }
            )

    structural_errors = []
    if missing_ids:
        structural_errors.append(f"{missing_ids} rows missing issue_id")
    if duplicate_ids:
        structural_errors.append(f"duplicate issue_ids: {duplicate_ids}")
    if missing_labels:
        structural_errors.append(f"{len(missing_labels)} rows missing labels")
    if invalid_labels:
        structural_errors.append(f"invalid labels: {invalid_labels}")

    problem_counts = Counter(
        problem
        for item in evidence_issues
        for problem in item["problems"].split(";")
        if problem
    )
    return {
        "ok": not structural_errors and not evidence_issues,
        "structural_ok": not structural_errors,
        "evidence_ok": not evidence_issues,
        "rows": len(rows),
        "unique_issue_ids": len(set(item for item in ids if item)),
        "label_counts": dict(sorted(label_counts.items())),
        "structural_errors": structural_errors,
        "problem_counts": dict(sorted(problem_counts.items())),
        "evidence_issue_count": len(evidence_issues),
        "evidence_issues": evidence_issues,
    }


def write_markdown(path: str | Path, report: dict[str, Any], sheet: str | Path) -> None:
    lines = [
        "# Label Evidence Audit",
        "",
        f"Sheet: `{sheet}`",
        "",
        f"Overall ok: `{report['ok']}`",
        f"Structural ok: `{report['structural_ok']}`",
        f"Evidence ok: `{report['evidence_ok']}`",
        f"Rows: `{report['rows']}`",
        f"Evidence issue count: `{report['evidence_issue_count']}`",
        "",
        "## Label Counts",
        "",
    ]
    for label, count in report["label_counts"].items():
        lines.append(f"- `{label}`: `{count}`")
    lines.extend(["", "## Problem Counts", ""])
    if report["problem_counts"]:
        for problem, count in report["problem_counts"].items():
            lines.append(f"- `{problem}`: `{count}`")
    else:
        lines.append("- none")
    lines.extend(["", "## Evidence Queue", ""])
    if report["evidence_issues"]:
        for item in report["evidence_issues"][:80]:
            lines.append(
                f"- `{item['issue_id']}` `{item['label']}` `{item['problems']}` "
                f"evidence_chars={item['evidence_chars']} notes_chars={item['notes_chars']} "
                f"title={item['paper_title']}"
            )
    else:
        lines.append("- none")
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    report = audit_sheet(
        load_tsv(args.sheet),
        min_evidence_chars=args.min_evidence_chars,
        min_notes_chars=args.min_notes_chars,
    )
    output_path = Path(args.output_json)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.output_md:
        write_markdown(args.output_md, report, args.sheet)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
