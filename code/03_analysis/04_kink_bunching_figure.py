"""Bunching at the kinks of the MPDU bonus schedule, raw data.

Run code/03_analysis/01_mpdu_simulation/main.py first.

The Chapter 59 bonus schedule (rules.bonus_pct) buys 0.88% bonus density per
0.1% of MPDUs between 12.5% and 15%, then 0.16% per 0.1% up to 20%, then 0.1%
per 0.1%. Its kinks are at 15% and 20% MPDU shares; 12.5% is the minimum
requirement, a different margin. A developer whose marginal MPDU becomes much
less rewarding above a kink should stop exactly at it.

Sample: every project (annual reports and building permits), with no
restrictions. That includes
fully affordable projects and the projects whose required minimum is already
15% (high-income planning areas, from 07_site_plan_regime.py), for which 15%
is the requirement rather than a kink.

Figure: histogram of the MPDU share, 0.25-point bins (wider bins in the
broken-off panel for shares above MAIN_MAX), full range, stacked:
red (bottom) = projects exactly at their own required minimum (MPDUs equal
ceil(min_share x total units), min_share 12.5% or 15%), blue = the rest.

Table: for each kink, projects by MPDUs minus the fewest MPDUs that reach the
kink share, ceil(k x total), in units (0 = exactly at the kink). Integer
rounding puts a project that targets 15% slightly above 15% in share terms;
counting units does not.

VERIFY: the 20% tier dates from the 2014 zoning rewrite. Under the earlier
code the bonus stopped at 22% (15% MPDUs), so 15% was a cap rather than a
kink and there was no 20% kink. Only the offering date is observed, not the
approval date, so the sample is not split by code.

Output: output/figures/mpdu_kink_bunching.pdf and
        output/tables/mpdu_kink_bunching_counts.csv

Usage:
  python 04_kink_bunching_figure.py
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "data" / "int" / "03_analysis" / "01_mpdu_simulation_results.csv"
FIG_DIR = ROOT / "output" / "figures"
TAB_DIR = ROOT / "output" / "tables"

BLUE, RED, GRAY, DARK, PURPLE = "#5b7fa6", "#b04a4a", "#888888", "#444444", "#7a5c99"
KINKS = [0.15, 0.20]
MAIN_MAX = 35          # x-axis break above this share (%), if any project lies beyond

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
    "font.size": 12, "axes.labelsize": 12, "xtick.labelsize": 11, "ytick.labelsize": 11,
    "legend.fontsize": 10, "axes.spines.top": False, "axes.spines.right": False,
})


def units_from_kink(d, k):
    """MPDUs minus the fewest that reach share k."""
    need = np.ceil(k * d["actual_units_total"] - 1e-9)
    return (d["actual_units_mpdu"] - need).astype(int)


def main():
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    TAB_DIR.mkdir(parents=True, exist_ok=True)
    d = pd.read_csv(RESULTS)
    d["share_pct"] = 100 * d["actual_sh_mpdu"]

    hi = np.ceil(d["share_pct"].max()) + 0.25
    bins = np.arange(0, hi, 0.25)
    # at its own minimum (12.5% or 15%): exactly the fewest MPDUs that minimum requires
    d["at_min"] = d["actual_units_mpdu"] == np.ceil(d["min_share"] * d["actual_units_total"] - 1e-9)
    groups = [d.loc[d["at_min"], "share_pct"], d.loc[~d["at_min"], "share_pct"]]
    labels = [f"At its required minimum (n = {d['at_min'].sum()})", f"Other projects (n = {(~d['at_min']).sum()})"]

    # every project is shown; when a few shares sit far out (fully affordable
    # projects), the x-axis is broken so the main range stays readable
    gap = d["share_pct"][d["share_pct"] > MAIN_MAX]
    if len(gap):
        fig, (ax, ax2) = plt.subplots(1, 2, figsize=(10, 4.4), sharey=True,
                                      gridspec_kw={"width_ratios": [7, 1], "wspace": 0.05})
    else:
        fig, ax = plt.subplots(figsize=(10, 4.4))
    axes = [ax, ax2] if len(gap) else [ax]
    counts, _, _ = ax.hist(groups, bins=bins, stacked=True, color=[RED, BLUE], edgecolor="white",
                           linewidth=0.3, label=labels)
    if len(gap):
        # the outer panel can span tens of points: bins of ~1/12 of its range so its bars show
        lo2, hi2 = np.floor(gap.min()) - 1, np.ceil(gap.max()) + 1
        w2 = max(1.0, (hi2 - lo2) / 12)
        ax2.hist(groups, bins=np.arange(lo2, hi2 + w2, w2), stacked=True, color=[RED, BLUE],
                 edgecolor="white", linewidth=0.3)
    ymax = counts[-1].max() * 1.15
    ax.set_ylim(0, ymax)
    # required minimum red dashed, kinks purple dash-dot (15% is also the
    # required minimum in high-income planning areas)
    for k, lab, y, color, ls in [(12.5, "12.5% required minimum", 0.97, RED, "--"),
                                 (15, "15% kink / minimum", 0.89, PURPLE, "-."),
                                 (20, "20% kink", 0.97, PURPLE, "-.")]:
        ax.axvline(k, color=color, ls=ls, lw=0.8)
        # the minimum's label goes left of its line so it doesn't run into 15%
        left = k == 12.5
        ax.text(k - 0.2 if left else k + 0.2, ymax * y, lab, color=color, fontsize=9, va="top",
                ha="right" if left else "left")
    ax.legend(frameon=False, loc="center right")
    ax.set_ylabel("Projects")
    ax.set_title(f"MPDU share, all projects (n = {len(d)})", loc="left", fontsize=12)
    if len(gap):
        ax.set_xlim(0, MAIN_MAX)
        ax2.set_xlim(np.floor(gap.min()) - 1, np.ceil(gap.max()) + 1)
        ax2.spines["left"].set_visible(False)
        ax2.tick_params(axis="y", left=False)
        for a, x in [(ax, 1), (ax2, 0)]:   # break marks
            a.plot([x - 0.01 * (1 if x else -7), x + 0.01 * (1 if x else 7)], [-0.02, 0.02],
                   transform=a.transAxes, color="k", lw=0.8, clip_on=False)
        fig.supxlabel("MPDU share of total units (%)", fontsize=12, y=0.02)
    else:
        ax.set_xlim(0, hi)
        ax.set_xlabel("MPDU share of total units (%)")

    rows = []
    for k in KINKS:
        gaps = units_from_kink(d, k)
        c = gaps.value_counts().reindex(range(gaps.min(), gaps.max() + 1), fill_value=0)
        rows.append(pd.DataFrame({"kink": k, "units_from_kink": c.index, "projects": c.values}))
        near = c.loc[-3:3]
        print(f"{100 * k:g}% kink: at 0 units {c[0]}; mean of -3..-1 and +1..+3: "
              f"{near.drop(0).mean():.1f}; below kink {(gaps < 0).sum()}, at or above {(gaps >= 0).sum()}")

    if len(gap):
        fig.subplots_adjust(left=0.07, right=0.98, bottom=0.14, top=0.92)
    else:
        fig.tight_layout()
    fig.savefig(FIG_DIR / "mpdu_kink_bunching.pdf")
    pd.concat(rows).to_csv(TAB_DIR / "mpdu_kink_bunching_counts.csv", index=False)
    print(f"projects: {len(d)}; MPDU share {d['share_pct'].min():.1f}-{d['share_pct'].max():.1f}%")
    print(f"[saved] {FIG_DIR / 'mpdu_kink_bunching.pdf'}; {TAB_DIR / 'mpdu_kink_bunching_counts.csv'}")


if __name__ == "__main__":
    main()
