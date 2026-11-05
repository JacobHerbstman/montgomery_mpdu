"""MPDU projects from county building permits.

Inputs
  data/raw/permits/commercial_permits_i26v-w6bd.csv   (09_download_commercial_permits.py)
  data/raw/permits/residential_permits_m88u-pqki.csv  (05_download_county_state_data.py)
  data/raw/mcplanning/site_plans.geojson              (03_download_planning_gis.py)
  data/int/02_data_cleaning/01_mpdu_offerings_combined.dta

Permit descriptions that mention MPDUs come in two kinds:
  * building-level: a multifamily building permit that states its MPDU count,
    usually with its unit count ("185 residential RENTAL UNITS including 46
    MPDUs", "NO MPDU'S");
  * unit-level: a permit for one townhouse, duplex or two-over-two unit that
    is an MPDU ("Lot 61 ... THIS UNIT IS AN MPDU"). Each counts as one MPDU.
"Pure model" permits are plan reviews of a house model, not dwellings, and
are dropped (site-specific permits refer back to them).

Each permit is placed in a Planning site plan by its coordinates: among the
site plans containing the point, the one with approved dwelling units whose
Planning Board date is the latest before the permit, else the latest. A
project is the site plan's 8-character stem (the original plan and its
amendments).

Project counts
  * building-level: total units and MPDUs summed over distinct buildings
    (permits with the same address and counts are one building).
  * unit-level: MPDUs = unit-level MPDU permits; total units = every new
    one-unit dwelling permit in the stem (MPDU or not), so both counts come
    from the same permit coverage. Stems that also hold building-level
    permits are left to the building-level count.
Permits start in 2000, so projects partly built earlier are undercounted;
units_coverage = permit units / approved dwelling units on the site plan
flags them.

Projects whose stem appears in the annual-report offerings are kept but
flagged in_reports = 1; they are not added to the sample, and serve to check
the permit counts against the reports (printed).

Output
  data/int/02_data_cleaning/09_permit_mpdu_permits.csv   one row per MPDU permit
  data/int/02_data_cleaning/09_permit_mpdu_projects.csv  one row per project
  data/int/02_data_cleaning/09_permit_units_by_stem.csv  dwelling units permitted per
      site plan stem (one-unit permits plus building permits' stated units;
      buildings_missing_units counts building permits that state none)
"""

import html
import re
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
INT = ROOT / "data" / "int" / "02_data_cleaning"
PERMIT_FILES = {
    "commercial": RAW / "permits" / "commercial_permits_i26v-w6bd.csv",
    "residential": RAW / "permits" / "residential_permits_m88u-pqki.csv",
}
SITE_PLANS = RAW / "mcplanning" / "site_plans.geojson"
OFFERINGS = INT / "01_mpdu_offerings_combined.dta"
OUT_PERMITS = INT / "09_permit_mpdu_permits.csv"
OUT_PROJECTS = INT / "09_permit_mpdu_projects.csv"
OUT_UNITS = INT / "09_permit_units_by_stem.csv"

DWELLING_USES = {
    "TOWNHOUSE", "SINGLE FAMILY DWELLING", "DUPLEX", "MULTI-FAMILY DWELLING",
    "MULTIFAMILY DWELLING LOW RISE", "MULTIFAMILY DWELLING HIGH RISE",
    "MULTI-FAMILY SENIOR CITIZEN BL",
}

MP = r"M\.?P\.?D\.?U['’]?s?\b"
# "46 MPDUs", "8 MPDU'S", "(139 MPDU)"; not "Unit A-2 MPDU" or "#2137=mpdu"
MPDU_COUNT = re.compile(rf"(?<![\w#/.-])(\d{{1,4}})\s*(?:\(\w+\)\s*)?(?:affordable\s*)?{MP}", re.I)
# a number right after these words labels a lot, model or unit, not a count
NOT_A_COUNT = re.compile(r"(?:\blot|\bmodel:?|\bunit:?|\birc|\belev\.?|\bno\.?|\bof)\s*$", re.I)
UNIT_COUNT = re.compile(
    r"(?<![\w#/.-])(\d[\d,]{0,5})[\s-]*(?:total\s*)?(?:new\s*)?(?:residential\s*|rental\s*|apartment\s*"
    r"|dwelling\s*|multi-?family\s*|MFD\s*|condo(?:minium)?\s*|for-sale\s*)*"
    r"(?:units?|apartments|DU'?s)\b(?!\s*[:#]?\s*\d)", re.I)
