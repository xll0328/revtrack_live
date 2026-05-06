from __future__ import annotations

import csv
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "render_figure1_revision_tracking.py"
SPEC = importlib.util.spec_from_file_location("render_figure1_revision_tracking", SCRIPT)
assert SPEC is not None
assert SPEC.loader is not None
render_figure1_revision_tracking = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(render_figure1_revision_tracking)


def write_tsv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def test_render_figure1_uses_selected_issue(tmp_path: Path) -> None:
    signoff = tmp_path / "signoff.tsv"
    output = tmp_path / "figure.svg"
    write_tsv(
        signoff,
        [
            {
                "issue_id": "case1",
                "paper_title": "A Paper About Efficient Revision",
            }
        ],
        ["issue_id", "paper_title"],
    )

    row = render_figure1_revision_tracking.load_row(signoff, "case1")
    output.write_text(render_figure1_revision_tracking.render(row), encoding="utf-8")

    svg = output.read_text(encoding="utf-8")
    assert "A Paper About Efficient Revision" in svg
    assert "RevTrack evaluates whether a scientific criticism still holds" in svg
    assert "RevTrack label: fixed" in svg
