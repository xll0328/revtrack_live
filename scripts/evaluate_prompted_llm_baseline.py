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

from revtrack.io import load_examples, save_predictions
from revtrack.metrics import evaluate_predictions
from revtrack.schema import LABELS, Prediction


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate prompted-LLM RevTrack baseline JSONL outputs.")
    parser.add_argument("--examples", required=True)
    parser.add_argument("--llm-outputs", required=True)
    parser.add_argument("--normalized-predictions", required=True)
    parser.add_argument("--metrics-json", required=True)
    parser.add_argument("--details-json", required=True)
    parser.add_argument("--audit-json", required=True)
    parser.add_argument("--metrics-md", required=True)
    parser.add_argument("--model-key", required=True)
    parser.add_argument("--allow-subset", action="store_true")
    parser.add_argument("--fail-on-invalid", action="store_true")
    return parser.parse_args()


def compact(value: str | None) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def extract_json_field(text: str, field: str) -> str:
    if not text:
        return ""
    patterns = (
        rf'"{field}"\s*:\s*"([^"]+)"',
        rf"'{field}'\s*:\s*'([^']+)'",
        rf'"{field}"\s*:\s*([a-zA-Z_]+)',
        rf"'{field}'\s*:\s*([a-zA-Z_]+)",
    )
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return compact(match.group(1))
    return ""


def load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def label_from_row(row: dict[str, Any]) -> str:
    label = compact(str(row.get("predicted_label") or row.get("label") or "")).lower()
    if label in LABELS:
        return label
    raw = str(row.get("raw_output") or "")
    fallback = extract_json_field(raw, "predicted_label") or extract_json_field(raw, "label")
    return fallback.lower()


def normalize_outputs(rows: list[dict[str, Any]]) -> tuple[list[Prediction], dict[str, Any]]:
    predictions: list[Prediction] = []
    seen: set[str] = set()
    invalid_rows: list[dict[str, str]] = []
    duplicate_ids: list[str] = []
    missing_evidence: list[str] = []
    label_counts: Counter[str] = Counter()

    for index, row in enumerate(rows, start=1):
        issue_id = compact(str(row.get("id") or row.get("issue_id") or ""))
        if not issue_id:
            invalid_rows.append({"row": str(index), "issue_id": "", "error": "missing id"})
            continue
        if issue_id in seen:
            duplicate_ids.append(issue_id)
            continue
        seen.add(issue_id)

        label = label_from_row(row)
        if label not in LABELS:
            invalid_rows.append({"row": str(index), "issue_id": issue_id, "error": f"invalid label: {label!r}"})
            label = "invalid"
        evidence = compact(str(row.get("evidence_span") or ""))
        if not evidence:
            evidence = extract_json_field(str(row.get("raw_output") or ""), "evidence_span")
        if not evidence:
            missing_evidence.append(issue_id)
        label_counts[label] += 1
        predictions.append(
            Prediction(
                id=issue_id,
                predicted_label=label,
                raw_output=json.dumps(row, ensure_ascii=False),
                metadata={
                    "evidence_span": evidence,
                    "rationale": compact(str(row.get("rationale") or ""))
                    or extract_json_field(str(row.get("raw_output") or ""), "rationale"),
                },
            )
        )

    audit = {
        "rows": len(rows),
        "normalized_predictions": len(predictions),
        "label_distribution": dict(sorted(label_counts.items())),
        "invalid_rows": invalid_rows,
        "duplicate_ids": duplicate_ids,
        "missing_evidence_ids": missing_evidence,
        "status": "ok" if not invalid_rows and not duplicate_ids else "error",
    }
    return predictions, audit


def write_json(path: str | Path, payload: Any) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_metrics_md(path: str | Path, *, model_key: str, summary: dict[str, Any], audit: dict[str, Any]) -> None:
    per_label = summary["per_label"]
    lines = [
        f"# {model_key} Prompted-LLM Baseline Metrics",
        "",
        f"- Rows: `{int(summary['num_examples'])}`",
        f"- Accuracy: `{float(summary['accuracy']):.3f}`",
        f"- Macro-F1: `{float(summary['macro_f1']):.3f}`",
        f"- Invalid output rows: `{len(audit['invalid_rows'])}`",
        f"- Duplicate IDs: `{len(audit['duplicate_ids'])}`",
        f"- Missing evidence spans: `{len(audit['missing_evidence_ids'])}`",
        "",
        "| label | precision | recall | F1 | support |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for label in LABELS:
        item = per_label[label]
        lines.append(
            f"| {label} | {item['precision']:.3f} | {item['recall']:.3f} | "
            f"{item['f1']:.3f} | {int(item['support'])} |"
        )
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def evaluate_llm_outputs(
    *,
    examples_path: str | Path,
    llm_outputs_path: str | Path,
    normalized_predictions_path: str | Path,
    metrics_json: str | Path,
    details_json: str | Path,
    audit_json: str | Path,
    metrics_md: str | Path,
    model_key: str,
    allow_subset: bool = False,
    fail_on_invalid: bool = False,
) -> dict[str, Any]:
    examples = load_examples(examples_path)
    predictions, audit = normalize_outputs(load_jsonl(llm_outputs_path))
    prediction_ids = {item.id for item in predictions}
    if allow_subset:
        examples = [example for example in examples if example.id in prediction_ids]
    save_predictions(normalized_predictions_path, predictions)
    summary, details = evaluate_predictions(examples, predictions)
    audit["allow_subset"] = allow_subset
    audit["evaluated_examples"] = len(examples)
    audit["missing_prediction_ids"] = sorted({example.id for example in load_examples(examples_path)} - prediction_ids)
    if audit["missing_prediction_ids"] and not allow_subset:
        audit["status"] = "error"
    write_json(metrics_json, summary)
    write_json(details_json, details)
    write_json(audit_json, audit)
    write_metrics_md(metrics_md, model_key=model_key, summary=summary, audit=audit)
    if fail_on_invalid and audit["status"] != "ok":
        raise SystemExit(1)
    return {"summary": summary, "audit": audit}


def main() -> None:
    args = parse_args()
    result = evaluate_llm_outputs(
        examples_path=args.examples,
        llm_outputs_path=args.llm_outputs,
        normalized_predictions_path=args.normalized_predictions,
        metrics_json=args.metrics_json,
        details_json=args.details_json,
        audit_json=args.audit_json,
        metrics_md=args.metrics_md,
        model_key=args.model_key,
        allow_subset=args.allow_subset,
        fail_on_invalid=args.fail_on_invalid,
    )
    print(json.dumps(result["audit"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
