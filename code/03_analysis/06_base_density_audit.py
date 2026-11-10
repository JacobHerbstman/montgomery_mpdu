"""Audit the resolution-based base density, one row per project.

Run 01_mpdu_simulation/main.py first.

Keeps the projects whose base comes from a Planning Board resolution
(base_source == "resolution"), not inferred from their MPDU count, plus the ones
put back below (OTHER_RULE, OTHER_PROGRAM). About a third come out below base,
i.e. built fewer units than zoning allowed without any bonus. This table puts
each project's checks side by side so the below-base cases can be read against
the resolution by hand.

Checks (columns):
  gis_agrees        approved units parsed from the resolution are within 5% of
                    the Planning GIS layer's APPR_DU_TOT for the same plan
  report_vs_res     annual-report total units / resolution approved units; far
                    from 1 means the report project is a phase of the plan, or
                    the wrong amendment was matched
  route_spread      largest / smallest candidate base across the five routes,
                    minus 1 (NaN when only one route applies)
  far_zone          CR-family, TS or CBD zone: the base is a floor area, turned
                    into units with an assumed unit size
  gross_acres       zone_table route with no net or usable area hand-coded, so
                    units/acre is applied to gross tract area
  mpdu_vs_min       MPDUs relative to the fewest required at the minimum share:
                    below / at / above. Above while below base is odd, since
                    extra MPDUs only pay through the bonus.

The base reaches a project as base_ratio (base / approved units), applied to the
report's total, so bonus_used = 1 / base_ratio - 1: a report project that is one
phase of a plan is not itself a problem, only a wrong approved-unit count or a
wrong base is. likely_cause takes the first that applies: at or above base;
within 5% of base (rounding); approved units disagree with GIS (misread or
wrong amendment); stated base or bonus, really below; gross acres (zone_table,
not a floor-area zone); floor area -> units (assumed unit size); CR floor area,
really below. manual is True where a value was hand-coded in manual_coding.csv.

One project can be listed twice: the same units under revised totals, another
plan number or another source, or one building or area of a listed plan.
data/raw/mpdu_annual_reports/project_fixes.csv (hand-made, optional) lists
them (fix = duplicate or part, same_as = the row kept) and the projects whose
report plan number is another project's (fix = other project's plan), so
their base is not theirs. All three are left out here.

tdr: density from a source other than the MPDU bonus, counted in the base:
the project bought transferable development rights (used), sat in a TDR zone
but built without them (available, not used), took floor area transferred
from neighbouring lots under an easement (density transfer), or none; tdrs is
the number of rights bought, where the documents give it. From
data/raw/mpdu_annual_reports/project_tdr.csv (hand-made, optional), checked
against each project's resolution or staff report: every project whose zone or
documents mention TDRs was read.

subsidy: why a project's MPDU share is not a market developer's response to
the bonus: LIHTC (the building was financed with tax credits; restricted_units
is the number of income-restricted units), LIHTC planned, LIHTC after completion
(a market building bought and converted later; its MPDU share was the original
developer's), HOC without tax credits, public land (the county set the share
when it sold the land), or none. From data/raw/mpdu_annual_reports/
project_subsidy.csv (hand-made, optional): every project with 20% MPDUs or more,
a nonprofit or HOC developer, a HUD LIHTC property within 100 m, or a county
Housing Initiative Fund loan was checked (Nov 3 2026).

impact_tax: the MPDU share was set at 25% for the county's development impact
tax exemption (Ch. 52, Sec. 52-41(g)(5) and 52-54(c)(5): no transportation or
school impact tax at 25% MPDUs or more), a second notch apart from the bonus:
stated (the staff report says so), likely (exactly 25%, no reason stated), or
none. From data/raw/mpdu_annual_reports/project_impact_tax.csv (hand-made,
optional). Both files match on site_plan, or on id where a row gives one (two
report projects on one plan, e.g. the Laureate and The Daley).

base_check: checked (the base was read against the project's own data table or
documents) or unverified (no data table: BASE_UNVERIFIED).

NAME_FIXES: the 2023 report's agreements table (p. 11) pairs some plan numbers
and unit counts with the neighbouring row's name and developer; the counts and
plan numbers agree with the resolutions, so only the name is corrected. The
2025 report lists some projects without a name; they get the name on their
site plan resolution.

OTHER_RULE: bases that 04_build_base_density.py drops because the bonus is
above the sliding MPDU schedule, where the bonus came from another rule. They
are put back here with their hand-coded base:
  - the 2014 CR rule that exempts MPDU floor area from FAR (Sec. 4.7.3.D.6.c.iii,
    15% MPDUs or more): the bonus is the MPDUs' own floor area, which passes the
    schedule above about 27% MPDUs;
  - the 2014 RE-1 MPDU optional method (Sec. 4.4.6.D): a flat 1.22 du/ac against
    the standard 1.09 for any MPDUs, so about 12% at the minimum share.

OTHER_PROGRAM: bases that 04 drops because the project went over base through
a density program other than the MPDU bonus (Jacob, Nov 3 2026: keep them,
flagged). Their bonus_used mixes the MPDU bonus with that program, so it is not
a measure of the MPDU bonus alone. Column other_program: Bethesda Overlay,
workforce housing, master plan bonus, PD zone bonus, ZTA 21-07 (floor area for
income-restricted housing exempt from FAR), or none.

MIN_SHARE_FIXES: minimums that 07_site_plan_regime.py sets from location and
date but the law sets otherwise. Bill 38-17 Sec. 2 reviews an applicant whose
sketch plan was accepted as complete before Oct 31, 2018 under the 12.5%
minimum (Jacob, Nov 9 2026).

Inputs:
  data/int/03_analysis/01_mpdu_simulation_results.csv
  data/raw/mpdu_annual_reports/project_fixes.csv
  data/raw/mpdu_annual_reports/project_tdr.csv
  data/raw/mpdu_annual_reports/project_subsidy.csv
  data/raw/mpdu_annual_reports/project_impact_tax.csv
  data/int/02_data_cleaning/04_base_density_by_plan.csv
  data/int/02_data_cleaning/03_pb_resolutions_parsed.csv (source text)
  data/raw/mcplanning/site_plans.geojson (APPR_DU_TOT)

Output: output/tables/base_density_audit.csv

Usage:
  python 06_base_density_audit.py
"""

