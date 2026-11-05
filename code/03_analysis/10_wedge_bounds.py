"""What each project's choice reveals about its wedge on the density limit, in units of the MPDU discount.

Run 08_building_size_bunching.py first.

A project with base B builds N = nB units and owes the fewest MPDUs that make N
legal, s(n)N, where s(n) is the minimum share up to base (and, with a 15%
minimum, up to the bonus that share already earns) and rises along the bonus
schedule above it (rules.share_for_bonus: 8.8 points of bonus per point of
MPDUs to 22%, then 1.6 to 30%, then 1.0). An MPDU costs the developer d, its
market value minus its controlled value. The MPDUs carried by one more unit are

  MC(n) = s(n) + n s'(n)

and the wedge is what one more permitted unit is worth beyond the MPDUs the
minimum share already charges on it: w = MC - s_min, in units of d. A developer
who chose n reveals (profit maximization only; no elasticity):
  below base        w = 0: the density limit did not bind
  at base           0 <= w <= MC just above base - s_min (1/8.8 = 0.114 at a
                    12.5% minimum)
  between, above    w = MC(n) - s_min at the observed n, exactly
    22%
  at 22%            MC just below 22% - s_min (1.44/8.8 = 0.164) <= w, and
                    w <= MC just above 22% - s_min under ZTA 18-06 (0.79);
                    no upper bound under the old schedule, where the bonus
                    stops at 22%
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
The schedule is continuous here; integer MPDUs make the price lumpy in small
projects (one MPDU in a 40-unit building is 2.5 points of share), and an
interior project's n carries that rounding.

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


def wedge(n, s_min, old):
    """MPDUs carried by one more unit at density n, beyond the minimum share: MC(n) - s_min."""
    if old and n > 1 + TOP:
        return np.inf
    s, s_up = share(n, s_min), share(n + EPS, s_min)
    return s + n * (s_up - s) / EPS - s_min


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
    if pos == "at base":
        hi = wedge(1 + EPS, s_min, old)
        return 0.0, hi, "upper" if hi > 0 else "zero"
    if pos == "at 22%":
        lo, hi = wedge(1 + TOP - EPS, s_min, old), wedge(1 + TOP + EPS, s_min, old)
        return lo, hi, "lower" if np.isinf(hi) else "interval"
    w = wedge(n, s_min, old)
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
    p = d[d["bound"] != "not modeled"].reset_index(drop=True)
    cap = 0.9
    fig, ax = plt.subplots(figsize=(8, 7))
    for i, r in p.iterrows():
        color = RED if r["period"] == "new" else BLUE
        if r["bound"] in ("zero", "exact"):
            ax.plot(min(r["w_lo"], cap), i, ">" if r["w_lo"] > cap else "o", ms=3.5, color=color)
        elif np.isinf(r["w_hi"]):
            ax.annotate("", xy=(cap, i), xytext=(r["w_lo"], i),
                        arrowprops=dict(arrowstyle="->", color=GRAY if r["bound"] == "height binds" else color, lw=1))
        else:
            ax.plot([r["w_lo"], r["w_hi"]], [i, i], color=color, lw=1.5, solid_capstyle="butt")
    for v, lab, ha in [(1 / 8.8, "first bonus unit, 0.114 ", "right"), (1.44 / 8.8, " last unit to 22%, 0.164", "left")]:
        ax.axvline(v, color=GRAY, ls="--", lw=0.8)
        ax.text(v, 1.0, lab, color=GRAY, fontsize=9, va="bottom", ha=ha, transform=ax.get_xaxis_transform())
    ax.set_xlim(-0.02, cap)
    ax.set_yticks([])
    ax.set_ylabel(f"Projects, sorted ({len(p)}; {(d['bound'] == 'not modeled').sum()} own schedule not shown)")
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
