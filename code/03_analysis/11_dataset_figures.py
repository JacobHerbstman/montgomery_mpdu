"""Evan's figures redrawn on the project-level dataset, and the list of projects.

Run 09_descriptives.py first.

02-05 and 07 draw on the simulation results, one row per report project (219):
a project listed twice is in twice, a plan's phases are separate, and the
groups of 08 are not there. These are the same figures on 09's project table
(descriptives_projects.csv): projects listed twice counted once, a plan group
as one project, the minimum and base as 06 and 08 set them.

  share          04_kink_bunching_figure: MPDU share, all projects, stacked at
                 its required minimum / other
  share_regime   07_kink_bunching_by_regime: the same, old schedule and ZTA 18-06
  bunching       02_bunching_figure: (A) MPDU share below 50%, (B) bonus used
                 against MPDU share, projects with a resolution base
  bunching_bonus panel B for the bonus-available projects only

And the wedge sample (08's wedge_sample, 100 projects, with 10's bounds):
  wedge_schedule units over base against MPDU share: bonus available with the
                 old Chapter 25A table and ZTA 18-06 (left); height limit, CR
                 lump at 15% and own schedule (right)
  tax_schedules  the two schedules side by side, old Chapter 25A table (left) and
                 ZTA 18-06 (right): MPDU share required against units over base
                 (top), and the price of one more unit beyond the 12.5% every
                 unit owes, in MPDUs (bottom; w in 10). Old 1% steps drawn as
                 the table has them on top and as a line below, as 10 prices them

Output: output/figures/dataset/*.png (one per figure above),
        output/tables/dataset_projects.md (one row per project) and
        output/tables/dataset_wedge.md (one row per wedge-sample project, with
        its bound), for docs/dataset_overview.md

Usage:
  python 11_dataset_figures.py
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

PROJECTS = ROOT / "output" / "tables" / "descriptives_projects.csv"
BOUNDS = ROOT / "output" / "tables" / "wedge_bounds.csv"
WEDGE_TABLE = ROOT / "output" / "tables" / "dataset_wedge.md"
FIG_DIR = ROOT / "output" / "figures" / "dataset"
TABLE = ROOT / "output" / "tables" / "dataset_projects.md"

BLUE, RED, GRAY, PURPLE = "#5b7fa6", "#b04a4a", "#888888", "#7a5c99"
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
    "font.size": 12, "axes.labelsize": 12, "xtick.labelsize": 11, "ytick.labelsize": 11,
    "legend.fontsize": 10, "axes.spines.top": False, "axes.spines.right": False,
})
MAIN_MAX = 35          # percent; 04's axis break, 07's last bin
GROUPS = ["bonus available", "ceiling at base", "height limit", "lump at 15%", "own schedule", "other program",
          "unclear", "base from approved units", "no resolution base"]
POSITIONS = ["below base", "at base", "between", "at 22%", "above 22%"]
OLD_LAST_STEP = (0.15 * 1.22 - 0.145 * 1.20) / 0.02 - 0.125   # 10's OLD_LAST: average price over the 20-22% lump


def share_all(d):
    """04: every project, 0.25-point bins, broken axis above MAIN_MAX."""
    groups = [d.loc[d["at_min"], "share_pct"], d.loc[~d["at_min"], "share_pct"]]
    labels = [f"At its required minimum (n = {d['at_min'].sum()})", f"Other projects (n = {(~d['at_min']).sum()})"]
    gap = d.loc[d["share_pct"] > MAIN_MAX, "share_pct"]
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(10, 4.4), sharey=True,
                                  gridspec_kw={"width_ratios": [7, 1], "wspace": 0.05})
    counts, _, _ = ax.hist(groups, bins=np.arange(0, MAIN_MAX + 0.25, 0.25), stacked=True, color=[RED, BLUE],
                           edgecolor="white", linewidth=0.3, label=labels)
    lo2, hi2 = np.floor(gap.min()) - 1, np.ceil(gap.max()) + 1
    w2 = max(1.0, (hi2 - lo2) / 12)
    ax2.hist(groups, bins=np.arange(lo2, hi2 + w2, w2), stacked=True, color=[RED, BLUE], edgecolor="white",
             linewidth=0.3)
    ymax = counts[-1].max() * 1.15
    ax.set_ylim(0, ymax)
    for k, lab, y, color, ls in [(12.5, "12.5% required minimum", 0.97, RED, "--"),
                                 (15, "15% kink / minimum", 0.89, PURPLE, "-."),
                                 (20, "20% kink", 0.97, PURPLE, "-.")]:
        ax.axvline(k, color=color, ls=ls, lw=0.8)
        left = k == 12.5
        ax.text(k - 0.2 if left else k + 0.2, ymax * y, lab, color=color, fontsize=9, va="top",
                ha="right" if left else "left")
    ax.legend(frameon=False, loc="center right")
    ax.set_ylabel("Projects")
    ax.set_title(f"MPDU share, all projects (n = {len(d)})", loc="left", fontsize=12)
    ax.set_xlim(0, MAIN_MAX)
    ax2.set_xlim(lo2, hi2)
    ax2.spines["left"].set_visible(False)
    ax2.tick_params(axis="y", left=False)
    for a, x in [(ax, 1), (ax2, 0)]:   # break marks
        a.plot([x - 0.01 * (1 if x else -7), x + 0.01 * (1 if x else 7)], [-0.02, 0.02], transform=a.transAxes,
               color="k", lw=0.8, clip_on=False)
    fig.supxlabel("MPDU share of total units (%)", fontsize=12, y=0.02)
    fig.subplots_adjust(left=0.07, right=0.98, bottom=0.14, top=0.92)
    return fig


def share_regime(d):
    """07: old schedule and ZTA 18-06 side by side; unknown regime left out."""
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    for ax, regime, title in [(axes[0], "old", "Accepted before 31 Oct 2018 (old schedule)"),
                              (axes[1], "new", "Accepted on or after 31 Oct 2018 (ZTA 18-06)")]:
        g = d[d["regime"] == regime]
        s = g["share_pct"].clip(upper=MAIN_MAX - 0.01)
        counts, _, _ = ax.hist([s[g["at_min"]], s[~g["at_min"]]], bins=np.arange(0, MAIN_MAX + 0.25, 0.25),
                               stacked=True, color=[RED, BLUE], edgecolor="white", linewidth=0.3,
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
        ax.set_xlim(0, MAIN_MAX)
        ax.set_title(f"{title}, n = {len(g)}", loc="left", fontsize=11)
        ax.set_xlabel(f"MPDU share of total units (%; above {MAIN_MAX}% piled at the right)")
        ax.legend(frameon=False, loc="center right", fontsize=9)
    axes[0].set_ylabel("Projects")
    fig.tight_layout()
    return fig


def bonus_panel(ax, o, title):
    """02 panel B: bonus used against MPDU share, with the Chapter 59 schedule."""
    top = 30
    s = np.linspace(0.125, 0.30, 200)
    ax.plot(100 * s, 100 * rules.bonus_pct(s), color="#b87878", lw=1.5, label="Bonus schedule (Chapter 59)")
    ax.axhline(0, color=GRAY, lw=0.8)
    used = 100 * o["bonus_used"]
    below = used < 0
    ax.scatter(o.loc[~below, "share_pct"].clip(upper=top), used[~below], s=22, color=BLUE, alpha=0.8,
               label="Built at or above base")
    ax.scatter(o.loc[below, "share_pct"].clip(upper=top), used[below].clip(lower=-60), s=22, facecolors="none",
               edgecolors=BLUE, alpha=0.8, label="Built below base (clipped at -60%)")
    for k, color, ls in [(12.5, "#b87878", "--"), (15, PURPLE, "-."), (20, PURPLE, "-.")]:
        ax.axvline(k, color=color, ls=ls, lw=0.8, alpha=0.5)
    ax.set_xlim(10, top)
    ax.set_ylim(-62, 40)
    ax.set_xlabel("MPDU share of total units (%)")
    ax.set_ylabel("Density bonus used (%)")
    ax.set_title(title, loc="left", fontsize=12)
    ax.legend(frameon=False, loc="lower right")


def bunching(d):
    """02: (A) MPDU share below 50%, 0.5-point bins, 30%+ pooled; (B) bonus used, projects with a base."""
    d = d[d["share_pct"] < 50]
    top = 30
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.6))
    counts, _, _ = ax1.hist(d["share_pct"].clip(upper=top - 0.01), bins=np.arange(5, top + 0.5, 0.5), color=BLUE,
                            edgecolor="white", linewidth=0.5)
    ymax = counts.max() * 1.18
    ax1.set_ylim(0, ymax)
    for (k, lab, color, ls), y in zip([(12.5, "12.5% required minimum", "#b87878", "--"),
                                       (15, "15% kink: 22% bonus", PURPLE, "-."),
                                       (20, "20% kink: 30% bonus", PURPLE, "-.")], [1.0, 0.9, 0.8]):
        ax1.axvline(k, color=color, ls=ls, lw=1)
        ax1.text(k + 0.35, ymax * y, lab, color=color, fontsize=9, va="top", ha="left",
                 bbox=dict(facecolor="white", edgecolor="none", pad=1))
    ax1.set_xlabel("MPDU share of total units (%)")
    ax1.set_ylabel("Projects")
    ax1.set_xlim(5, top)
    ax1.set_title(f"A. MPDU share (n = {len(d)} projects; {top}%+ pooled)", loc="left", fontsize=12)
    o = d[d["plan"].notna()]
    bonus_panel(ax2, o, f"B. Bonus used, projects with a base (n = {len(o)})")
    fig.tight_layout()
    return fig


def bunching_bonus(d):
    o = d[(d["group"] == "bonus available") & (d["share_pct"] < 50)]
    fig, ax = plt.subplots(figsize=(6.5, 4.6))
    bonus_panel(ax, o, f"Bonus used, bonus available (n = {len(o)})")
    fig.tight_layout()
    return fig


def old_bonus_pct(share):
    """Chapter 25A table before ZTA 18-06 (Bill 34-17 pp. 19-20): a bonus "up to" k% for 12.5% + 0.1k% MPDUs, k = 1
    to 20, and up to 22% for 15%; nothing more above 15%."""
    return np.where(share >= 0.15 - 1e-9, 0.22, np.minimum(np.floor(1000 * (share - 0.125) + 1e-6) / 100, 0.20))


def wedge_schedule(w):
    """Wedge sample: units over base against MPDU share, with the schedule each group faced."""
    w = w.assign(share_pct=100 * w["actual_units_mpdu"] / w["actual_units_total"],
                 used=(100 * w["bonus_used"]).clip(-40, 40))
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.8), sharey=True)
    s = np.linspace(0.125, 0.35, 2251)
    ax1.plot(100 * s, 100 * old_bonus_pct(s), color=BLUE, lw=1.3, drawstyle="steps-post",
             label="Old schedule (Chapter 25A table)")
    ax1.plot(100 * s, 100 * rules.bonus_pct(s), color=RED, lw=1.3, ls="--", label="ZTA 18-06")
    b = w[w["group"] == "bonus available"]
    for period, color, marker, lab in [("old", BLUE, "o", "old schedule"), ("new", RED, "s", "ZTA 18-06")]:
        g = b[b["period"] == period]
        ax1.scatter(g["share_pct"].clip(upper=34.9), g["used"], s=26, color=color, marker=marker, alpha=0.8,
                    edgecolors="white", linewidths=0.4, label=f"Project, {lab} ({len(g)})")
    ax1.set_title(f"Bonus available (n = {len(b)})", loc="left", fontsize=12)
    ax1.set_ylabel("Units over base (%; clipped at ±40)")
    ax1.legend(frameon=False, loc="lower right", fontsize=9)
    ax2.plot([12.5, 15, 15, 35], [0, 0, 100 * (1 / 0.85 - 1), 100 * (1 / 0.85 - 1)], color=PURPLE, lw=1.3,
             drawstyle="steps-post", label="CR lump: +17.6% at 15%")
    o = w[w["group"] != "bonus available"]
    for group, color, marker in [("height limit", GRAY, "^"), ("lump at 15%", PURPLE, "D"),
                                 ("own schedule", "#c9a227", "v")]:
        g = o[o["group"] == group]
        ax2.scatter(g["share_pct"].clip(upper=34.9), g["used"], s=26, color=color, marker=marker, alpha=0.85,
                    edgecolors="white", linewidths=0.4, label=f"{group[0].upper() + group[1:]} ({len(g)})")
    ax2.set_title(f"Height limit, CR lump at 15%, own schedule (n = {len(o)})", loc="left", fontsize=12)
    ax2.legend(frameon=False, loc="lower right", fontsize=9)
    for ax in (ax1, ax2):
        ax.axhline(0, color=GRAY, lw=0.8)
        ax.axhline(22, color=GRAY, lw=0.6, ls=":")
        ax.set_xlim(12, 35)
        ax.set_ylim(-42, 42)
        ax.set_xlabel("MPDU share of total units (%; above 35% at the right edge)")
    fig.tight_layout()
    return fig


def tax_schedules():
    """Old Chapter 25A table and ZTA 18-06: share required (top) and price of one more unit (bottom)."""
    eps, top, xmax = 1e-6, 22, 35
    b = np.linspace(-10, xmax, 4501) / 100                                   # units over base
    old_share = np.where(b <= 0, 0.125, np.where(b <= 0.20 + 1e-9, 0.125 + 0.001 * np.ceil(100 * b - 1e-6), 0.15))
    old_share = np.where(b > 0.22 + 1e-9, np.nan, old_share)
    new_share = np.maximum(rules.share_for_bonus(np.maximum(b, 0)), 0.125)
    n = 1 + b
    old_price = np.select([b <= 0, b <= 0.20, b <= 0.22], [0.0, 0.1 * (2 * n - 1), OLD_LAST_STEP], np.nan)
    new_m = lambda x: np.maximum(rules.share_for_bonus(np.maximum(x - 1, 0)), 0.125) * x
    new_price = np.where(b < 0, 0.0, (new_m(n + eps) - new_m(n)) / eps - 0.125)

    fig, axes = plt.subplots(2, 2, figsize=(12, 7.5), sharex=True, sharey="row")
    for col, (title, color, share, price) in enumerate([
            ("Before 31 Oct 2018: Chapter 25A table", BLUE, old_share, old_price),
            ("From 31 Oct 2018: ZTA 18-06", RED, new_share, new_price)]):
        a1, a2 = axes[0, col], axes[1, col]
        a1.plot(100 * b, 100 * share, color=color, lw=1.6)
        a2.plot(100 * b, price, color=color, lw=1.6)
        a1.set_title(title, loc="left", fontsize=12)
        for ax in (a1, a2):
            ax.axvline(0, color=GRAY, lw=0.6, ls=":")
            ax.axvline(top, color=GRAY, lw=0.6, ls=":")
            if col == 0:
                ax.axvspan(top, xmax, color=GRAY, alpha=0.15, lw=0)
    axes[0, 0].text(28.5, 22, "no bonus\nabove 22%", ha="center", va="center", fontsize=10, color="#444444")
    axes[1, 0].text(28.5, 0.9, "no bonus\nabove 22%", ha="center", va="center", fontsize=10, color="#444444")
    for ax, pts in [(axes[0, 0], [(20, 14.5, "14.5% for 20%"), (22, 15.0, "15% for 22%")]),
                    (axes[0, 1], [(22, 15.0, "15% for 22%"), (30, 20.0, "20% for 30%")])]:
        for x, y, lab in pts:
            ax.plot(x, y, "o", color="#444444", ms=4)
            below = lab.startswith("14.5")                  # keep clear of the 15% label just above
            ax.annotate(lab, (x, y), xytext=(8, -14) if below else (-6, 8), textcoords="offset points", ha="left" if below else "right",
                        fontsize=9)
    for ax, pts in [(axes[1, 0], [(0, 0.10, "0.10"), (20, 0.138, "0.138"), (22, OLD_LAST_STEP, "0.325 (average\nover the lump)")]),
                    (axes[1, 1], [(0, 1 / 8.8, "0.114"), (22, 1.44 / 8.8, "0.164"), (22, 0.7875, "0.79"),
                                  (100 / 3, float(new_price[np.argmin(abs(b - 1 / 3))]), "1.44 (Knowles, +33%)")])]:
        for x, y, lab in pts:
            ax.plot(x, y, "o", color="#444444", ms=4)
            ax.annotate(lab, (x, y), xytext=(-6, 6), textcoords="offset points", ha="right", fontsize=9)
    axes[0, 0].set_ylabel("MPDU share required (% of all units)")
    axes[1, 0].set_ylabel("Price of one more unit, in MPDUs\n(beyond the 12.5% it owes anyway)")
    axes[0, 0].set_ylim(12, 24)
    axes[1, 0].set_ylim(0, 1.6)
    for ax in axes[1]:
        ax.set_xlabel("Units over base (%)")
        ax.set_xlim(-10, xmax)
    fig.tight_layout()
    return fig


def wedge_table(w):
    order = ["zero", "upper", "upper (average)", "height binds", "exact", "interval (average upper)", "interval",
             "lower (average)", "inside last step", "not modeled"]
    t = w.assign(b=pd.Categorical(w["bound"], order, ordered=True)).sort_values(["b", "w_lo", "bonus_used",
                                                                                 "project_name"])
    num = lambda x: "" if pd.isna(x) else f"{x:.3f}"   # noqa: E731
    rows = pd.DataFrame({
        "Project": t["project_name"].str.replace("|", "/", regex=False),
        "Plan": t["plan"],
        "Group": t["group"],
        "Rules": t["period"],
        "Units": t["actual_units_total"].astype(int),
        "MPDUs": t["actual_units_mpdu"].astype(int),
        "Share %": (100 * t["actual_units_mpdu"] / t["actual_units_total"]).round(1),
        "Min %": (100 * t["min_share"]).round(1),
        "Base": t["frontier_base_units"].astype(int),
        "Over base %": (100 * t["bonus_used"]).map(lambda x: f"{x:+.1f}"),
        "Position": t["position"],
        "Bound": t["bound"],
        "w low": t["w_lo"].map(num),
        "w high": np.where(np.isinf(t["w_hi"]), "none", t["w_hi"].map(num)),
    })
    head = "| " + " | ".join(rows.columns) + " |\n|" + "---|" * len(rows.columns) + "\n"
    return head + "".join("| " + " | ".join(str(v) for v in r) + " |\n" for r in rows.itertuples(index=False))


def project_table(d):
    t = d.assign(g=pd.Categorical(d["group"], GROUPS, ordered=True),
                 p=pd.Categorical(d["position"], POSITIONS, ordered=True)).sort_values(["g", "p", "bonus_used",
                                                                                         "project_name"])
    pct = lambda x: "" if pd.isna(x) else f"{100 * x:+.1f}"   # noqa: E731
    rows = pd.DataFrame({
        "Project": t["project_name"].str.replace("|", "/", regex=False),
        "Plan": t["plan"].fillna(t["site_plan"]).fillna(""),
        "Year": t["year_offering"].astype("Int64").astype(str).replace("<NA>", ""),
        "Tenure": t["tenure"].fillna("").str.replace(r"^Rental.*", "Rental", regex=True).str.replace("For-Sale",
                                                                                                       "For-sale"),
        "Units": t["actual_units_total"].astype(int),
        "MPDUs": t["actual_units_mpdu"].astype(int),
        "Share %": (100 * t["actual_sh_mpdu"]).round(1),
        "Min %": (100 * t["min_share"]).round(1),
        "Rules": t["regime"],
        "Group": t["group"],
        "Base": t["frontier_base_units"].astype("Int64").astype(str).replace("<NA>", ""),
        "Over base %": t["bonus_used"].map(pct),
        "Position": t["position"].fillna(""),
        "Choice": np.where(t["choice"], "yes", ""),
        "Wedge": np.where(t["wedge_sample"], "yes", ""),
    })
    head = "| " + " | ".join(rows.columns) + " |\n|" + "---|" * len(rows.columns) + "\n"
    return head + "".join("| " + " | ".join(str(v) for v in r) + " |\n" for r in rows.itertuples(index=False))


def main():
    d = pd.read_csv(PROJECTS, dtype={"plan": str, "site_plan": str})
    d["share_pct"] = 100 * d["actual_sh_mpdu"]
    d["at_min"] = d["actual_units_mpdu"] == np.ceil(d["min_share"] * d["actual_units_total"] - 1e-9)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    for name, fig in [("share", share_all(d)), ("share_regime", share_regime(d)), ("bunching", bunching(d)),
                      ("bunching_bonus", bunching_bonus(d))]:
        fig.savefig(FIG_DIR / f"{name}.png", dpi=200)
        plt.close(fig)
    TABLE.write_text(project_table(d))

    w = pd.read_csv(BOUNDS, dtype={"plan": str})
    assert len(w) == d["wedge_sample"].sum(), "wedge_bounds.csv and the wedge sample differ"
    fig = wedge_schedule(w)
    fig.savefig(FIG_DIR / "wedge_schedule.png", dpi=200)
    plt.close(fig)
    fig = tax_schedules()
    fig.savefig(FIG_DIR / "tax_schedules.png", dpi=200)
    plt.close(fig)
    WEDGE_TABLE.write_text(wedge_table(w))
    print(f"wedge sample: {len(w)}; bounds {w['bound'].value_counts().to_dict()}")
    print(f"projects: {len(d)}; at its minimum {d['at_min'].sum()}; with a base {d['plan'].notna().sum()}; "
          f"regime {d['regime'].value_counts().to_dict()}")
    print(f"[saved] {FIG_DIR}/*.png; {TABLE}; {WEDGE_TABLE}")


if __name__ == "__main__":
    main()