from pathlib import Path

import numpy as np
import pandas as pd
import pyogrio

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "data" / "int" / "03_analysis" / "01_mpdu_simulation_results.csv"
BASE = ROOT / "data" / "int" / "02_data_cleaning" / "04_base_density_by_plan.csv"
PARSED = ROOT / "data" / "int" / "02_data_cleaning" / "03_pb_resolutions_parsed.csv"
SITE_PLANS = ROOT / "data" / "raw" / "mcplanning" / "site_plans.geojson"
OUT_FILE = ROOT / "output" / "tables" / "base_density_audit.csv"
FIXES = ROOT / "data" / "raw" / "mpdu_annual_reports" / "project_fixes.csv"
TDR = ROOT / "data" / "raw" / "mpdu_annual_reports" / "project_tdr.csv"
SUBSIDY = ROOT / "data" / "raw" / "mpdu_annual_reports" / "project_subsidy.csv"
IMPACT_TAX = ROOT / "data" / "raw" / "mpdu_annual_reports" / "project_impact_tax.csv"

ROUTES = ["stated_bonus", "stated_base", "cr_floor_area", "zone_table", "cr_mapped_fa"]
SNIPPET_CHARS = 300
BASE_UNVERIFIED = {
    # Wentworth House (820050340, Parcel E of G-801) is coded at plan level on the site-wide 1,350 du cap
    # (MCPB 22-066), which the Parcel G and H resolutions state, and grouped with Parcels F, G and H in 08
    "82005001A": ("unverified", "The Veridian: the approved 2005 staff report has no data table"),
    "820060380": ("unverified", "Heritage at Silver Spring: no data table"),
    # White Oak (82005018C, Whitehall Square Phase 2) takes Phase 1's ratio; checked against the 2014 staff
    # report's plan-wide table (29.34 ac x 4.39 = 128 du) and grouped with Phase 1 in 08
}
NAME_FIXES = {"820220020": "Park Montgomery", "820190130": "Hillandale Gateway",
              "820220060": "4725 Cheltenham Drive", "820220170": "Sligo Apartments",
              # unnamed in the 2025 report: the resolution's name
              "820220220": "4910-4920 Strathmore Avenue", "82012004C": "North Bethesda Market II",
              "820220100": "North Bethesda Center Parcel H", "820230080": "2115 East Jefferson Street",
              "820220110": "White Oak Apartments", "820220050": "PSTA", "820240040": "Springvale Terrace",
              "E20250010": "Tevis Place", "820240080": "Tregoning Property", "820210110": "Ashford Woods",
              "820190110": "Metro Tower"}
