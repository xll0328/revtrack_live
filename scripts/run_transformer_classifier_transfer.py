from __future__ import annotations

import argparse
import json
import random
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from torch.optim import AdamW
from torch.utils.data import DataLoader, Dataset
from transformers import AutoModelForSequenceClassification, AutoTokenizer, get_linear_schedule_with_warmup

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from revtrack.io import load_examples, save_predictions
from revtrack.metrics import evaluate_predictions
from revtrack.schema import LABELS, IssueExample, Prediction


@dataclass(frozen=True)
class EvalSpec:
    name: str
    path: Path


class EncodedDataset(Dataset):
    def __init__(self, examples: list[IssueExample], tokenizer, label2id: dict[str, int], max_length: int) -> None:
        texts = [build_text(example) for example in examples]
        encoded = tokenizer(
            texts,
            truncation=True,
            padding=True,
            max_length=max_length,
            return_tensors="pt",
        )
        self.input_ids = encoded["input_ids"]
        self.attention_mask = encoded["attention_mask"]
        self.labels = torch.tensor([label2id[example.gold_label] for example in examples], dtype=torch.long)

    def __len__(self) -> int:
        return int(self.labels.shape[0])

    def __getitem__(self, idx: int) -> dict[str, torch.Tensor]:
        return {
            "input_ids": self.input_ids[idx],
            "attention_mask": self.attention_mask[idx],
            "labels": self.labels[idx],
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Train a fine-tuned transformer classifier on RevTrack labels and evaluate transfer splits."
    )
    parser.add_argument("--train-data", required=True)
    parser.add_argument(
        "--eval-spec",
        action="append",
        required=True,
        help="Evaluation spec in the form name:path. Repeat for multiple splits.",
    )
    parser.add_argument("--model", default="answerdotai/ModernBERT-base")
    parser.add_argument("--output-dir", default="outputs/day1/strong_baselines/modernbert_finetune_v1")
    parser.add_argument("--max-length", type=int, default=512)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--epochs", type=int, default=6)
    parser.add_argument("--lr", type=float, default=2e-5)
    parser.add_argument("--weight-decay", type=float, default=0.01)
    parser.add_argument("--warmup-ratio", type=float, default=0.1)
    parser.add_argument("--grad-accum", type=int, default=1)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    parser.add_argument("--local-files-only", action="store_true")
    return parser.parse_args()


def parse_eval_specs(values: list[str]) -> list[EvalSpec]:
    specs: list[EvalSpec] = []
    for value in values:
        name, sep, raw_path = value.partition(":")
        if not sep or not name.strip() or not raw_path.strip():
            raise ValueError(f"Invalid --eval-spec: {value!r}. Expected name:path")
        path = Path(raw_path.strip())
        if not path.is_absolute():
            path = ROOT / path
        specs.append(EvalSpec(name=name.strip(), path=path))
    return specs


def build_text(example: IssueExample) -> str:
    return (
        f"TITLE: {example.paper_title}\n"
        f"ABSTRACT: {example.abstract}\n"
        f"REVIEW_CONCERN: {example.review_text}\n"
        f"AUTHOR_RESPONSE_EVIDENCE: {example.author_response}\n"
        f"REVISION_EVIDENCE: {example.revision_summary}\n"
    )


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def class_weight_tensor(examples: list[IssueExample], label2id: dict[str, int], device: str) -> torch.Tensor:
    counts = np.zeros(len(LABELS), dtype=np.float64)
    for example in examples:
        counts[label2id[example.gold_label]] += 1.0
    counts = np.maximum(counts, 1.0)
    inv = counts.sum() / (len(LABELS) * counts)
    weights = torch.tensor(inv, dtype=torch.float32, device=device)
    return weights


def train_model(
    *,
    model,
    train_loader: DataLoader,
    optimizer,
    scheduler,
    class_weights: torch.Tensor,
    device: str,
    epochs: int,
    grad_accum: int,
) -> list[dict[str, float]]:
    history: list[dict[str, float]] = []
    for epoch_idx in range(epochs):
        model.train()
        running_loss = 0.0
        step_count = 0
        optimizer.zero_grad(set_to_none=True)
        for step_idx, batch in enumerate(train_loader, start=1):
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            loss = F.cross_entropy(outputs.logits, labels, weight=class_weights)
            loss = loss / max(1, grad_accum)
            loss.backward()
            running_loss += float(loss.item()) * max(1, grad_accum)
            step_count += 1
            if step_idx % max(1, grad_accum) == 0:
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad(set_to_none=True)
        avg_loss = running_loss / max(1, step_count)
        history.append({"epoch": float(epoch_idx + 1), "train_loss": avg_loss})
        print(json.dumps({"epoch": epoch_idx + 1, "train_loss": avg_loss}))
    return history


