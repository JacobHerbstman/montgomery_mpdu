"""Base (pre-bonus) density for each site plan, from the parsed resolutions
(and, for plans approved before resolutions went online, staff reports).

Run 03_parse_resolutions.py first.

For each site plan, one resolution is used: usable (describes the residential
program), preferring the exact plan over another amendment of the same
project, then the one with the most direct base-density evidence. The base is
taken from the first route that applies:

  1 stated_bonus   the resolution states the bonus used:
                   base = approved units / (1 + bonus)
  2 stated_base    the resolution states units permitted before any bonus
  3 cr_floor_area  CR-family zone with approved residential floor area:
                   base = approved units x mapped / approved residential
                   floor area (Bethesda Overlay Zone density excluded)
  4 zone_table     zone density table (data/raw/zoning_rules/zone_density_table.csv)
                   x tract acres; TS-M and other FAR limits use route 5's
                   floor area per unit
  5 cr_mapped_fa   CR-family zone without residential floor area:
                   base = mapped residential floor area / typical gross
                   floor area per unit (median over route-3 resolutions)

The result is kept as base_ratio = base units / approved units, so it can be
applied to annual-report totals that cover only part of a site plan.

Site adjustments (hand-coded in data/raw/pb_resolutions/manual_coding.csv
from the resolutions' data tables): net/usable area where stated, approved
non-residential floor area under a total-FAR cap, and building type for the
floor-area-to-units conversion; TS-R's 2.5 FAR limit also applies. The
earlier gross-area method is kept alongside (*_v1 columns) for comparison.

Caveats. Where no net area is stated, routes 4 uses gross tract area, while
the code measures density on usable, net, or residential area, so it can
overstate base density. Routes 3-5 treat mapped density as the base; projects
using the optional method in pre-2014 CBD zones may be limited by FAR before
the unit cap. TDR, MXPD, RMX, TOMX, RNC and similar zones take density from
master or development plans and have no code table entry: those plans get no
base here unless a resolution states it.

Output: data/int/02_data_cleaning/04_base_density_by_plan.csv (one row per site plan with a
usable resolution), with the route used, every route's candidate value for
comparison, and the resolution file.

Usage:
  python 04_build_base_density.py
"""

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "03_analysis" / "01_mpdu_simulation"))
import rules  # noqa: E402  (MPDU bonus schedule, for the consistency check)

PARSED = ROOT / "data" / "int" / "02_data_cleaning" / "03_pb_resolutions_parsed.csv"
ZONE_TABLE = ROOT / "data" / "raw" / "zoning_rules" / "zone_density_table.csv"
OUT_FILE = ROOT / "data" / "int" / "02_data_cleaning" / "04_base_density_by_plan.csv"

SQFT_PER_ACRE = 43560
CR_FAMILY = {"CR", "CRT", "CRF", "CRN", "CRNF", "EOF", "LSC"}
ROUTES = ["stated_bonus", "stated_base", "cr_floor_area", "zone_table", "cr_mapped_fa"]


def norm_zone(z):
    """Zone string as written in the table: 'CBD-R-2' -> 'CBD-R2', 'RT12.5' -> 'RT-12.5'.
    Multi-zone sites ('A & B') and TDR zones ('R-200/TDR-7') return None."""
    if not isinstance(z, str) or "&" in z or "TDR" in z.upper():
        return None
    z = z.strip().upper().replace(" ", "")
    z = re.sub(r"^CBD-R-?(\d)", r"CBD-R\1", z)
    z = re.sub(r"^(RT|PD|R|RE|CBD|TS)-?(?=[\d.])", r"\1-", z)
    return z


def num(r, field):
    v = getattr(r, field, np.nan)
    return float(v) if pd.notna(v) and v != "" else np.nan


