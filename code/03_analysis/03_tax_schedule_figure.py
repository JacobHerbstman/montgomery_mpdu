"""Average and marginal tax rates of the MPDU schedule (analog of San Diego
code/02_simulation/frontier_tax_schedule.py).

Run code/03_analysis/01_mpdu_simulation/main.py first.

Definitions follow San Diego, on each project's frontier R(h) (fewest legal
MPDUs at each total h):
  ATR(h) = 1 - R(h) / (r_m h)
  MTR(h) = 1 - [R(h+1) - R(h)] / r_m          (adjacent frontier points)
With one controlled-rent tier these reduce to
  ATR = (1 - k) x MPDU share,   MTR = (1 - k) x extra MPDUs per extra unit,
where k = MPDU rent / market rent. The schedule sets the second factor; k
depends on the standardized market rent (rules.RENT_MKT_STANDARD), so tax
levels are illustrative. Unlike San Diego, the MPDU tax is positive at base
density: 12.5% (15% in high-income areas) of units are MPDUs from the first
unit, and the bonus only adds to that.

Regimes: every project's frontier is built under the 12.5% minimum (the rule
applied in the simulation) and, for comparison, under the 15% minimum, with
each project's own base units, AMI and market rent.

Panels
  A  ATR vs density bonus above base: 20 quantile bins of pooled frontier
     points (h >= base, non-fully-affordable projects, bonus up to 45%),
     with the continuous schedule (no rounding) as a line.
  B  MTR vs density bonus, same bins; line = continuous schedule.
  C  One project's R(h) under both minimums, the all-market line r_m h, base
     units, and the observed choice.

Output: output/figures/mpdu_tax_schedule.pdf and
        output/tables/mpdu_tax_schedule_bins.csv

Usage:
  python 03_tax_schedule_figure.py
"""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code" / "03_analysis" / "01_mpdu_simulation"))
import rules  # noqa: E402

RESULTS = ROOT / "data" / "int" / "03_analysis" / "01_mpdu_simulation_results.csv"
FIG_DIR = ROOT / "output" / "figures"
TAB_DIR = ROOT / "output" / "tables"

N_BINS = 20
MAX_BONUS = 45     # % bonus shown: MPDU shares up to ~35%; the schedule continues to 110% at 100% MPDUs
EXAMPLE_SITE_PLAN = "820120120"   # 7770 Norfolk Avenue: 200 rental units, base 164, 15% MPDUs, 22% bonus
REGIMES = {"12.5% minimum": (0.125, "#5b7fa6", "o"), "15% minimum": (0.15, "#b87878", "D")}
GRAY = "#888888"

plt.rcParams.update({
    "font.family": "serif", "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
    "font.size": 12, "axes.labelsize": 12, "xtick.labelsize": 11, "ytick.labelsize": 11,
    "legend.fontsize": 10, "legend.frameon": False,
    "axes.spines.top": False, "axes.spines.right": False,
})
PCT = mticker.FuncFormatter(lambda v, _: f"{v:.0f}%")


def frontier(base, min_share, ami, rent_mkt):
    f = rules.calculate_frontier(int(base), min_share=min_share, ami=ami, rent_mkt=rent_mkt)
    f["mtr"] = 1 - f["rent_roll"].diff(-1).mul(-1) / (rent_mkt * f["units_total"].diff(-1).mul(-1))
    return f


def continuous(min_share, k, max_bonus):
    """Schedule without rounding: share(b) = max(min, share_for_bonus(b)),
    MPDUs per base unit m(b) = share(b) (1 + b); ATR = (1-k) share,
    MTR = (1-k) dm/db."""
    b = np.linspace(0, max_bonus, 800)
    share = np.maximum(min_share, rules.share_for_bonus(b))
    m = share * (1 + b)
    mtr = np.gradient(m, b)
    return 100 * b, 100 * (1 - k) * share, 100 * (1 - k) * mtr


def binscatter(df, y, n_bins=N_BINS):
    df = df[np.isfinite(df[y])].copy()
    df["_bin"] = pd.qcut(df["pct_bonus_pct"], n_bins, labels=False, duplicates="drop")
    return df.groupby("_bin").agg(x=("pct_bonus_pct", "median"), y=(y, "mean"), n=(y, "size")).reset_index()


