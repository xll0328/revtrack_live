from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


VALID_LABELS = {"fixed", "partially_fixed", "unresolved", "regressed"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a local chat model over a prompted-LLM baseline packet.")
    parser.add_argument("--prompt-packet", required=True)
    parser.add_argument("--output-jsonl", required=True)
    parser.add_argument("--model-path", required=True)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--dtype", default="auto", choices=["auto", "float16", "bfloat16", "float32"])
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--max-new-tokens", type=int, default=192)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--top-p", type=float, default=1.0)
    return parser.parse_args()


def load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: str | Path, rows: list[dict[str, Any]]) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def first_json_object(text: str) -> dict[str, Any]:
    decoder = json.JSONDecoder()
    for match in re.finditer(r"\{", text):
        try:
            obj, _ = decoder.raw_decode(text[match.start() :])
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            return obj
    return {}


def normalize_generation(issue_id: str, text: str) -> dict[str, Any]:
    parsed = first_json_object(text)
    label = str(parsed.get("predicted_label") or parsed.get("label") or "").strip().lower()
    if label not in VALID_LABELS:
        label = "invalid"
    return {
        "id": issue_id,
        "predicted_label": label,
        "evidence_span": str(parsed.get("evidence_span") or "").strip(),
        "rationale": str(parsed.get("rationale") or "").strip(),
        "raw_output": text.strip(),
    }


def torch_dtype(value: str):
    import torch

    if value == "float16":
        return torch.float16
    if value == "bfloat16":
        return torch.bfloat16
    if value == "float32":
        return torch.float32
    return "auto"


def run_local_model(
    *,
    prompt_packet: str | Path,
    output_jsonl: str | Path,
    model_path: str | Path,
    device: str = "cuda:0",
    dtype: str = "auto",
    limit: int = 0,
    max_new_tokens: int = 192,
    temperature: float = 0.0,
    top_p: float = 1.0,
) -> list[dict[str, Any]]:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    rows = load_jsonl(prompt_packet)
    if limit > 0:
        rows = rows[:limit]

    tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        local_files_only=True,
        torch_dtype=torch_dtype(dtype),
        device_map={"": device},
    )
    model.eval()

    outputs: list[dict[str, Any]] = []
    do_sample = temperature > 0
    for index, row in enumerate(rows, start=1):
        messages = row["messages"]
        prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        with torch.inference_mode():
            generated = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=do_sample,
                temperature=temperature if do_sample else None,
                top_p=top_p if do_sample else None,
                pad_token_id=tokenizer.eos_token_id,
            )
        new_tokens = generated[0][inputs["input_ids"].shape[-1] :]
        text = tokenizer.decode(new_tokens, skip_special_tokens=True)
        item = normalize_generation(str(row["id"]), text)
        item["model_path"] = str(model_path)
        item["prompt_packet"] = str(prompt_packet)
        item["row_index"] = index
        outputs.append(item)
        write_jsonl(output_jsonl, outputs)
    return outputs


def main() -> None:
    args = parse_args()
    outputs = run_local_model(
        prompt_packet=args.prompt_packet,
        output_jsonl=args.output_jsonl,
        model_path=args.model_path,
        device=args.device,
        dtype=args.dtype,
        limit=args.limit,
        max_new_tokens=args.max_new_tokens,
        temperature=args.temperature,
        top_p=args.top_p,
    )
    print(json.dumps({"rows": len(outputs), "output_jsonl": args.output_jsonl}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
