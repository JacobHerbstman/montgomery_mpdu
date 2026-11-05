"""Extract MPDU Agreements to Build (Attachment A) from the DHCA annual reports.

An Agreement to Build is signed before the first building permit and fixes
the project's total units and MPDUs, so it gives project totals for
developments whose offerings the reports do not list (offered before 2005,
not yet offered, or offered with no totals printed).

Sources, all DHCA:
  * 2005-2012: FOIA spreadsheets (Agree*to Build*.xls), read as in
    08_extract_foia_offerings.py;
  * 2013-2017, 2020, 2022: scanned reports, transcribed by hand from the page
    images into data/raw/mpdu_annual_reports/agreements_to_build_transcribed.csv;
  * 2018-2019, 2021, 2023-2025: text reports, tables read with PyMuPDF
    find_tables() (sideways pages come out transposed).
Each year is checked against the agreement count and totals the report
prints (OFFICIAL); mismatches are printed.

Output: data/int/02_data_cleaning/00_agreements_to_build.csv, one row per
agreement: year, project_name, aka, site_plan, total_units, mpdus, wfh_units,
tenure, agreement_date, starred (name marked "*": Alternative Agreement in the
FOIA sheets, LIHTC in some later tables), source file and page.

Usage:
  python 11_extract_agreements_to_build.py
"""

import importlib.util
import re
from pathlib import Path

import pandas as pd
import pymupdf

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "mpdu_annual_reports"
OUT_FILE = ROOT / "data" / "int" / "02_data_cleaning" / "00_agreements_to_build.csv"
TRANSCRIBED = RAW / "agreements_to_build_transcribed.csv"

TEXT_PAGES = [
    ("annual_report_mpdu_2018-2019.pdf", 5),
    ("annual_report_mpdu_2021.pdf", 8),
    ("annual_report_mpdu_2023.pdf", 11),
    ("annual_report_mpdu_2024.pdf", 11),
    ("annual_report_mpdu_2025.pdf", 11),
]

# (agreements, total units, MPDUs) as printed in each report (table totals
# rows, or the memo text where the table has none); None = not printed
OFFICIAL = {
    # 2005-2012: agreement counts from the memos to the Council (no totals);
    # 2005 and 2012 list 2 and 1 more rows than the memo counts
    2005: (15, None, None), 2006: (10, None, None), 2007: (5, None, None), 2008: (6, None, None),
    2009: (2, None, None), 2010: (8, None, None), 2011: (9, None, None), 2012: (10, None, None),
    2013: (14, 3424, 461), 2014: (11, 1929, 258), 2015: (16, 3704, 491), 2016: (12, 2000, 274),
    2017: (3, 696, 88), 2018: (12, 3204, 541), 2019: (11, 1781, 310), 2020: (6, 960, 183),
    2021: (12, None, 440), 2022: (11, 3965, 612), 2023: (14, 4101, 807), 2024: (12, 1495, 238),
    2025: (11, None, 564),
}


