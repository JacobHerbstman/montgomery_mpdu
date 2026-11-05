"""MPDU minimum (12.5% or 15%) for each site plan, from its location and the
date its application was accepted.

Run code/01_data_collection/03_download_planning_gis.py first.

Rules (Chapter 25A as described in the 2024 MPDU staff report, policy/):
  * High-income planning areas (Bill 38-17, effective October 2018): 15% in
    planning areas designated by the Planning Board each year. The minimum is
    set "at the time the Planning Board accepts an application as complete",
    so the application's acceptance date picks the designation in force.
    Designation lists: data/raw/mcplanning/high_income_planning_areas_{2019..2026}.
    A list applies from its adoption date until the next list is adopted.
    Adoption dates: 2024-01-18 and 2025-01-23 (Planning Board staff reports);
    VERIFY the others, assumed January 31 of the year. Acceptances from
    October 2018 until the first (2019) list is adopted get no designation.
  * 15% master-plan areas (mpdu_15pct_master_plans.geojson): Bethesda Downtown
    (Bethesda Overlay Zone), Silver Spring Downtown and Adjacent Communities,
    and later plans, from each plan's approval date. VERIFY: SSDAC and Great
    Seneca have no approval date in the layer; SSDAC is taken as 2022-10-25
    (2022 plan) and Great Seneca is not applied.
  Note: the Bethesda Overlay Zone also has its own bonus schedule (17.5% plus
  0.1% per 0.1% of MPDUs above 17.5%), which the simulation does not model.

Each site plan is placed by the representative point of its polygon (or its
X/Y point when there is no polygon). The date is ACCEPTDATE, or SUBMITDATE
when acceptance is missing (date_source says which). Amendments (plan numbers
ending in a letter) keep the minimum of the original application, so they take
the original plan's date (original_plan, date_source "original_..."). Acceptances in January to
March are flagged (designation_boundary): they may fall under the previous
year's list if that year's list was adopted later than assumed.

Output: data/int/02_data_cleaning/07_site_plan_regime.csv
  site_plan, original_plan, date_regime, date_source, planning_area, designation_year,
  high_income_area, master_plan_15, bethesda_downtown, ssdac,
  designation_boundary, min_share, override_note (OVERRIDES: resolution sets a
  different minimum, e.g. review under an older preliminary plan's zoning)

Usage:
  python 07_site_plan_regime.py
"""

from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
MC = ROOT / "data" / "raw" / "mcplanning"
OUT_FILE = ROOT / "data" / "int" / "02_data_cleaning" / "07_site_plan_regime.csv"

REQUIREMENT_START = pd.Timestamp("2018-10-01")
DESIGNATION_YEARS = range(2019, 2027)
ADOPTED = {2024: "2024-01-18", 2025: "2025-01-23"}           # staff reports
ASSUMED_ADOPTION = "{y}-01-31"                                # VERIFY other years
MASTER_PLAN_DATES = {                                         # when the layer has no date
    "SILVER SPRING DOWNTOWN - ADJACENT COMMUNITIES PLAN": "2022-10-25",   # VERIFY
}
MASTER_PLAN_SKIP = {"GREAT SENECA PLAN"}                      # no date; not applied
# Site plans whose resolution sets a different minimum than location and date
# imply (checked against the resolution text)
OVERRIDES = {
    "820220100": (0.125, "North Bethesda Center Parcel H: reviewed under the TS-M zoning of Preliminary Plan "
                         "120040490 (2004); resolution requires 12.5% MPDUs (MCPB 22-066)"),
}


def site_plan_points():
    sp = gpd.read_file(MC / "site_plans.geojson")
    has_poly = sp.geometry.notna() & ~sp.geometry.is_empty
    pts = sp.copy()
    pts.loc[has_poly, "geometry"] = sp.loc[has_poly].geometry.to_crs(26985).representative_point().to_crs(4326)
    xy = ~has_poly & sp["X"].notna() & sp["Y"].notna()
    pts.loc[xy, "geometry"] = gpd.GeoSeries(gpd.points_from_xy(sp.loc[xy, "X"], sp.loc[xy, "Y"]),
                                            index=sp.index[xy], crs=2248).to_crs(4326)
    pts = pts[has_poly | xy].set_crs(4326, allow_override=True)
    acc = pd.to_datetime(pts["ACCEPTDATE"], unit="ms", errors="coerce")
    sub = pd.to_datetime(pts["SUBMITDATE"], unit="ms", errors="coerce")
    pts["own_date"] = acc.fillna(sub).dt.normalize()
    pts["own_source"] = np.where(acc.notna(), "accepted", "submitted")
    pts = pts.rename(columns={"APNO": "site_plan"})

    # Amendments (8200xxxxA, ...B) keep the MPDU minimum of the original
    # application, so they take the original plan's (8200xxxx0) date.
    orig = pts["site_plan"].str.slice(0, 8) + "0"
    first = pts.drop_duplicates("site_plan").set_index("site_plan")
    is_amend = pts["site_plan"].str[-1].str.isalpha() & orig.isin(first.index)
    pts["date_regime"] = np.where(is_amend, orig.map(first["own_date"]), pts["own_date"])
    pts["date_regime"] = pd.to_datetime(pts["date_regime"])
    pts["date_source"] = np.where(is_amend, "original_" + orig.map(first["own_source"]).fillna(""),
                                  pts["own_source"])
    pts["original_plan"] = np.where(is_amend, orig, None)
    return pts[["site_plan", "original_plan", "date_regime", "date_source", "geometry"]]


