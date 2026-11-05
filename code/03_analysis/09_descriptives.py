"""Descriptive tables and figures for the MPDU dataset, version 1.

Run 07_kink_bunching_by_regime.py and 08_building_size_bunching.py first.

Four nested samples:
  all      every report project counted in 07 (projects listed twice counted
           once), with the phases of an 08 plan group summed into one project
           (PLAN_GROUPS: the MPDU obligation is set for the whole plan; the
           plan's earliest acceptance date sets its regime), and with its
           regime: old (site plan accepted before 31 Oct 2018, Chapter 25A
           table) or new (ZTA 18-06). The MPDU-share sample: needs no base.
           Its group is 08's (project_group.csv), or "no resolution base".
  base     every row of 08: projects with a resolution base, plan groups once.
  bonus    base rows whose rule let MPDUs buy units above base (08 group
           "bonus available").
  choice   bonus rows whose MPDU share was the developer's to pick: no subsidy
           (LIHTC after completion counts as a choice, since the market
           developer set the share), no 25% impact-tax flag, and a 12.5%
           minimum. For reference only; no analysis is filtered on it yet.
  wedge    base rows with 08's wedge_sample: a known price for density (bonus
           available, height limit, lump at 15%, own schedule) and the
           project's own share; counted in the sample table only.

MPDU share category (share_category), in units, so rounding does not move a
project: with N total units, a project is "at x%" when its MPDUs equal
ceil(x N), the fewest that reach x. Taken in order: fully affordable; below its
minimum; at its minimum (12.5%, or 15% where that is required); between the
minimum and 15%; at 15%; 15-20%; at 20%; 20-25%; at 25%; above 25%. In a small
project the minimum can round up to 14-15% (4 MPDUs of 28 units is "at its
minimum").

Period (base samples), from date_regime as in 08: before Oct 2014 (old code),
Oct 2014 to Oct 2018 (2014 code, old Chapter 25A table), from Oct 2018 (ZTA
18-06).

Output: output/tables/descriptives_*.csv (one per table below) and
        output/figures/descriptives.pdf (one figure per page; also as PNGs in
        output/figures/descriptives/)
  sample      how the samples are built
  summary     size, MPDU share, tenure, year and tract rent (ACS 2019 median
              gross rent; rent_mkt is the simulation's constant), by sample
  share       MPDU share category by regime (all)
  share_by_group   MPDU share category by group, old regime (all), plus the
              old-regime choice sample
  position    08 position by group, plus the choice sample (base)
  position_by_share   position by MPDU share category (bonus)
  flags       flagged projects by group (base)
  choice_by   position by period and by tenure (choice)

Usage:
  python 09_descriptives.py
"""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code" / "03_analysis" / "01_mpdu_simulation"))
import rules  # noqa: E402

RESULTS = ROOT / "data" / "int" / "03_analysis" / "01_mpdu_simulation_results.csv"
REGIME = ROOT / "output" / "tables" / "project_regime.csv"
PROJECT_GROUP = ROOT / "output" / "tables" / "project_group.csv"
BSB = ROOT / "output" / "tables" / "building_size_bunching.csv"
FIXES = ROOT / "data" / "raw" / "mpdu_annual_reports" / "project_fixes.csv"
TAB_DIR = ROOT / "output" / "tables"
FIG_FILE = ROOT / "output" / "figures" / "descriptives.pdf"
PNG_DIR = ROOT / "output" / "figures" / "descriptives"

NEW_RULES = pd.Timestamp("2018-10-31")      # Bill 34-17 Sec. 3, ZTA 18-06
CODE_2014 = pd.Timestamp("2014-10-30")      # zoning rewrite
POSITIONS = ["below base", "at base", "between", "at 22%", "above 22%"]
SHARES = ["fully affordable", "below its minimum", "at its minimum", "minimum to 15%", "at 15%", "15-20%",
          "at 20%", "20-25%", "at 25%", "above 25%"]
PERIODS = ["before Oct 2014", "Oct 2014 - Oct 2018", "from Oct 2018"]
GROUP_ORDER = ["bonus available", "ceiling at base", "height limit", "lump at 15%", "own schedule", "other program",
               "unclear", "base from approved units", "no resolution base"]
