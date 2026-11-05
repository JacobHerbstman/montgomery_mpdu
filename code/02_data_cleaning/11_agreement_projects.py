"""Projects with an MPDU Agreement to Build but no offerings in the reports.

Input: data/int/02_data_cleaning/00_agreements_to_build.csv
       (code/01_data_collection/11_extract_agreements_to_build.py)
       data/int/02_data_cleaning/01_mpdu_offerings_combined.dta

An Agreement to Build records the project's total units and MPDUs. Where
both sources have a project, the agreement's totals equal the report
project's totals for most agreements (printed), so an agreement is as good a
record of the MPDU choice as the offering tables. Agreements for projects
not in the offerings (signed but not yet offered, or offered outside
2005-2025) are added to the project sample.

An agreement is already in the sample if a report project has the same total
units and MPDUs, the same site plan stem, or the same name (or aka). Not
added: Alternative Agreements (name starred in the FOIA sheets; MPDUs off
site or paid out) and agreements with no MPDUs, which the offering tables
cannot contain either. Repeated agreements for one site plan and totals
(e.g. amended) count once, at the first agreement date.

Output: data/int/02_data_cleaning/11_agreement_projects.csv, one row per
agreement with match (how it matched the sample, blank if not) and
add_to_sample.
"""

import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
INT = ROOT / "data" / "int" / "02_data_cleaning"
OUT_FILE = INT / "11_agreement_projects.csv"


def name_key(s):
    s = re.sub(r"\b(the|at|phase|ph)\b", " ", str(s or "").lower())
    return re.sub(r"[^a-z0-9]", "", s)


def main():
    a = pd.read_csv(INT / "00_agreements_to_build.csv", dtype={"site_plan": str},
                    parse_dates=["agreement_date"])
    off = pd.read_stata(INT / "01_mpdu_offerings_combined.dta")
    proj = off[off["total_units"].notna()].drop_duplicates(["site_plan", "total_units", "total_mpdus"])
    counts = set(zip(proj["total_units"].astype(int), proj["total_mpdus"].astype(int)))
    stems = {p.strip()[:8] for v in off["site_plan"] for p in str(v).split("/") if p.strip()}
    names = {name_key(v) for c in ["project_name", "aka"] for v in off[c] if len(name_key(v)) >= 5}

    def match(r):
        if (r["total_units"], r["mpdus"]) in counts:
            return "counts"
        if isinstance(r["site_plan"], str) and r["site_plan"][:8] in stems:
            return "site plan"
        k = name_key(r["project_name"])
        if len(k) >= 5 and any(k in n or n in k for n in names):
            return "name"
        return ""

    a["match"] = a.apply(match, axis=1)
    a = a.sort_values("agreement_date")
    first = ~a.duplicated(["site_plan", "total_units", "mpdus"])
    a["add_to_sample"] = ((a["match"] == "") & ~a["starred"] & (a["mpdus"] > 0)
                          & (a["site_plan"].notna() | a["project_name"].notna()) & first).astype(int)
    a.to_csv(OUT_FILE, index=False)

    m = a[a["match"].isin(["counts", "site plan"])]
    print(f"agreements: {len(a)}; matched to report projects: {(a['match'] != '').sum()} "
          f"({a['match'].value_counts().to_dict()})")
    print(f"  totals equal a report project's: {(m['match'] == 'counts').sum()} of {len(m)} matched by counts or site plan")
    print(f"not in the sample: {(a['match'] == '').sum()}; added: {a['add_to_sample'].sum()}")
    print(a[a["match"] == ""][["year", "project_name", "site_plan", "total_units", "mpdus", "starred",
                               "add_to_sample"]].to_string(index=False))
    print("name matches (check):", a.loc[a["match"] == "name", "project_name"].tolist())
    print(f"[saved] {OUT_FILE}")


if __name__ == "__main__":
    main()
