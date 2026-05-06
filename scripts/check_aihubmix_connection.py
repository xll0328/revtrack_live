from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check AIHubMix/OpenAI-compatible Chat Completions connectivity.")
    parser.add_argument("--model", default="gpt-5.5")
    parser.add_argument("--base-url", default="https://aihubmix.com/v1")
    parser.add_argument("--api-key-env", default="AIHUBMIX_API_KEY")
    parser.add_argument("--api-key-file", default="")
    return parser.parse_args()


def read_api_key(*, env_name: str, key_file: str = "") -> str:
    if key_file:
        return Path(key_file).read_text(encoding="utf-8").strip()
    return os.environ.get(env_name, "").strip()


def run_probe_completion(client, model: str, temperature: float = 0) -> str:
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
        "temperature": temperature,
    }

    try:
        response = client.chat.completions.create(
            **payload,
            max_tokens=16,
        )
    except Exception as error:
        # Some newer OpenAI-compatible models require the newer parameter.
        try:
            import openai

            if isinstance(error, openai.BadRequestError):
                response = client.chat.completions.create(
                    **payload,
                    max_completion_tokens=16,
                )
            else:
                raise
        except Exception:
            raise error

    content = str(response.choices[0].message.content or "").strip()
    return content


def main() -> None:
    args = parse_args()
    api_key = read_api_key(env_name=args.api_key_env, key_file=args.api_key_file)
    if not api_key:
        raise SystemExit(f"Missing API key. Set {args.api_key_env} or pass --api-key-file.")

    import openai

    client = openai.OpenAI(api_key=api_key, base_url=args.base_url)
    content = run_probe_completion(client=client, model=args.model, temperature=0)
    print(
        json.dumps(
            {
                "status": "ok",
                "model": args.model,
                "base_url": args.base_url,
                "response_preview": content[:80],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
