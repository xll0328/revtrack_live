from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from revtrack.io import load_examples, save_predictions
from revtrack.metrics import evaluate_predictions
from revtrack.schema import LABELS, IssueExample, Prediction


DEFAULT_DATASETS = [
    (
        "iclr2024_clean_dev_v7",
        "data/processed/iclr2024_clean_dev_assistant_v7.jsonl",
    ),
    (
        "iclr2025_expanded80_standard_validation_v1",
        "data/processed/iclr2025_expanded80_standard_validation_v1.jsonl",
    ),
    (
        "neurips2024_limit100_standard_validation_v1",
        "data/processed/neurips2024_limit100_standard_validation_v1.jsonl",
    ),
    (
        "iclr2023_limit80_random80_standard_validation_v1",
        "data/processed/iclr2023_limit80_random80_standard_validation_v1.jsonl",
    ),
]

LABEL_HYPOTHESES = {
    "fixed": "The reviewer concern has been fully addressed with concrete revision evidence.",
    "partially_fixed": "The reviewer concern has been partially addressed, but a material part remains unresolved.",
    "unresolved": "The reviewer concern remains unresolved after the response and revision evidence.",
    "regressed": "The attempted fix made this concern worse or introduced a related new problem on the same axis.",
}


@dataclass(frozen=True)
class DatasetSpec:
    name: str
    path: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run an NLI-hypothesis baseline for RevTrack issue-status classification."
    )
    parser.add_argument(
        "--dataset",
        action="append",
        default=None,
        help="Dataset spec in name:path format (repeatable). Defaults to canonical paper-facing splits.",
    )
    parser.add_argument(
        "--model",
        default="MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli",
        help="HF NLI model with entailment label.",
    )
    parser.add_argument("--max-length", type=int, default=768)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--output-dir", default="outputs/day1/nli_hypothesis_baseline")
    parser.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    parser.add_argument("--local-files-only", action="store_true")
    parser.add_argument(
        "--model-load-retries",
        type=int,
        default=5,
        help="Retry count for loading tokenizer/model (handles flaky HF downloads).",
    )
    parser.add_argument(
        "--model-load-retry-sleep",
        type=float,
        default=10.0,
        help="Base sleep seconds between model-load retries (linear backoff).",
    )
    parser.add_argument(
        "--hf-download-timeout",
        type=int,
        default=1200,
        help="HF download timeout in seconds (exported to HF_HUB_DOWNLOAD_TIMEOUT if unset).",
    )
    return parser.parse_args()


def parse_datasets(values: list[str] | None) -> list[DatasetSpec]:
    raw_specs: list[tuple[str, str]]
    if values:
        raw_specs = []
        for value in values:
            name, sep, raw_path = value.partition(":")
            if not sep or not name.strip() or not raw_path.strip():
                raise ValueError(f"Invalid --dataset spec: {value!r}. Expected name:path")
            raw_specs.append((name.strip(), raw_path.strip()))
    else:
        raw_specs = list(DEFAULT_DATASETS)

    datasets: list[DatasetSpec] = []
    for name, raw_path in raw_specs:
        path = Path(raw_path)
        if not path.is_absolute():
            path = ROOT / path
        datasets.append(DatasetSpec(name=name, path=path))
    return datasets


def build_premise(example: IssueExample) -> str:
    return (
        f"Paper: {example.paper_title}\n"
        f"Concern: {example.review_text}\n"
        f"Author response evidence: {example.author_response}\n"
        f"Revision evidence: {example.revision_summary}\n"
    )


def find_entailment_index(model: AutoModelForSequenceClassification) -> int:
    id2label = getattr(model.config, "id2label", None) or {}
    for idx, label in id2label.items():
        label_text = str(label).lower()
        if "entail" in label_text and "not_entail" not in label_text:
            return int(idx)
    raise ValueError(f"Could not find entailment label in model id2label={id2label}")


