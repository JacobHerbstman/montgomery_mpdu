"""Build one offering-level MPDU file from the DHCA annual reports.

Python version of 01_combine_reports.do, so the pipeline runs without Stata.
Same steps and same output; put it in code/02_data_cleaning/ to run.

Inputs: data/int/02_data_cleaning/00_foia_reports.dta  2005-2012, FOIA spreadsheets
                                                         (08_extract_foia_offerings.py)
        data/int/02_data_cleaning/00_ocr_reports.dta   2013-2025, published PDFs
                                                         (02_extract_mpdu_offerings.py)

The 2024 report prints no site plan numbers, the cropped 2025 report prints
no project names, and the 2005 FOIA sheet prints no site plans, so offerings
of one project can carry different partial keys. They are filled in from
other offerings of the same project (originals kept in site_plan_orig and
project_name_orig; key_linked flags rows that changed):
  a. site plan: the unique most common one among offerings with the same
     name and totals;
  b. site plan for named offerings without one: from unnamed offerings with
     the same total units, total MPDUs and tenure, one-to-one matches only;
  c. name and developer for unnamed offerings: from the most recent named
     offering with the same site plan and totals.

Not in the .do file: where data/raw/mpdu_annual_reports/site_plan_fills.csv
exists (file, project_name, site_plan, note), its site plans are filled in for
the offerings of that report and name that still have none (d.; flagged in
site_plan_hand). These are 2024-report projects that no other report links,
looked up by name, aka and units in the Planning GIS site plan layer. Without
the file the output is the same as the .do file's.

Also not in the .do file: where data/raw/mpdu_annual_reports/total_fixes.csv
exists (file, project_name, total_units_reported, total_units, note), the
total units of that report's offerings of that project are corrected (e.;
flagged in totals_hand). For totals that no Planning Board document, the GIS
or the county's later records support. Without the file the output is the same.

total_mpdus is a project attribute repeated on every offering row; sum
mpdus_in_offering, not total_mpdus, for MPDUs built.

Output: data/int/02_data_cleaning/01_mpdu_offerings_combined.dta
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
INT = ROOT / "data" / "int" / "02_data_cleaning"
OUT_FILE = INT / "01_mpdu_offerings_combined.dta"
FILLS = ROOT / "data" / "raw" / "mpdu_annual_reports" / "site_plan_fills.csv"
TOTAL_FIXES = ROOT / "data" / "raw" / "mpdu_annual_reports" / "total_fixes.csv"

PLACEHOLDER = r"(?i)(n\s*/?\s*a|none|null|tbd|unknown|not applicable|-+)"
TOTALS = ["total_units", "total_mpdus"]
FIRST_COLS = ["report_series", "offering_year", "offering_date", "project_name", "aka", "site_plan",
              "prelim_plan", "street_address", "city", "zip", "total_units", "total_mpdus",
              "mpdus_in_offering", "wfh_units", "tenure", "developer", "unit_description"]
LABELS = {
    "report_series": "Report series: published (2013-2025 PDFs) or foia (2005-2012 spreadsheets)",
    "offering_date": "Offering Agreement date (DHCA counts MPDUs as built on this date)",
    "total_mpdus": "Total MPDUs in the project (repeated per offering)",
    "mpdus_in_offering": "MPDUs released in this offering",
    "file": "Source report (relative to data/raw/mpdu_annual_reports)",
    "site_plan_orig": "Site plan as extracted, before cross-report linking",
    "project_name_orig": "Project name as extracted, before cross-report linking",
    "key_linked": "Site plan or name filled/changed by cross-report linking",
    "site_plan_hand": "Site plan filled by hand (site_plan_fills.csv)",
    "totals_hand": "Total units corrected by hand (total_fixes.csv)",
}


def lookup(d, keys, values):
    """values (a Series indexed by keys) for each row of d; NaN where none."""
    return d[keys].merge(values.rename("_v").reset_index(), on=keys, how="left")["_v"]


def unique_mode(s):
    counts = s.value_counts()
    top = counts[counts == counts.max()].index
    return top[0] if len(top) == 1 else None


def main():
    foia = pd.read_stata(INT / "00_foia_reports.dta").assign(report_series="foia")
    ocr = pd.read_stata(INT / "00_ocr_reports.dta").assign(report_series="published")
    d = pd.concat([foia, ocr], ignore_index=True).rename(columns={"project_mpdus": "total_mpdus"})
    text = d.columns[d.dtypes == object]
    d[text] = d[text].fillna("")
    assert not set(foia["offering_year"]) & set(ocr["offering_year"]), "series overlap in years"

    # WFH-only offerings leave the project's MPDUs blank; take them from the
    # same project's other offerings in the same report
    same = d.groupby(["file", "site_plan", "project_name"])["total_mpdus"].transform("max")
    print(f"total_mpdus filled from same project in same report: {(d['total_mpdus'].isna() & same.notna()).sum()}")
    d["total_mpdus"] = d["total_mpdus"].fillna(same)

    for c in text:
        blank = d[c].str.strip().str.fullmatch(PLACEHOLDER)
        if blank.any():
            print(f"{c}: {blank.sum()} placeholder values set to blank")
        d.loc[blank, c] = ""

    d["site_plan_orig"] = d["site_plan"]
    d["project_name_orig"] = d["project_name"]
    d["name_key"] = d["project_name"].str.lower().str.replace("phase", "ph").str.replace(r"[^a-z0-9]", "", regex=True)

    # a. site plan from offerings with the same name and totals
    keys = ["name_key"] + TOTALS
    named = d["name_key"] != ""
    mode = lookup(d, keys, d[named & (d["site_plan"] != "")].groupby(keys)["site_plan"].agg(unique_mode))
    fix = named & mode.notna() & (d["site_plan"] != mode)
    print(f"a. site plan filled/overridden from same name and totals: {fix.sum()}")
    d.loc[fix, "site_plan"] = mode[fix]

    # b. site plan for named offerings without one, from unnamed offerings
    # with the same totals and tenure (one site plan and one name per group)
    keys = TOTALS + ["tenure"]
    has_keys = d[TOTALS].notna().all(axis=1) & (d["tenure"] != "")
    gets = has_keys & (d["site_plan"] == "") & named
    gives = has_keys & (d["site_plan"] != "") & ~named
    plans = d[gives].groupby(keys)["site_plan"].agg(lambda s: s.iloc[0] if s.nunique() == 1 else None)
    names = d[gets].groupby(keys)["name_key"].nunique()
    plan = lookup(d, keys, plans[names.reindex(plans.index) == 1])
    fix = gets & plan.notna()
    print(f"b. site plan filled from unnamed offerings with the same totals: {fix.sum()}")
    d.loc[fix, "site_plan"] = plan[fix]

    # c. name and developer from the most recent named offering with the
    # same site plan and totals
    keys = ["site_plan"] + TOTALS
    for c in ["project_name", "developer"]:
        known = d[(d["site_plan"] != "") & (d[c] != "")]
        latest = lookup(d, keys, known.sort_values("offering_date", ascending=False, kind="stable").groupby(keys)[c].first())
        fix = (d["site_plan"] != "") & (d[c] == "") & latest.notna()
        print(f"c. {c} filled from same site plan and totals: {fix.sum()}")
        d.loc[fix, c] = latest[fix]

    d["key_linked"] = ((d["site_plan"] != d["site_plan_orig"]) | (d["project_name"] != d["project_name_orig"])).astype("int8")

    # d. site plans looked up by hand, for offerings no other report links
    d["site_plan_hand"] = 0
    if FILLS.exists():
        fills = pd.read_csv(FILLS, dtype=str).set_index(["file", "project_name"])["site_plan"]
        plan = pd.Series([fills.get((f, n)) for f, n in zip(d["file"], d["project_name"])], index=d.index)
        fix = (d["site_plan"] == "") & plan.notna()
        print(f"d. site plan filled by hand (site_plan_fills.csv): {fix.sum()}")
        d.loc[fix, "site_plan"] = plan[fix]
        d["site_plan_hand"] = fix
    d["site_plan_hand"] = d["site_plan_hand"].astype("int8")

    # e. total units corrected by hand
    d["totals_hand"] = 0
    if TOTAL_FIXES.exists():
        for r in pd.read_csv(TOTAL_FIXES).itertuples(index=False):
            rows = (d["file"] == r.file) & (d["project_name"] == r.project_name)
            assert rows.any() and (d.loc[rows, "total_units"] == r.total_units_reported).all(), \
                f"total_fixes.csv: {r.project_name} in {r.file} is not {r.total_units_reported} units"
            d.loc[rows, "total_units"] = r.total_units
            d.loc[rows, "totals_hand"] = 1
        print(f"e. total units corrected by hand (total_fixes.csv): {int(d['totals_hand'].sum())}")
    d["totals_hand"] = d["totals_hand"].astype("int8")
    d = d.drop(columns="name_key")
    d = d[FIRST_COLS + [c for c in d.columns if c not in FIRST_COLS]]
    d = d.sort_values(["offering_date", "report_series"], kind="stable")
    assert d["offering_year"].notna().all() and d["offering_date"].notna().all()

    d.to_stata(OUT_FILE, version=118, write_index=False, convert_dates={"offering_date": "td"}, variable_labels=LABELS,
               data_label="MPDU offerings: DHCA annual reports 2005-2012 (FOIA) and 2013-2025 (published)")
    print(pd.crosstab(d["offering_year"], d["report_series"]).to_string())
    print(f"[saved] {OUT_FILE}")


if __name__ == "__main__":
    main()