UNITS_PAREN = re.compile(r"units\s*\((\d[\d,]{0,5})\)", re.I)
MARKET_UNITS = re.compile(r"(\d[\d,]{0,5})\s*(?:market[- ]rate|market value)\s*(?:units?)?", re.I)
NO_MPDU = re.compile(rf"\bno {MP}|\(no {MP}\)", re.I)
IN_THIS_ROW = re.compile(r"in this row", re.I)
# without a unit count, an MPDU count is a building's only in a building context
BLDG_CONTEXT = re.compile(r"build|bldg|\bMFD\b|multi-?family|apartment|high[- ]?rise|condo", re.I)
# usable project: its permits account for this share of the site plan's approved units
COVERAGE = (0.9, 1.1)


def clean(s):
    return re.sub(r"\s+", " ", html.unescape(str(s or ""))).strip()


def load_permits():
    frames = []
    for src, path in PERMIT_FILES.items():
        d = pd.read_csv(path, dtype=str)
        d["src"] = src
        frames.append(d)
    p = pd.concat(frames, ignore_index=True)
    p["desc"] = p["Description"].map(clean)
    p["added"] = pd.to_datetime(p["Added Date"], errors="coerce")
    xy = p["Location"].fillna("").str.extract(r"\(([-\d.]+),\s*([-\d.]+)\)").astype(float)
    p["lat"], p["lon"] = xy[0], xy[1]
    p["address"] = (p["Street Number"].fillna("") + " " + p["Street Name"].fillna("") + " "
                    + p["Street Suffix"].fillna("")).str.strip()
    new = p["Work Type"].fillna("").str.startswith(("CONSTRUCT", "FOUNDATION"))
    p = p[new & p["Use Code"].isin(DWELLING_USES)].copy()
    p["pure_model"] = (p["desc"].str.contains(r"pure model", case=False)
                       & ~p["desc"].str.contains(r"refer ?back", case=False))
    p["mentions_mpdu"] = p["desc"].str.contains(MP, case=False, regex=True)
    return p


def counts(s):
    """(MPDUs, total units) stated in a description, or None."""
    mp = [int(x.group(1)) for x in MPDU_COUNT.finditer(s) if not NOT_A_COUNT.search(s[:x.start()])]
    n_mpdu = max(mp) if mp else (0 if NO_MPDU.search(s) else None)
    un = [int(x.replace(",", "")) for x in UNIT_COUNT.findall(s) + UNITS_PAREN.findall(s)]
    n_units = max(un) if un else None
    # "162 market rate units and 24 MPDU units": the total is their sum
    mk = [int(x.replace(",", "")) for x in MARKET_UNITS.findall(s)]
    if mk and n_mpdu and (n_units is None or n_units <= max(mk)):
        n_units = max(mk) + n_mpdu
    return n_mpdu, n_units


def classify(p):
    c = p["desc"].map(counts)
    p["n_mpdu"] = [x[0] for x in c]
    p["n_units"] = [x[1] for x in c]
    row = p["desc"].str.contains(IN_THIS_ROW)
    context = p["desc"].str.contains(BLDG_CONTEXT) & p["n_mpdu"].ge(2)
    bldg = (p["mentions_mpdu"] & p["n_mpdu"].notna() & ~row
            & (p["n_units"].gt(1) | (p["n_units"].isna() & context)))
    p["level"] = np.select(
        [p["pure_model"], bldg, p["mentions_mpdu"], p["n_units"].fillna(1) > 1],
        ["pure_model", "building", "unit", "building_no_mpdu_info"],
        default="unit_no_mpdu")
    return p


NEAR_FT = 150   # address points sit on the street, outside the parcel