def foia_module():
    spec = importlib.util.spec_from_file_location("foia", Path(__file__).parent / "08_extract_foia_offerings.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def clean(s):
    return re.sub(r"\s+", " ", str(s or "").replace("‐", "-")).strip()


def to_int(s):
    s = clean(s).replace(",", "")
    return int(s) if re.fullmatch(r"\d+", s) else None


def to_date(s):
    m = re.search(r"(\d{1,2})/(\d{1,2})/(\d{2,4})", clean(s).replace(" ", ""))
    if not m:
        return None
    y = int(m.group(3))
    y += 2000 if y < 100 else 0
    if not 1990 <= y <= 2035:
        return None
    try:
        return pd.Timestamp(y, int(m.group(1)), int(m.group(2)))
    except ValueError:
        return None


def map_header(h):
    h = clean(h).lower().replace("‐", "-")
    if not h:
        return None
    if h.startswith("project name") and "aka" in h:
        return "aka"
    if h.startswith("project name"):
        return "project_name"
    if h == "aka":
        return "aka"
    if h.startswith("site plan"):
        return "site_plan"
    if h.startswith("total units") or h == "total":
        return "total_units"
    if h in ("mpdu", "mpdus"):
        return "mpdus"
    if h.startswith("wfh") or h.startswith("workforce"):
        return "wfh_units"
    if h.startswith("rental or"):
        return "tenure"
    if h.startswith("agreeme"):
        return "agreement_date"
    if h.startswith("developer"):
        return "developer"
    return None


def text_tables():
    """Agreement rows from the text reports. A table without a header row
    (2019 on the 2018-2019 page) takes the previous table's columns. Dates
    cut off at the cell edge ("10/19/202" in 2021) take the year of a
    single-year report."""
    rows = []
    for fname, pg in TEXT_PAGES:
        years = [int(y) for y in re.findall(r"20\d\d", fname)]
        page = pymupdf.open(RAW / fname)[pg - 1]
        fields = None
        for tab in page.find_tables(strategy="lines").tables:
            grid = [[clean(c) for c in r] for r in tab.extract()]
            # sideways page: header labels run down the first column
            if sum(map_header(r[0]) is not None for r in grid if r) >= 3:
                grid = [list(col) for col in zip(*grid)]
            hdr = next((i for i, r in enumerate(grid) if any(map_header(c) == "agreement_date" for c in r)), None)
            if hdr is not None:
                fields, body = [map_header(c) for c in grid[hdr]], grid[hdr + 1:]
            elif fields is not None and len(grid[0]) == len(fields):
                body = grid
            elif fields is not None and len(grid) == len(fields):     # sideways, no header column
                body = [list(col) for col in zip(*grid)]
            else:
                continue
            for r in grid[hdr + 1:] if hdr is not None else body:
                rec = {f: v for f, v in zip(fields, r) if f}
                d = rec.get("agreement_date", "")
                m = re.fullmatch(r"(\d{1,2}/\d{1,2}/)20\d", d.replace(" ", ""))
                if m and len(years) == 1:
                    rec["agreement_date"] = f"{m.group(1)}{years[0]}"
                    rec["note"] = "agreement date cut off in the PDF; year from the report"
                if to_date(rec.get("agreement_date")) is None:
                    continue
                rec.update(file=fname, page=pg)
                rows.append(rec)
    return pd.DataFrame(rows)


def foia_tables():
    """2005-2012 Agreement to Build sheets."""
    foia = foia_module()
    rows = []
    for y in range(2005, 2013):
        for path in foia.year_dir(y).glob("*gree*uild*.xls"):
            for r in foia.read_table(path, "projectname"):
                rows.append({"project_name": clean(r.get("project_name")), "aka": clean(r.get("aka")),
                             "site_plan": foia.norm_plan(r.get("site_plan")),
                             "total_units": r.get("total_units"), "mpdus": r.get("project_mpdus"),
                             "agreement_date": r.get("date_executed"),
                             "file": path.relative_to(RAW).as_posix(), "page": None})
    d = pd.DataFrame(rows)
    return d[d["project_name"].ne("") & d["agreement_date"].map(lambda v: to_date(v) is not None or hasattr(v, "year"))]


def main():
    parts = [
        foia_tables().assign(method="foia_xls"),
        pd.read_csv(TRANSCRIBED, comment="#", dtype=str).assign(method="transcribed"),
        text_tables().assign(method="text"),
    ]
    d = pd.concat(parts, ignore_index=True)
    if "note" not in d:
        d["note"] = ""
    d["agreement_date"] = pd.to_datetime(
        d["agreement_date"].map(lambda v: pd.Timestamp(v) if hasattr(v, "year") else to_date(v)))
    print("rows without a readable agreement date:", d["agreement_date"].isna().sum())
    d = d[d["agreement_date"].notna()]
    d["year"] = d["agreement_date"].dt.year
    for c in ["total_units", "mpdus", "wfh_units"]:
        d[c] = d[c].map(lambda v: v if isinstance(v, (int, float)) and pd.notna(v) else to_int(v)).astype("Int64")
    d["site_plan"] = d["site_plan"].fillna("").map(lambda s: re.sub(r"[\s-]", "", s).upper())
    for c in ["project_name", "aka", "tenure", "developer"]:
        d[c] = d[c].fillna("").map(clean)
    # "*" after a name marks an Alternative Agreement (MPDUs off site or paid
    # out) in the FOIA sheets and LIHTC units in some later tables
    d["starred"] = d["project_name"].str.endswith("*")
    d["project_name"] = d["project_name"].str.rstrip("* ")
    d = d[["year", "agreement_date", "starred", "project_name", "aka", "site_plan", "total_units", "mpdus",
           "wfh_units", "tenure", "developer", "file", "page", "method", "note"]].sort_values(["year", "agreement_date"])
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    d.to_csv(OUT_FILE, index=False)

    by = d.groupby("year").agg(agreements=("site_plan", "size"), units=("total_units", "sum"),
                               mpdus=("mpdus", "sum"))
    print(f"wrote {len(d)} agreements to {OUT_FILE}")
    for y, r in by.iterrows():
        off = OFFICIAL.get(y)
        flag = ""
        if off:
            got = (r["agreements"], r["units"], r["mpdus"])
            bad = [lab for lab, o, g in zip(["agreements", "units", "MPDUs"], off, got) if o is not None and o != g]
            flag = "ok" if not bad else "MISMATCH " + ", ".join(f"{b} (official {o})" for b, o in
                                                                 zip(["agreements", "units", "MPDUs"], off)
                                                                 if b in bad)
        print(f"  {y}: {r['agreements']:3d} agreements, {r['units']:6d} units, {r['mpdus']:5d} MPDUs  {flag}")


if __name__ == "__main__":
    main()
