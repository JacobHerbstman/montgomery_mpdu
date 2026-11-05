"""Project table for site plans beyond the annual reports: 20+ unit site plans
approved from 2008 on, with MPDU counts, zoning at approval and base density
from their Planning Board resolutions.

Inputs (run first):
  code/01_data_collection/03_download_planning_gis.py
  code/01_data_collection/04_download_pb_resolutions.py --universe
  02_extract_resolution_text.py, 03_parse_resolutions.py,
  04_build_base_density.py, 07_site_plan_regime.py

One row per site plan in the Montgomery Planning site-plan layer with 20+
dwelling units (approved, else proposed) and a Planning Board date from
2008 on (not denied), plus:
  * layer: dates, approved/proposed units, site acres;
  * current zone: zoning block with the largest overlap. This is today's
    zoning; nearly all blocks date from the 2014 District Map Amendment
    (G-956) or later, so it differs from the zone at approval for most plans
    approved before 2014-10-30 (current_zone_after_approval);
  * zoning cases: the case labels (G-, E-, BA-, ...) of the zoning history
    annotations that fall on the site;
  * preliminary plan: the preliminary plan (1-) whose polygon overlaps the
    site plan the most, among plans with a Planning Board date on or before
    the site plan's; subdivision-level units and acres;
  * resolution (04 / 05): zone at approval, approved units, MPDU share and
    count, base density and route. The resolution is the one 05 picked for
    the plan when it has one, else the parsed resolution with the plan's
    exact number;
  * MPDU minimum (08) and whether the plan is in the annual reports.

zone_at_approval is the resolution's zone, else the current zone when the
plan was approved after its zoning block began (zone_source).
mpdus: the resolution's MPDU count, else round(MPDU share x approved units).

Output: data/int/02_data_cleaning/08_resolution_projects.csv

Usage:
  python 08_resolution_projects.py
"""

from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
MC = ROOT / "data" / "raw" / "mcplanning"
INT = ROOT / "data" / "int" / "02_data_cleaning"
OUT_FILE = INT / "08_resolution_projects.csv"

MIN_UNITS = 20
START = pd.Timestamp("2008-01-01")
CRS = 2248        # Maryland State Plane, feet


def ms(s):
    """Epoch-millisecond dates (bad values, e.g. year 9999, become NaT)."""
    if pd.api.types.is_datetime64_any_dtype(s):
        return s.dt.tz_localize(None) if s.dt.tz is not None else s
    s = pd.to_numeric(s, errors="coerce")
    return pd.to_datetime(s.where(s.abs() < 4e12), unit="ms")


def units(df):
    appr = df["APPR_DU_TOT"].fillna(0)
    return appr.where(appr > 0, df["PROP_DU_TOT"].fillna(0))


def load_site_plans():
    sp = gpd.read_file(MC / "site_plans.geojson").to_crs(CRS)
    sp["pb_date"] = ms(sp["PBDATE"])
    sp["units_layer"] = units(sp)
    keep = (sp["units_layer"] >= MIN_UNITS) & (sp["pb_date"] >= START) & (sp["DECISIONTYPE"] != "DENIED")
    sp = sp[keep].copy()
    sp["geometry"] = sp.geometry.make_valid()
    return sp.rename(columns={"APNO": "site_plan"})


def largest_overlap(left, right, cols, filt=None):
    """For each left row, the right row with the largest intersection area
    (optionally only pairs passing filt(joined) )."""
    j = gpd.overlay(left[["site_plan", "geometry"]], right[cols + ["geometry"]],
                    how="intersection", keep_geom_type=True)
    if filt is not None:
        j = filt(j)
    j["overlap_sf"] = j.area
    j = j.sort_values("overlap_sf", ascending=False).drop_duplicates("site_plan")
    return j.drop(columns="geometry").set_index("site_plan")


