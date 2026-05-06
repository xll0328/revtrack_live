from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from revtrack.openreview_api import DEFAULT_API_MODE, OpenReviewClient, normalize_submission


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect public OpenReview submissions for RevTrack.")
    parser.add_argument("--venue-id", required=True, help="Example: ICLR.cc/2024/Conference")
    parser.add_argument("--output", required=True)
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument(
        "--api-mode",
        choices=["auto", "v2-notes", "v2-search", "v1-notes"],
        default=DEFAULT_API_MODE,
        help="OpenReview API strategy. Defaults to v2-notes; auto tries fallbacks.",
    )
    parser.add_argument("--timeout", type=int, default=30, help="Per-request timeout in seconds.")
    parser.add_argument("--retries", type=int, default=5, help="Request retry count.")
    parser.add_argument(
        "--disable-direct-fallback",
        action="store_true",
        help="Disable no-proxy retry after proxy failures.",
    )
    parser.add_argument("--diagnostics-json", help="Optional structured diagnostics output.")
    parser.add_argument("--download-pdfs-dir", help="Optional directory for downloading current PDFs.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    client = OpenReviewClient(
        api_mode=args.api_mode,
        request_timeout=args.timeout,
        retry_total=args.retries,
        fallback_without_proxy=not args.disable_direct_fallback,
    )
    notes = client.iter_submissions(args.venue_id, limit=args.limit)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as handle:
        for note in notes:
            normalized = normalize_submission(note)
            pdf_path = normalized.get("pdf_path")
            if args.download_pdfs_dir and pdf_path:
                filename = f"{normalized['id']}.pdf"
                local_pdf = Path(args.download_pdfs_dir) / filename
                client.download_pdf(str(pdf_path), local_pdf)
                normalized["downloaded_pdf"] = str(local_pdf)
            handle.write(json.dumps(normalized, ensure_ascii=False) + "\n")

    print(f"Wrote {len(notes)} submissions to {output_path}")

    if args.diagnostics_json:
        diagnostics: dict[str, Any] = {
            "venue_id": args.venue_id,
            "api_mode": args.api_mode,
            "limit": args.limit,
            "submissions": len(notes),
            "output": str(output_path),
            "diagnostics": client.diagnostics,
        }
        diagnostics_path = Path(args.diagnostics_json)
        diagnostics_path.parent.mkdir(parents=True, exist_ok=True)
        diagnostics_path.write_text(
            json.dumps(diagnostics, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"Wrote OpenReview diagnostics to {diagnostics_path}")


if __name__ == "__main__":
    main()
