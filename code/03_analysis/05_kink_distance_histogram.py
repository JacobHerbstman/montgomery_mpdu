"""Distance of the MPDU share from the 15% kink, pooled across minimum-share regimes.

Run code/03_analysis/01_mpdu_simulation/main.py first.

The Chapter 59 bonus schedule (rules.bonus_pct) buys 0.88% bonus per 0.1% of MPDUs
from 12.5% to 15%, then only 0.16% per 0.1% to 20% (0.1% beyond). The 15% kink is
the large drop in the marginal bonus (and, under the pre-2014 code, the bonus cap);
the 20% kink is minor and is only marked. MPDU shares are of total units, as in the
statute, so the kink sits at 15% for every project.
  top:    s - 15, percentage points (e.g. 12.5% = -2.5)
  bottom: ln(s) - ln(15)            (e.g. 12.5% = ln(12.5 / 15) = -0.18)
Bars are stacked by regime: the required minimum is 12.5% in most of the county and
15% in high-income planning areas (07_site_plan_regime.py), where 15% is both the
minimum and the kink. Values beyond the axis are piled in the end bins (fully
affordable projects at the right). Every project has MPDUs, so s > 0 throughout.

Sample: every project in the simulation results (annual reports and building
permits), as in 04_kink_bunching_figure.py.

Output: output/figures/mpdu_kink_distance_histogram.pdf

Usage:
  python 05_kink_distance_histogram.py
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "data" / "int" / "03_analysis" / "01_mpdu_simulation_results.csv"
FIG_DIR = ROOT / "output" / "figures"

BLUE, RED, DARK, PURPLE = "#5b7fa6", "#b04a4a", "#444444", "#7a5c99"
KINK, KINK2 = 15.0, 20.0
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
    "font.size": 12, "axes.labelsize": 12, "xtick.labelsize": 11, "ytick.labelsize": 11,
    "legend.fontsize": 10, "axes.spines.top": False, "axes.spines.right": False,
})
# min_share: label, color
REGIMES = {0.125: ("12.5% required minimum", BLUE), 0.15: ("15% required minimum (high-income areas)", RED)}
PANELS = [  # column, axis range, bin width, x label, position of the 12.5% minimum and the 20% kink
    ("diff", (-12.0, 25.0), 0.25, "MPDU share of total units minus 15% kink, percentage points",
     (12.5 - KINK, KINK2 - KINK)),
    ("logdiff", (-1.0, 1.0), 0.0125, "Log distance from kink: ln(MPDU share) - ln(15%)",
     (np.log(12.5 / KINK), np.log(KINK2 / KINK))),
]


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    d = pd.read_csv(RESULTS)
    d["s"] = 100 * d["actual_sh_mpdu"]
    assert (d["s"] > 0).all() and d["min_share"].isin(list(REGIMES)).all()
    d["diff"] = d["s"] - KINK
    d["logdiff"] = np.log(d["s"] / KINK)

    fig, axes = plt.subplots(2, 1, figsize=(10, 7.4))
    for ax, (col, (lo, hi), w, xlabel, (mn, k2)) in zip(axes, PANELS):
        x = d[col].clip(lo + 1e-9, hi - 1e-9)
        out_lo, out_hi = int((d[col] < lo).sum()), int((d[col] > hi).sum())
        bins = np.arange(lo, hi + w / 2, w)
        counts, _, _ = ax.hist([x[d["min_share"].eq(r)] for r in REGIMES], bins=bins, stacked=True,
                               color=[c for _, c in REGIMES.values()], edgecolor="white", linewidth=0.3,
                               label=[f"{lab}, n = {int(d['min_share'].eq(r).sum())}"
                                      for r, (lab, _) in REGIMES.items()])
        ymax = max(counts[-1].max(), 1) * 1.15
        ax.set_ylim(0, ymax)
        ax.set_xlim(lo, hi)
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        for pos, lab, color, ls in [(0, "15% kink", DARK, "--"), (mn, "12.5% minimum", RED, ":"),
                                    (k2, "20% kink", PURPLE, "-.")]:
            ax.axvline(pos, color=color, ls=ls, lw=0.9)
            # the minimum's label goes left of its line so it doesn't run into the kink's
            left = lab.endswith("minimum")
            ax.text(pos + (-1 if left else 1) * 0.005 * (hi - lo), ymax * 0.97, lab, color=color, fontsize=9,
                    va="top", ha="right" if left else "left")
        notes = [f"{out_lo} below {lo:g} in first bin"] * bool(out_lo) + [f"{out_hi} above {hi:g} in last bin"] * bool(out_hi)
        ax.set_title(f"n = {len(d)}" + (f" ({'; '.join(notes)})" if notes else ""), loc="left", fontsize=11)
        ax.set_xlabel(xlabel)
        ax.set_ylabel("Projects")
        ax.legend(frameon=False, loc="center right", fontsize=9)
        print(f"{col}: below {lo:g}: {out_lo}, above {hi:g}: {out_hi}; in the first bin at or above the kink "
              f"[0, {w:g}): {int(d[col].between(0, w - 1e-12).sum())}; in the bin below: "
              f"{int(d[col].between(-w, -1e-12).sum())}")
    fig.tight_layout()
    out = FIG_DIR / "mpdu_kink_distance_histogram.pdf"
    fig.savefig(out)
    plt.close(fig)
    print(f"[saved] {out}")


if __name__ == "__main__":
    main()