BLUE, RED, GRAY = "#5b7fa6", "#b04a4a", "#888888"
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
    "font.size": 12, "axes.labelsize": 12, "xtick.labelsize": 11, "ytick.labelsize": 11,
    "legend.fontsize": 10, "axes.spines.top": False, "axes.spines.right": False,
})


def fewest(d, share):
    """Fewest MPDUs that reach share x of total units."""
    return np.ceil(share * d["actual_units_total"] - 1e-9)


def share_category(d):
    m = d["actual_units_mpdu"]
    conds = [d["is_fully_affordable"].fillna(False).astype(bool), m < fewest(d, d["min_share"]),
             m == fewest(d, d["min_share"]), m < fewest(d, 0.15), m == fewest(d, 0.15), m < fewest(d, 0.20),
             m == fewest(d, 0.20), m < fewest(d, 0.25), m == fewest(d, 0.25)]
    return pd.Categorical(np.select(conds, SHARES[:-1], SHARES[-1]), categories=SHARES, ordered=True)


def by_plan(a):
    """One row per plan group: units and MPDUs summed, the earliest acceptance date and offering year, the rest
    from the first phase."""
    g = a.groupby(a["plan_group"].fillna(a["id"].astype(str)), sort=False)
    one = g.first()
    sums = ["actual_units_total", "actual_units_mpdu"]
    one[sums] = g[sums].sum()
    one["date_regime"] = g["date_regime"].min()
    one["year_offering"] = g["year_offering"].min()
    grouped = one["plan_group"].notna()
    one.loc[grouped, "project_name"] = one.loc[grouped, "plan_group"]
    one.loc[grouped, "regime"] = np.select([one["date_regime"] < NEW_RULES, one["date_regime"] >= NEW_RULES],
                                           ["old", "new"], "unknown")[grouped]
    one["actual_sh_mpdu"] = one["actual_units_mpdu"] / one["actual_units_total"]
    return one.reset_index(drop=True)


def real_choice(b):
    return (b["subsidy"].isin(["none", "LIHTC, after completion"]) & (b["impact_tax"] == "none")
            & (b["min_share"] == 0.125))


def summary(d, new):
    rental = d["tenure"].fillna("").str.startswith("Rental")
    forsale = d["tenure"].fillna("").str.startswith("For-Sale")
    return pd.Series({
        "projects": len(d),
        "units, total": d["actual_units_total"].sum(),
        "units, median": d["actual_units_total"].median(),
        "units, 25th pct": d["actual_units_total"].quantile(0.25),
        "units, 75th pct": d["actual_units_total"].quantile(0.75),
        "MPDUs, total": d["actual_units_mpdu"].sum(),
        "MPDU share, median (%)": 100 * d["actual_sh_mpdu"].median(),
        "at its minimum (%)": 100 * (d["share_category"] == "at its minimum").mean(),
        "at 15% (%)": 100 * (d["share_category"] == "at 15%").mean(),
        "15% minimum (%)": 100 * (d["min_share"] == 0.15).mean(),
        "fully affordable (%)": 100 * d["is_fully_affordable"].fillna(False).astype(bool).mean(),
        "rental (%)": 100 * rental.mean(),
        "for-sale (%)": 100 * forsale.mean(),
        "offering year, median": d["year_offering"].median(),
        "offering year, first": d["year_offering"].min(),
        "offering year, last": d["year_offering"].max(),
        "new regime (%)": 100 * new.mean(),
        "tract median gross rent 2019, median ($/mo)": d["acs19_median_gross_rent"].median(),
    })


def mark(ax, lines):
    """Dashed vertical lines, labelled at the top of the panel (above the bars, given headroom)."""
    for v, lab in lines:
        ax.axvline(v, color=GRAY, ls="--", lw=0.8)
        ax.text(v, 0.99, f" {lab}", color=GRAY, fontsize=9, va="top", transform=ax.get_xaxis_transform())


def save(t, name):
    t.to_csv(TAB_DIR / f"descriptives_{name}.csv")
    print(f"\n{name}:\n{t.to_string()}")


