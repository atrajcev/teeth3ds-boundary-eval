from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

LABELS = {
    11: "11 (incisor)",
    16: "16 (molar)",
}  # can extend to more teeth, add here and an offset for it below
OFFSETS = {11: (6, -14), 16: (6, 6)}  # shift the numbers around the dots on the plot
OUT = Path("docs/images/dice_vs_boundary.png")


"""Plot Dice vs p95 boundary shift for the Phase 1 ring sweep."""

if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(6, 4))
    for tooth in LABELS:
        label, offset = LABELS[tooth], OFFSETS[tooth]
        df = pd.read_csv(f"results/boundary_stats_{tooth}.csv")
        ax.plot(df.mm_p95_shift, df.dice_score, marker="o", label=label)
        # number each point with how many rings were peeled
        for x, y, rings in zip(df.mm_p95_shift, df.dice_score, df.peeled_rings):
            ax.annotate(
                str(rings),
                (x, y),
                textcoords="offset points",
                xytext=offset,
                fontsize=8,
            )

    ax.axhline(0.9, ls="--", color="grey", lw=1)  # Dice stays above 0.9
    ax.set_xlabel("p95 boundary shift (mm)")
    ax.set_ylabel("Dice")
    ax.set_title("Dice stays above 0.9 while the edge moves")
    ax.legend(title="numbers = rings peeled")
    ax.grid(alpha=0.3)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=150, bbox_inches="tight")
    print(f"Saved {OUT}")
