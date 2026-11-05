"""Bunching of MPDU shares at the Chapter 25A / 59 thresholds.

Run code/03_analysis/01_mpdu_simulation/main.py first.

Panel A: distribution of project MPDU shares (annual-report projects, MPDU
share below 50%), with the 12.5% minimum and the kinks of the bonus schedule
at 15% (22% bonus) and 20% (30% bonus). Because MPDU counts round up, a
project at the 12.5% minimum shows a share slightly above 12.5%.

Panel B: projects with an observed base density (Planning Board resolutions):
density bonus used (total units / base units - 1) against MPDU share, with
the statutory schedule. Projects below the schedule used less bonus than
their MPDUs earn; bonus below zero means building under base density.

Also compares panel B under the earlier gross-area base and the adjusted base
(net area, commercial floor area, unit type): mpdu_bunching_base_methods.

Output: output/figures/mpdu_bunching.pdf,
        output/figures/mpdu_bunching_base_methods.pdf

Usage:
  python 02_bunching_figure.py
"""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code" / "03_analysis" / "01_mpdu_simulation"))
import rules  # noqa: E402

RESULTS = ROOT / "data" / "int" / "03_analysis" / "01_mpdu_simulation_results.csv"
BASE_FILE = ROOT / "data" / "int" / "02_data_cleaning" / "04_base_density_by_plan.csv"
FIG_DIR = ROOT / "output" / "figures"

BLUE, RED, GRAY = "#5b7fa6", "#b87878", "#888888"
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
    "font.size": 12, "axes.labelsize": 12, "xtick.labelsize": 11, "ytick.labelsize": 11,
    "legend.fontsize": 10, "axes.spines.top": False, "axes.spines.right": False,
})

PURPLE = "#7a5c99"
# (share %, label, kind): the required minimum is drawn red dashed, kinks purple dash-dot
KINKS = [(12.5, "12.5% required minimum", "minimum"), (15, "15% kink: 22% bonus", "kink"),
         (20, "20% kink: 30% bonus", "kink")]
STYLE = {"minimum": (RED, "--"), "kink": (PURPLE, "-.")}


def main():
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    d = pd.read_csv(RESULTS)
    d = d[d["actual_sh_mpdu"] < 0.5].copy()
    d["share_pct"] = 100 * d["actual_sh_mpdu"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.6))

    # ---- A. distribution of MPDU shares ----
    top = 30
    x = d["share_pct"].clip(upper=top - 0.01)
    bins = np.arange(5, top + 0.5, 0.5)
    counts, _, _ = ax1.hist(x, bins=bins, color=BLUE, edgecolor="white", linewidth=0.5)
    ymax = counts.max() * 1.18
    ax1.set_ylim(0, ymax)
    for (k, lab, kind), y in zip(KINKS, [1.0, 0.9, 0.8]):
        color, ls = STYLE[kind]
        ax1.axvline(k, color=color, ls=ls, lw=1)
        ax1.text(k + 0.35, ymax * y, lab, color=color, fontsize=9, va="top", ha="left",
                 bbox=dict(facecolor="white", edgecolor="none", pad=1))
    ax1.set_xlabel("MPDU share of total units (%)")
    ax1.set_ylabel("Projects")
    ax1.set_xlim(5, top)
    ax1.set_title(f"A. MPDU share (n = {len(d)} projects; {top}%+ pooled)", loc="left", fontsize=12)

    # ---- B. bonus used vs MPDU share, observed bases ----
    o = d[d["base_source"].eq("resolution")].copy()
    o["bonus_used_pct"] = 100 * (o["actual_units_total"] / o["frontier_base_units"] - 1)
    s = np.linspace(0.125, 0.30, 200)
    ax2.plot(100 * s, 100 * rules.bonus_pct(s), color=RED, lw=1.5, label="Bonus schedule (Chapter 59)")
    ax2.axhline(0, color=GRAY, lw=0.8)
    below = o["bonus_used_pct"] < 0
    ax2.scatter(o.loc[~below, "share_pct"].clip(upper=top), o.loc[~below, "bonus_used_pct"],
                s=22, color=BLUE, alpha=0.8, label="Built at or above base")
    ax2.scatter(o.loc[below, "share_pct"].clip(upper=top), o.loc[below, "bonus_used_pct"].clip(lower=-60),
                s=22, facecolors="none", edgecolors=BLUE, alpha=0.8, label="Built below base (clipped at -60%)")
    for k, _, kind in KINKS:
        color, ls = STYLE[kind]
        ax2.axvline(k, color=color, ls=ls, lw=0.8, alpha=0.5)
    ax2.set_xlim(10, top)
    ax2.set_ylim(-62, 40)
    ax2.set_xlabel("MPDU share of total units (%)")
    ax2.set_ylabel("Density bonus used (%)")
    ax2.set_title(f"B. Bonus used, projects with observed base (n = {len(o)})", loc="left", fontsize=12)
    ax2.legend(frameon=False, loc="lower right")

    fig.tight_layout()
    fig.savefig(FIG_DIR / "mpdu_bunching.pdf")
    print(f"[saved] {FIG_DIR / 'mpdu_bunching.pdf'}")

    compare_base_methods(d)

    # numbers behind panel A
    sh = d["share_pct"]
    print(f"projects: {len(d)}; at 12.5-13.2%: {sh.between(12.5, 13.2).sum()}; "
          f"at 15.0-15.6%: {sh.between(15.0, 15.6).sum()}; 20%+: {(sh >= 20).sum()}")


