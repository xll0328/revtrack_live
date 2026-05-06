from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


CITE_RE = re.compile(r"\\cite[a-zA-Z]*\s*(?:\[[^\]]*\]\s*)*\{([^{}]+)\}")
BIBLIOGRAPHY_RE = re.compile(r"\\bibliography\s*\{([^{}]+)\}")
BIB_ENTRY_RE = re.compile(r"@(?P<kind>[A-Za-z]+)\s*\{\s*(?P<key>[^,\s]+)\s*,", re.MULTILINE)
FIELD_RE = re.compile(r"^\s*([A-Za-z][A-Za-z0-9_-]*)\s*=", re.MULTILINE)
LOG_PROBLEM_RE = re.compile(
    r"(undefined citations|Citation .* undefined|Reference .* undefined|"
    r"Package natbib Warning|Fatal error|Emergency stop|Rerun to get cross-references right)",
    re.IGNORECASE,
)


REQUIRED_FIELDS = {
    "article": {"author", "title", "year", "journal"},
    "inproceedings": {"author", "title", "year", "booktitle"},
    "misc": {"author", "title", "year"},
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit paper citations against BibTeX and LaTeX build logs.")
    parser.add_argument("--paper-dir", default=str(ROOT / "paper"))
    parser.add_argument("--bib", default=str(ROOT / "paper/refs.bib"))
    parser.add_argument("--log", default=str(ROOT / "paper/main.log"))
    parser.add_argument("--output-json", default=str(ROOT / "outputs/day1/paper_assets/paper_citation_audit.json"))
    parser.add_argument("--output-md", default=str(ROOT / "outputs/day1/paper_assets/paper_citation_audit.md"))
    return parser.parse_args()


def strip_latex_comments(text: str) -> str:
    return "\n".join(re.sub(r"(?<!\\)%.*", "", line) for line in text.splitlines())


def find_latex_files(paper_dir: str | Path) -> list[Path]:
    base = Path(paper_dir)
    return sorted(path for path in base.rglob("*.tex") if "acl_style" not in path.parts)


def split_cite_keys(raw_keys: str) -> list[str]:
    return [key.strip() for key in raw_keys.split(",") if key.strip()]


def collect_citations(latex_files: list[Path]) -> tuple[list[str], dict[str, list[str]], list[str]]:
    keys: list[str] = []
    key_locations: dict[str, list[str]] = {}
    bibliography_names: list[str] = []
    for path in latex_files:
        text = strip_latex_comments(path.read_text(encoding="utf-8"))
        for match in CITE_RE.finditer(text):
            for key in split_cite_keys(match.group(1)):
                keys.append(key)
                key_locations.setdefault(key, []).append(str(path))
        for match in BIBLIOGRAPHY_RE.finditer(text):
            bibliography_names.extend(split_cite_keys(match.group(1)))
    return keys, key_locations, bibliography_names


def entry_span(text: str, start: int, end: int | None) -> str:
    return text[start : end if end is not None else len(text)]


def parse_bib_entries(bib_path: str | Path) -> tuple[list[dict[str, Any]], list[str]]:
    text = Path(bib_path).read_text(encoding="utf-8")
    matches = list(BIB_ENTRY_RE.finditer(text))
    entries: list[dict[str, Any]] = []
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else None
        body = entry_span(text, start, end)
        fields = {field.lower() for field in FIELD_RE.findall(body)}
        entries.append(
            {
                "kind": match.group("kind").lower(),
                "key": match.group("key"),
                "fields": sorted(fields),
                "has_locator": bool(fields.intersection({"doi", "url", "eprint", "howpublished"})),
            }
        )
    return entries, [match.group("key") for match in matches]


def missing_required_fields(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    missing: list[dict[str, Any]] = []
    for entry in entries:
        required = REQUIRED_FIELDS.get(entry["kind"], {"author", "title", "year"})
        absent = sorted(required.difference(entry["fields"]))
        if entry["kind"] == "misc" and not entry["has_locator"]:
            absent.append("locator")
        if absent:
            missing.append({"key": entry["key"], "kind": entry["kind"], "missing_fields": absent})
    return missing


def read_log_problems(log_path: str | Path) -> list[str]:
    path = Path(log_path)
    if not path.exists():
        return [f"missing log file: {path}"]
    problems: list[str] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if LOG_PROBLEM_RE.search(line):
            problems.append(line.strip())
    return problems


def status_for(report: dict[str, Any]) -> str:
    if report["missing_bib_keys"] or report["duplicate_bib_keys"] or report["missing_required_fields"]:
        return "blocker"
    if report["unused_bib_keys"] or report["log_problems"]:
        return "warning"
    return "pass"


def audit_citations(*, paper_dir: str | Path, bib_path: str | Path, log_path: str | Path) -> dict[str, Any]:
    latex_files = find_latex_files(paper_dir)
    cited_keys, key_locations, bibliography_names = collect_citations(latex_files)
    entries, bib_keys = parse_bib_entries(bib_path)
    key_counts = Counter(bib_keys)
    cited_unique = sorted(set(cited_keys))
    bib_unique = sorted(set(bib_keys))
    report: dict[str, Any] = {
        "paper_dir": str(paper_dir),
        "bib_path": str(bib_path),
        "log_path": str(log_path),
        "latex_files": [str(path) for path in latex_files],
        "bibliography_names": sorted(set(bibliography_names)),
        "citation_occurrences": len(cited_keys),
        "cited_key_count": len(cited_unique),
        "bib_entry_count": len(bib_keys),
        "cited_keys": cited_unique,
        "bib_keys": bib_unique,
        "missing_bib_keys": sorted(set(cited_unique).difference(bib_unique)),
        "unused_bib_keys": sorted(set(bib_unique).difference(cited_unique)),
        "duplicate_bib_keys": sorted(key for key, count in key_counts.items() if count > 1),
        "missing_required_fields": missing_required_fields(entries),
        "entries_with_locator_count": sum(1 for entry in entries if entry["has_locator"]),
        "citation_locations": {key: sorted(set(paths)) for key, paths in sorted(key_locations.items())},
        "log_problems": read_log_problems(log_path),
    }
    report["status"] = status_for(report)
    report["ok"] = report["status"] == "pass"
    return report


def write_markdown(path: str | Path, report: dict[str, Any]) -> None:
    lines = [
        "# Paper Citation Audit",
        "",
        f"Status: `{report['status']}`",
        "",
        "## Summary",
        "",
        f"- Citation occurrences: `{report['citation_occurrences']}`",
        f"- Unique cited keys: `{report['cited_key_count']}`",
        f"- BibTeX entries: `{report['bib_entry_count']}`",
        f"- Entries with DOI/URL/eprint/howpublished locator: `{report['entries_with_locator_count']}`",
        "",
        "## Gate Checks",
        "",
        f"- Missing BibTeX keys: `{len(report['missing_bib_keys'])}`",
        f"- Unused BibTeX keys: `{len(report['unused_bib_keys'])}`",
        f"- Duplicate BibTeX keys: `{len(report['duplicate_bib_keys'])}`",
        f"- Entries missing required fields: `{len(report['missing_required_fields'])}`",
        f"- LaTeX citation/reference log problems: `{len(report['log_problems'])}`",
        "",
    ]
    for title, key in [
        ("Missing BibTeX Keys", "missing_bib_keys"),
        ("Unused BibTeX Keys", "unused_bib_keys"),
        ("Duplicate BibTeX Keys", "duplicate_bib_keys"),
    ]:
        if report[key]:
            lines.extend([f"## {title}", ""])
            lines.extend(f"- `{item}`" for item in report[key])
            lines.append("")
    if report["missing_required_fields"]:
        lines.extend(["## Entries Missing Required Fields", ""])
        for item in report["missing_required_fields"]:
            fields = ", ".join(f"`{field}`" for field in item["missing_fields"])
            lines.append(f"- `{item['key']}` ({item['kind']}): {fields}")
        lines.append("")
    if report["log_problems"]:
        lines.extend(["## LaTeX Log Problems", ""])
        lines.extend(f"- `{line}`" for line in report["log_problems"])
        lines.append("")
    lines.extend(["## Cited Keys", ""])
    for key in report["cited_keys"]:
        lines.append(f"- `{key}`")
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    report = audit_citations(paper_dir=args.paper_dir, bib_path=args.bib, log_path=args.log)
    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(args.output_md, report)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
