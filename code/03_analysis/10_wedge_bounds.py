"""What each project's choice reveals about its wedge on the density limit, in units of the MPDU discount.

Run 08_building_size_bunching.py first.

A project with base B builds N = nB units and owes the fewest MPDUs that make N
legal, s(n)N, where s(n) is the minimum share up to base (and, with a 15%
minimum, up to the bonus that share already earns) and rises along the bonus
schedule above it. The schedule is the one in force when the site plan was
accepted (date_regime):
  old (before 31 Oct 2018)  the Chapter 25A table (struck text in Bill 34-17,
                    sources/law/3_bill_34-17_2018.pdf pp. 19-20): "Up to 1%"
                    bonus needs 12.6% MPDUs, ... "Up to 20%" 14.5%, "Up to 22%"
                    15.0%, nothing above 22%. Its 1% steps are taken as a line,
                    10 points of bonus per point of MPDUs; the last step is a
                    lump (any bonus above 20% needs 15%)
  ZTA 18-06         rules.share_for_bonus: 8.8 points of bonus per point of
                    MPDUs to 22%, then 1.6 to 30%, then 1.0
An MPDU costs the developer d, its
market value minus its controlled value. The MPDUs carried by one more unit are

  MC(n) = s(n) + n s'(n)

and the wedge is what one more permitted unit is worth beyond the MPDUs the
minimum share already charges on it: w = MC - s_min, in units of d. A developer
who chose n reveals (profit maximization only; no elasticity):
  below base        w = 0: the density limit did not bind
  ZTA 18-06
    at base         0 <= w <= MC just above base - s_min (1/8.8 = 0.114 at a
                    12.5% minimum)
    between, above  w = MC(n) - s_min at the observed n, exactly
      22%
    at 22%          MC just below 22% - s_min (1.44/8.8 = 0.164) <= w <= MC just
                    above 22% - s_min (0.79)
  old schedule, positions read in whole units on the steps (old_bounds)
    at base         0 <= w <= 0.10 (the first step)
    between         w = 0.1 (2n - 1), exactly (7001 Arlington, n = 1.176: 0.135)
    at 20%          0.14 (just below 20%) <= w <= 0.325, the average over the
                    last step: (0.15 x 1.22 - 0.145 x 1.20) / 0.02 - 0.125
    inside the      paid for 22% (15% MPDUs) and built less: no bound
      last step
    at 22%          the average w over the last step >= 0.325; no upper bound,
                    the bonus stops at 22%
RMX zones (old 59-C-10.3.7(c)): each MPDU adds one unit, so above base the bonus
adds no market units; not modeled.
With a 15% minimum (from Oct 2018, high-income planning areas) the 22% bonus
comes with the minimum (rules.mpdus_required), so w = 0 below 22% and at 22%
0 <= w <= 0.76.
VERIFY: that a 15% minimum earns the 22% bonus at no extra MPDUs follows
rules.py; the high-income-area rule text is not in policy/.

Other groups in 08's wedge_sample:
  lump at 15%     2014 CR rule (Oct 2014 - Oct 2018): MPDU floor area is
                  exempt from FAR only at 15% MPDUs, so the choice is base at
                  12.5% or 1/0.85 = 1.176 x base at 15%. A project at base
                  reveals that the average w over that band is at most
                  (0.15/0.85 - 0.125)/(1/0.85 - 1) - 0.125 = 1/6 (an average,
                  not a marginal value); below base, w = 0
  height limit    below base, w = 0; at base the height limit stops the bonus,
                  so the price was not faced and w is not bounded above
  own schedule    Bethesda Overlay and the RE-1 MPDU step: not modeled
Apart from placing old projects on the table's steps, the schedule is taken as
continuous; integer MPDUs make the price lumpy in small projects (one MPDU in a
40-unit building is 2.5 points of share), and an interior project's n carries
that rounding.

Output: output/tables/wedge_bounds.csv (one row per wedge-sample project:
        w_lo, w_hi in units of d, bound), output/tables/wedge_bounds_summary.csv
        and output/figures/wedge_bounds.pdf (and .png)

Usage:
  python 10_wedge_bounds.py
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

BSB = ROOT / "output" / "tables" / "building_size_bunching.csv"
TAB_FILE = ROOT / "output" / "tables" / "wedge_bounds.csv"
SUM_FILE = ROOT / "output" / "tables" / "wedge_bounds_summary.csv"
FIG_FILE = ROOT / "output" / "figures" / "wedge_bounds.pdf"

NEW_RULES = pd.Timestamp("2018-10-31")      # Bill 34-17 Sec. 3, ZTA 18-06
TOP = 0.22
LUMP_AVG = (0.15 / 0.85 - 0.125) / (1 / 0.85 - 1) - 0.125
EPS = 1e-6
# the Chapter 25A table before ZTA 18-06 (struck text in Bill 34-17, sources/law/3_bill_34-17_2018.pdf pp. 19-20):
# "Up to 1%" bonus needs 12.6% MPDUs, ... "Up to 20%" 14.5%, "Up to 22%" 15.0%
OLD_SLOPE = 0.10                            # points of MPDU share per point of bonus, to a 20% bonus
OLD_KINK = 0.20
OLD_LAST = (0.15 * (1 + TOP) - (0.125 + OLD_SLOPE * OLD_KINK) * (1 + OLD_KINK)) / (TOP - OLD_KINK) - 0.125
BLUE, RED, GRAY, DARK = "#5b7fa6", "#b04a4a", "#888888", "#444444"
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
    "font.size": 12, "axes.labelsize": 12, "xtick.labelsize": 11, "ytick.labelsize": 11,
    "legend.fontsize": 10, "axes.spines.top": False, "axes.spines.right": False,
})


def share(n, s_min):
    """Fewest MPDUs per unit that make density n (units / base) legal."""
    return max(float(rules.share_for_bonus(max(n - 1, 0.0))), s_min)


def wedge(n, s_min):
    """ZTA 18-06: MPDUs carried by one more unit at density n, beyond the minimum share: MC(n) - s_min."""
    s, s_up = share(n, s_min), share(n + EPS, s_min)
    return s + n * (s_up - s) / EPS - s_min


def old_bounds(r):
    """Bonus available before Oct 2018, on the Chapter 25A table. Its 1% steps are taken as a line (0.1 point of
    MPDUs per point of bonus, MC - s_min = 0.1 (2n - 1)); the last step is a lump: any bonus above 20%, up to 22%,
    needs 15%, so the units above 20% cost OLD_LAST each on average and nothing at the margin. Position is read in
    whole units on the frontier base B, as the steps are: at 22% when N reaches floor(1.22 B); at 20% when N needs
    the 20% step (above floor(1.19 B), at most floor(1.20 B)) and is short of floor(1.22 B); inside the last step in
    between (it paid for 22% and did not build it); otherwise between, at its bonus."""
    n_units, base = r["actual_units_total"], r["frontier_base_units"]
    if r["position"] == "at base":
        return 0.0, OLD_SLOPE, "upper"
    u19, u20, u22 = (np.floor((1 + k) * base + EPS) for k in (OLD_KINK - 0.01, OLD_KINK, TOP))
    if n_units >= u22:
        return OLD_LAST, np.inf, "lower (average)"
    if u19 < n_units <= u20:
        return OLD_SLOPE * (2 * (1 + OLD_KINK) - 1), OLD_LAST, "interval (average upper)"
    if n_units > u20:
        return np.nan, np.nan, "inside last step"
    w = OLD_SLOPE * (2 * n_units / base - 1)
    return w, w, "exact"


def bounds(r):
    old = r["date_regime"] < NEW_RULES
    s_min, n, pos, group = r["min_share"], r["actual_units_total"] / r["frontier_base_units"], r["position"], r["group"]
    if group == "own schedule":
        return np.nan, np.nan, "not modeled"
    if pos == "below base":
        return 0.0, 0.0, "zero"
    if group == "height limit":
        return 0.0, np.inf, "height binds"
    if group == "lump at 15%":
        return (0.0, LUMP_AVG, "upper (average)") if pos == "at base" else (np.nan, np.nan, "not modeled")
    if r["bonus_rule"] == "RMX bonus":
        # each MPDU adds one unit, so above the free units of the minimum share the bonus adds no market units
        return np.nan, np.nan, "not modeled"
    if old:
        assert s_min == 0.125, f"{r['project_name']}: old schedule with a {s_min} minimum"
        return old_bounds(r)
    if pos == "at base":
        hi = wedge(1 + EPS, s_min)
        return 0.0, hi, "upper" if hi > 0 else "zero"
    if pos == "at 22%":
        lo, hi = wedge(1 + TOP - EPS, s_min), wedge(1 + TOP + EPS, s_min)
        return lo, hi, "lower" if np.isinf(hi) else "interval"
    w = wedge(n, s_min)
    return w, w, "exact" if w > 0 else "zero"


def main():
    b = pd.read_csv(BSB, parse_dates=["date_regime"])
    d = b[b["wedge_sample"]].copy()
    d[["w_lo", "w_hi", "bound"]] = d.apply(bounds, axis=1, result_type="expand")
    d["period"] = np.where(d["date_regime"] < NEW_RULES, "old", "new")
    cols = ["id", "project_name", "plan", "group", "period", "min_share", "tenure", "planning_area",
            "actual_units_total", "actual_units_mpdu", "frontier_base_units", "bonus_used", "position",
            "w_lo", "w_hi", "bound", "acs19_median_gross_rent", "year_offering"]
    d = d[cols].sort_values(["w_lo", "w_hi", "bonus_used"])
    d.to_csv(TAB_FILE, index=False, float_format="%.4g")

    s = (d.assign(w_hi=d["w_hi"].replace(np.inf, np.nan))
         .groupby(["bound", "group", "position"], dropna=False)
         .agg(projects=("id", "size"), w_lo_min=("w_lo", "min"), w_lo_max=("w_lo", "max"),
              w_hi_min=("w_hi", "min"), w_hi_max=("w_hi", "max")))
    s.to_csv(SUM_FILE, float_format="%.3g")
    print(s.round(3).to_string())
    print(f"\n{len(d)} projects: " + ", ".join(f"{k} {v}" for k, v in d["bound"].value_counts().items()))

    # one row per project, sorted: dot = exact or zero, bar = interval, arrow = no upper bound
    p = d[d["w_lo"].notna()].reset_index(drop=True)
    cap = 0.9
    fig, ax = plt.subplots(figsize=(8, 7))
    for i, r in p.iterrows():
        color = RED if r["period"] == "new" else BLUE
        if r["w_lo"] == r["w_hi"]:
            ax.plot(min(r["w_lo"], cap), i, ">" if r["w_lo"] > cap else "o", ms=3.5, color=color)
        elif np.isinf(r["w_hi"]):
            ax.annotate("", xy=(cap, i), xytext=(r["w_lo"], i),
                        arrowprops=dict(arrowstyle="->", color=GRAY if r["bound"] == "height binds" else color, lw=1))
        else:
            ax.plot([r["w_lo"], r["w_hi"]], [i, i], color=color, lw=1.5, solid_capstyle="butt")
    for v, lab, ha, color in [(OLD_SLOPE, "old: first unit 0.10 ", "right", BLUE),
                              (OLD_LAST, " old: last step, average 0.325", "left", BLUE),
                              (1 / 8.8, "", "right", RED), (1.44 / 8.8, " 2018: 0.114, 0.164", "left", RED)]:
        ax.axvline(v, color=color, ls="--", lw=0.8, alpha=0.7)
        ax.text(v, 1.0, lab, color=color, fontsize=8, va="bottom", ha=ha, transform=ax.get_xaxis_transform())
    ax.set_xlim(-0.02, cap)
    ax.set_yticks([])
    ax.set_ylabel(f"Projects, sorted ({len(p)}; {d['w_lo'].isna().sum()} with no bound not shown)")
    ax.set_xlabel(f"Wedge w: value of one more permitted unit, in MPDU discounts d (> {cap} piled at {cap})")
    ax.plot([], [], "o", color=BLUE, label="old schedule")
    ax.plot([], [], "o", color=RED, label="ZTA 18-06")
    ax.plot([], [], color=GRAY, label="height limit (not bounded)")
    ax.legend(frameon=False, loc="lower right")
    fig.tight_layout()
    fig.savefig(FIG_FILE)
    fig.savefig(FIG_FILE.with_suffix(".png"), dpi=150)


if __name__ == "__main__":
    main()