OTHER_PROGRAM = {   # plan: program, as checked in NOTES.md rounds 1-5
    "820180170": "Bethesda Overlay",    # The Edge: 138,083 sf Bethesda Overlay density above base
    "820190110": "Bethesda Overlay",    # Metro Tower: 188,506 sf
    "820190030": "Bethesda Overlay",    # 7607 Old Georgetown Road
    "82017003A": "Bethesda Overlay",    # St. Elmo
    "820200130": "Bethesda Overlay",    # 8015 Old Georgetown Road
    "820190100": "Bethesda Overlay",    # 4909 Auburn Avenue
    "820220060": "Bethesda Overlay",    # 4725 Cheltenham Drive (the 2023 report's "7340 Wisconsin Avenue")
    "820130220": "workforce housing",   # Shady Grove Station-Westside: base 960 + 192 TDR units, 116 workforce on top
    "82013022A": "workforce housing",   # The Daley, Laureate (same plan)
    "82013022E": "workforce housing",   # Westside Lennar phase (same plan)
    "820170140": "workforce housing",   # Elizabeth House III: Elizabeth Square's 10% workforce bonus on top of 22%
    "820060110": "master plan bonus",   # Preserve at Rock Creek: Upper Rock Creek master plan bonus, 0.2 to 0.4 du/ac
    "820040230": "PD zone bonus",       # Jefferson at Inigo's Crossing: the PD zone's own bonus
    "820220170": "ZTA 21-07",           # Sligo Apartments: income-restricted floor area exempt from FAR
    "82011006A": "workforce housing",   # The Core: 5.5 FAR vs CBD-2 5.0 and 143 to 161 ft for 17 WFHUs (59-A-6.18);
                                        # its base (292) includes the workforce density, so it sits at base
}
OTHER_RULE = {
    "820190080": "Knowles Manor: Sketch Plan 320180210 (accepted 13 Jun 2018), condition 1: "
                 "30,805 sf of MPDUs exempt from FAR under Sec. 59.4.7.3.D.6.c.iii",
    "820240080": "Tregoning: RE-1 MPDU optional method, 1.22 du/ac (46) against standard 1.09 (41.26), "
                 "6 MPDUs (MCPB 24-091 p. 8)",
}

MIN_SHARE_FIXES = {
    "820220070": (0.125, "Strathmore Square: Sketch Plan 320190010 accepted Aug 3, 2018, before Oct 31, 2018 "
                         "(Bill 38-17 Sec. 2); it chose 15% under the 2014 CR rule (Sec. 59.4.7.3.D.6.c.iii)"),
}


def matched_plan(site_plan, plans):
    """First plan of a composite "A/B" site plan that has a base (as in utils.attach_observed_base)."""
    for p in str(site_plan).split("/"):
        if p.strip() in plans:
            return p.strip()
    return None


def by_id_or_plan(d, f, col):
    """f's col for each row of d: on id where f gives one (two projects share a plan), else on site_plan."""
    assert set(f["id"].dropna()) <= set(d["id"]), f"not in the results: {set(f['id'].dropna()) - set(d['id'])}"
    assert set(f["site_plan"]) <= set(d["site_plan"]), \
        f"not in the results: {set(f['site_plan']) - set(d['site_plan'])}"
    on_id = f.dropna(subset=["id"]).set_index("id")[col]
    on_plan = f[f["id"].isna()].drop_duplicates("site_plan").set_index("site_plan")[col]
    return d["id"].map(on_id).fillna(d["site_plan"].map(on_plan))


