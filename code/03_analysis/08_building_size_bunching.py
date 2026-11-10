"""Building size relative to base density, by whether MPDUs could buy units above base.

Run 06_base_density_audit.py first.

On a site with base B, units up to B carry 0.125 MPDUs each; above B the MPDU
share must rise toward 15%, so each bonus unit carries about 0.26 MPDUs, up to
a 22% bonus at 15% MPDUs. That kink at B (and the stop or kink at 22%) exists
only where a unit bonus was available. Where base was a hard ceiling, a project
at base says nothing about the response to the kink, so each project is first
sorted by the rule it faced (bonus_rule), from its zone and the date its site
plan was accepted (date_regime, 07_site_plan_regime.py; DATE_FIXES where the
report's plan number has no GIS record; no date makes it unclear):
  plan cap          development plan, binding element or covenant caps total
                    units including MPDUs (PLAN_CAPS, checked in the resolutions)
  height cap        bonus available, but the building is at its height limit
                    at or below its base floor area, so the bonus had no room
                    (HEIGHT_CAPS, from the resolutions); only the CBD/CR choice
                    projects at base or within 15% below it were checked, so
                    the group is selected on position and is not a
                    comparison group
  approved units    base set from the approved units (stated bonus of 0)
  Bethesda Overlay  Bethesda Downtown plan area, own schedule (not modeled)
  RE-1 MPDU step    RE-1 under the 2014 code, MPDU optional method (Sec.
                    4.4.6.D): a flat 1.22 du/ac against the standard 1.09 for
                    any MPDUs, so no choice of share (RE1_STEP); own schedule
  ZTA 18-06         accepted on or after 31 Oct 2018: unit bonus in every zone
  CR points         CR zones, 2010 to Oct 2014 (59-C-15): no density above the
                    mapped FAR; extra MPDUs earn points toward reaching it
  CR lump at 15%    CR zones without a "T", Oct 2014 to Oct 2018 (2014 code
                    4.7.3.D.6.c): no unit bonus; MPDU floor area exempt from
                    FAR, which pays only at 15% MPDUs; also a CR plan accepted
                    after Oct 2018 whose density was set by an earlier sketch
                    plan under that rule (CR_LUMP)
  no bonus zone     R-90, R-60, R-40 under the 2014 code (PHED memo on ZTA
                    18-06, 20 Sep 2018, p. 2: MPDU density below the 2014
                    standard density)
  25A bonus         Chapter 25A table: CR "T" zones (T_ZONES; the parsed zone
                    drops the T); R-90, R-60, R-200 before Oct 2014 (old-code
                    MPDU density = standard x 1.22, e.g. R-60 5.0 -> 6.10); R-200
                    after (up to 12%); RE, R-30/R-20/R-10, RT, PD, RH; RNC before
                    Oct 2014 (the resolutions state the bonus); CBD and TS from
                    1 Apr 2005 (Ord. 15-35), and CBD plans heard after the
                    ordinance was adopted (CBD_HEARD)
  RMX bonus         RMX zones, old 59-C-10.3.7(c): master plan units "may be
                    increased by a number equal to the number of" MPDUs, up to
                    22% (quoted in ZTA 06-15)
  CBD before        CBD heard before Ord. 15-35 was adopted: the Council found
    Ord. 15-35      the CBD zones had no language letting residential density
                    rise for the MPDU bonus
  other program     went over base through a density program other than the
                    MPDU bonus (workforce housing, a master plan or PD zone
                    bonus, ZTA 21-07); bonus_used mixes the two, so it is not
                    the MPDU bonus alone (other_program, 06_base_density_audit.py).
                    Bethesda Overlay projects stay under Bethesda Overlay.
  unclear           C-2 and I-3 residential (old code text not found; UNCLEAR);
                    no zone parsed before Oct 2018
Sources and caveats: docs/NOTES.md. The zone parsed from the resolution
can be the current zone of an amendment (e.g. Century), and the code that
applied follows the application's review basis, which date_regime only
approximates.

PLAN_GROUPS: phases of one plan whose density limit and MPDU obligation are
set for the whole plan (Cabin Branch, Clarksburg Village, Whitehall Square), and buildings
listed separately under one capped plan (Park Potomac, Darcy/Flats, North Bethesda Center), are coded
at plan level, so they share one base ratio; they are summed into one row,
whose bonus_used is the group's units over its base, and whose flags list
those of its phases.

tdr: TDRs used, available but not used, density transfer, or none (06_base_density_audit.py).
subsidy: LIHTC, LIHTC planned, LIHTC after completion, HOC without tax
credits, public land, or none (06_base_density_audit.py). Except LIHTC after
completion, it means the project made no real choice of MPDU share, like a 15%
minimum.
impact_tax: stated, likely, or none: the share was set at 25% for the impact
tax exemption, not the bonus (06_base_density_audit.py).
base_check: checked or unverified (no data table) (06_base_density_audit.py).
other_program: Bethesda Overlay, workforce housing, master plan bonus, PD zone
bonus, ZTA 21-07, or none (06_base_density_audit.py).
min_share: the required MPDU share. Where it is 15% (high-income planning areas
and 15% master-plan areas, from Oct 2018), 15% MPDUs and the 22% bonus that
goes with them are the requirement, so a project there made no real choice at
the 15% kink. These projects are kept; a later sample of real choices would
drop them.

position: bonus_used = units / base - 1, against base (0) and the 22% top,
within one unit or 0.5% of base, whichever is larger.

wedge_sample: the project faced a known price for density (group bonus
available, height limit, lump at 15% or own schedule) and chose its own MPDU
share (no subsidy except LIHTC after completion, no 25% impact-tax share), so
its position on the schedule bounds its wedge on the density limit (Jacob, Nov
4 2026; height-limited projects stay in, their height wedge is not measured).

Output: output/tables/building_size_bunching.csv (one row per project),
        output/tables/project_group.csv (one row per report project: its plan
        group and group, for 09_descriptives.py) and
        output/figures/building_size_bunching.pdf

Usage:
  python 08_building_size_bunching.py
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "output" / "tables" / "base_density_audit.csv"
RESULTS = ROOT / "data" / "int" / "03_analysis" / "01_mpdu_simulation_results.csv"
TAB_FILE = ROOT / "output" / "tables" / "building_size_bunching.csv"
GROUP_FILE = ROOT / "output" / "tables" / "project_group.csv"
FIG_FILE = ROOT / "output" / "figures" / "building_size_bunching.pdf"

NEW_RULES = pd.Timestamp("2018-10-31")      # Bill 34-17 Sec. 3, ZTA 18-06
CODE_2014 = pd.Timestamp("2014-10-30")      # zoning rewrite
CBD_TS_BONUS = pd.Timestamp("2005-04-01")   # Ord. 15-35
TOP = 0.22
BLUE, RED, GRAY = "#5b7fa6", "#b04a4a", "#888888"
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
    "font.size": 12, "axes.labelsize": 12, "xtick.labelsize": 11, "ytick.labelsize": 11,
    "legend.fontsize": 10, "axes.spines.top": False, "axes.spines.right": False,
})

# caps on total units including MPDUs, from the resolutions (manual_coding_additions.csv)
PLAN_CAPS = {
    "820150120": "Glenmont: Development Plan G-862/G-863, 50.1 du/ac including MPDUs",
    "820130270": "Glenmont: Development Plan G-862/G-863, 50.1 du/ac including MPDUs",
    "820070180": "Darcy/Flats: Development Plan G-850, max 250 du including MPDUs",
    "82007008A": "Quince Trace: Schematic Development Plan G-839, 7.4 du/ac including MPDUs",
    "820050240": "National Park Seminary: Development Plan G-828, 280 du",
    "820110100": "Solaire Wheaton: LMA binding element, max 245 du including 12.5% MPDUs",
    "820170020": "North Quarter: private covenant, 109 du",
    "82004015A": "Park Potomac: Potomac Master Plan 600 du including 75 MPDUs (450 MF + 150 TH)",
    "82005038A": "Gallery Park: Development Plan G-824, 290 du including 40 MPDUs",
    "82009001A": "Stonehall: Development Plan Amendment 06-01, 46 du including 8 MPDUs",
    "82001010A": "Wisconsin Place: project plan cap of 1,050,000 sf total, office traded for housing",
    "820130040": "Chelsea Heights: SDP binding element, max 64 du including MPDUs",
    "820180160": "Ashton Market: LMA H-119 binding element, 20 market-rate du + 3 MPDUs",
    "820060070": "Rock Creek Overlook: Schematic Development Plan G-822, 30 du including MPDUs",
    "820120090": "Germantown Park: Zoning Case G-878 binding element, max 105 du including MPDUs",
    "820220020": "Park Montgomery: LMA H-140 binding element, max 217 du including MPDUs",
    "820040270": "Leesborough: G-798 binding element, max 201 du including MPDUs",
    "820210010": "Linthicum West: Clarksburg Master Plan, 225 du plus 28 MPDUs; Preliminary Plan 12005003A limited "
                 "to 253 including 32 MPDUs",
    "820070190": "Villa Cortese: Development Plan Amendment 07-1, Building V max 48 du including MPDUs",
    "820120070": "Little Falls Place (Hoyt Property): G-907 binding element, no more than 30 townhouses of which "
                 "no more than 5 MPDUs",
    "820220220": "4910-4920 Strathmore: LMA H-143 binding element, up to 125 du including a minimum of 15% MPDUs",
    "820120100": "Clarksburg Square: Development Plan G-832, 408 du including 51 MPDUs (11 du/ac)",
    "820060150": "Towns at Oak Hill (Gateway Park Residential): Schematic Development Plan G-833 binding element, "
                 "not more than 29 one-family attached units including MPDUs",
    "820040220": "Arora Hills (Greenway Village Ph. 3-5): Development Plan G-735, 1,330 du including MPDUs; 486 in "
                 "Phases 1-2, so this site plan is limited to 844",
    "820130140": "Kensington Overlook: LMA G-877, max 27 du including MPDUs",
    **dict.fromkeys(["82008011A", "820050340", "820180010", "820220100"],
                    "North Bethesda Center (Parcels F Aurora, E Wentworth House, G Arrowwood, H): Development Plan "
                    "G-801, 1,350 du for the whole site; 1,312 approved, 38 left (MCPB 22-066)"),
    "820150060": "Black Hill: Sector Plan 0.7 FAR total; residential is all of it left after the commercial",
    "820070220": "Clarksburg Town Center: Project Plan 9-94004, max 1,300 du; MCPB 09-015 re-approved the whole "
                 "town center at 1,213 du including 152 MPDUs",
    "820170160": "Mt. Prospect: LMA G-884 and MCPB 18-017 condition 12, max 187 du including 24 MPDUs "
                 "(master plan 170 + 17 TDRs)",
    **dict.fromkeys(["82006029A", "820070140", "820110080", "820100030", "820120150", "820180060"],
                    "Cabin Branch: Development Plan G-806, 1,886 du including MPDUs"),
    "820140170": "The Blairs: Project Plan 920130050 condition 1, 2,800 du on the 30.4-ac site including the 1,110 "
                 "existing (2.89 FAR, below the CBD-R2 5.0); F1-F2 is the first phase",
    "82005006A": "Bentley Park (Fairland Park Community): DPA 09-1 binding element, 248 du in the Southern "
                 "Portion of G-813 Part I including a maximum of 31 MPDUs",
}
# at the height limit at or below the base floor area: the bonus floor area had no room (CBD-1 60 ft, up to
# 90 ft, 59-C-6.235(b); CBD-2 143 ft, up to 200 ft)
HEIGHT_CAPS = {
    "82006025A": "Eleven55 Ripley: MCPB 10-65, 5.0 FAR at the cap, 1155 Ripley tower 200 ft (CBD-2 maximum)",
    "82006036B": "Flats 8300: MCPB 12-83, 3.0 FAR (CBD-1 optional maximum), 90 ft (CBD-1 maximum)",
    "820060280": "Argent: 2006 staff report, 125 du/ac x 0.77 ac = 96 du, 90 ft (CBD-1 maximum); all 96 LIHTC",
    "820130240": "Element 28: MCPB 13-137, 5.0 FAR at the cap, 143 ft; Bethesda Metro Core 'limited to 143 feet, "
                 "with the limited opportunity to reach 200 feet'",
    "820130050": "8415 Fenton Street: MCPB 13-26 data table, height permitted/approved 75/75 CBD, 60/60 Fenton "
                 "Village Overlay, 35/35 R-60; 257,002 sf permitted, 260,921 approved",
    "820170100": "Guardian Building: MCPB 17-091, office conversion (5 storeys on 6), 4.75 FAR at the cap, "
                 "138 ft of 145",
    "820060140": "1200 East West Highway: 2005 staff report data table, height 143 ft permitted, 142 approved "
                 "(14 storeys); 4.51 FAR of 5.0",
    "82005001A": "Veridian: March 2005 staff report, heights taper at 2:1 from 90 ft to 143 ft per the South "
                 "Silver Spring urban design guidelines; 4.66 FAR of 5.0",
    "820120080": "Fenwick: Project Plan 920110010 (MCPB 11-105) data table, height 60 ft required, 60 approved, at "
                 "the CBD edge next to one-family homes; 109 of 125 du/ac",
    "82008023A": "The Premier: Project Plan 920050020 staff report (19 Jan 2006), 13 storeys, 'the maximum height of "
                 "143 feet'; 152,740 sf (4.0 FAR); the 2011 conversion kept density and height",
    "820060370": "Cameron: Project Plan 92006003A staff report (20 Jul 2006), 15 storeys, 143 ft (the CBD-2 "
                 "maximum without a finding for 200); 4.82 FAR of 5.0",
    "820060380": "Heritage at Silver Spring: CBD-1 and South Silver Spring Overlay, 90 ft (the maximum), keeping "
                 "parts of two Locational Atlas buildings; source the Downtown Silver Spring description of the "
                 "proposal, no data table",
}
# CR zones mapped with a "T" ("H-145T" in the resolution): Chapter 25A bonus (2014 Sec. 4.5.2.C.2)
T_ZONES = {"82003007B", "820180220", "820170100", "820170040", "82016007A", "820150130", "820150090", "820160110"}
# phases of one plan whose density and MPDUs are set for the whole plan: one observation each
PLAN_GROUPS = {
    **dict.fromkeys(["82006029A", "820070140", "820110080", "820100030", "820120150", "820180060"],
                    "Cabin Branch (G-806)"),
    **dict.fromkeys(["820030020", "82003002B", "820050410"], "Clarksburg Village Phases I-II (1-01030)"),
    **dict.fromkeys(["820120020", "820130120"], "Pike & Rose (320110010)"),
    **dict.fromkeys(["820150040", "820150050"], "Chevy Chase Lake (32014003A/120150130)"),
    **dict.fromkeys(["820130220", "82013022A", "82013022E"], "Shady Grove Station-Westside (820130220)"),
    "820060110": "Preserve at Rock Creek (820060110)",
    # Phase 2 (amendment 82005018C, PB 22 May 2014) adds 3.04 ac and 22 TH (4 MPDUs); its data table sets
    # 128 du (29.34 ac x 4.39) and 20 MPDUs at 15% (16 existing + 4 proposed) for the whole plan
    **dict.fromkeys(["820050180", "82005018C"], "Whitehall Square (820050180)"),
    # two report rows under one plan cap, each with its own MPDUs (The Perry 61 of 450, Park Potomac
    # Townhomes 14 of 150: 75 of 600, the master plan's 75; The Darcy 13 of 88, The Flats 14 of 162)
    "82004015A": "Park Potomac (82004015A)",
    "820070180": "Darcy/Flats (820070180)",
    # four parcels under one G-801 cap of 1,350 du, each with its own MPDUs (MCPB 18-003, 22-066)
    **dict.fromkeys(["82008011A", "820050340", "820180010", "820220100"], "North Bethesda Center (G-801)"),
}
# zones whose old-code text on MPDU density I could not get, and documents that state no bonus
UNCLEAR = {
    "820040140": "Upstairs at Bethesda Row (Arlington East): C-2 residential (59-C-4.35, ZTA 01-08), 2.5 FAR; "
                 "staff report states no MPDU bonus",
    "820090140": "The Rae (Ourisman Ford): C-2 residential (59-C-4.35), 2.36 FAR of 2.5; MCPB 09-123 states "
                 "no MPDU bonus",
    "81989049I": "Montgomery Row at Rock Spring: I-3 residential, 1989 plan; documents state no MPDU rule",
}
# CBD plans heard after Ord. 15-35 was adopted (30 Nov 2004) whose date_regime is earlier
CBD_HEARD = {
    "81999002H": "Citron: site plan heard 13 Jul 2006, after Ord. 15-35; 12% bonus for 13.7% MPDUs (staff report)",
    "820050200": "Portico: heard 31 Mar 2005, after Ord. 15-35 was adopted (30 Nov 2004); 22% bonus for 15% MPDUs",
    "82005001A": "Veridian (Silver Spring Gateway): re-heard 17 Mar 2005, after Ord. 15-35 was adopted; "
                 "4.66 FAR of 5.0, 12.5% MPDUs",
}
# CR plans accepted after Oct 2018 whose density an earlier sketch plan set under the 2014 rule
CR_LUMP = {"820190080": "Knowles Manor: Sketch Plan 320180210 (accepted 13 Jun 2018) exempts the 30,805 sf of "
                        "MPDUs (30%) from FAR, Sec. 59.4.7.3.D.6.c.iii; MCPB 19-102 keeps the same density "
                        "under ZTA 18-06",
           "820190050": "850 Sligo Avenue: Sketch Plan 320180090 (filed 5 Jan 2018, MCPB 18-025) binds maximum "
                        "density 82,941 sf (3.0 FAR, the mapped maximum) and height 60 ft (H-60; Sector Plan limit "
                        "east of Fenton Street) at 12.5% MPDUs; site plan MCPB 19-039 keeps both"}
# RE-1 plans under the 2014 code that took the MPDU optional method's flat density
RE1_STEP = {"820240080": "Tregoning: RE-1 MPDU optional method, 1.22 du/ac (46) against standard 1.09 (41.26) "
                         "for the minimum 6 MPDUs (MCPB 24-091 p. 8); 2 of the 46 are development rights not built"}
# acceptance dates for plans whose report plan number has no GIS record, from the documents; as in
# 07_kink_bunching_by_regime.py, an amendment takes the original plan's date unless it created the units
DATE_FIXES = {
    "8-71011A": ("2005-01-18", "Woodlake: 59 townhouses added to the 1971 apartment plan, filed 18 Jan 2005"),
    "82016008C": ("2016-02-19", "The Astrid: site plan 81982098C (820160080) filed 19 Feb 2016; "
                                "the 2020 amendment cut density"),
    "8198806A": ("2021-05-05", "Sandy Spring Village: amendment 81988060A filed 5 May 2021 turned two office "
                               "buildings into the 56 units"),
    "E20250010": ("2025-02-12", "Tevis Place: MCPB 25-047, filed 12 Feb 2025"),
}
# RMX plan whose staff report states the 22% MPDU bonus on the master plan's units
RMX_BONUS = {"820030030": "Buckingham Station (Fairfield at Germantown): RMX-2 optional method, "
                          "residential NTE 22% above the master plan's 500 du (Preliminary Plan 1-02068 cap 610)"}

# carried from the simulation results for 09_descriptives.py (a plan group takes its first phase's)
DESCRIBE = ["tenure", "planning_area", "acs19_median_gross_rent", "is_fully_affordable"]

GROUPS = {   # bonus_rule -> group
    "ZTA 18-06": "bonus available", "25A bonus": "bonus available", "RMX bonus": "bonus available",
    "plan cap": "ceiling at base", "CR points": "ceiling at base", "no bonus zone": "ceiling at base",
    "CBD before Ord. 15-35": "ceiling at base", "height cap": "height limit",
    "CR lump at 15%": "lump at 15%", "Bethesda Overlay": "own schedule", "RE-1 MPDU step": "own schedule",
    "approved units": "base from approved units", "other program": "other program", "unclear": "unclear",
}
WEDGE_GROUPS = ["bonus available", "height limit", "lump at 15%", "own schedule"]


def bonus_rule(r):
    zone = str(r["zone"]).upper()
    if r["plan"] in PLAN_CAPS:
        return "plan cap"
    if r["other_program"] == "Bethesda Overlay":
        return "Bethesda Overlay"
    if r["other_program"] != "none":
        return "other program"
    if r["plan"] in HEIGHT_CAPS:
        return "height cap"
    if r["plan"] in UNCLEAR or pd.isna(r["date_regime"]) or (pd.isna(r["zone"]) and r["date_regime"] < NEW_RULES):
        return "unclear"
    if r["route"] == "stated_bonus" and r["base_ratio"] == 1:
        return "approved units"
    if r["master_plan_15"] == "BETHESDA DOWNTOWN PLAN":
        return "Bethesda Overlay"
    if r["plan"] in RE1_STEP:
        return "RE-1 MPDU step"
    if r["plan"] in CR_LUMP:
        return "CR lump at 15%"
    if r["date_regime"] >= NEW_RULES:
        return "ZTA 18-06"
    if r["plan"] in T_ZONES or r["plan"] in CBD_HEARD:
        return "25A bonus"
    if zone.startswith("CR"):
        return "CR points" if r["date_regime"] < CODE_2014 else "CR lump at 15%"
    if zone.startswith(("R-90", "R-60", "R-40")):
        return "25A bonus" if r["date_regime"] < CODE_2014 else "no bonus zone"
    if zone.startswith(("CBD", "TS")):
        return "25A bonus" if r["date_regime"] >= CBD_TS_BONUS else "CBD before Ord. 15-35"
    if zone.startswith("RMX"):
        return "RMX bonus"
    if zone.startswith("RNC") and r["date_regime"] < CODE_2014:
        return "25A bonus"
    if zone.startswith(("R-200", "RE-", "R-30", "R-20", "R-10", "RT", "PD", "RH", "R-H")):
        return "25A bonus"
    return "unclear"


def main():
    d = pd.read_csv(AUDIT, dtype={"plan": str, "site_plan": str})
    s = pd.read_csv(RESULTS, usecols=["id", "date_regime", "master_plan_15", *DESCRIBE], parse_dates=["date_regime"])
    d = d.merge(s, on="id", how="left")
    fixed = d["plan"].map({k: pd.Timestamp(v[0]) for k, v in DATE_FIXES.items()})
    assert d.loc[fixed.notna(), "date_regime"].isna().all(), "DATE_FIXES: plan already has a date"
    d["date_regime"] = d["date_regime"].fillna(fixed)
    d["bonus_rule"] = d.apply(bonus_rule, axis=1)
    d["group"] = d["bonus_rule"].map(GROUPS)
    d["note"] = d["plan"].map({**PLAN_CAPS, **HEIGHT_CAPS, **UNCLEAR, **RMX_BONUS, **CBD_HEARD, **CR_LUMP, **RE1_STEP})

    # a plan group's phases share one base ratio, so they are summed into one row
    d["plan_group"] = d["plan"].map(PLAN_GROUPS)
    g = d.dropna(subset=["plan_group"]).groupby("plan_group")
    one = g.first()
    sums = ["actual_units_total", "actual_units_mpdu", "frontier_base_units"]
    one[sums] = g[sums].sum()
    for c, default in [("tdr", "none"), ("subsidy", "none"), ("impact_tax", "none"), ("base_check", "checked"),
                       ("other_program", "none")]:
        one[c] = g[c].agg(lambda x: "; ".join(sorted(set(x) - {default})) or default)
    one = one.reset_index().assign(project_name=lambda x: x["plan_group"], id=np.nan,
                                   actual_sh_mpdu=lambda x: x["actual_units_mpdu"] / x["actual_units_total"],
                                   bonus_used=lambda x: x["actual_units_total"] / x["frontier_base_units"] - 1)
    projects = d[["id", "plan_group", "group"]].copy()
    projects["group"] = projects["plan_group"].map(one.set_index("plan_group")["group"]).fillna(projects["group"])
    d = pd.concat([d[d["plan_group"].isna()], one], ignore_index=True)

    tol = np.maximum(0.005, 1 / d["frontier_base_units"])
    b = d["bonus_used"]
    d["position"] = np.select([b < -tol, b <= tol, b < TOP - tol, b <= TOP + tol],
                              ["below base", "at base", "between", f"at {TOP:.0%}"], f"above {TOP:.0%}")
    d["wedge_sample"] = (d["group"].isin(WEDGE_GROUPS) & d["subsidy"].isin(["none", "LIHTC, after completion"])
                         & (d["impact_tax"] == "none"))

    cols = ["id", "project_name", "plan", "zone", "tdr", "subsidy", "impact_tax", "base_check", "other_program",
            "min_share", "date_regime", "route", "bonus_rule", "group", "note",
            "actual_units_total", "actual_units_mpdu", "actual_sh_mpdu", "frontier_base_units",
            "bonus_used", "position", "wedge_sample", "year_offering", *DESCRIBE]
    d = d[cols].sort_values(["group", "bonus_used"])
    TAB_FILE.parent.mkdir(parents=True, exist_ok=True)
    d.to_csv(TAB_FILE, index=False, float_format="%.4g")
    projects.astype({"id": int}).to_csv(GROUP_FILE, index=False)

    order = ["below base", "at base", "between", f"at {TOP:.0%}", f"above {TOP:.0%}"]
    print(f"projects with a resolution base: {len(d)} (plan groups counted once)")
    print(pd.crosstab(d["bonus_rule"], d["position"]).reindex(columns=order, fill_value=0).to_string())
    print()
    print(pd.crosstab(d["group"], d["position"]).reindex(columns=order, fill_value=0).to_string())

    # figure: bonus used, 1-point bins, for the projects that could buy density and those that could not
    bins = np.arange(-0.30, 0.41, 0.01)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4), sharey=True)
    for ax, group, color in [(axes[0], "bonus available", BLUE), (axes[1], "ceiling at base", RED)]:
        x = d.loc[d["group"] == group, "bonus_used"].clip(-0.295, 0.395)
        ax.hist(x, bins=bins, color=color, edgecolor="white", linewidth=0.3)
        for v, lab in [(0, "base"), (TOP, f"{TOP:.0%} bonus")]:
            ax.axvline(v, color=GRAY, ls="--", lw=0.8)
            ax.text(v + 0.005, ax.get_ylim()[1] * 0.95, lab, color=GRAY, fontsize=9, va="top")
        ax.set_title(f"{group.capitalize()} (n = {len(x)})", loc="left", fontsize=11)
        ax.set_xlabel("Units / base units - 1 (ends piled at -30% and +40%)")
    axes[0].set_ylabel("Projects")
    fig.tight_layout()
    FIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG_FILE)
    print(f"[saved] {TAB_FILE}; {GROUP_FILE}; {FIG_FILE}")


if __name__ == "__main__":
    main()
