"""README figures from the committed result tables.

Run from the repo root: python docs/figures/make_figures.py
Writes PNGs next to this file. No network, no quantum simulation.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parent
RESULTS = OUT.parents[1] / "results"

SURFACE = "#fcfcfb"
TEXT = "#0b0b0b"
TEXT_2 = "#52514e"
GRID = "#e4e3df"
NEUTRAL = "#a3a29c"
ETF = "#2a78d6"  # categorical slot 1
STOCK = "#eb6834"  # categorical slot 2
QUANTUM = "#6250d6"  # categorical slot 7
DEVICE = "#e34948"  # categorical slot 8

plt.rcParams.update({
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
    "axes.edgecolor": GRID,
    "axes.labelcolor": TEXT_2,
    "axes.titlecolor": TEXT,
    "axes.titlesize": 12,
    "axes.titleweight": "bold",
    "axes.titlelocation": "left",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "xtick.color": TEXT_2,
    "ytick.color": TEXT_2,
    "font.size": 10,
    "legend.frameon": False,
})


def style_grid(ax, axis="x"):
    ax.grid(axis=axis, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(length=0)


def landscape():
    orig = pd.read_csv(RESULTS / "landscape_n16_k5.csv")
    orig = orig[orig.lam == 3.0].n_local_opt
    ls = pd.read_csv(RESULTS / "longshort_landscape.csv")
    ls = ls[(ls.universe == "ETFs") & (ls.n == 16)].n_local_opt

    top = int(max(orig.max(), ls.max()))
    bins = np.arange(0.5, top + 1.5)
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.2), sharey=True, sharex=True)
    panels = [
        (axes[0], orig, NEUTRAL, "Original: pick 5 of 16 ETFs (λ = 3)"),
        (axes[1], ls, ETF, "Long–short book: 8 long / 8 short ETFs"),
    ]
    for ax, data, color, title in panels:
        ax.hist(data, bins=bins, color=color, edgecolor=SURFACE, linewidth=2)
        ax.set_title(title, fontsize=10.5)
        ax.set_xlabel("Local optima under single swaps")
        style_grid(ax, "y")
        ax.text(0.97, 0.9, f"median {np.median(data):g}", transform=ax.transAxes,
                ha="right", color=TEXT_2)
    axes[0].set_ylabel("Windows (of 64)")
    fig.suptitle("The original problem has one peak; the long–short book is rugged",
                 x=0.01, ha="left", fontweight="bold", color=TEXT)
    fig.tight_layout()
    fig.savefig(OUT / "landscape.png", dpi=200)
    plt.close(fig)


METHOD_LABELS = {
    "locally balanced": "Locally balanced swaps (classical, many evals/step)",
    "complete+full": "Quantum: complete mixer + full phase",
    "multi-swap": "Multi-swap (classical)",
    "ordered ring+full": "Quantum: ordered ring + full phase",
    "ordered ring+ring phase (hw)": "Quantum: ordered ring + ring phase (hardware-cheap)",
    "ring+full": "Quantum: ring + full phase",
    "ring+linear (hw target)": "Quantum: ring + linear phase",
}


def mixing():
    d = pd.read_csv(RESULTS / "longshort_fair_tuning_n12.csv")
    med = {}
    for uni, du in d.groupby("universe"):
        train, test = du[du.w % 2 == 0], du[du.w % 2 == 1]
        chosen = train.groupby(["method", "setting"]).ratio.median().groupby(level=0).idxmax()
        med[uni] = {m: test[(test.method == m) & (test.setting == s)].ratio.median()
                    for m, s in chosen}
    order = sorted(METHOD_LABELS, key=lambda m: med["ETFs"][m])
    y = np.arange(len(order))
    h = 0.38
    fig, ax = plt.subplots(figsize=(9, 4.2))
    ax.barh(y + h / 2, [med["ETFs"][m] for m in order], height=h - 0.04, color=ETF, label="ETFs")
    ax.barh(y - h / 2, [med["stocks"][m] for m in order], height=h - 0.04, color=STOCK,
            label="Stocks")
    ax.axvline(1, color=TEXT, linewidth=1)
    ax.text(1.03, len(order) - 0.45, "single swap = 1", color=TEXT_2, va="bottom")
    ax.set_yticks(y, [METHOD_LABELS[m] for m in order])
    for lbl in ax.get_yticklabels():
        if lbl.get_text().startswith("Quantum: complete"):
            lbl.set_fontweight("bold")
            lbl.set_color(TEXT)
    ax.set_xlabel("Spectral-gap ratio vs single swap (median, 32 held-out windows)")
    fig.suptitle("In simulation, the score-informed circuit mixes faster than multi-swap",
                 x=0.01, ha="left", fontweight="bold", color=TEXT)
    style_grid(ax, "x")
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(OUT / "mixing.png", dpi=200)
    plt.close(fig)


def race():
    d = pd.read_csv(RESULTS / "longshort_race_n16.csv")
    methods = ["single swap", "quantum complete+full", "parallel tempering", "multi-swap"]
    found = set(d.method.unique())
    methods = [m for m in methods if m in found] or sorted(found)
    rows = d[d.method.isin(methods)].groupby(["method", "universe"]).attempts.median().unstack()
    rows = rows.loc[methods]
    y = np.arange(len(methods))[::-1]
    h = 0.38
    fig, ax = plt.subplots(figsize=(9, 3))
    ax.barh(y + h / 2, rows["ETFs"], height=h - 0.04, color=ETF, label="ETFs")
    ax.barh(y - h / 2, rows["stocks"], height=h - 0.04, color=STOCK, label="Stocks")
    ax.set_yticks(y, [m.capitalize() for m in methods])
    ax.set_xlabel("Median attempts to first reach the best book (8 long / 8 short)")
    fig.suptitle("But plain single swaps still reach the best book first",
                 x=0.01, ha="left", fontweight="bold", color=TEXT)
    style_grid(ax, "x")
    ax.legend(loc="lower right", bbox_to_anchor=(1, 1.0), ncol=2)
    fig.tight_layout()
    fig.savefig(OUT / "race.png", dpi=200)
    plt.close(fig)


def hardware():
    # Spectral gaps from experiments/hardware/README.md (python -m qemcmc.hardware analyze).
    labels = ["Ideal circuit", "Circuit, shot noise only", "Single-swap Metropolis",
              "IBM hardware (ibm_marrakesh)"]
    gaps = [0.090, 0.088, 0.061, 0.043]
    colors = [QUANTUM, QUANTUM, NEUTRAL, DEVICE]
    y = np.arange(len(labels))[::-1]
    fig, ax = plt.subplots(figsize=(9, 2.8))
    ax.barh(y, gaps, height=0.6, color=colors)
    for yi, g in zip(y, gaps):
        ax.text(g + 0.001, yi, f"{g:.3f}", va="center", color=TEXT_2)
    ax.set_yticks(y, labels)
    ax.set_xlabel("Spectral gap of the Metropolis chain (higher mixes faster)")
    fig.suptitle("On today's hardware, noise erases the gain (4 long / 4 short, 35 books)",
                 x=0.01, ha="left", fontweight="bold", color=TEXT)
    style_grid(ax, "x")
    fig.tight_layout()
    fig.savefig(OUT / "hardware.png", dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    landscape()
    mixing()
    race()
    hardware()
    print("wrote", sorted(p.name for p in OUT.glob("*.png")))