def candidates(r, table, sqft, adjust=True):
    """Base units under each route for one resolution row (NaN where n/a).

    sqft: gross residential floor area per unit, {"MF": .., "TH": .., "all": ..}.
    adjust=True applies the hand-coded site adjustments (manual_coding.csv):
      density_acres  net/usable area the zone density applies to
      nonres_gfa_sf  approved non-residential floor area; in CR-family and TS-M
                     zones it uses the total FAR cap, so residential capacity
                     = min(R x area, total FAR x area - non-residential)
      unit_type      TH/MF: floor area per unit for floor-area -> unit conversion
    plus a zone's secondary FAR limit (TS-R: 2.5 FAR). adjust=False is the
    earlier gross-area method, kept for comparison.
    """
    out = dict.fromkeys(ROUTES, np.nan)
    units = r.approved_units
    if pd.notna(r.bonus_pct) and pd.notna(units):
        out["stated_bonus"] = units / (1 + r.bonus_pct / 100)
    if pd.notna(r.base_units_permitted):
        out["stated_base"] = r.base_units_permitted

    tract = r.tract_acres
    area = num(r, "density_acres") if adjust and pd.notna(num(r, "density_acres")) else tract
    nonres = num(r, "nonres_gfa_sf") if adjust else np.nan
    utype = getattr(r, "unit_type", None) if adjust else None
    sf = sqft.get(utype, sqft["MF"]) if adjust else sqft["all"]

    cr = r.zone_family in CR_FAMILY and pd.notna(r.cr_r_far)
    res_cap = np.nan
    if cr and pd.notna(tract):
        res_cap = r.cr_r_far * tract * SQFT_PER_ACRE
        if pd.notna(nonres) and pd.notna(r.cr_total_far):
            res_cap = min(res_cap, r.cr_total_far * tract * SQFT_PER_ACRE - nonres)
    if cr and pd.notna(units) and pd.notna(r.approved_res_gfa_sf) and pd.notna(res_cap):
        res_used = r.approved_res_gfa_sf - (num(r, "boz_density_sf") if pd.notna(num(r, "boz_density_sf")) else 0)
        if res_used > 0:
            out["cr_floor_area"] = units * res_cap / res_used
    z = norm_zone(r.zone)
    if z in table.index and pd.notna(area):
        t = table.loc[z]
        if t.density_unit == "du/acre":
            out["zone_table"] = t.base_density * area
            if adjust and pd.notna(t.far_limit):
                out["zone_table"] = min(out["zone_table"], t.far_limit * area * SQFT_PER_ACRE / sf)
        elif t.density_unit == "FAR":
            cap = t.base_density * area * SQFT_PER_ACRE - (nonres if pd.notna(nonres) else 0)
            out["zone_table"] = cap / sf
    if cr and pd.notna(res_cap):
        out["cr_mapped_fa"] = res_cap / sf
    return out


def pick(u, cand):
    """Route used (first available) and its base units."""
    route = cand.notna().idxmax(axis=1).where(cand.notna().any(axis=1))
    base = [cand.loc[i, rt] if isinstance(rt, str) else np.nan for i, rt in zip(u.index, route)]
    return route, pd.Series(base, index=u.index, dtype=float)


def consistent(base_ratio, mpdu_pct):
    """Approved units can exceed the base only by the bonus the MPDU share
    earns under the Chapter 59 schedule (+3 points for rounding)."""
    implied = 1 / base_ratio - 1
    earned = rules.bonus_pct(mpdu_pct.fillna(12.5) / 100)
    return implied, earned, base_ratio.notna() & (implied <= earned + 0.03)


