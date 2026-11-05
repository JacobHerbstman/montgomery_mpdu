"""Project-level helpers for the MPDU simulation (analog of San Diego utils.py)."""

from pathlib import Path

import numpy as np
import pandas as pd

import rules

ROOT = Path(__file__).resolve().parents[3]
CLEAN_DIR = ROOT / "data" / "int" / "02_data_cleaning"     # inputs from code/02_data_cleaning
ANALYSIS_DIR = ROOT / "data" / "int" / "03_analysis"      # simulation outputs
OFFERINGS_FILE = CLEAN_DIR / "01_mpdu_offerings_combined.dta"
BASE_FILE = CLEAN_DIR / "04_base_density_by_plan.csv"
AMI_FILE = CLEAN_DIR / "05_hud_ami_montgomery.csv"
TRACT_FILE = CLEAN_DIR / "06_site_plan_tracts.csv"
REGIME_FILE = CLEAN_DIR / "07_site_plan_regime.csv"
PERMIT_FILE = CLEAN_DIR / "09_permit_mpdu_projects.csv"
FILL_FILE = CLEAN_DIR / "10_dhca_fills.csv"
AGREEMENT_FILE = CLEAN_DIR / "11_agreement_projects.csv"

# Projects with at least this MPDU share are treated like San Diego's
# fully-affordable projects: kept, but outside the profit-maximizing logic.
FULLY_AFFORDABLE_SHARE = 0.50


# ==============================================================================
# Load and collapse offerings to projects
# ==============================================================================
def load_projects(path=OFFERINGS_FILE, permit_path=PERMIT_FILE, fill_path=FILL_FILE,
                  agreement_path=AGREEMENT_FILE):
    """One row per project from the annual-report offerings (2005-2012 FOIA
    reports and 2013-2025 published reports), plus the building-permit
    projects not in the reports (add_to_sample in 09_permit_mpdu_projects.csv)
    and the Agreement to Build projects with no offerings
    (add_to_sample in 11_agreement_projects.csv). source says which. Report projects whose offering tables print no totals
    take them from 10_dhca_fills.csv where DHCA and the permits agree
    (totals_filled = True).

    total_units and total_mpdus are project attributes repeated on every
    offering row. A project is a (site plan, total_units, total_mpdus)
    combination, so phases of one site plan with different totals stay
    separate. Rows without a site plan fall back to the project name, and the
    2025 rows (no name either) to their row position.
    """
    d = pd.read_stata(path)
    d["totals_filled"] = False
    if fill_path is not None and Path(fill_path).exists():
        f = pd.read_csv(fill_path, dtype={"report_site_plan": str}).fillna({"report_site_plan": ""})
        for _, r in f.iterrows():
            hit = (d["project_name"].eq(r["project_name"]) & d["site_plan"].eq(r["report_site_plan"])
                   & d["total_units"].isna())
            d.loc[hit, ["total_units", "total_mpdus"]] = [r["total_units"], r["total_mpdus"]]
            d.loc[hit, "totals_filled"] = True

    key = d["site_plan"].str.strip()
    key = key.where(key != "", "name:" + d["project_name"].str.strip())
    key = key.where(key != "name:", "row:" + d.index.astype(str))
    d["project_key"] = key

    grp = d.groupby(["project_key", "total_units", "total_mpdus"], sort=False)
    out = grp.agg(
        site_plan=("site_plan", "first"),
        project_name=("project_name", "first"),
        developer=("developer", "first"),
        tenure=("tenure", lambda s: s.mode().iat[0] if not s.mode().empty else ""),
        first_offering_date=("offering_date", "min"),
        last_offering_date=("offering_date", "max"),
        n_offerings=("offering_date", "size"),
        mpdus_offered=("mpdus_in_offering", "sum"),
        wfh_units=("wfh_units", "sum"),
        totals_filled=("totals_filled", "any"),
    ).reset_index()
    out["source"] = "report"

    if permit_path is not None and Path(permit_path).exists():
        pm = pd.read_csv(permit_path, dtype={"site_plan": str, "stem": str}, parse_dates=["first_permit"])
        pm = pm[pm["add_to_sample"] == 1]
        out = pd.concat([out, pd.DataFrame({
            "project_key": "permit:" + pm["site_plan"], "total_units": pm["total_units"],
            "total_mpdus": pm["mpdus"], "site_plan": pm["site_plan"], "project_name": pm["sp_name"],
            "developer": "", "tenure": "",
            # the first building permit stands in for the (unobserved) offering date
            "first_offering_date": pm["first_permit"], "last_offering_date": pm["first_permit"],
            "n_offerings": 0, "mpdus_offered": np.nan, "wfh_units": np.nan, "source": "permit",
        })], ignore_index=True)

    if agreement_path is not None and Path(agreement_path).exists():
        ag = pd.read_csv(agreement_path, dtype={"site_plan": str}, parse_dates=["agreement_date"])
        ag = ag[ag["add_to_sample"] == 1]
        out = pd.concat([out, pd.DataFrame({
            "project_key": "agreement:" + ag["site_plan"].fillna(ag["project_name"]),
            "total_units": ag["total_units"], "total_mpdus": ag["mpdus"],
            "site_plan": ag["site_plan"].fillna(""), "project_name": ag["project_name"].fillna(""),
            "developer": ag["developer"].fillna(""), "tenure": ag["tenure"].fillna(""),
            # the agreement date stands in for the (not yet observed) offering date
            "first_offering_date": ag["agreement_date"], "last_offering_date": ag["agreement_date"],
            "n_offerings": 0, "mpdus_offered": np.nan, "wfh_units": ag["wfh_units"],
            "source": "agreement",
        })], ignore_index=True)

    out = out.rename(columns={"total_units": "actual_units_total",
                              "total_mpdus": "actual_units_mpdu"})
    out["actual_units_total"] = out["actual_units_total"].astype(int)
    out["actual_units_mpdu"] = out["actual_units_mpdu"].astype(int)
    out["actual_units_mkt"] = out["actual_units_total"] - out["actual_units_mpdu"]
    out["actual_sh_mpdu"] = out["actual_units_mpdu"] / out["actual_units_total"]
    out["year_offering"] = out["first_offering_date"].dt.year
    out["is_fully_affordable"] = out["actual_sh_mpdu"] >= FULLY_AFFORDABLE_SHARE

    # Placeholder: the annual reports have no planning area, so every project
    # starts at the 12.5% county minimum; attach_regime() then sets 15% from
    # the site plan's location and acceptance date (07_site_plan_regime.py).
    out["min_share"] = [rules.min_share_for(dt) for dt in out["first_offering_date"]]
    out.insert(0, "id", np.arange(1, len(out) + 1))
    return out


