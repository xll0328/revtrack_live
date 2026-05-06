from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import torch
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVC
from transformers import AutoModel, AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from revtrack.io import load_examples, save_predictions
from revtrack.metrics import evaluate_predictions
from revtrack.schema import Prediction


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run an encoder-embedding + LinearSVC baseline with leave-one-out CV.")
    parser.add_argument("--data", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--eval-json")
    parser.add_argument("--max-length", type=int, default=512)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    parser.add_argument("--local-files-only", action="store_true")
    return parser.parse_args()


def build_text(example) -> str:
    return (
        f"TITLE: {example.paper_title}\n"
        f"ABSTRACT: {example.abstract}\n"
        f"REVIEW: {example.review_text}\n"
        f"AUTHOR_RESPONSE: {example.author_response}\n"
        f"REVISION_SUMMARY: {example.revision_summary}\n"
    )


def mean_pool(last_hidden_state: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
    mask = attention_mask.unsqueeze(-1).expand(last_hidden_state.size()).float()
    masked = last_hidden_state * mask
    summed = masked.sum(dim=1)
    counts = mask.sum(dim=1).clamp(min=1e-9)
    return summed / counts


def embed_texts(
    texts: list[str],
    tokenizer,
    model,
    max_length: int,
    batch_size: int,
    device: str,
) -> torch.Tensor:
    outputs = []
    model.eval()
    with torch.no_grad():
        for start in range(0, len(texts), batch_size):
            batch = texts[start : start + batch_size]
            encoded = tokenizer(
                batch,
                padding=True,
                truncation=True,
                max_length=max_length,
                return_tensors="pt",
            )
            encoded = {key: value.to(device) for key, value in encoded.items()}
            result = model(**encoded)
            pooled = mean_pool(result.last_hidden_state, encoded["attention_mask"])
            outputs.append(pooled.cpu())
    return torch.cat(outputs, dim=0)


def main() -> None:
    args = parse_args()
    examples = load_examples(args.data)
    texts = [build_text(example) for example in examples]
    labels = [example.gold_label for example in examples]

    tokenizer = AutoTokenizer.from_pretrained(args.model, local_files_only=args.local_files_only)
    model = AutoModel.from_pretrained(args.model, local_files_only=args.local_files_only)
    model.to(args.device)

    embeddings = embed_texts(
        texts=texts,
        tokenizer=tokenizer,
        model=model,
        max_length=args.max_length,
        batch_size=args.batch_size,
        device=args.device,
    ).numpy()

    predictions = []
    for idx, example in enumerate(examples):
        train_x = [embeddings[j] for j in range(len(examples)) if j != idx]
        train_y = [labels[j] for j in range(len(examples)) if j != idx]
        test_x = [embeddings[idx]]

        clf = Pipeline(
            steps=[
                ("scaler", StandardScaler()),
                ("svc", LinearSVC(class_weight="balanced", max_iter=20000)),
            ]
        )
        clf.fit(train_x, train_y)
        pred_label = str(clf.predict(test_x)[0])
        scores = clf.decision_function(test_x)
        raw_output = json.dumps(
            {
                "label": pred_label,
                "scores": scores.tolist() if hasattr(scores, "tolist") else list(scores),
                "classes": list(clf.named_steps["svc"].classes_),
            },
            ensure_ascii=False,
        )
        predictions.append(
            Prediction(
                id=example.id,
                predicted_label=pred_label,
                raw_output=raw_output,
                metadata={"backend": "encoder_linear_svc", "model": args.model},
            )
        )

    save_predictions(args.output, predictions)
    print(f"Wrote {len(predictions)} predictions to {args.output}")

    if args.eval_json:
        summary, details = evaluate_predictions(examples, predictions)
        target = Path(args.eval_json)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps({"summary": summary, "details": details}, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
