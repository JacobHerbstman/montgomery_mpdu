"""Fill missing project totals with DHCA's MPDU layers and building permits.

Inputs
  data/raw/mcplanning/mpdu_rental_buildings.geojson   DHCA rental buildings, MPDUs by bedroom
  data/raw/mcplanning/mpdu_ownership_projects.geojson DHCA for-sale projects, MPDUs
  data/raw/mcplanning/site_plans.geojson              approved dwelling units (APPR_DU_TOT)
  data/int/02_data_cleaning/09_permit_units_by_stem.csv (09_permit_mpdu_projects.py)
  data/int/02_data_cleaning/01_mpdu_offerings_combined.dta

The DHCA layers count the MPDUs a project has in the program today, not at
approval: for-sale MPDUs drop out as their control periods end (10 years for
older projects) and some rentals hold only part of a site plan's MPDUs. The
site plan's approved units are a cap, often above what was built. Neither is
reliable alone, so a total is used only when two independent sources agree on
both numbers:
  * MPDUs: the DHCA count equals the MPDUs the annual reports show offered
    for the project;
  * units: the dwelling units permitted on the site plan (one-unit permits
    plus building permits' stated units, none missing) equal the approved
    units, which are then taken as the total (within 5% was not enough:
    approved and built totals still differed);
  * and the MPDUs meet the 12.5% legal minimum. An MPDU count can match one
    early offering of a project offered in phases (Wisconsin Place: 28 in
    the DHCA layer and in its 2008 offering, 55 in total), which shows up as
    a share below the minimum.
This fills report projects whose offering tables print no totals (2005-2006
FOIA reports). The same rule is checked on report projects that do have
totals, by recomputing them as if missing (printed).

DHCA projects not in the reports are written as candidates but not added:
DHCA counts plus approved units match report projects too rarely (printed).

Output
  data/int/02_data_cleaning/10_dhca_fills.csv       report projects given totals
  data/int/02_data_cleaning/10_dhca_candidates.csv  DHCA projects not in the reports
"""

import re
import warnings
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore", category=RuntimeWarning)

ROOT = Path(__file__).resolve().parents[2]
MC = ROOT / "data" / "raw" / "mcplanning"
INT = ROOT / "data" / "int" / "02_data_cleaning"
OUT_FILLS = INT / "10_dhca_fills.csv"
OUT_CANDIDATES = INT / "10_dhca_candidates.csv"

NEAR_FT = 300          # DHCA points to the nearest site plan with approved units
UNITS_AGREE = 0.0      # permitted vs approved units: must be equal
MIN_SHARE = 0.125      # legal minimum, as a plausibility check on filled totals
BEDROOM_COLS = ["EFFICIENCY", "ONE_BEDROOM", "ONE_BEDROOM_AND_DEN", "F2_BEDROOMS__1_BATHROOM",
                "F2_BEDROOMS__2_BATHROOMS", "F3_BEDROOMS"]


def name_key(s):
    s = str(s or "").lower()
    s = re.sub(r"\b(the|at|aka|fka|apartments?|condominiums?|townhomes)\b", " ", s)
    return re.sub(r"[^a-z0-9]", "", s)


def load_dhca():
    own = gpd.read_file(MC / "mpdu_ownership_projects.geojson")
    own = own.assign(name=own["PROJECTNAME"], mpdus=own["MPDUS"], kind="ownership")
    ren = gpd.read_file(MC / "mpdu_rental_buildings.geojson")
    # cells read "15, Rent: $1,444": the leading number is the MPDU count
    ren["mpdus"] = ren[BEDROOM_COLS].apply(
        lambda r: sum(int(re.match(r"\s*(\d+)", str(v)).group(1)) for v in r
                      if v and re.match(r"\s*\d", str(v))), axis=1)
    ren = ren.assign(name=ren["NAME"], kind="rental")
    d = pd.concat([own[["name", "mpdus", "kind", "geometry"]], ren[["name", "mpdus", "kind", "geometry"]]])
    d = gpd.GeoDataFrame(d, geometry="geometry", crs=own.crs)
    return d[d.geometry.notna() & ~d.geometry.is_empty].to_crs(2248).reset_index(drop=True)


def place(d):
    sp = gpd.read_file(MC / "site_plans.geojson")[["APNO", "APPR_DU_TOT", "geometry"]].to_crs(2248)
    j = gpd.sjoin_nearest(d, sp[sp["APPR_DU_TOT"] > 0], max_distance=NEAR_FT, distance_col="dist_ft")
    j = j.sort_values("dist_ft")
    j = j[~j.index.duplicated()]
    d = d.join(j[["APNO", "APPR_DU_TOT", "dist_ft"]])
    d = d.rename(columns={"APNO": "site_plan", "APPR_DU_TOT": "approved_units"})
    d["stem"] = d["site_plan"].str[:8]
    return pd.DataFrame(d.drop(columns="geometry"))