def main():
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    TAB_DIR.mkdir(parents=True, exist_ok=True)
    d = pd.read_csv(RESULTS, dtype={"site_plan": str})
    d = d[~d["is_fully_affordable"]]

    # ---- pooled frontiers under both minimums ----
    parts = []
    for r in d.itertuples(index=False):
        for lab, (ms, _, _) in REGIMES.items():
            f = frontier(r.frontier_base_units, ms, r.ami, r.rent_mkt)
            f["regime"], f["id"] = lab, r.id
            parts.append(f)
    env = pd.concat(parts, ignore_index=True)
    env["pct_bonus_pct"] = 100 * env["pct_bonus"]
    env["atr_pct"] = 100 * env["atr"]
    env["mtr_pct"] = 100 * env["mtr"]
    env = env[env["pct_bonus_pct"] <= MAX_BONUS]
    k_med = float((rules.mpdu_rent(d["ami"], d["rent_mkt"]) / d["rent_mkt"]).median())
    xmax = float(env["pct_bonus_pct"].max())

    bins = []
    fig, (ax_a, ax_m, ax_r) = plt.subplots(1, 3, figsize=(17, 5.4))
    for lab, (ms, color, marker) in REGIMES.items():
        e = env[env["regime"] == lab]
        ba, bm = binscatter(e, "atr_pct"), binscatter(e, "mtr_pct")
        ax_a.scatter(ba["x"], ba["y"], s=40, marker=marker, color=color, alpha=0.85, label=lab, zorder=3)
        ax_m.scatter(bm["x"], bm["y"], s=40, marker=marker, color=color, alpha=0.85, label=lab, zorder=3)
        bx, catr, cmtr = continuous(ms, k_med, xmax / 100)
        ax_a.plot(bx, catr, color=color, lw=1, alpha=0.6)
        ax_m.plot(bx, cmtr, color=color, lw=1, alpha=0.6)
        bins += [ba.assign(regime=lab, measure="atr"), bm.assign(regime=lab, measure="mtr")]

    for ax, title in [(ax_a, "A. Average tax rate"), (ax_m, "B. Marginal tax rate")]:
        for kink, lab in [(22, "22%: 15% MPDUs"), (30, "30%: 20% MPDUs")]:
            ax.axvline(kink, color=GRAY, ls=":", lw=0.8)
            ax.text(kink - 0.6, 0.98, lab, transform=ax.get_xaxis_transform(), color=GRAY, fontsize=9,
                    va="top", ha="right", rotation=90)
        ax.xaxis.set_major_formatter(PCT)
        ax.yaxis.set_major_formatter(PCT)
        ax.set_xlabel("Density bonus above base")
        ax.set_xlim(0, xmax)
        ax.set_ylim(bottom=0)
        ax.set_title(title, loc="left", fontsize=12)
    ax_a.yaxis.set_major_locator(mticker.MultipleLocator(5))
    ax_a.legend(loc="center left")
    ax_m.text(0.98, 0.02, f"points: pooled frontiers, {N_BINS} quantile bins\n"
                          f"lines: continuous schedule, k = {k_med:.2f}",
              transform=ax_m.transAxes, ha="right", va="bottom", fontsize=9, color=GRAY)

    # ---- C. example project ----
    row = d[d["site_plan"] == EXAMPLE_SITE_PLAN].iloc[0]
    base, h_act, m_act = int(row["frontier_base_units"]), int(row["actual_units_total"]), int(row["actual_units_mpdu"])
    rm, ami = float(row["rent_mkt"]), float(row["ami"])
    to_m = 12 / 1e6
    lo, hi = base - 5, int(base * (1 + MAX_BONUS / 100)) + 5
    hh = np.linspace(lo, hi, 200)
    ax_r.plot(hh, rm * hh * to_m, color=GRAY, ls="--", lw=1.2, label=r"All-market ($r_m \times h$)")
    for lab, (ms, color, _) in REGIMES.items():
        f = rules.calculate_frontier(base, min_share=ms, ami=ami, rent_mkt=rm)
        f = f[f["units_total"] <= hi]
        ax_r.plot(f["units_total"], f["rent_roll"] * to_m, color=color, lw=1.8, label=f"$R(h)$, {lab}")
    r_act = (rm * (h_act - m_act) + rules.mpdu_rent(ami, rm) * m_act) * to_m
    ax_r.scatter([h_act], [r_act], s=90, color=REGIMES["12.5% minimum"][1], edgecolors="black", zorder=5)
    ax_r.annotate(f"Chosen: {h_act} units,\n{m_act} MPDUs ({100 * m_act / h_act:.0f}%)", xy=(h_act, r_act),
                  xytext=(-12, 14), textcoords="offset points", ha="right", fontsize=10,
                  arrowprops=dict(arrowstyle="-", lw=0.7))
    ax_r.axvline(base, color=GRAY, ls=":", lw=0.9)
    ax_r.text(base + 0.5, 0.02, f"Base ({base})", transform=ax_r.get_xaxis_transform(), color=GRAY, fontsize=10)
    ax_r.set_xlim(lo, hi)
    ax_r.set_xlabel("Total units")
    ax_r.set_title(f"C. Annual rent roll ($ millions): {row['project_name']}", loc="left", fontsize=12)
    ax_r.legend(loc="upper left")

    fig.tight_layout()
    fig.savefig(FIG_DIR / "mpdu_tax_schedule.pdf")
    out = pd.concat(bins, ignore_index=True)
    out.to_csv(TAB_DIR / "mpdu_tax_schedule_bins.csv", index=False)
    print(f"[saved] {FIG_DIR / 'mpdu_tax_schedule.pdf'}; {TAB_DIR / 'mpdu_tax_schedule_bins.csv'}")
    print(f"projects: {d['id'].nunique()}; frontier points: {len(env):,}; median k = {k_med:.3f}")
    for lab in REGIMES:
        a = out[(out.regime == lab) & (out.measure == "atr")]
        print(f"  {lab}: ATR at base {a.y.iloc[0]:.1f}% -> at ~22% bonus "
              f"{np.interp(22, a.x, a.y):.1f}%; max bin {a.y.max():.1f}%")


if __name__ == "__main__":
    main()