# ==============================================================================
# MPDU minimum (12.5% / 15%) by location and acceptance date
# ==============================================================================
def attach_regime(df, path=REGIME_FILE):
    """Set min_share from 07_site_plan_regime.csv: 15% in the high-income
    planning area designated when the application was accepted, or in a 15%
    master-plan area (Bethesda Downtown, Silver Spring Downtown). Composite
    site plans take the first plan found; projects without a located site plan
    keep the 12.5% default (regime_source "default")."""
    out = df.copy()
    out["regime_source"] = "default"
    for c in ("planning_area", "high_income_area", "master_plan_15", "designation_year", "date_regime"):
        out[c] = None
    if not path.exists():
        return out
    r = pd.read_csv(path, dtype={"site_plan": str}).drop_duplicates("site_plan").set_index("site_plan")
    for i, sp in out["site_plan"].items():
        for p in str(sp).split("/"):
            p = p.strip()
            if p in r.index:
                out.loc[i, "min_share"] = float(r.loc[p, "min_share"])
                for c in ("planning_area", "high_income_area", "master_plan_15", "designation_year", "date_regime"):
                    out.loc[i, c] = r.loc[p, c]
                out.loc[i, "regime_source"] = "site_plan"
                break
    return out


# ==============================================================================
# Area median income by year
# ==============================================================================
def attach_ami(df, path=AMI_FILE):
    """Add each project's AMI: HUD FY median for Montgomery County, MD in the
    year of its first offering (when MPDU prices are set for lease-up).
    Years outside FY2004-FY2026 take the nearest year; without the file,
    rules.AMI_DEFAULT is used."""
    out = df.copy()
    if not path.exists():
        out["ami"] = rules.AMI_DEFAULT
        return out
    a = pd.read_csv(path).set_index("fy")["ami"]
    yrs = out["year_offering"].clip(a.index.min(), a.index.max())
    out["ami"] = yrs.map(a).fillna(rules.AMI_DEFAULT).astype(float)
    return out