def predict_examples(
    *,
    model,
    tokenizer,
    examples: list[IssueExample],
    id2label: dict[int, str],
    max_length: int,
    batch_size: int,
    device: str,
) -> list[Prediction]:
    model.eval()
    predictions: list[Prediction] = []
    with torch.no_grad():
        for start in range(0, len(examples), batch_size):
            chunk = examples[start : start + batch_size]
            encoded = tokenizer(
                [build_text(example) for example in chunk],
                truncation=True,
                padding=True,
                max_length=max_length,
                return_tensors="pt",
            )
            encoded = {key: value.to(device) for key, value in encoded.items()}
            outputs = model(**encoded)
            probs = torch.softmax(outputs.logits, dim=-1).cpu()
            pred_ids = torch.argmax(probs, dim=-1).tolist()
            for example, pred_id, prob_row in zip(chunk, pred_ids, probs, strict=False):
                prob_list = prob_row.tolist()
                predicted_label = id2label[int(pred_id)]
                predictions.append(
                    Prediction(
                        id=example.id,
                        predicted_label=predicted_label,
                        raw_output=json.dumps(
                            {
                                "label": predicted_label,
                                "probs": prob_list,
                                "labels": [id2label[idx] for idx in range(len(LABELS))],
                            },
                            ensure_ascii=False,
                        ),
                        metadata={"backend": "finetuned_transformer_classifier"},
                    )
                )
    return predictions


def main() -> None:
    args = parse_args()
    set_seed(args.seed)
    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = ROOT / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    eval_specs = parse_eval_specs(args.eval_spec)
    train_examples = load_examples(args.train_data)

    label2id = {label: idx for idx, label in enumerate(LABELS)}
    id2label = {idx: label for label, idx in label2id.items()}

    tokenizer = AutoTokenizer.from_pretrained(args.model, local_files_only=args.local_files_only)
    model = AutoModelForSequenceClassification.from_pretrained(
        args.model,
        num_labels=len(LABELS),
        id2label=id2label,
        label2id=label2id,
        local_files_only=args.local_files_only,
    )
    model.to(args.device)

    train_ds = EncodedDataset(train_examples, tokenizer, label2id, args.max_length)
    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True)
    class_weights = class_weight_tensor(train_examples, label2id, args.device)

    total_update_steps = max(1, (len(train_loader) * args.epochs) // max(1, args.grad_accum))
    warmup_steps = int(total_update_steps * max(0.0, args.warmup_ratio))
    optimizer = AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=warmup_steps,
        num_training_steps=total_update_steps,
    )

    history = train_model(
        model=model,
        train_loader=train_loader,
        optimizer=optimizer,
        scheduler=scheduler,
        class_weights=class_weights,
        device=args.device,
        epochs=args.epochs,
        grad_accum=args.grad_accum,
    )
    (output_dir / "train_history.json").write_text(json.dumps(history, indent=2), encoding="utf-8")

    model.save_pretrained(output_dir / "model")
    tokenizer.save_pretrained(output_dir / "model")

    run_summary = {
        "train_data": str(Path(args.train_data)),
        "eval_specs": [{"name": spec.name, "path": str(spec.path)} for spec in eval_specs],
        "model": args.model,
        "max_length": args.max_length,
        "batch_size": args.batch_size,
        "epochs": args.epochs,
        "lr": args.lr,
        "weight_decay": args.weight_decay,
        "warmup_ratio": args.warmup_ratio,
        "grad_accum": args.grad_accum,
        "seed": args.seed,
        "device": args.device,
    }

    metrics_rows: list[dict[str, float | str]] = []
    for spec in eval_specs:
        examples = load_examples(spec.path)
        preds = predict_examples(
            model=model,
            tokenizer=tokenizer,
            examples=examples,
            id2label=id2label,
            max_length=args.max_length,
            batch_size=args.batch_size,
            device=args.device,
        )
        pred_path = output_dir / f"{spec.name}_predictions.jsonl"
        eval_path = output_dir / f"{spec.name}_metrics.json"
        save_predictions(pred_path, preds)
        summary, details = evaluate_predictions(examples, preds)
        eval_path.write_text(json.dumps({"summary": summary, "details": details}, indent=2), encoding="utf-8")
        metrics_rows.append(
            {
                "split": spec.name,
                "rows": summary["num_examples"],
                "accuracy": summary["accuracy"],
                "macro_f1": summary["macro_f1"],
                "fixed_f1": summary["per_label"]["fixed"]["f1"],
                "partially_fixed_f1": summary["per_label"]["partially_fixed"]["f1"],
                "unresolved_f1": summary["per_label"]["unresolved"]["f1"],
                "regressed_f1": summary["per_label"]["regressed"]["f1"],
            }
        )
        print(json.dumps({"split": spec.name, "summary": summary}))

    (output_dir / "run_config.json").write_text(json.dumps(run_summary, indent=2), encoding="utf-8")
    (output_dir / "metrics_summary.json").write_text(json.dumps(metrics_rows, indent=2), encoding="utf-8")
    print(f"Wrote outputs to {output_dir}")


if __name__ == "__main__":
    main()
