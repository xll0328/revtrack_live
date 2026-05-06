from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from revtrack.annotation_packet import load_sheet_rows, render_annotation_packet


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a browsable HTML packet for manual issue annotation.")
    parser.add_argument("--sheet", required=True, help="TSV annotation sheet to render.")
    parser.add_argument("--output", required=True, help="Output HTML path.")
    parser.add_argument("--title", default="RevTrack annotation packet")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = load_sheet_rows(args.sheet)
    html = render_annotation_packet(
        rows,
        title=args.title,
        sheet_name=Path(args.sheet).name,
    )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    print(f"Wrote annotation packet with {len(rows)} rows to {output_path}")


if __name__ == "__main__":
    main()