def within(points, polys, name_col):
    j = gpd.sjoin(points[["geometry"]], polys[[name_col, "geometry"]].to_crs(4326), how="left", predicate="within")
    return j[~j.index.duplicated()][name_col]


def designation_year(d):
    """Designation list in force on date d (None before the first list)."""
    if pd.isna(d) or d < REQUIREMENT_START:
        return None
    for y in sorted(DESIGNATION_YEARS, reverse=True):
        if d >= pd.Timestamp(ADOPTED.get(y, ASSUMED_ADOPTION.format(y=y))):
            return y
    return None


def main():
    pts = site_plan_points()
    pts["planning_area"] = within(pts, gpd.read_file(MC / "planning_areas.geojson"), "NAME")
    pts["designation_year"] = pts["date_regime"].map(designation_year)

    # high-income area under the list in force at the acceptance date
    hi = pd.Series(False, index=pts.index)
    for y in DESIGNATION_YEARS:
        rows = pts["designation_year"] == y
        if rows.any():
            inside = within(pts[rows], gpd.read_file(MC / f"high_income_planning_areas_{y}.geojson"), "NAME")
            hi.loc[inside.index] = inside.notna().astype(bool)
    pts["high_income_area"] = hi

    # 15% master-plan areas, from each plan's approval date
    mp = gpd.read_file(MC / "mpdu_15pct_master_plans.geojson")
    mp = mp[~mp["NAME"].isin(MASTER_PLAN_SKIP)].copy()
    mp["approved"] = pd.to_datetime(mp["APPROVALDATE"], unit="ms", errors="coerce").dt.normalize()
    mp["approved"] = mp["approved"].fillna(mp["NAME"].map(MASTER_PLAN_DATES).pipe(pd.to_datetime))
    j = gpd.sjoin(pts[["date_regime", "geometry"]], mp[["NAME", "approved", "geometry"]].to_crs(4326),
                  how="left", predicate="within")
    j = j[j["NAME"].notna() & (j["date_regime"] >= j["approved"])]
    pts["master_plan_15"] = j.groupby(level=0)["NAME"].first()
    pts["bethesda_downtown"] = pts["master_plan_15"].eq("BETHESDA DOWNTOWN PLAN")
    pts["ssdac"] = pts["master_plan_15"].eq("SILVER SPRING DOWNTOWN - ADJACENT COMMUNITIES PLAN")

    pts["designation_boundary"] = pts["designation_year"].notna() & pts["date_regime"].dt.month.le(3)
    pts["min_share"] = np.where(pts["high_income_area"] | pts["master_plan_15"].notna(), 0.15, 0.125)
    pts["override_note"] = None
    for plan, (share, note) in OVERRIDES.items():
        rows = pts["site_plan"] == plan
        pts.loc[rows, "min_share"] = share
        pts.loc[rows, "override_note"] = note

    out = pd.DataFrame(pts.drop(columns="geometry"))
    out["date_regime"] = out["date_regime"].dt.date
    out.to_csv(OUT_FILE, index=False)
    print(f"site plans: {len(out):,} ({out['date_source'].value_counts().to_dict()})")
    print(f"  in a planning area: {out['planning_area'].notna().sum():,}")
    print(f"  15% minimum: {int((out['min_share'] == 0.15).sum())} "
          f"(high-income area {int(out['high_income_area'].sum())}, master plan {int(out['master_plan_15'].notna().sum())}: "
          f"{out['master_plan_15'].value_counts().to_dict()})")
    print(f"[saved] {OUT_FILE}")


if __name__ == "__main__":
    main()