def main():
    # samples
    r = pd.read_csv(RESULTS, dtype={"site_plan": str})
    reg = pd.read_csv(REGIME, parse_dates=["date_regime"])
    a = r.drop(columns="date_regime").merge(reg, on="id", how="inner")
    a = a.merge(pd.read_csv(PROJECT_GROUP), on="id", how="left")
    n_rows = len(a)
    a = by_plan(a)
    a["group"] = a["group"].fillna("no resolution base")
    b = pd.read_csv(BSB, dtype={"plan": str}, parse_dates=["date_regime"])
    for d in (a, b):
        d["share_category"] = share_category(d)
    b["period"] = pd.Categorical(np.select([b["date_regime"] < CODE_2014, b["date_regime"] < NEW_RULES],
                                           PERIODS[:2], PERIODS[2]), categories=PERIODS, ordered=True)
    bonus = b[b["group"] == "bonus available"]
    choice = bonus[real_choice(bonus)]
    fixes = pd.read_csv(FIXES) if FIXES.exists() else pd.DataFrame(columns=["fix"])

    save(pd.DataFrame([
        ("report projects (annual reports, agreements, permits)", len(r)),
        ("report projects listed twice counted once (project_fixes.csv)", n_rows),
        ("all: plan groups once (08)", len(a)),
        ("  of which regime unknown", int((a["regime"] == "unknown").sum())),
        ("base: with a resolution base, plan groups once (08)", len(b)),
        ("bonus: MPDUs could buy units above base", len(bonus)),
        ("choice: no subsidy, impact-tax flag or 15% minimum", len(choice)),
        ("wedge: priced density and own share (08 wedge_sample)", int(b["wedge_sample"].sum())),
    ], columns=["step", "projects"]).set_index("step"), "sample")
    print(f"(project_fixes.csv rows: {fixes['fix'].value_counts().to_dict()}; 08 also leaves out the other "
          f"project's plan rows and projects with no resolution base)")

    t = pd.concat({"all": summary(a, a["regime"] == "new"),
                   "base": summary(b, b["period"] == PERIODS[2]),
                   "bonus": summary(bonus, bonus["period"] == PERIODS[2]),
                   "choice": summary(choice, choice["period"] == PERIODS[2])}, axis=1)
    save(t.round(1), "summary")

    save(pd.crosstab(a["share_category"], a["regime"], margins=True, margins_name="total", dropna=False)
         .reindex(columns=["old", "new", "unknown", "total"], fill_value=0), "share")

    a_old = a[a["regime"] == "old"]
    t = pd.crosstab(a_old["share_category"], a_old["group"], dropna=False).reindex(columns=GROUP_ORDER, fill_value=0)
    t["total"] = t.sum(axis=1)
    t["choice (within bonus available)"] = (choice.loc[choice["period"] != PERIODS[2], "share_category"]
                                            .value_counts().reindex(t.index, fill_value=0))
    t.loc["total"] = t.sum()
    save(t, "share_by_group")

    pos = pd.crosstab(b["group"], b["position"]).reindex(columns=POSITIONS, fill_value=0)
    pos.loc["choice (within bonus available)"] = choice["position"].value_counts().reindex(POSITIONS, fill_value=0)
    pos["total"] = pos.sum(axis=1)
    save(pos, "position")

    save(pd.crosstab(bonus["share_category"], bonus["position"], margins=True, margins_name="total", dropna=False)
         .reindex(columns=POSITIONS + ["total"], fill_value=0), "position_by_share")

    flags = pd.DataFrame({
        "projects": b.groupby("group").size(),
        "TDRs or transfer": b.assign(x=b["tdr"] != "none").groupby("group")["x"].sum(),
        "subsidy": b.assign(x=~b["subsidy"].isin(["none", "LIHTC, after completion"])).groupby("group")["x"].sum(),
        "25% impact tax": b.assign(x=b["impact_tax"] != "none").groupby("group")["x"].sum(),
        "15% minimum": b.assign(x=b["min_share"] == 0.15).groupby("group")["x"].sum(),
        "other program": b.assign(x=b["other_program"] != "none").groupby("group")["x"].sum(),
        "base not checked": b.assign(x=b["base_check"] != "checked").groupby("group")["x"].sum(),
    })
    flags.loc["total"] = flags.sum()
    save(flags.astype(int), "flags")

    tenure = choice["tenure"].fillna("unknown").str.replace(r"^Rental.*", "Rental", regex=True)
    by = pd.concat({"period": pd.crosstab(choice["period"], choice["position"], dropna=False),
                    "tenure": pd.crosstab(tenure, choice["position"])}).reindex(columns=POSITIONS, fill_value=0)
    by["total"] = by.sum(axis=1)
    save(by, "choice_by")

    # figures
    PNG_DIR.mkdir(parents=True, exist_ok=True)
    figs = []

    # 1. projects by offering year and regime
    fig, ax = plt.subplots(figsize=(9, 3.8))
    years = np.arange(a["year_offering"].min(), a["year_offering"].max() + 1)
    old = a[a["regime"] == "old"]["year_offering"].value_counts().reindex(years, fill_value=0)
    new = a[a["regime"] == "new"]["year_offering"].value_counts().reindex(years, fill_value=0)
    ax.bar(years, old, color=BLUE, edgecolor="white", linewidth=0.5, label=f"Old schedule ({old.sum()})")
    ax.bar(years, new, bottom=old, color=RED, edgecolor="white", linewidth=0.5, label=f"ZTA 18-06 ({new.sum()})")
    ax.set_ylim(top=ax.get_ylim()[1] * 1.15)
    ax.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
    ax.set_xlabel("Year of first MPDU offering")
    ax.set_ylabel("Projects")
    ax.set_title(f"Projects by year (all, n = {len(a)}; {int((a['regime'] == 'unknown').sum())} unknown regime "
                 "not shown)", loc="left", fontsize=11)
    ax.legend(frameon=False, loc="upper left")
    figs.append(("year", fig))

    # 2. MPDU share by regime
    bins = np.arange(10, 35.5, 0.5)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4), sharey=True)
    for ax, regime, title in [(axes[0], "old", "Old schedule"), (axes[1], "new", "ZTA 18-06")]:
        s = 100 * a.loc[a["regime"] == regime, "actual_sh_mpdu"]
        ax.hist(s.clip(10.01, 34.99), bins=bins, color=BLUE, edgecolor="white", linewidth=0.3)
        mark(ax, [(v, f"{v:g}%") for v in [12.5, 15, 20, 25]])
        ax.set_title(f"{title} (n = {len(s)})", loc="left", fontsize=11)
        ax.set_xlabel("MPDU share, % (0.5-point bins from 12.5%; ends piled at 10% and 35%)")
    axes[0].set_ylim(top=axes[0].get_ylim()[1] * 1.12)   # y is shared: once
    axes[0].set_ylabel("Projects")
    figs.append(("share", fig))

    # 3. MPDU share, old regime: where MPDUs could buy units above base, and where base was a ceiling
    bins = np.arange(10, 35.5, 0.5)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4), sharey=True)
    for ax, group, color in [(axes[0], "bonus available", BLUE), (axes[1], "ceiling at base", RED)]:
        s = 100 * a_old.loc[a_old["group"] == group, "actual_sh_mpdu"]
        ax.hist(s.clip(10.01, 34.99), bins=bins, color=color, edgecolor="white", linewidth=0.3)
        mark(ax, [(v, f"{v:g}%") for v in [12.5, 15, 20, 25]])
        ax.set_title(f"Old schedule, {group} (n = {len(s)})", loc="left", fontsize=11)
        ax.set_xlabel("MPDU share, % (0.5-point bins from 12.5%; ends piled at 10% and 35%)")
    axes[0].set_ylim(top=axes[0].get_ylim()[1] * 1.12)
    axes[0].set_ylabel("Projects")
    figs.append(("share_by_group", fig))

    # 4. units over base: choice sample against projects with a ceiling at base; bins centred on
    # multiples of 2.5%, so base (0) and 22% (in 21.25-23.75%) each sit inside one bin
    bins = np.arange(-0.3125, 0.3126, 0.025)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4), sharey=True)
    for ax, d, title, color in [(axes[0], choice, "Bonus available, real choice", BLUE),
                                (axes[1], b[b["group"] == "ceiling at base"], "Ceiling at base", RED)]:
        ax.hist(d["bonus_used"].clip(-0.30, 0.30), bins=bins, color=color, edgecolor="white", linewidth=0.3)
        mark(ax, [(0, "base"), (0.22, "22% bonus")])
        ax.set_title(f"{title} (n = {len(d)})", loc="left", fontsize=11)
        ax.set_xlabel("Units / base units - 1 (2.5-point bins centred on 0; ends piled at ±30%)")
        ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    axes[0].set_ylim(top=axes[0].get_ylim()[1] * 1.12)
    axes[0].set_ylabel("Projects")
    figs.append(("units_over_base", fig))

    # 5. MPDU share against units over base, with the two bonus schedules
    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.linspace(0.10, 0.35, 501)
    ax.plot(100 * x, 100 * rules.bonus_pct(x), color=RED, lw=1.5, label="ZTA 18-06 schedule")
    ax.plot([10, 12.5, 14.5, 15, 35], [0, 0, 20, 22, 22], color=GRAY, lw=1.5, ls="--",
            label="Old Chapter 25A table")
    flagged = bonus[~real_choice(bonus)]
    ax.scatter(100 * choice["actual_sh_mpdu"].clip(upper=34.9 / 100), 100 * choice["bonus_used"].clip(-0.4, 0.4),
               s=36, color=BLUE, edgecolor="white", linewidth=0.8, zorder=3, label=f"Real choice ({len(choice)})")
    ax.scatter(100 * flagged["actual_sh_mpdu"].clip(upper=34.9 / 100), 100 * flagged["bonus_used"].clip(-0.4, 0.4),
               s=36, facecolor="none", edgecolor=GRAY, linewidth=1, zorder=3,
               label=f"Subsidy, 25% tax notch or 15% minimum ({len(flagged)})")
    ax.axhline(0, color=GRAY, lw=0.6)
    ax.set_xlim(10, 35)
    ax.set_xlabel("MPDU share, % (piled at 35%)")
    ax.set_ylabel("Units above base, % (piled at -40% and +40%)")
    ax.set_title(f"Bonus available (n = {len(bonus)})", loc="left", fontsize=11)
    ax.legend(frameon=False, loc="upper left")
    figs.append(("share_vs_units", fig))

    # 6. the wedge sample, every schedule together: MPDU share and units over base, old and new rules stacked
    w = b[b["wedge_sample"]]
    new = w["period"] == PERIODS[2]
    labels = [f"Old schedule ({(~new).sum()})", f"ZTA 18-06 ({new.sum()})"]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4), sharey=True)
    s = 100 * w["actual_sh_mpdu"].clip(0.1001, 0.3499)
    axes[0].hist([s[~new], s[new]], bins=np.arange(10, 35.5, 0.5), stacked=True, color=[BLUE, RED],
                 edgecolor="white", linewidth=0.3, label=labels)
    mark(axes[0], [(v, f"{v:g}%") for v in [12.5, 15, 20, 25]])
    axes[0].set_title(f"Wedge sample, MPDU share (n = {len(w)})", loc="left", fontsize=11)
    axes[0].set_xlabel("MPDU share, % (0.5-point bins from 12.5%; ends piled at 10% and 35%)")
    u = w["bonus_used"].clip(-0.30, 0.30)
    axes[1].hist([u[~new], u[new]], bins=np.arange(-0.3125, 0.3126, 0.025), stacked=True, color=[BLUE, RED],
                 edgecolor="white", linewidth=0.3, label=labels)
    mark(axes[1], [(0, "base"), (0.22, "22% bonus")])
    axes[1].set_title(f"Wedge sample, units over base (n = {len(w)})", loc="left", fontsize=11)
    axes[1].set_xlabel("Units / base units - 1 (2.5-point bins centred on 0; ends piled at ±30%)")
    axes[1].xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    axes[0].set_ylim(top=axes[0].get_ylim()[1] * 1.12)
    axes[0].set_ylabel("Projects")
    axes[1].legend(frameon=False, loc="upper left")
    figs.append(("wedge_sample", fig))

    FIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with PdfPages(FIG_FILE) as pdf:
        for name, fig in figs:
            fig.tight_layout()
            pdf.savefig(fig)
            fig.savefig(PNG_DIR / f"{name}.png", dpi=150)
            plt.close(fig)
    print(f"\n[saved] {TAB_DIR}/descriptives_*.csv; {FIG_FILE}; {PNG_DIR}/*.png")


if __name__ == "__main__":
    main()
