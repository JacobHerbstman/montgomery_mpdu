"""Census tract and ACS 2019 tract medians for each site plan.

Run code/01_data_collection/03_download_planning_gis.py and
07_copy_citycomparison_census.py first.

Each site plan's polygon (Montgomery Planning site plan layer) is placed in
the 2010-vintage census tract containing its representative point; plans
without a polygon use the layer's X/Y point (Maryland State Plane, feet).
The tract gets the ACS 2019 5-year medians from the Social Explorer extract:
median gross rent, median home value, median household income, renter share.

These are medians over the tract's whole housing stock, in 2019 dollars. They
locate a project in the county's rent distribution but understate rents in
new buildings, which is what the simulation's market rent should be.

Output: data/int/02_data_cleaning/06_site_plan_tracts.csv
  site_plan, tract_geoid, acs19_median_gross_rent, acs19_median_value,
  acs19_median_hh_income, acs19_renter_share, location_source

Usage:
  python 06_tract_rents.py
"""

from pathlib import Path

import geopandas as gpd
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
SITE_PLANS = RAW / "mcplanning" / "site_plans.geojson"
TRACTS = RAW / "acs_tract" / "tracts_2019_montgomery_md.geojson"
ACS = RAW / "acs_tract" / "R50079860_SL140.txt"
OUT_FILE = ROOT / "data" / "int" / "02_data_cleaning" / "06_site_plan_tracts.csv"

ACS_VARS = {
    "SE_A18009_001": "acs19_median_gross_rent",
    "SE_A10036_001": "acs19_median_value",
    "SE_A14006_001": "acs19_median_hh_income",
    "SE_A10060_001": "acs19_occupied_units",
    "SE_A10060_003": "acs19_renter_units",
}


def load_acs():
    d = pd.read_csv(ACS, sep="\t", dtype=str, encoding="latin-1",
                    usecols=["Geo_FIPS", "Geo_STATE", "Geo_COUNTY", *ACS_VARS])
    d = d[(d["Geo_STATE"] == "24") & (d["Geo_COUNTY"] == "031")]
    d = d.rename(columns={"Geo_FIPS": "tract_geoid", **ACS_VARS})
    for c in ACS_VARS.values():
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d["acs19_renter_share"] = d["acs19_renter_units"] / d["acs19_occupied_units"]
    return d.drop(columns=["Geo_STATE", "Geo_COUNTY", "acs19_occupied_units", "acs19_renter_units"])


def main():
    tracts = gpd.read_file(TRACTS)[["GEOID", "geometry"]].rename(columns={"GEOID": "tract_geoid"})
    sp = gpd.read_file(SITE_PLANS)[["APNO", "X", "Y", "geometry"]].rename(columns={"APNO": "site_plan"})

    has_poly = sp.geometry.notna() & ~sp.geometry.is_empty
    pts = sp.loc[has_poly, ["site_plan"]].copy()
    pts = gpd.GeoDataFrame(pts, geometry=sp.loc[has_poly].geometry.to_crs(26985).representative_point(),
                           crs=26985).to_crs(4326)
    pts["location_source"] = "polygon"
    xy = sp[~has_poly & sp["X"].notna() & sp["Y"].notna()]
    xy = gpd.GeoDataFrame(xy[["site_plan"]], crs=2248,  # MD State Plane, US feet
                          geometry=gpd.points_from_xy(xy["X"], xy["Y"])).to_crs(4326)
    xy["location_source"] = "xy_point"
    pts = pd.concat([pts, xy], ignore_index=True)

    j = gpd.sjoin(pts, tracts, how="left", predicate="within").drop(columns=["index_right", "geometry"])
    out = j.merge(load_acs(), on="tract_geoid", how="left").drop_duplicates("site_plan")
    out.to_csv(OUT_FILE, index=False)

    print(f"site plans located: {len(out):,} ({out['location_source'].value_counts().to_dict()})")
    print(f"  in a Montgomery tract: {out['tract_geoid'].notna().sum():,}; "
          f"with ACS median rent: {out['acs19_median_gross_rent'].notna().sum():,}")
    print(out["acs19_median_gross_rent"].describe().round(0).to_string())
    print(f"[saved] {OUT_FILE}")


if __name__ == "__main__":
    main()