def attach_site_plan(p):
    """Site plan for each permit: one containing the point, else the nearest
    with approved dwelling units within NEAR_FT. A building permit is not
    placed in a plan approving fewer units than the building has."""
    sp = gpd.read_file(SITE_PLANS)[["APNO", "PROJNAME", "PBDATE", "APPR_DU_TOT", "geometry"]].to_crs(2248)
    sp["pb_date"] = pd.to_datetime(sp["PBDATE"], unit="ms", errors="coerce")
    q = p[p["lat"].notna() & p["lon"].notna()]
    pts = gpd.GeoDataFrame(q[["added", "n_units"]], geometry=gpd.points_from_xy(q["lon"], q["lat"]),
                           crs="EPSG:4326").to_crs(2248)
    j = gpd.sjoin(pts, sp, predicate="within", how="inner").assign(dist_ft=0.0)
    rest = pts[~pts.index.isin(j.index)]
    near = gpd.sjoin_nearest(rest, sp[sp["APPR_DU_TOT"] > 0], max_distance=NEAR_FT, distance_col="dist_ft")
    j = pd.concat([j, near])
    j = j[~(j["n_units"] > 1.1 * j["APPR_DU_TOT"])]
    j["has_du"] = j["APPR_DU_TOT"].fillna(0) > 0
    j["before"] = j["pb_date"] <= j["added"]
    j = j.sort_values(["has_du", "before", "dist_ft", "pb_date"], ascending=[False, False, True, False])
    best = j[~j.index.duplicated()]
    for col, src in [("site_plan", "APNO"), ("sp_name", "PROJNAME"), ("sp_appr_du", "APPR_DU_TOT"),
                     ("sp_pb_date", "pb_date"), ("sp_dist_ft", "dist_ft")]:
        p[col] = best[src].reindex(p.index)
    p["stem"] = p["site_plan"].str[:8]
    return p


def report_stems():
    rep = pd.read_stata(OFFERINGS)
    plans = {s.strip() for v in rep["site_plan"] for s in str(v).split("/") if s.strip()}
    stems = {s[:8] for s in plans if re.fullmatch(r"8\d{7}[0-9A-Z]", s)}
    rep["stem"] = rep["site_plan"].str[:8]
    proj = (rep[rep["total_units"].notna()]
            .groupby(["stem", "total_units", "total_mpdus"]).size().reset_index()
            [["stem", "total_units", "total_mpdus"]])
    names = {name_key(v) for c in ("project_name", "aka") for v in rep[c] if len(name_key(v)) >= 6}
    return stems, proj, names


STREET_NAME = re.compile(r"\b(?:lane|ln|avenue|ave|road|rd|street|st|drive|dr|blvd|boulevard|way|pike)\.?\s*$", re.I)


def name_key(s):
    return re.sub(r"[^a-z0-9]", "", str(s or "").lower().replace("the ", ""))


def in_reports(proj, stems, rep, names):
    """A permit project is already in the reports if its site plan stem is
    there, or a report project has the same total units and MPDUs (the 2024
    report prints no site plans), or its site plan name is a report project
    name or aka."""
    same_counts = proj.set_index(["total_units", "mpdus"]).index.isin(
        rep.set_index(["total_units", "total_mpdus"]).index)
    # a site plan named after its street ("Hampden Lane") matches too much
    street = proj["sp_name"].fillna("").str.contains(STREET_NAME)
    same_name = ~street & proj["sp_name"].map(lambda s: any(k in name_key(s) or name_key(s) in k
                                                            for k in names if len(name_key(s)) >= 6))
    return np.select([proj["stem"].isin(stems), same_counts, same_name],
                     ["site plan", "counts", "name"], default="")


def building_projects(m):
    b = m[m["level"] == "building"].copy()
    # one building per address and counts (revisions and sister permits repeat them)
    b = b.sort_values("added").drop_duplicates(["stem", "address", "n_units", "n_mpdu"])
    g = b.groupby("stem", dropna=False)
    out = g.agg(site_plan=("site_plan", "first"), sp_name=("sp_name", "first"),
                sp_appr_du=("sp_appr_du", "first"), first_permit=("added", "min"),
                n_buildings=("address", "size"), total_units=("n_units", "sum"),
                mpdus=("n_mpdu", "sum"), units_missing=("n_units", lambda s: s.isna().sum()),
                permits=("Permit Number", lambda s: " ".join(s)),
                addresses=("address", lambda s: "; ".join(sorted(set(s))))).reset_index()
    out.loc[out["units_missing"] > 0, "total_units"] = np.nan  # some building's units unknown
    out["level"] = "building"
    return out