def report_projects():
    rep = pd.read_stata(INT / "01_mpdu_offerings_combined.dta")
    rep["key"] = rep["project_name"].map(name_key)
    rep["aka_key"] = rep["aka"].map(name_key)
    g = rep.groupby(["key", "site_plan"], dropna=False)
    out = g.agg(project_name=("project_name", "first"), aka_key=("aka_key", "first"),
                total_units=("total_units", "max"), total_mpdus=("total_mpdus", "max"),
                offered=("mpdus_in_offering", "sum"), first_year=("offering_year", "min")).reset_index()
    out["stem"] = out["site_plan"].str[:8]
    return out[out["key"] != ""]


def same_name(a, b):
    return bool(a) and bool(b) and (a in b or b in a)


def main():
    d = place(load_dhca())
    units = pd.read_csv(INT / "09_permit_units_by_stem.csv", dtype={"stem": str})
    d = d.merge(units[["stem", "permit_units", "buildings_missing_units"]], on="stem", how="left")
    d["units_agree"] = (d["buildings_missing_units"].eq(0)
                        & ((d["permit_units"] - d["approved_units"]).abs()
                           <= UNITS_AGREE * d["approved_units"]))
    d["key"] = d["name"].map(name_key)
    rp = report_projects()

    # each DHCA project to the report project with the same name
    rows = []
    for i, r in d.iterrows():
        hit = rp[[same_name(r["key"], k) or same_name(r["key"], a) for k, a in zip(rp["key"], rp["aka_key"])]]
        for _, h in hit.iterrows():
            rows.append({"dhca": i, "project_name": h["project_name"], "report_site_plan": h["site_plan"],
                         "first_year": h["first_year"], "rep_units": h["total_units"],
                         "rep_mpdus": h["total_mpdus"], "offered": h["offered"]})
    m = d.join(pd.DataFrame(rows).set_index("dhca"), how="left")
    meets_min = m["mpdus"] >= np.ceil(MIN_SHARE * m["approved_units"] - 1e-9)
    m["rule"] = m["units_agree"] & (m["mpdus"] == m["offered"]) & meets_min

    # check: the rule on report projects that have totals
    chk = m[m["rule"] & m["rep_units"].notna()]
    ok = (chk["approved_units"] == chk["rep_units"]) & (chk["mpdus"] == chk["rep_mpdus"])
    print(f"rule checked on report projects with totals: {len(chk)}; both totals exact {ok.mean():.0%}; "
          f"share within 0.5 pt {((chk['mpdus'] / chk['approved_units'] - chk['rep_mpdus'] / chk['rep_units']).abs() <= 0.005).mean():.0%}")
    print(chk.assign(exact=ok)[["name", "kind", "mpdus", "approved_units", "rep_mpdus", "rep_units", "exact"]]
          .to_string(index=False))

    fills = m[m["rule"] & m["rep_units"].isna()].copy()
    fills = fills.rename(columns={"approved_units": "total_units", "mpdus": "total_mpdus"})
    fills = fills[["project_name", "report_site_plan", "first_year", "name", "kind", "site_plan",
                   "total_units", "total_mpdus", "offered", "permit_units"]]
    fills.to_csv(OUT_FILLS, index=False)
    print(f"\nreport projects without totals filled: {len(fills)}")
    print(fills.to_string(index=False))

    # DHCA projects with no report counterpart by name or site plan stem
    report_stems = set(rp["stem"].dropna())
    cand = m[m["project_name"].isna() & ~m["stem"].isin(report_stems)].copy()
    rental_chk = m[(m["kind"] == "rental") & m["units_agree"] & m["rep_units"].notna()]
    rok = (rental_chk["mpdus"] / rental_chk["approved_units"]
           - rental_chk["rep_mpdus"] / rental_chk["rep_units"]).abs() <= 0.005
    print(f"\nDHCA projects not in the reports: {len(cand)} ({cand['kind'].value_counts().to_dict()}); "
          f"with units agreeing: {cand['units_agree'].sum()}")
    print(f"  (not added: DHCA count / approved units match report shares within 0.5 pt for only "
          f"{rok.mean():.0%} of {len(rental_chk)} rental report projects with agreeing units)")
    cand.drop(columns=["key"]).to_csv(OUT_CANDIDATES, index=False)
    print(f"[saved] {OUT_FILLS}\n[saved] {OUT_CANDIDATES}")


if __name__ == "__main__":
    main()