def score_label_hypotheses(
    *,
    model: AutoModelForSequenceClassification,
    tokenizer,
    examples: list[IssueExample],
    max_length: int,
    batch_size: int,
    device: str,
    entailment_index: int,
) -> list[Prediction]:
    model.eval()
    predictions: list[Prediction] = []

    premises = [build_premise(example) for example in examples]
    hypotheses = [LABEL_HYPOTHESES[label] for label in LABELS]

    with torch.no_grad():
        for start in range(0, len(examples), batch_size):
            chunk_examples = examples[start : start + batch_size]
            chunk_premises = premises[start : start + batch_size]
            chunk_scores = torch.zeros((len(chunk_examples), len(LABELS)), dtype=torch.float32)

            for label_idx, hypothesis in enumerate(hypotheses):
                encoded = tokenizer(
                    chunk_premises,
                    [hypothesis] * len(chunk_examples),
                    truncation=True,
                    padding=True,
                    max_length=max_length,
                    return_tensors="pt",
                )
                encoded = {key: value.to(device) for key, value in encoded.items()}
                logits = model(**encoded).logits
                probs = torch.softmax(logits, dim=-1).cpu()
                chunk_scores[:, label_idx] = probs[:, entailment_index]

            # Normalize entailment scores across candidate labels.
            normalized = torch.softmax(chunk_scores, dim=-1)
            pred_ids = torch.argmax(normalized, dim=-1).tolist()

            for row_idx, example in enumerate(chunk_examples):
                pred_label = LABELS[pred_ids[row_idx]]
                label_scores = {
                    LABELS[idx]: float(normalized[row_idx, idx].item())
                    for idx in range(len(LABELS))
                }
                predictions.append(
                    Prediction(
                        id=example.id,
                        predicted_label=pred_label,
                        raw_output=json.dumps(
                            {
                                "predicted_label": pred_label,
                                "label_scores": label_scores,
                                "backend": "nli_hypothesis",
                            },
                            ensure_ascii=False,
                        ),
                        metadata={"backend": "nli_hypothesis"},
                    )
                )
    return predictions


