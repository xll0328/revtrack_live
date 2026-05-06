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
from revtrack.schema import IssueExample, Prediction


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train an encoder-based classifier on labeled examples and predict unlabeled candidates.")
    parser.add_argument("--train-data", required=True)
    parser.add_argument("--candidate-data", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--max-length", type=int, default=512)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    parser.add_argument("--local-files-only", action="store_true")
    return parser.parse_args()


def build_text(example: IssueExample) -> str:
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


def embed_texts(texts, tokenizer, model, max_length, batch_size, device):
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
    return torch.cat(outputs, dim=0).numpy()


def load_candidate_examples(path: str | Path) -> list[IssueExample]:
    rows = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if "issue_id" in row:
                rows.append(
                    IssueExample(
                        id=row["issue_id"],
                        source=row.get("source", "openreview"),
                        venue=row.get("venue", ""),
                        paper_title=row.get("paper_title", ""),
                        abstract=row.get("abstract", ""),
                        review_text=row.get("review_excerpt", ""),
                        author_response=row.get("aligned_response_excerpt", ""),
                        revision_summary=row.get("revision_summary", ""),
                        gold_label="",
                        metadata={
                            "submission_id": row.get("submission_id", ""),
                            "review_id": row.get("review_id", ""),
                        },
                    )
                )
                continue
            rows.append(
                IssueExample(
                    id=row["id"],
                    source=row.get("source", "openreview"),
                    venue=row.get("venue", ""),
                    paper_title=row.get("paper_title", ""),
                    abstract=row.get("abstract", ""),
                    review_text=row.get("review_text", ""),
                    author_response=row.get("author_response", ""),
                    revision_summary=row.get("revision_summary", ""),
                    gold_label="",
                    metadata=row.get("metadata", {}),
                )
            )
    return rows


def main() -> None:
    args = parse_args()
    train_examples = load_examples(args.train_data)
    candidate_examples = load_candidate_examples(args.candidate_data)

    tokenizer = AutoTokenizer.from_pretrained(args.model, local_files_only=args.local_files_only)
    model = AutoModel.from_pretrained(args.model, local_files_only=args.local_files_only)
    model.to(args.device)

    train_embeddings = embed_texts(
        [build_text(example) for example in train_examples],
        tokenizer=tokenizer,
        model=model,
        max_length=args.max_length,
        batch_size=args.batch_size,
        device=args.device,
    )
    candidate_embeddings = embed_texts(
        [build_text(example) for example in candidate_examples],
        tokenizer=tokenizer,
        model=model,
        max_length=args.max_length,
        batch_size=args.batch_size,
        device=args.device,
    )

    clf = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            ("svc", LinearSVC(class_weight="balanced", max_iter=20000)),
        ]
    )
    clf.fit(train_embeddings, [example.gold_label for example in train_examples])
    pred_labels = clf.predict(candidate_embeddings)
    scores = clf.decision_function(candidate_embeddings)
    classes = list(clf.named_steps["svc"].classes_)

    predictions = []
    for example, pred_label, score in zip(candidate_examples, pred_labels, scores, strict=False):
        raw_output = json.dumps(
            {
                "label": str(pred_label),
                "scores": score.tolist() if hasattr(score, "tolist") else list(score),
                "classes": classes,
            },
            ensure_ascii=False,
        )
        predictions.append(
            Prediction(
                id=example.id,
                predicted_label=str(pred_label),
                raw_output=raw_output,
                metadata={"backend": "encoder_transfer", "model": args.model},
            )
        )

    save_predictions(args.output, predictions)
    print(f"Wrote {len(predictions)} predictions to {args.output}")


if __name__ == "__main__":
    main()