def compare_base_methods(d):
    """Panel B under the gross-area base (v1) and the adjusted base, side by side.

    Bonus used = 1 / base_ratio - 1 from 04_base_density_by_plan.csv, where
    base_ratio = base units / approved units; each method keeps only bases that
    pass its own consistency check. Output: mpdu_bunching_base_methods.pdf
    """
    b = pd.read_csv(BASE_FILE, dtype={"target_plan": str}).set_index("target_plan")
    first = d["site_plan"].astype(str).str.split("/").str[0].str.strip()
    s = np.linspace(0.125, 0.30, 200)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6), sharey=True)
    for ax, (ratio, ok, title) in zip(axes, [
            ("base_ratio_v1", "base_consistent_v1", "Gross-area base (earlier)"),
            ("base_ratio", "base_consistent", "Adjusted base (net area, commercial FA, unit type)")]):
        keep = first.isin(b.index[b[ok]])
        x = d.loc[keep, "share_pct"].clip(upper=30)
        y = 100 * (1 / first[keep].map(b[ratio]) - 1)
        below = y < -0.5
        ax.plot(100 * s, 100 * rules.bonus_pct(s), color=RED, lw=1.5, label="Bonus schedule (Chapter 59)")
        ax.axhline(0, color=GRAY, lw=0.8)
        ax.scatter(x[~below], y[~below], s=22, color=BLUE, alpha=0.8, label="At or above base")
        ax.scatter(x[below], y[below].clip(lower=-60), s=22, facecolors="none", edgecolors=BLUE, alpha=0.8,
                   label="Below base (clipped at -60%)")
        for k, _, kind in KINKS:
            color, ls = STYLE[kind]
            ax.axvline(k, color=color, ls=ls, lw=0.8, alpha=0.5)
        ax.set_xlim(10, 30)
        ax.set_ylim(-62, 40)
        ax.set_xlabel("MPDU share of total units (%)")
        ax.set_title(f"{title}\nn = {int(keep.sum())}; below base {int(below.sum())}; "
                     f"more than 20% below {int((y < -20).sum())}", loc="left", fontsize=11)
        print(f"{title}: n={int(keep.sum())}, below base {int(below.sum())}, >20% below {int((y < -20).sum())}, "
              f"median bonus {y.median():.1f}%")
    axes[0].set_ylabel("Density bonus used (%)")
    axes[1].legend(frameon=False, loc="lower right")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "mpdu_bunching_base_methods.pdf")
    print(f"[saved] {FIG_DIR / 'mpdu_bunching_base_methods.pdf'}")


if __name__ == "__main__":
    main()