def summarize_result(dataset_name: str, summary: dict[str, Any]) -> dict[str, Any]:
    per_label = summary.get("per_label", {})
    return {
        "dataset": dataset_name,
        "rows": int(summary.get("num_examples", 0)),
        "accuracy": float(summary.get("accuracy", 0.0)),
        "macro_f1": float(summary.get("macro_f1", 0.0)),
        "fixed_f1": float(per_label.get("fixed", {}).get("f1", 0.0)),
        "partially_fixed_f1": float(per_label.get("partially_fixed", {}).get("f1", 0.0)),
        "unresolved_f1": float(per_label.get("unresolved", {}).get("f1", 0.0)),
        "regressed_f1": float(per_label.get("regressed", {}).get("f1", 0.0)),
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = [
        "dataset",
        "rows",
        "accuracy",
        "macro_f1",
        "fixed_f1",
        "partially_fixed_f1",
        "unresolved_f1",
        "regressed_f1",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_md(path: Path, rows: list[dict[str, Any]], model_name: str) -> None:
    lines = [
        "# NLI Hypothesis Baseline Transfer Summary",
        "",
        f"- model: `{model_name}`",
        "",
        "| Dataset | Rows | Accuracy | Macro-F1 | Fixed F1 | Partial F1 | Unresolved F1 | Regressed F1 |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            "| {dataset} | {rows} | {accuracy:.3f} | {macro_f1:.3f} | {fixed_f1:.3f} | "
            "{partially_fixed_f1:.3f} | {unresolved_f1:.3f} | {regressed_f1:.3f} |".format(**row)
        )
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_latex(path: Path, rows: list[dict[str, Any]]) -> None:
    lines = [
        r"\begin{table}[t]",
        r"\centering",
        r"\small",
        r"\begin{tabular}{lcccc}",
        r"\toprule",
        r"Dataset & Acc. & Macro-F1 & Fixed F1 & Unresolved F1 \\",
        r"\midrule",
    ]
    for row in rows:
        dataset = row["dataset"].replace("_", r"\_")
        lines.append(
            f"{dataset} & {row['accuracy']:.3f} & {row['macro_f1']:.3f} & "
            f"{row['fixed_f1']:.3f} & {row['unresolved_f1']:.3f} \\\\"
        )
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}",
            r"\caption{NLI-hypothesis baseline on paper-facing RevTrack splits.}",
            r"\label{tab:nli-hypothesis-transfer}",
            r"\end{table}",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def load_model_and_tokenizer(args: argparse.Namespace):
    # Allow callers to increase timeout without mutating global shell env.
    os.environ.setdefault("HF_HUB_DOWNLOAD_TIMEOUT", str(args.hf_download_timeout))

    last_error: Exception | None = None
    for attempt in range(1, args.model_load_retries + 1):
        try:
            tokenizer = AutoTokenizer.from_pretrained(
                args.model,
                local_files_only=args.local_files_only,
            )
            model = AutoModelForSequenceClassification.from_pretrained(
                args.model,
                local_files_only=args.local_files_only,
            )
            return tokenizer, model
        except Exception as exc:  # pragma: no cover - runtime/network dependent
            last_error = exc
            if attempt >= args.model_load_retries:
                raise
            wait_seconds = args.model_load_retry_sleep * attempt
            print(
                json.dumps(
                    {
                        "event": "model_load_retry",
                        "attempt": attempt,
                        "max_attempts": args.model_load_retries,
                        "wait_seconds": wait_seconds,
                        "model": args.model,
                        "error_type": type(exc).__name__,
                        "error": str(exc)[:240],
                    }
                ),
                file=sys.stderr,
                flush=True,
            )
            time.sleep(wait_seconds)

    if last_error is not None:  # pragma: no cover - defensive
        raise last_error
    raise RuntimeError("Unexpected model loading state")


def main() -> None:
    args = parse_args()
    datasets = parse_datasets(args.dataset)

    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = ROOT / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    tokenizer, model = load_model_and_tokenizer(args)
    model.to(args.device)
    entailment_index = find_entailment_index(model)

    all_rows: list[dict[str, Any]] = []
    all_metrics: dict[str, Any] = {
        "model": args.model,
        "device": args.device,
        "entailment_index": entailment_index,
        "datasets": {},
    }

    for spec in datasets:
        examples = load_examples(spec.path)
        predictions = score_label_hypotheses(
            model=model,
            tokenizer=tokenizer,
            examples=examples,
            max_length=args.max_length,
            batch_size=args.batch_size,
            device=args.device,
            entailment_index=entailment_index,
        )
        pred_path = output_dir / f"{spec.name}_predictions.jsonl"
        save_predictions(pred_path, predictions)
        summary, _ = evaluate_predictions(examples, predictions)
        row = summarize_result(spec.name, summary)
        all_rows.append(row)
        all_metrics["datasets"][spec.name] = summary
        print(
            json.dumps(
                {
                    "dataset": spec.name,
                    "rows": row["rows"],
                    "accuracy": row["accuracy"],
                    "macro_f1": row["macro_f1"],
                }
            )
        )

    smoke_like = len(datasets) == 1 and datasets[0].name.lower().startswith("smoke")
    if smoke_like:
        print(json.dumps({"status": "ok", "note": "smoke run: skipped paper asset export"}))
        return

    csv_path = ROOT / "outputs/day1/paper_assets/nli_hypothesis_transfer_20260506.csv"
    md_path = ROOT / "outputs/day1/paper_assets/nli_hypothesis_transfer_20260506.md"
    json_path = ROOT / "outputs/day1/paper_assets/nli_hypothesis_transfer_20260506.json"
    tex_path = ROOT / "paper/tables/nli_hypothesis_transfer.tex"

    write_csv(csv_path, all_rows)
    write_md(md_path, all_rows, args.model)
    write_latex(tex_path, all_rows)
    json_path.write_text(json.dumps(all_metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "status": "ok",
                "csv": str(csv_path.relative_to(ROOT)),
                "md": str(md_path.relative_to(ROOT)),
                "json": str(json_path.relative_to(ROOT)),
                "tex": str(tex_path.relative_to(ROOT)),
            }
        )
    )


if __name__ == "__main__":
    main()