def unit_projects(p, building_stems):
    u = p[p["stem"].notna() & ~p["stem"].isin(building_stems)
          & p["level"].isin(["unit", "unit_no_mpdu"])]
    g = u.groupby("stem")
    out = g.agg(site_plan=("site_plan", "first"), sp_name=("sp_name", "first"),
                sp_appr_du=("sp_appr_du", "first"), first_permit=("added", "min"),
                total_units=("Permit Number", "size"),
                mpdus=("level", lambda s: (s == "unit").sum()),
                permits=("Permit Number", lambda s: " ".join(s[u.loc[s.index, "level"] == "unit"])),
                addresses=("address", lambda s: f"{s.nunique()} addresses")).reset_index()
    out = out[out["mpdus"] > 0]
    out["level"] = "unit"
    out["n_buildings"] = np.nan
    out["units_missing"] = 0
    return out


def units_by_stem(p):
    """Dwelling units permitted in each site plan stem: one per one-unit
    permit, plus the stated units of building permits (one row per building)."""
    q = p[p["stem"].notna() & ~p["pure_model"]]
    one = q[q["level"].isin(["unit", "unit_no_mpdu"])].groupby("stem").size().rename("one_unit_permits")
    b = (q[q["level"].isin(["building", "building_no_mpdu_info"])]
         .drop_duplicates(["stem", "address", "n_units"]))
    bl = b.groupby("stem").agg(building_units=("n_units", "sum"),
                               buildings_missing_units=("n_units", lambda s: s.isna().sum()))
    out = pd.concat([one, bl], axis=1).fillna({"one_unit_permits": 0, "building_units": 0,
                                               "buildings_missing_units": 0})
    out["permit_units"] = out["one_unit_permits"] + out["building_units"]
    return out.reset_index()


def main():
    p = attach_site_plan(classify(load_permits()))
    m = p[p["mentions_mpdu"] | p["level"].eq("building")].copy()
    print("MPDU permits by level:", m["level"].value_counts().to_dict())
    print(f"  located in a site plan: {m['stem'].notna().sum()} / {len(m)}")

    b = building_projects(m[m["stem"].notna()])
    u = unit_projects(p, set(b["stem"]))
    proj = pd.concat([b, u], ignore_index=True)
    proj["share"] = proj["mpdus"] / proj["total_units"]
    proj["units_coverage"] = proj["total_units"] / proj["sp_appr_du"].replace(0, np.nan)
    proj["usable"] = proj["units_coverage"].between(*COVERAGE).astype(int)

    stems, rep, names = report_stems()
    proj["in_reports_by"] = in_reports(proj, stems, rep, names)
    proj["in_reports"] = (proj["in_reports_by"] != "").astype(int)
    proj["add_to_sample"] = ((proj["in_reports"] == 0) & (proj["usable"] == 1)
                             & (proj["level"] == "building")).astype(int)
    proj = proj.sort_values(["in_reports", "level", "first_permit"])

    m.drop(columns=["Description", "Location"]).to_csv(OUT_PERMITS, index=False)
    units_by_stem(p).to_csv(OUT_UNITS, index=False)
    proj.to_csv(OUT_PROJECTS, index=False)

    print(f"\nprojects: {len(proj)} ({proj['level'].value_counts().to_dict()})")
    print(pd.crosstab([proj["level"], proj["usable"]],
                      proj["in_reports"].map({0: "new", 1: "in reports"})).to_string())

    # check against the reports where both have the project: the report
    # project of the same stem closest in total units
    chk = proj[proj["in_reports"] == 1].merge(rep, on="stem", suffixes=("", "_rep"))
    chk["gap"] = (chk["total_units"] - chk["total_units_rep"]).abs()
    chk = chk.sort_values("gap").drop_duplicates(["stem", "level"])
    chk["mpdu_diff"] = chk["mpdus"] - chk["total_mpdus"]
    chk["share_diff"] = chk["share"] - chk["total_mpdus"] / chk["total_units_rep"]
    print("\ncheck against the reports (permit minus report):")
    for (lvl, ok), c in chk.groupby(["level", "usable"]):
        print(f"  {lvl}, usable={ok}: n={len(c)}; MPDUs exact {(c['mpdu_diff'] == 0).mean():.0%}, "
              f"share within 1 pt {(c['share_diff'].abs() <= 0.01).mean():.0%}, "
              f"median share diff {100 * c['share_diff'].median():+.1f} pts")
    chk.to_csv(INT / "09_permit_mpdu_check.csv", index=False)
    print(f"[saved] {OUT_PERMITS}\n[saved] {OUT_PROJECTS}")


if __name__ == "__main__":
    main()
