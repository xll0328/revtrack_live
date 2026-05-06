from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from revtrack.openreview_api import OpenReviewClient, OpenReviewRequestError, normalize_submission
from revtrack.openreview_tasks import build_issue_candidates


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Probe OpenReview venue accessibility and candidate-extraction quality."
    )
    parser.add_argument("--venue-id", required=True)
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--timeout", type=int, default=8, help="Per-request timeout in seconds.")
    parser.add_argument("--retries", type=int, default=0, help="Probe retry count. Defaults to fast-fail.")
    parser.add_argument("--output-json", help="Optional machine-readable probe report.")
    return parser.parse_args()


def summarize_mode(venue_id: str, mode: str, limit: int, timeout: int, retries: int) -> dict[str, Any]:
    client = OpenReviewClient(
        api_mode=mode,
        request_timeout=timeout,
        retry_total=retries,
        retry_backoff=0.2,
    )
    try:
        notes = client.iter_submissions(venue_id, limit=limit)
    except OpenReviewRequestError as exc:
        return {
            "mode": mode,
            "status": "error",
            "error": str(exc),
            "diagnostics": client.diagnostics,
        }

    normalized = [normalize_submission(note) for note in notes]
    candidate_counts = [len(build_issue_candidates(note)) for note in normalized]
    reply_counts = [len(note.get("replies", [])) for note in normalized]
    non_empty = sum(1 for count in candidate_counts if count > 0)
    return {
        "mode": mode,
        "status": "ok",
        "submissions": len(normalized),
        "submissions_with_candidates": non_empty,
        "issue_candidates": sum(candidate_counts),
        "min_replies": min(reply_counts) if reply_counts else 0,
        "max_replies": max(reply_counts) if reply_counts else 0,
        "candidate_rate": non_empty / len(normalized) if normalized else 0.0,
        "diagnostics": client.diagnostics,
    }


def main() -> None:
    args = parse_args()
    report = {
        "venue_id": args.venue_id,
        "limit": args.limit,
        "timeout": args.timeout,
        "retries": args.retries,
        "modes": [
            summarize_mode(args.venue_id, mode, args.limit, args.timeout, args.retries)
            for mode in ["v2-notes", "v2-search", "v1-notes"]
        ],
    }
    text = json.dumps(report, indent=2, sort_keys=True)
    print(text)
    if args.output_json:
        output_path = Path(args.output_json)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
