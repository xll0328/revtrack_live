from __future__ import annotations

import argparse
import json
import os
import re
import time
from pathlib import Path
from typing import Any


VALID_LABELS = {"fixed", "partially_fixed", "unresolved", "regressed"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run AIHubMix/OpenAI-compatible Chat Completions baseline.")
    parser.add_argument("--prompt-packet", required=True)
    parser.add_argument("--output-jsonl", required=True)
    parser.add_argument("--model", default="gpt-5.5")
    parser.add_argument("--base-url", default="https://aihubmix.com/v1")
    parser.add_argument("--api-key-env", default="AIHUBMIX_API_KEY")
    parser.add_argument(
        "--api-key-file",
        default="",
        help="Optional local secret file. The file is read at runtime and is never copied to outputs.",
    )
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=512)
    parser.add_argument("--sleep-seconds", type=float, default=0.0)
    parser.add_argument("--request-timeout", type=float, default=60.0)
    parser.add_argument("--max-retries", type=int, default=3)
    parser.add_argument("--resume", action=argparse.BooleanOptionalAction, default=True)
    return parser.parse_args()


def load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def append_jsonl(path: str | Path, row: dict[str, Any]) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def completed_ids(path: str | Path) -> set[str]:
    output = Path(path)
    if not output.exists():
        return set()
    ids: set[str] = set()
    for row in load_jsonl(output):
        issue_id = str(row.get("id", "")).strip()
        if issue_id:
            ids.add(issue_id)
    return ids


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


def chat_content(response: Any) -> str:
    choice = response.choices[0]
    content = choice.message.content
    if isinstance(content, list):
        return "".join(str(part.get("text", "")) if isinstance(part, dict) else str(part) for part in content)
    return str(content or "")


def completion_with_retry(
    *,
    client: Any,
    model: str,
    messages: list[dict[str, str]],
    temperature: float,
    max_tokens: int,
    max_retries: int = 3,
) -> Any:
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }
    import time as _time
    last_error: Exception | None = None

    for _ in range(max(1, max_retries)):
        # 1) try JSON mode first (gpt-5 class models often require this to
        #    return parsed text)
        # 2) fall back to plain chat completion if response_format is rejected.
        for use_json in (True, False):
            attempt_payload = dict(payload)
            if use_json:
                attempt_payload["response_format"] = {"type": "json_object"}

            # Newer chat completion endpoints (including gpt-5 class models)
            # use max_completion_tokens instead of max_tokens.
            for use_completion in (False, True):
                try:
                    call_payload = dict(attempt_payload)
                    if use_completion:
                        call_payload["max_completion_tokens"] = max_tokens
                    else:
                        call_payload["max_tokens"] = max_tokens
                    return client.chat.completions.create(**call_payload)
                except Exception as error:
                    last_error = error
                    try:
                        import openai

                        if isinstance(error, openai.BadRequestError):
                            message = str(error)
                            # If JSON response mode is rejected, retry without it.
                            if "response_format" in message and use_json:
                                break
                            # If max_tokens is unsupported, try max_completion_tokens.
                            if "max_tokens" in message and "max_completion_tokens" in message:
                                continue
                    except Exception:
                        pass
                    _time.sleep(1.0)

    raise RuntimeError(f"Chat completion failed after {max_retries} attempts: {last_error}")


def run_aihubmix(
    *,
    prompt_packet: str | Path,
    output_jsonl: str | Path,
    model: str = "gpt-5.5",
    base_url: str = "https://aihubmix.com/v1",
    api_key: str,
    limit: int = 0,
    temperature: float = 0.0,
    max_tokens: int = 512,
    sleep_seconds: float = 0.0,
    resume: bool = True,
    request_timeout: float = 60.0,
    max_retries: int = 3,
    client: Any | None = None,
) -> dict[str, Any]:
    if not api_key:
        raise ValueError("API key is required; pass it via environment, not code.")
    if client is None:
        import openai

        client = openai.OpenAI(api_key=api_key, base_url=base_url, timeout=request_timeout)

    rows = load_jsonl(prompt_packet)
    if limit > 0:
        rows = rows[:limit]
    done = completed_ids(output_jsonl) if resume else set()
    if not resume and Path(output_jsonl).exists():
        Path(output_jsonl).unlink()

    attempted = 0
    written = 0
    skipped = 0
    for index, row in enumerate(rows, start=1):
        issue_id = str(row["id"])
        if issue_id in done:
            skipped += 1
            continue
        attempted += 1
        response = completion_with_retry(
            client=client,
            model=model,
            messages=row["messages"],
            temperature=temperature,
            max_tokens=max_tokens,
            max_retries=max_retries,
        )
        text = chat_content(response)
        output = normalize_generation(issue_id, text)
        output.update(
            {
                "model": model,
                "base_url": base_url,
                "prompt_packet": str(prompt_packet),
                "row_index": index,
            }
        )
        append_jsonl(output_jsonl, output)
        written += 1
        if sleep_seconds > 0:
            time.sleep(sleep_seconds)

    return {
        "prompt_rows": len(rows),
        "attempted_rows": attempted,
        "written_rows": written,
        "skipped_rows": skipped,
        "output_jsonl": str(output_jsonl),
        "model": model,
        "base_url": base_url,
    }


def read_api_key(*, env_name: str, key_file: str | Path = "") -> str:
    if key_file:
        return Path(key_file).read_text(encoding="utf-8").strip()
    return os.environ.get(env_name, "").strip()


def main() -> None:
    args = parse_args()
    api_key = read_api_key(env_name=args.api_key_env, key_file=args.api_key_file)
    if not api_key:
        raise SystemExit(f"Missing API key. Set {args.api_key_env} or pass --api-key-file.")
    result = run_aihubmix(
        prompt_packet=args.prompt_packet,
        output_jsonl=args.output_jsonl,
        model=args.model,
        base_url=args.base_url,
        api_key=api_key,
        limit=args.limit,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        request_timeout=args.request_timeout,
        max_retries=args.max_retries,
        sleep_seconds=args.sleep_seconds,
        resume=args.resume,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
