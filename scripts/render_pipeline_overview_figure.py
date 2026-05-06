from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "outputs/day1/paper_assets/figure_pipeline_overview.pdf"
DEFAULT_PAPER_OUTPUT = ROOT / "paper/figures/figure_pipeline_overview.pdf"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a pipeline overview figure for RevTrack.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--paper-output", default=str(DEFAULT_PAPER_OUTPUT))
    parser.add_argument("--dpi", type=int, default=300)
    return parser.parse_args()


def add_box(
    ax: plt.Axes,
    *,
    x: float,
    y: float,
    w: float,
    h: float,
    title: str,
    subtitle: str,
    face: str,
    edge: str = "#1f2937",
) -> None:
    box = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.012,rounding_size=0.03",
        linewidth=1.2,
        edgecolor=edge,
        facecolor=face,
    )
    ax.add_patch(box)
    ax.text(x + 0.02, y + h - 0.05, title, fontsize=10.5, fontweight="bold", va="top", ha="left", color="#111827")
    ax.text(
        x + 0.02,
        y + h - 0.11,
        subtitle,
        fontsize=8.8,
        va="top",
        ha="left",
        color="#1f2937",
        wrap=True,
    )


def add_arrow(ax: plt.Axes, x0: float, y0: float, x1: float, y1: float) -> None:
    arrow = FancyArrowPatch(
        (x0, y0),
        (x1, y1),
        arrowstyle="-|>",
        mutation_scale=12,
        linewidth=1.2,
        color="#374151",
        connectionstyle="arc3,rad=0.0",
    )
    ax.add_patch(arrow)


def draw(path: Path, dpi: int) -> None:
    fig, ax = plt.subplots(figsize=(12.8, 4.8), dpi=dpi)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.text(
        0.01,
        0.97,
        "RevTrack Pipeline: From OpenReview Threads to Auditable Claims",
        fontsize=14,
        fontweight="bold",
        va="top",
        ha="left",
        color="#111827",
    )
    ax.text(
        0.01,
        0.92,
        "Two evidence lanes are tracked separately: disagreement-focused active frontiers and broader random/stratified slices.",
        fontsize=9.3,
        va="top",
        ha="left",
        color="#374151",
    )

    # Top row (construction + gates)
    add_box(
        ax,
        x=0.02,
        y=0.58,
        w=0.18,
        h=0.26,
        title="1) Collection",
        subtitle="Collect OpenReview submissions and discussions by venue/year.",
        face="#dbeafe",
    )
    add_box(
        ax,
        x=0.23,
        y=0.58,
        w=0.18,
        h=0.26,
        title="2) Issue Extraction",
        subtitle="Extract concern-response-revision triples at issue level.",
        face="#e0f2fe",
    )
    add_box(
        ax,
        x=0.44,
        y=0.58,
        w=0.18,
        h=0.26,
        title="3) Candidate Pool Gates",
        subtitle="Check completeness, duplicates, and disagreement signal.",
        face="#dcfce7",
    )
    add_box(
        ax,
        x=0.65,
        y=0.58,
        w=0.16,
        h=0.26,
        title="4) Slice Routing",
        subtitle="Route to active-frontier lane or random/stratified lane.",
        face="#fef3c7",
    )
    add_box(
        ax,
        x=0.83,
        y=0.58,
        w=0.15,
        h=0.26,
        title="5) Packet Build",
        subtitle="Create blind/key/audit sheets and HTML validation packet.",
        face="#fee2e2",
    )

    # Bottom row (validation + claims)
    add_box(
        ax,
        x=0.10,
        y=0.18,
        w=0.25,
        h=0.25,
        title="6) Human Validation",
        subtitle="Standard single-user labeling with explicit evidence span + notes.",
        face="#ede9fe",
    )
    add_box(
        ax,
        x=0.40,
        y=0.18,
        w=0.25,
        h=0.25,
        title="7) Transfer + Failure Analysis",
        subtitle="Model evaluation, per-label recovery, confusion/failure taxonomy.",
        face="#f5f3ff",
    )
    add_box(
        ax,
        x=0.70,
        y=0.18,
        w=0.28,
        h=0.25,
        title="8) Claim Governance",
        subtitle="Packet audits + readiness audit + claim ledger boundaries (not IAA / not prevalence).",
        face="#ecfeff",
    )

    # Flow arrows
    add_arrow(ax, 0.20, 0.71, 0.23, 0.71)
    add_arrow(ax, 0.41, 0.71, 0.44, 0.71)
    add_arrow(ax, 0.62, 0.71, 0.65, 0.71)
    add_arrow(ax, 0.81, 0.71, 0.83, 0.71)
    add_arrow(ax, 0.905, 0.58, 0.225, 0.43)
    add_arrow(ax, 0.225, 0.43, 0.225, 0.43)
    add_arrow(ax, 0.35, 0.305, 0.40, 0.305)
    add_arrow(ax, 0.65, 0.305, 0.70, 0.305)

    # Lane annotations
    ax.text(0.655, 0.52, "Active-frontier lane", fontsize=8.4, color="#92400e", ha="left", va="center")
    ax.text(0.655, 0.49, "Random/stratified lane", fontsize=8.4, color="#0f766e", ha="left", va="center")

    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    args = parse_args()
    output = Path(args.output)
    paper_output = Path(args.paper_output)
    draw(output, args.dpi)
    draw(paper_output, args.dpi)
    print(f"Wrote {output}")
    print(f"Wrote {paper_output}")


if __name__ == "__main__":
    main()