def likely_cause(r):
    if not r["below_base"]:
        return "at or above base"
    if r["bonus_used"] > -0.05:
        return "within 5% of base (rounding)"
    if pd.notna(r["gis_agrees"]) and not r["gis_agrees"]:
        return "approved units disagree with GIS"
    if r["route"] in ("stated_base", "stated_bonus"):
        return "stated base, really below"
    if r["route"] == "zone_table" and not r["far_zone"]:
        return "units/acre x gross tract acres"
    if r["route"] == "cr_floor_area":
        return "CR floor area, really below"
    return "floor area -> units (assumed unit size)"


def main():
    s = pd.read_csv(RESULTS, dtype={"site_plan": str})
    if FIXES.exists():
        f = pd.read_csv(FIXES, dtype={"site_plan": str})
        listed = set(zip(f["site_plan"], f["total_units"], f["total_mpdus"], f["source"]))
        key = list(zip(s["site_plan"], s["actual_units_total"], s["actual_units_mpdu"], s["source"]))
        assert listed <= set(key), f"project_fixes.csv: not in the results: {listed - set(key)}"
        s = s[[k not in listed for k in key]]
        print(f"left out (project_fixes.csv): {f['fix'].value_counts().to_dict()}")
    put_back = set(OTHER_RULE) | set(OTHER_PROGRAM)
    s = s[(s["base_source"] == "resolution") | s["site_plan"].isin(put_back)].copy()

    b = pd.read_csv(BASE, dtype={"target_plan": str, "resolution_plan": str})
    b = b[b["base_consistent"] | b["target_plan"].isin(put_back)]
    s["plan"] = s["site_plan"].map(lambda sp: matched_plan(sp, set(b["target_plan"])))
    d = s.merge(b, left_on="plan", right_on="target_plan", how="left", suffixes=("", "_res"))
    other = d["plan"].isin(put_back)   # base as in utils.attach_observed_base
    d.loc[other, "frontier_base_units"] = np.maximum(
        1, np.round(d.loc[other, "actual_units_total"] * d.loc[other, "base_ratio"]))

    # a staff report can be filed under two plans, so match on plan and file
    src = pd.read_csv(PARSED, dtype={"target_plan": str},
                      usecols=["file", "target_plan", "manual", "approved_units_src", "tract_acres_src",
                               "density_snippets"])
    d = d.merge(src, on=["file", "target_plan"], how="left")
    for c in ["approved_units_src", "tract_acres_src", "density_snippets"]:
        d[c] = d[c].str.replace(r"\s+", " ", regex=True).str[:SNIPPET_CHARS]

    gis = pyogrio.read_dataframe(SITE_PLANS, read_geometry=False, columns=["APNO", "APPR_DU_TOT"])
    gis = gis.assign(APNO=gis["APNO"].str.strip()).drop_duplicates("APNO")
    d = d.merge(gis.rename(columns={"APNO": "plan", "APPR_DU_TOT": "gis_units"}), on="plan", how="left")
    d["gis_units"] = d["gis_units"].where(d["gis_units"] > 0)

    # checks
    d["bonus_used"] = d["actual_units_total"] / d["frontier_base_units"] - 1
    d["below_base"] = d["bonus_used"] < -0.005
    d["gis_agrees"] = ((d["approved_units"] / d["gis_units"] - 1).abs() <= 0.05).where(d["gis_units"].notna())
    d["report_vs_res"] = d["actual_units_total"] / d["approved_units"]
    cand = d[[f"base_{r}" for r in ROUTES]]
    d["n_routes"] = cand.notna().sum(axis=1)
    d["route_spread"] = (cand.max(axis=1) / cand.min(axis=1) - 1).where(d["n_routes"] > 1)
    d["far_zone"] = (d["route"].isin(["cr_floor_area", "cr_mapped_fa"])
                     | d["zone_norm"].fillna("").str.match(r"^(TS|CBD)"))
    d["gross_acres"] = (d["route"] == "zone_table") & d["density_acres"].isna()
    assert set(MIN_SHARE_FIXES) <= set(d["plan"]), \
        f"MIN_SHARE_FIXES: not in the results: {set(MIN_SHARE_FIXES) - set(d['plan'])}"
    fix = d["plan"].map({k: v[0] for k, v in MIN_SHARE_FIXES.items()})
    d["min_share"] = fix.fillna(d["min_share"])
    min_mpdus = np.ceil(d["min_share"] * d["actual_units_total"] - 1e-9)
    d["mpdu_vs_min"] = np.select([d["actual_units_mpdu"] < min_mpdus, d["actual_units_mpdu"] == min_mpdus],
                                 ["below", "at"], "above")
    d["likely_cause"] = d.apply(likely_cause, axis=1)

    d["tdr"], d["tdrs"] = "none", np.nan
    if TDR.exists():
        t = pd.read_csv(TDR, dtype={"site_plan": str}).drop_duplicates("site_plan")
        assert set(t["site_plan"]) <= set(d["site_plan"]), \
            f"project_tdr.csv: not in the results: {set(t['site_plan']) - set(d['site_plan'])}"
        d["tdr"] = d["site_plan"].map(t.set_index("site_plan")["tdr"]).fillna("none")
        d["tdrs"] = d["site_plan"].map(t.set_index("site_plan")["tdrs"])
    d["subsidy"], d["restricted_units"] = "none", np.nan
    if SUBSIDY.exists():
        u = pd.read_csv(SUBSIDY, dtype={"site_plan": str, "id": "Int64"})
        d["subsidy"] = by_id_or_plan(d, u, "subsidy").fillna("none")
        d["restricted_units"] = by_id_or_plan(d, u, "restricted_units")
    d["impact_tax"] = "none"
    if IMPACT_TAX.exists():
        x = pd.read_csv(IMPACT_TAX, dtype={"site_plan": str, "id": "Int64"})
        d["impact_tax"] = by_id_or_plan(d, x, "impact_tax").fillna("none")
    assert set(BASE_UNVERIFIED) <= set(d["plan"])
    d["base_check"] = d["plan"].map({k: v[0] for k, v in BASE_UNVERIFIED.items()}).fillna("checked")
    d["other_program"] = d["plan"].map(OTHER_PROGRAM).fillna("none")
    d["project_name"] = d["site_plan"].map(NAME_FIXES).fillna(d["project_name"])

    cols = ["id", "project_name", "site_plan", "plan", "resolution_plan", "doc_type", "file",
            "year_offering", "zone", "tdr", "tdrs", "subsidy", "restricted_units", "impact_tax", "base_check",
            "other_program", "route", "likely_cause",
            "actual_units_total", "actual_units_mpdu", "actual_sh_mpdu", "min_share", "mpdu_vs_min",
            "frontier_base_units", "bonus_used", "below_base",
            "approved_units", "gis_units", "gis_agrees", "report_vs_res",
            "tract_acres", "density_acres", "far_zone", "gross_acres", "manual",
            "base_units", "base_ratio", *[f"base_{r}" for r in ROUTES], "n_routes", "route_spread",
            "approved_units_src", "tract_acres_src", "density_snippets"]
    d = d[cols].sort_values(["below_base", "likely_cause", "bonus_used"], ascending=[False, True, True])

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    d.to_csv(OUT_FILE, index=False, float_format="%.4g")

    below = d[d["below_base"]]
    n_rule, n_program = int(d["plan"].isin(OTHER_RULE).sum()), int(d["plan"].isin(OTHER_PROGRAM).sum())
    print(f"projects with a resolution base: {len(d)} (put back: OTHER_RULE {n_rule}, OTHER_PROGRAM {n_program}), "
          f"below base: {len(below)}")
    print(f"parsed approved units agree with GIS (5%): {int(d['gis_agrees'].sum())} of {d['gis_agrees'].notna().sum()}")
    print("\nbelow base by route (below / all):")
    print(pd.crosstab(d["route"], d["below_base"]).to_string())
    print("\nlikely cause:")
    print(d["likely_cause"].value_counts().to_string())
    print("\nTDRs (project_tdr.csv):")
    print(d["tdr"].value_counts().to_string())
    print("\nsubsidy (project_subsidy.csv):")
    print(d["subsidy"].value_counts().to_string())
    print("\nimpact tax at 25% (project_impact_tax.csv):")
    print(d["impact_tax"].value_counts().to_string())
    print("\nother program (OTHER_PROGRAM):")
    print(d["other_program"].value_counts().to_string())
    print("\nbase check:")
    print(d["base_check"].value_counts().to_string())
    print("\nMPDUs vs minimum, below-base projects:")
    print(below["mpdu_vs_min"].value_counts().to_string())
    print(f"[saved] {OUT_FILE}")


if __name__ == "__main__":
    main()