# ==============================================================================
# Market rent
# ==============================================================================
def attach_market_rent(df, tract_path=TRACT_FILE, ami_path=AMI_FILE):
    """Add each project's market rent.

    Default (rules.USE_TRACT_RENT = False): rules.RENT_MKT_STANDARD for every
    project. Otherwise: the ACS 2019 5-year median gross rent of
    its site plan's census tract (06_tract_rents.py), moved to the offering year
    with Montgomery's AMI growth (AMI_year / AMI_FY2019), then scaled by
    rules.NEW_CONSTRUCTION_PREMIUM.

    Indexing by AMI keeps the market / MPDU rent ratio fixed over time within a
    tract (MPDU rents are indexed to AMI), so cross-tract differences drive the
    variation. Projects without a located site plan get the county median of
    located projects. Requires attach_ami() first.
    """
    out = df.copy()
    out["tract_geoid"] = None
    out["acs19_median_gross_rent"] = np.nan
    if tract_path.exists():
        t = pd.read_csv(tract_path, dtype={"site_plan": str, "tract_geoid": str}).set_index("site_plan")
        for i, sp in out["site_plan"].items():
            for p in str(sp).split("/"):
                p = p.strip()
                if p in t.index and pd.notna(t.loc[p, "acs19_median_gross_rent"]):
                    out.loc[i, "tract_geoid"] = t.loc[p, "tract_geoid"]
                    out.loc[i, "acs19_median_gross_rent"] = t.loc[p, "acs19_median_gross_rent"]
                    break
    if not rules.USE_TRACT_RENT:
        # standardized market rent; tract columns kept for reference only
        out["rent_mkt_source"] = "standard"
        out["rent_mkt"] = rules.RENT_MKT_STANDARD
        return out
    located = out["acs19_median_gross_rent"].notna()
    out["rent_mkt_source"] = np.where(located, "acs_tract", "county_median")
    base = out["acs19_median_gross_rent"].fillna(out.loc[located, "acs19_median_gross_rent"].median()
                                                 if located.any() else rules.RENT_MKT_PLACEHOLDER)
    ami19 = rules.AMI_DEFAULT
    if ami_path.exists():
        a = pd.read_csv(ami_path).set_index("fy")["ami"]
        ami19 = float(a.get(2019, ami19))
    out["rent_mkt"] = (base * out["ami"] / ami19 * rules.NEW_CONSTRUCTION_PREMIUM).round(0)
    return out


# ==============================================================================
# Observed base density (Planning Board resolutions)
# ==============================================================================
def attach_observed_base(df, path=BASE_FILE):
    """Add observed base units from 04_base_density_by_plan.csv.

    Only bases that pass the consistency check are used. The resolution's
    base_ratio (base units / approved units) is applied to the annual-report
    total, since a report project can be one phase of a larger site plan.
    Composite site plans ("A/B") take the first plan with a base.
    """
    out = df.copy()
    out["obs_base_ratio"] = np.nan
    out["obs_base_route"] = None
    if not path.exists():
        return out
    b = pd.read_csv(path, dtype={"target_plan": str})
    b = b[b["base_consistent"]].set_index("target_plan")
    for i, sp in out["site_plan"].items():
        for p in str(sp).split("/"):
            p = p.strip()
            if p in b.index:
                out.loc[i, "obs_base_ratio"] = b.loc[p, "base_ratio"]
                out.loc[i, "obs_base_route"] = b.loc[p, "route"]
                break
    out["obs_base_units"] = np.maximum(1, np.round(out["actual_units_total"] * out["obs_base_ratio"]))
    return out


# ==============================================================================
# Reverse-engineer base units
# ==============================================================================
def infer_base_units(h, m, min_share=rules.MIN_SHARE_DEFAULT):
    """Base units consistent with an observed (total units h, MPDUs m).

    Required MPDUs at h fall as base units rise (less bonus is needed), so
    the base units that reproduce m exactly form an interval. We take its
    smallest value, i.e. assume the developer used all the bonus its MPDUs
    earned, matching San Diego's choice of the smallest valid base.

    Returns (base_units, base_units_max, label):
      Dominant           exact match; m is the fewest legal MPDUs at h
      Approximate Match  rounding skips m; nearest base units used
      Below Minimum      m is below the minimum share even with no bonus
    """
    h, m = int(h), int(m)
    bases = np.arange(1, h + 1)
    m_req = rules.mpdus_required(h, bases, min_share)

    if m < m_req[-1]:
        return h, h, "Below Minimum"
    exact = np.flatnonzero(m_req == m)
    if exact.size:
        return int(bases[exact[0]]), int(bases[exact[-1]]), "Dominant"
    k = int(np.argmin(np.abs(m_req - m)))
    return int(bases[k]), int(bases[k]), "Approximate Match"


# ==============================================================================
# Concave upper envelope of R(h), as in San Diego main.py
# ==============================================================================
def concave_upper_envelope(h, r):
    """Concave hull of (h, r) points (h sorted ascending), evaluated at each h."""
    n = len(h)
    if n < 3:
        return r.astype(float).copy()
    hull = []
    for i in range(n):
        while len(hull) >= 2:
            i2, i1 = hull[-2], hull[-1]
            cross = ((h[i1] - h[i2]) * (r[i] - r[i1])
                     - (r[i1] - r[i2]) * (h[i] - h[i1]))
            if cross >= 0:
                hull.pop()
            else:
                break
        hull.append(i)
    new_r = r.astype(float).copy()
    for a, b in zip(hull[:-1], hull[1:]):
        if h[b] > h[a]:
            slope = (r[b] - r[a]) / (h[b] - h[a])
            new_r[a + 1:b] = r[a] + slope * (h[a + 1:b] - h[a])
    return new_r