def main():
    sp = load_site_plans()
    print(f"site plans (20+ units, PB date >= {START.date()}): {len(sp):,}")
    sp["site_acres"] = sp.area / 43560

    # current zone
    zb = gpd.read_file(MC / "zoning_blocks.geojson").to_crs(CRS)
    zb["geometry"] = zb.geometry.make_valid()
    zb["zone_begin"] = ms(zb["BEGINDATE"])
    z = largest_overlap(sp, zb, ["LONGZONE", "zone_begin", "BEGINREASON"])

    # zoning history annotations on the site
    an = gpd.read_file(MC / "zoning_history_annotations.geojson").to_crs(CRS)
    an = an[an["TEXTSTRING"].notna()]
    aj = gpd.sjoin(sp[["site_plan", "geometry"]], an[["TEXTSTRING", "geometry"]], predicate="intersects")
    cases = aj.groupby("site_plan")["TEXTSTRING"].agg(lambda s: "; ".join(sorted(set(s.str.strip()))))

    # preliminary plan
    pp = gpd.read_file(MC / "preliminary_plans.geojson").to_crs(CRS)
    pp["geometry"] = pp.geometry.make_valid()
    pp = pp.rename(columns={"APNO": "prelim_plan"})
    pp["prelim_pb_date"] = ms(pp["PBDATE"])
    pp["prelim_units"] = units(pp)
    pp["prelim_acres"] = pp.area / 43560
    pbd = sp.set_index("site_plan")["pb_date"]
    pr = largest_overlap(sp, pp, ["prelim_plan", "prelim_pb_date", "prelim_units", "prelim_acres"],
                         filt=lambda j: j[j["prelim_pb_date"].isna()
                                          | (j["prelim_pb_date"] <= j["site_plan"].map(pbd))])

    out = pd.DataFrame({
        "site_plan": sp["site_plan"].values,
        "project_name": sp["PROJNAME"].values,
        "accept_date": ms(sp["ACCEPTDATE"]).values,
        "pb_date": sp["pb_date"].values,
        "decision": sp["DECISIONTYPE"].values,
        "units_approved_layer": sp["APPR_DU_TOT"].values,
        "units_proposed_layer": sp["PROP_DU_TOT"].values,
        "units_layer": sp["units_layer"].values,
        "site_acres": sp["site_acres"].round(3).values,
    }).set_index("site_plan")
    out["zone_current"] = z["LONGZONE"]
    out["zone_current_begin"] = z["zone_begin"]
    out["zone_current_reason"] = z["BEGINREASON"]
    out["current_zone_after_approval"] = out["zone_current_begin"] > out["pb_date"]
    out["zoning_cases"] = cases
    out = out.join(pr[["prelim_plan", "prelim_pb_date", "prelim_units", "prelim_acres"]])
    out["prelim_acres"] = out["prelim_acres"].round(3)

    # resolutions
    parsed = pd.read_csv(INT / "03_pb_resolutions_parsed.csv", dtype={"target_plan": str})
    base = pd.read_csv(INT / "04_base_density_by_plan.csv", dtype={"target_plan": str}).set_index("target_plan")
    usable = parsed[parsed["usable"].fillna(1).astype(bool)]
    exact = (usable[usable["plan_match"] == True]
             .sort_values("mcpb_no", ascending=False).drop_duplicates("target_plan").set_index("target_plan"))
    res_cols = ["file", "zone", "approved_units", "mpdu_pct", "mpdu_count", "tract_acres"]
    res = exact[res_cols].copy()
    # a staff report can serve several target plans: look up by file and plan
    by_file = parsed.drop_duplicates(["file", "target_plan"]).set_index(["file", "target_plan"])
    for p, f in base["file"].items():               # 05's choice wins
        res.loc[p, res_cols[1:]] = by_file.loc[(f, p), res_cols[1:]].values
        res.loc[p, "file"] = f
    res = res.add_prefix("res_")
    out = out.join(res)
    out["has_resolution"] = out.index.isin(parsed["target_plan"])
    b = base[["route", "base_units", "base_ratio", "implied_bonus", "earned_bonus", "base_consistent"]]
    out = out.join(b.add_prefix("res_"))

    out["zone_at_approval"] = out["res_zone"]
    out["zone_source"] = np.where(out["res_zone"].notna(), "resolution", None)
    cur_ok = out["zone_at_approval"].isna() & out["zone_current"].notna() & ~out["current_zone_after_approval"]
    out.loc[cur_ok, "zone_at_approval"] = out.loc[cur_ok, "zone_current"]
    out.loc[cur_ok, "zone_source"] = "current_zone"

    total = out["res_approved_units"].fillna(out["units_layer"])
    out["units"] = total
    out["mpdus"] = out["res_mpdu_count"]
    fill = out["mpdus"].isna() & out["res_mpdu_pct"].notna()
    out.loc[fill, "mpdus"] = np.round(out.loc[fill, "res_mpdu_pct"] / 100 * total[fill])
    out["mpdus_source"] = np.select([out["res_mpdu_count"].notna(), fill], ["count", "pct_x_units"], None)
    out["sh_mpdu"] = out["mpdus"] / out["units"]

    reg = pd.read_csv(INT / "07_site_plan_regime.csv", dtype={"site_plan": str}).drop_duplicates("site_plan")
    out = out.join(reg.set_index("site_plan")[["planning_area", "min_share", "date_regime"]])

    rep = pd.read_stata(INT / "01_mpdu_offerings_combined.dta")
    rep_plans = {p.strip() for s in rep["site_plan"] for p in str(s).split("/")}
    out["in_report"] = out.index.isin(rep_plans)

    out = out.reset_index().sort_values("pb_date")
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_FILE, index=False)

    n = len(out)
    print(f"with a downloaded resolution: {out['has_resolution'].sum()} / {n}")
    print(f"MPDUs from resolution: {out['mpdus'].notna().sum()} ({out['mpdus_source'].value_counts().to_dict()})")
    print(f"zone at approval: {out['zone_source'].value_counts(dropna=False).to_dict()}")
    print(f"consistent resolution base: {out['res_base_consistent'].fillna(False).astype(bool).sum()}")
    print(f"preliminary plan matched: {out['prelim_plan'].notna().sum()}; in annual reports: {out['in_report'].sum()}")
    print(f"[saved] {OUT_FILE}")


if __name__ == "__main__":
    main()
