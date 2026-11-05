"""Bunching at the 15% and 20% kinks, split by the bonus schedule in force.

Run code/03_analysis/01_mpdu_simulation/main.py first.

04_kink_bunching_figure.py pools all years, but the schedule changed in 2018:
  old   Chapter 25A table (Sec. 25A-5, deleted by Bill 34-17): 1% bonus per
        0.1% of MPDUs above 12.5% up to 20% at 14.5%, then 22% at 15%, and no
        more bonus above 15%. So 15% is where the bonus stops; there is no 20%
        kink. The zone could cap the bonus lower (Council PHED memo on ZTA
        18-06, 20 Sep 2018, p. 2: R-30, R-20, R-10 22%; R-200 12%; R-90, R-60,
        R-40 and most CR zones none).
  new   ZTA 18-06 (Ord. 18-52, effective 29 Oct 2018), as in rules.bonus_pct:
        0.88% per 0.1% to 15% (22%), 0.16% per 0.1% to 20% (30%), then 0.1%.
Bill 34-17 Sec. 3 (effective 31 Oct 2018) keeps any application accepted as
complete before 31 Oct 2018 on the old Chapter 25A, amendments included,
unless the applicant elects the new rules. So a project is "old" when its site
plan was accepted before 31 Oct 2018 (date_regime from 07_site_plan_regime.py:
acceptance date, or the original plan's for amendments) and "new" otherwise.
Not observed: sketch plans accepted before that date (also old) and elections
into the new rules (old projects counted as old). No old project's resolution
base implies a bonus above 22% beyond rounding, so none clearly elected.

REGIME_DATES fills the projects with no site plan match in the simulation
results (no plan number in the annual report, or a mistyped one), from the
Planning GIS site plan layer by project name, or from the documents. An
amendment takes the original plan's date unless it created the units (Woodlake,
Sandy Spring Village). Two stay unknown.

The 15% minimum areas (high-income planning areas, Bethesda Downtown, SSDAC)
start in October 2018 or later and sit almost all in the new regime; there 15%
is the requirement as well as the kink. The Bethesda Overlay Zone has its own
schedule (not modeled); its projects are counted with the rest.

Projects listed twice (fix = duplicate or part in the hand-made, optional
data/raw/mpdu_annual_reports/project_fixes.csv; see 06_base_density_audit.py)
are counted once.

Output: output/figures/mpdu_kink_bunching_by_regime.pdf,
        output/tables/mpdu_kink_bunching_by_regime.csv (regime, kink,
        units_from_kink = MPDUs minus ceil(kink x total units), projects) and
        output/tables/project_regime.csv (id, date_regime, regime; one row per
        project counted here, for 09_descriptives.py)

Usage:
  python 07_kink_bunching_by_regime.py
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "data" / "int" / "03_analysis" / "01_mpdu_simulation_results.csv"
FIG_FILE = ROOT / "output" / "figures" / "mpdu_kink_bunching_by_regime.pdf"
TAB_FILE = ROOT / "output" / "tables" / "mpdu_kink_bunching_by_regime.csv"
REGIME_FILE = ROOT / "output" / "tables" / "project_regime.csv"
FIXES = ROOT / "data" / "raw" / "mpdu_annual_reports" / "project_fixes.csv"

NEW_RULES = pd.Timestamp("2018-10-31")   # Bill 34-17 Sec. 3
KINKS = [0.15, 0.20]
SHARE_MAX = 35         # percent; higher shares are piled in the last bin
BLUE, RED, PURPLE = "#5b7fa6", "#b04a4a", "#7a5c99"
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
    "font.size": 12, "axes.labelsize": 12, "xtick.labelsize": 11, "ytick.labelsize": 11,
    "legend.fontsize": 10, "axes.spines.top": False, "axes.spines.right": False,
})

# acceptance date of the site plan (or of the original plan, for amendments),
# from data/raw/mcplanning/site_plans.geojson, for projects without one
REGIME_DATES = {
    "Woodlake": "2005-01-18",                      # 8-71011A filed 18 Jan 2005, the 59 townhouses (1971 plan 819710110)
    "The Astrid": "2016-02-19",                    # 82016008C: site plan 81982098C filed 19 Feb 2016 (not in GIS)
    "Armstrong Property": "2016-06-17",            # 820160110
    "7607 Old Georgetown Road": "2018-10-01",      # 820190030
    "Bloom Montgomery Village/ Bloom MV Areas I-VI": "2017-06-19",   # 820170130
    "Strathmore Square": "2021-11-17",             # 820220070
    "8787 Georgia (Atwell on Spring)": "2018-03-01",   # 820180100
    "St. Elmo": "2017-01-18",                      # 820170030
    "8015 Old Georgetown Road": "2020-02-27",      # 820200130
    "4909 Auburn Avenue": "2019-05-16",            # 820190100, "4915 Auburn Avenue"
    "Sandy Spring Village": "2021-05-05",          # 81988060A filed 5 May 2021: the 56 units, in 1988 office buildings
}
REGIME_DATES_BY_PLAN = {"E20250010": "2025-02-12"}   # Tevis Place, MCPB 25-047
# not found: Westside Shady Grove (GIS has only the 2025 Block U plan for a
# 2024 offering), Heritage Gardens


def units_from_kink(d, k):
    """MPDUs minus the fewest that reach share k."""
    return (d["actual_units_mpdu"] - np.ceil(k * d["actual_units_total"] - 1e-9)).astype(int)


def main():
    d = pd.read_csv(RESULTS, dtype={"site_plan": str}, parse_dates=["date_regime"])
    if FIXES.exists():
        f = pd.read_csv(FIXES, dtype={"site_plan": str})
        f = f[f["fix"].isin(["duplicate", "part"])]
        listed = set(zip(f["site_plan"], f["total_units"], f["total_mpdus"], f["source"]))
        key = list(zip(d["site_plan"], d["actual_units_total"], d["actual_units_mpdu"], d["source"]))
        assert listed <= set(key), f"project_fixes.csv: not in the results: {listed - set(key)}"
        d = d[[k not in listed for k in key]]
        print(f"listed twice, counted once (project_fixes.csv): {len(listed)}")
    d["date_regime"] = (d["date_regime"]
                        .fillna(pd.to_datetime(d["project_name"].map(REGIME_DATES)))
                        .fillna(pd.to_datetime(d["site_plan"].map(REGIME_DATES_BY_PLAN))))
    d["regime"] = np.select([d["date_regime"] < NEW_RULES, d["date_regime"] >= NEW_RULES],
                            ["old", "new"], "unknown")
    d[["id", "date_regime", "regime"]].to_csv(REGIME_FILE, index=False)
    d["share_pct"] = 100 * d["actual_sh_mpdu"]
    d["at_min"] = d["actual_units_mpdu"] == np.ceil(d["min_share"] * d["actual_units_total"] - 1e-9)

    rows = []
    for regime in ["old", "new"]:
        g = d[d["regime"] == regime]
        print(f"{regime}: {len(g)} projects ({int((g['min_share'] == 0.15).sum())} with a 15% minimum, "
              f"{int(g['master_plan_15'].eq('BETHESDA DOWNTOWN PLAN').sum())} in Bethesda Downtown)")
        for k in KINKS:
            gaps = units_from_kink(g, k)
            c = gaps.value_counts().reindex(range(gaps.min(), gaps.max() + 1), fill_value=0)
            rows.append(pd.DataFrame({"regime": regime, "kink": k, "units_from_kink": c.index,
                                      "projects": c.values}))
            near = c.reindex(range(-3, 4), fill_value=0)
            print(f"  {100 * k:g}%: at 0 units {near[0]}; mean of -3..-1 and +1..+3: "
                  f"{near.drop(0).mean():.1f}; below {(gaps < 0).sum()}, at or above {(gaps >= 0).sum()}")
    unknown = d.loc[d["regime"] == "unknown", "project_name"]
    print(f"unknown regime: {len(unknown)} ({', '.join(unknown)})")

    # figure: one panel per regime, as in 04_kink_bunching_figure.py
    bins = np.arange(0, SHARE_MAX + 0.25, 0.25)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    for ax, regime, title in [(axes[0], "old", "Accepted before 31 Oct 2018 (old schedule)"),
                              (axes[1], "new", "Accepted on or after 31 Oct 2018 (ZTA 18-06)")]:
        g = d[d["regime"] == regime]
        s = g["share_pct"].clip(upper=SHARE_MAX - 0.01)
        counts, _, _ = ax.hist([s[g["at_min"]], s[~g["at_min"]]], bins=bins, stacked=True, color=[RED, BLUE],
                               edgecolor="white", linewidth=0.3,
                               label=[f"At its required minimum ({g['at_min'].sum()})",
                                      f"Other ({(~g['at_min']).sum()})"])
        ax.set_ylim(0, counts[-1].max() * 1.3)
        lines = [(12.5, "12.5% minimum", RED, "--"),
                 (15, "15%: bonus stops (22%)" if regime == "old" else "15% kink", PURPLE, "-.")]
        if regime == "new":
            lines.append((20, "20% kink", PURPLE, "-."))
        top = ax.get_ylim()[1]
        for x, lab, color, ls in lines:
            ax.axvline(x, color=color, ls=ls, lw=0.8)
            ax.text(x + 0.3, top * (0.97 if x != 15 else 0.88), lab, color=color, fontsize=9, va="top")
        ax.set_xlim(0, SHARE_MAX)
        ax.set_title(f"{title}, n = {len(g)}", loc="left", fontsize=11)
        ax.set_xlabel(f"MPDU share of total units (%; above {SHARE_MAX}% piled at the right)")
        ax.legend(frameon=False, loc="center right", fontsize=9)
    axes[0].set_ylabel("Projects")
    fig.tight_layout()

    FIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    TAB_FILE.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG_FILE)
    pd.concat(rows).to_csv(TAB_FILE, index=False)
    print(f"[saved] {FIG_FILE}; {TAB_FILE}")


if __name__ == "__main__":
    main()