def main():
    p = pd.read_csv(PARSED)
    table = pd.read_csv(ZONE_TABLE).set_index("zone")

    for c in ("density_acres", "nonres_gfa_sf", "unit_type"):
        if c not in p.columns:
            p[c] = np.nan

    # typical gross residential floor area per unit, from CR resolutions that
    # state both residential floor area and units: all, and by building type
    fa = p[(p["usable"] == 1) & p["zone_family"].isin(CR_FAMILY)
           & p["approved_res_gfa_sf"].notna() & p["approved_units"].notna()].copy()
    fa["sf"] = fa["approved_res_gfa_sf"] / fa["approved_units"]
    sqft = {"all": float(fa["sf"].median()),
            "MF": float(fa.loc[fa["unit_type"].ne("TH"), "sf"].median()),
            "TH": float(fa.loc[fa["unit_type"].eq("TH"), "sf"].median())}
    print(f"gross residential sf per unit: all {sqft['all']:,.0f} (n={len(fa)}); "
          f"MF {sqft['MF']:,.0f}; TH {sqft['TH']:,.0f} (n={int(fa['unit_type'].eq('TH').sum())})")

    # staff reports: only where the OCR'd approved units match the project's
    # (the base is kept as a ratio to approved units)
    if "units_check" not in p.columns:
        p["units_check"] = np.nan
    staff = p["doc_type"].eq("staff_report")
    p = p[~staff | p["units_check"].astype(str).eq("True")].copy()
    # staff reports rarely state the MPDU share: use the project's for the check
    if "project_mpdu_pct" in p.columns:
        p["mpdu_pct"] = p["mpdu_pct"].fillna(p["project_mpdu_pct"].where(p["doc_type"].eq("staff_report")))
    u = p[(p["usable"] == 1) & (p["same_project"] != False)].copy()
    cand = pd.DataFrame([candidates(r, table, sqft) for r in u.itertuples(index=False)], index=u.index)
    cand_v1 = pd.DataFrame([candidates(r, table, sqft, adjust=False) for r in u.itertuples(index=False)],
                           index=u.index)
    u = pd.concat([u, cand.add_prefix("base_")], axis=1)
    u["route"], u["base_units"] = pick(u, cand)
    u["route_v1"], u["base_units_v1"] = pick(u, cand_v1)
    u["route_rank"] = u["route"].map({r: i for i, r in enumerate(ROUTES)}).fillna(len(ROUTES))

    # one document per plan: a resolution before a (pre-2008) staff report,
    # the exact plan first, then the most direct route, then the latest MCPB number
    u["exact"] = u["plan_match"].astype(str).eq("True")
    u["staff_report"] = u["doc_type"].eq("staff_report")
    u = (u.sort_values(["target_plan", "staff_report", "exact", "route_rank", "mcpb_no"],
                       ascending=[True, True, False, True, False])
           .drop_duplicates("target_plan"))
    u["base_ratio"] = u["base_units"] / u["approved_units"]
    u["base_ratio_v1"] = u["base_units_v1"] / u["approved_units"]
    u["zone_norm"] = u["zone"].map(norm_zone)

    # Consistency: approved units can exceed the base only by the bonus the
    # project's MPDU share earns under the Chapter 59 schedule. A larger
    # implied bonus means the base missed density from elsewhere (density
    # transfer, TDRs, workforce housing, BOZ), so the base is not used.
    u["implied_bonus"], u["earned_bonus"], u["base_consistent"] = consistent(u["base_ratio"], u["mpdu_pct"])
    _, _, u["base_consistent_v1"] = consistent(u["base_ratio_v1"], u["mpdu_pct"])
    u["base_binding"] = u["base_ratio"] <= 1.0 + 1e-9   # built at or above base density

    keep = (["target_plan", "resolution_plan", "file", "doc_type", "mcpb_no", "zone", "zone_norm", "tract_acres",
             "approved_units", "mpdu_pct", "route", "base_units", "base_ratio",
             "implied_bonus", "earned_bonus", "base_consistent", "base_binding",
             "route_v1", "base_units_v1", "base_ratio_v1", "base_consistent_v1",
             "density_acres", "nonres_gfa_sf", "unit_type"]
            + [f"base_{r}" for r in ROUTES]
            + ["bonus_pct", "max_units_permitted", "approved_res_gfa_sf", "mapped_res_gfa_sf", "res_gfa_ratio"])
    out = u[keep].reset_index(drop=True)
    uses_sf = out["route"].isin(["cr_mapped_fa"]) | (out["route"].eq("zone_table") & out["zone_norm"].isin(["TS-M", "TS-R"]))
    out["sqft_per_unit_assumed"] = np.where(uses_sf, out["unit_type"].map({"TH": sqft["TH"]}).fillna(sqft["MF"]), np.nan)
    out.to_csv(OUT_FILE, index=False)

    print(f"site plans with a usable resolution: {len(out)}")
    print("route used (consistent / total):")
    tab = out.groupby(out["route"].fillna("none"))["base_consistent"].agg(["sum", "size"])
    print(tab.to_string())
    print(f"consistent bases: {int(out['base_consistent'].sum())}; "
          f"of which binding (built at or above base): {int((out['base_consistent'] & out['base_binding']).sum())}")
    v1 = out["base_consistent_v1"] & (out["base_ratio_v1"] > 1 + 1e-9)
    v2 = out["base_consistent"] & (out["base_ratio"] > 1 + 1e-9)
    print(f"built below base: gross-area method {int(v1.sum())} of {int(out['base_consistent_v1'].sum())}; "
          f"adjusted {int(v2.sum())} of {int(out['base_consistent'].sum())}")
    print(f"[saved] {OUT_FILE}")


if __name__ == "__main__":
    main()
