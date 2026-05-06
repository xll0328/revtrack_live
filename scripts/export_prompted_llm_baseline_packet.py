from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from revtrack.io import load_examples
from revtrack.schema import LABELS, IssueExample


SYSTEM_PROMPT = (
    "You are evaluating scientific revision tracking examples. "
    "Return only valid JSON with keys predicted_label, evidence_span, and rationale."
)

RUBRIC = """Choose exactly one label:
- fixed: the revision/response directly resolves the reviewer concern.
- partially_fixed: the revision/response makes real progress but leaves a material part unresolved.
- unresolved: the concern remains substantively unaddressed, deferred, or only acknowledged.
- regressed: the revision introduces or worsens the same concern.

Use the response and revision evidence, not the plausibility of the original criticism alone.
Do not reward a long response unless it actually addresses the concern."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export JSONL prompts for a prompted-LLM RevTrack baseline.")
    parser.add_argument("--examples", required=True)
    parser.add_argument("--output-jsonl", required=True)
    parser.add_argument("--output-md", required=True)
    parser.add_argument("--dataset-name", required=True)
    parser.add_argument("--max-field-chars", type=int, default=4000)
    return parser.parse_args()


def compact(value: str | None) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def clip(value: str | None, max_chars: int) -> str:
    text = compact(value)
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(" ", 1)[0] + "..."


def user_prompt(example: IssueExample, *, max_field_chars: int) -> str:
    return "\n\n".join(
        [
            RUBRIC,
            f"Paper title:\n{clip(example.paper_title, max_field_chars)}",
            f"Reviewer concern:\n{clip(example.review_text, max_field_chars)}",
            f"Author response evidence:\n{clip(example.author_response, max_field_chars)}",
            f"Revision summary:\n{clip(example.revision_summary, max_field_chars)}",
            (
                "Return JSON only, for example: "
                '{"predicted_label":"partially_fixed","evidence_span":"short quote or paraphrase",'
                '"rationale":"why this label follows from the evidence"}'
            ),
        ]
    )


def prompt_item(example: IssueExample, *, dataset_name: str, max_field_chars: int) -> dict[str, Any]:
    return {
        "id": example.id,
        "dataset_name": dataset_name,
        "paper_title": example.paper_title,
        "valid_labels": list(LABELS),
        "expected_output_schema": {
            "predicted_label": "one of fixed, partially_fixed, unresolved, regressed",
            "evidence_span": "brief evidence from author response or revision summary",
            "rationale": "brief explanation grounded in the evidence",
        },
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt(example, max_field_chars=max_field_chars)},
        ],
        "metadata": {
            "source": example.source,
            "venue": example.venue,
            "gold_label_hidden": True,
            "example_provenance": example.metadata.get("provenance", ""),
        },
    }


def export_packet(
    *,
    examples_path: str | Path,
    output_jsonl: str | Path,
    output_md: str | Path,
    dataset_name: str,
    max_field_chars: int = 4000,
) -> dict[str, Any]:
    examples = load_examples(examples_path)
    output = Path(output_jsonl)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for example in examples:
            handle.write(
                json.dumps(
                    prompt_item(example, dataset_name=dataset_name, max_field_chars=max_field_chars),
                    ensure_ascii=False,
                )
                + "\n"
            )

    gold_distribution = Counter(example.gold_label for example in examples)
    manifest = {
        "dataset_name": dataset_name,
        "rows": len(examples),
        "output_jsonl": str(output_jsonl),
        "gold_labels_hidden_in_prompts": True,
        "gold_distribution_for_audit_only": dict(sorted(gold_distribution.items())),
        "max_field_chars": max_field_chars,
    }
    write_report(output_md, manifest)
    return manifest


def write_report(path: str | Path, manifest: dict[str, Any]) -> None:
    lines = [
        f"# {manifest['dataset_name']} Prompted-LLM Baseline Packet",
        "",
        "- Rows: `" + str(manifest["rows"]) + "`",
        "- Gold labels hidden in prompts: `true`",
        f"- Prompt JSONL: `{manifest['output_jsonl']}`",
        "- Expected output JSON keys: `predicted_label`, `evidence_span`, `rationale`",
        "",
        "## Boundary",
        "",
        "This packet only prepares prompts. It does not call any model and does not create benchmark results.",
    ]
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    manifest = export_packet(
        examples_path=args.examples,
        output_jsonl=args.output_jsonl,
        output_md=args.output_md,
        dataset_name=args.dataset_name,
        max_field_chars=args.max_field_chars,
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
