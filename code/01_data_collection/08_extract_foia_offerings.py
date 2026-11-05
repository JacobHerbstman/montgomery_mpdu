"""Extract MPDU Offering Agreements (Attachment B) from the 2005-2012 DHCA
annual reports obtained by FOIA.

Input: data/raw/mpdu_annual_reports/maryland_foia_pre_2013/<year> MPDU Annual Report/
  * Offerings*.xls / q_offerings*.xls   Attachment B, one row per offering
  * Agree*to Build*.xls                 Attachment A, new Agreements to Build
                                        (project total units and MPDUs)
  * q_Pipeline_Project_Status*.xls      MPDU pipeline, 2007-2012 (project
                                        total units and MPDUs)
  * *Annual Report to Council*.doc      memo with the official yearly totals
                                        (hard-coded in OFFICIAL below)

Unlike the 2013+ reports, the FOIA Attachment B tables print no project totals,
so total_units and project_mpdus are looked up by site plan (then by name) in
the pipeline and Agreement to Build sheets; totals_source records where each
came from. Year-specific quirks:
  * 2005: no site plans (DHCA subdivision numbers only), so totals and site
    plans come from name matches. The sheet also carries a back-file of
    1991-2004 offerings and a 2006 preview below the totals row; only offerings
    dated in the report's calendar year are kept, in every year.
  * 2008: an Arora Hills offering (24 MPDUs, 28 Aug 2008) was withdrawn by the
    builder; the sheet lists it and then a "Withdrawn:" reversal line. Both are
    dropped, as in the memo's MPDU totals.
  * 2010: the pipeline sheet's name columns are out of line with its plan and
    totals columns for many rows (e.g. Gallery Park's plan and totals under
    "Kingsview Village"), so it is used for site plan matches only.
  * 2008-2012: tenure comes from the "For Sale" / "Rental" section headers;
    2011 has none and the memo says every 2011 MPDU was for sale.
  * An asterisk on the project name marks LIHTC units used to meet the MPDU
    requirement; it is removed and recorded in note.

Output: data/int/02_data_cleaning/00_foia_reports.dta, same variables as
00_ocr_reports.dta (written by 02_extract_mpdu_offerings.py) plus prelim_plan
and totals_source. page is blank and row_on_page is the Excel row number.
The check against the memo totals is printed to the console.
"""

import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = ROOT / "data" / "raw" / "mpdu_annual_reports"
FOIA = REPORTS_DIR / "maryland_foia_pre_2013"
OUT_FILE = ROOT / "data" / "int" / "02_data_cleaning" / "00_foia_reports.dta"

FIELDS = [
    "project_name", "aka", "site_plan", "street_address", "city", "zip",
    "total_units", "project_mpdus", "mpdus_in_offering", "wfh_units",
    "tenure", "offering_date", "developer", "unit_description",
]
NUMERIC = ["total_units", "project_mpdus", "mpdus_in_offering", "wfh_units"]

# Official totals from each year's memo to the Council President.
OFFICIAL = pd.DataFrame(
    [
        (2005, 15, 385, 193, 192),
        (2006, 18, 396, 0, 396),
        (2007, 5, 77, 53, 24),
        (2008, 15, 278, 227, 51),
        (2009, 12, 165, 96, 69),
        (2010, 12, 170, 60, 110),
        (2011, 10, 113, 0, 113),
        (2012, 16, 229, 77, 152),
    ],
    columns=["year", "official_agreements", "official_mpdus",
             "official_rental_mpdus", "official_forsale_mpdus"],
)

# Offerings matched by hand to an Agreement to Build row, (year, project name
# as printed) -> name key of the row. Both rows name the same builder.
#   * Park Potomac townhouse offerings (FP Homes Associates) -> "Fortune Park
#     Townhomes" (Park Potomac Ph II, 8-2004015A). The 2006 sheet prints the
#     high-rise plan 8-20040150 for this offering; its builder and unit
#     description are the townhomes'.
#   * Clarksburg Village, Nov 2005 (Craftstar) -> "Clarksburg Village Phase I"
#     (8-20030020, agreement Feb 2005, signed from Craftstar's address).
MANUAL_MATCHES = {
    (2005, "Park Potomac Townhomes"): "fortuneparktownhomes",
    (2006, "Park Potomac"): "fortuneparktownhomes",
    (2005, "Clarksburg Village"): "clarksburgvillagephi",
}

VALIDATION_NOTES = {
    2005: "Attachment B lists 16 offerings / 400 MPDUs (208 rental); the memo says 15 / 385 (193 rental), "
          "i.e. without the Wheaton Forest rental offering (15). All 16 are kept.",
    2008: "the memo's 15 agreements include the withdrawn Arora Hills offering; its MPDU totals do not",
}


# ---------------------------------------------------------------- helpers

def clean(s) -> str:
    if s is None or (isinstance(s, float) and np.isnan(s)):
        return ""
    return re.sub(r"\s+", " ", str(s)).strip()


def norm_plan(s) -> str:
    """Site/prelim plan number without dashes or spaces: 8-2002022A -> 82002022A."""
    return re.sub(r"[\s-]", "", clean(s)).upper()


def name_key(s) -> str:
    s = clean(s).lower().replace("phase", "ph")
    s = re.sub(r"^the |, the\b", "", s)
    return re.sub(r"[^a-z0-9]", "", s)


def to_int(v):
    s = clean(v).replace(",", "")
    return int(float(s)) if re.fullmatch(r"\d+(\.0+)?", s) else None


def to_date(v):
    if isinstance(v, (pd.Timestamp, np.datetime64)) or hasattr(v, "year"):
        return pd.Timestamp(v)
    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", clean(v))
    return pd.Timestamp(int(m[3]), int(m[1]), int(m[2])) if m else None


def year_dir(y) -> Path:
    return FOIA / f"{y} MPDU Annual Report"


def one_file(y, pattern) -> Path:
    hits = sorted(year_dir(y).glob(pattern))
    assert len(hits) == 1, (y, pattern, hits)
    return hits[0]


def header_row(raw: pd.DataFrame, first_col_text: str) -> int:
    for i in range(len(raw)):
        cells = [clean(v).lower() for v in raw.iloc[i] if clean(v)]
        if cells and cells[0].replace(" ", "") == first_col_text:
            return i
    raise ValueError(f"header starting {first_col_text!r} not found")


def map_header(h: str):
    h = clean(h).lower()
    if h in ("project name", "projectname"):
        return "project_name"
    if h == "aka":
        return "aka"
    if h.startswith("site plan") or h == "plan #":  # 2005: "Site or Prelim." / "Plan #" on two rows
        return "site_plan"
    if h.startswith("prel plan"):
        return "prelim_plan"
    if h == "offering date":
        return "offering_date"
    if h in ("no. of units", "no of units", "no. of mpdus"):
        return "mpdus_in_offering"
    if h in ("sale/rental", "sale/ rental", "rental or for sale"):
        return "tenure"
    if h in ("builder name", "builder"):
        return "developer"
    if h == "description":
        return "unit_description"
    if h == "date executed":
        return "date_executed"
    if h.replace(" ", "") == "totalunits":
        return "total_units"
    if h == "total mpdus":
        return "project_mpdus"
    return None


def read_table(path: Path, first_col_text: str):
    """Rows below the header, as dicts keyed by our field names, with the
    Excel row number and any single-cell section label seen above them."""
    raw = pd.read_excel(path, header=None, dtype=object)
    h = header_row(raw, first_col_text)
    cols = {j: map_header(v) for j, v in raw.iloc[h].items()}
    header = [clean(v) for v in raw.iloc[h] if clean(v)]
    rows, section = [], ""
    for i in range(h + 1, len(raw)):
        cells = {j: v for j, v in raw.iloc[i].items() if clean(v)}
        if not cells:
            continue
        texts = [clean(v) for v in cells.values()]
        if len(cells) == 1 and texts[0].lower() in ("for sale", "rental"):
            section = texts[0]
            continue
        # the header repeats in the 2005 sheet above its 2006 preview
        if texts == header:
            break
        rec = {f: raw.iat[i, j] for j, f in cols.items() if f}
        rec["_row"] = i + 1
        rec["_section"] = section
        rec["_texts"] = texts
        rows.append(rec)
    return rows


# ---------------------------------------------------------------- project totals

def load_totals():
    """Project totals from every Agreement to Build and pipeline sheet:
    one row per (sheet, project) with site plan, name keys and totals."""
    out = []
    for y in range(2005, 2013):
        sources = [("agreement", p) for p in year_dir(y).glob("*gree*uild*.xls")]
        sources += [("pipeline", p) for p in year_dir(y).glob("*ipeline*.xls")]
        for kind, p in sources:
            first = "currentstatus" if kind == "pipeline" else "projectname"
            if kind == "pipeline" and y >= 2010:
                first = "current_status"
            for r in read_table(p, first):
                tu, tm = to_int(r.get("total_units")), to_int(r.get("project_mpdus"))
                if tu is None or tm is None or not clean(r.get("project_name")):
                    continue
                out.append({
                    "year": y, "kind": kind, "site_plan": norm_plan(r.get("site_plan")),
                    "name": name_key(r.get("project_name")), "aka": name_key(r.get("aka")),
                    "total_units": tu, "project_mpdus": tm,
                })
    return pd.DataFrame(out)


def find_totals(tot, site_plan, name, aka, year, offered):
    """(total_units, project_mpdus, site_plan, source) for one offering.

    Candidates, in order: same site plan; same 8-character site plan stem;
    same project name or aka (not from the 2010 pipeline, whose names are
    misaligned). Within the first tier that has candidates, the pipeline sheet
    of the offering's own year wins, then Agreements to Build, then the
    pipeline sheet nearest in time. Stem matches are used only when they point
    to a single site plan; name matches when the sheets nearest in time do.
    Candidates with fewer project MPDUs than the offering are dropped (e.g. the
    2006 sheet prints Bethesda Crest's plan for Ashmore at Germantown). If the
    chosen sheet lists the plan more than once with different totals (phases),
    the name decides; otherwise the totals are left blank."""
    tiers = []
    keys = {k for k in (name, aka) if k}
    if site_plan:
        tiers.append(("site plan", tot[tot.site_plan == site_plan]))
        if len(site_plan) >= 8:
            tiers.append(("site plan stem", tot[tot.site_plan.str[:8] == site_plan[:8]]))
    if keys:
        named = tot[~((tot.kind == "pipeline") & (tot.year == 2010))]
        c = named[named.name.isin(keys) | named.aka.isin(keys)]
        tiers.append(("name", c[(c.year - year).abs() == (c.year - year).abs().min()]))
    for how, c in tiers:
        if offered is not None:
            c = c[c.project_mpdus >= offered]
        if c.empty:
            continue
        if how != "site plan" and c.site_plan.nunique() > 1:
            continue
        c = c.assign(rank=np.select([(c.kind == "pipeline") & (c.year == year), c.kind == "agreement"], [0, 1], 2),
                     dist=(c.year - year).abs())
        best = c.sort_values(["rank", "dist", "year"]).iloc[0]
        same = c[(c.kind == best.kind) & (c.year == best.year)]
        if same[["total_units", "project_mpdus"]].drop_duplicates().shape[0] > 1:
            same = same[same.name.isin(keys) | same.aka.isin(keys)]
            if same[["total_units", "project_mpdus"]].drop_duplicates().shape[0] != 1:
                return None, None, None, f"ambiguous: phases of {best.site_plan} in {best.kind} {best.year}"
            best = same.iloc[0]
        label = {0: f"pipeline {year}", 1: f"agreement to build {best.year}"}.get(best["rank"], f"pipeline {best.year}")
        return best.total_units, best.project_mpdus, best.site_plan, f"{label} ({how})"
    return None, None, None, ""


# ---------------------------------------------------------------- offerings

def extract_year(y):
    path = one_file(y, "*ffering*.xls")
    rows = read_table(path, "subdivno" if y == 2005 else "projectname")
    out, n_other_year = [], 0
    for r in rows:
        if "Withdrawn:" in r["_texts"]:
            # reversal line: drop the offering it withdraws
            hit = [k for k, o in enumerate(out) if o["site_plan"] == norm_plan(r.get("site_plan"))
                   and o["mpdus_in_offering"] == to_int(r.get("mpdus_in_offering"))]
            assert len(hit) == 1, r["_texts"]
            gone = out.pop(hit[0])
            print(f"  {y}: dropped withdrawn offering {gone['project_name']} {gone['offering_date']:%d %b %Y} "
                  f"({gone['mpdus_in_offering']} MPDUs)")
            continue
        date = to_date(r.get("offering_date"))
        name = clean(r.get("project_name"))
        if date is None or not name:
            continue  # totals, subtotals, footnotes
        if date.year != y:
            n_other_year += 1
            continue
        note = []
        if name.endswith("*"):
            name = name.rstrip("* ")
            note.append("LIHTC units used to meet the MPDU requirement")
        tenure = clean(r.get("tenure")) or r["_section"] or ("For Sale" if y == 2011 else "")
        tenure = "Rental" if "rent" in tenure.lower() else "For-Sale" if "sale" in tenure.lower() else None
        out.append({
            "offering_year": y, "offering_date": date,
            "project_name": name, "aka": clean(r.get("aka")) or None,
            "site_plan": norm_plan(r.get("site_plan")) or None,
            "prelim_plan": norm_plan(r.get("prelim_plan")) or None,
            "mpdus_in_offering": to_int(r.get("mpdus_in_offering")),
            "tenure": tenure,
            "developer": clean(r.get("developer")) or None,
            "unit_description": clean(r.get("unit_description")) or None,
            "file": path.relative_to(REPORTS_DIR).as_posix(),
            "row_on_page": r["_row"], "method": "xls",
            "note": "; ".join(note) or None,
        })
    if n_other_year:
        print(f"  {y}: skipped {n_other_year} rows dated outside {y}")
    return out


def main():
    tot = load_totals()
    rows = []
    for y in range(2005, 2013):
        got = extract_year(y)
        print(f"{y}: {len(got)} offerings")
        rows += got
    df = pd.DataFrame(rows)

    filled = []
    for r in df.itertuples():
        manual = MANUAL_MATCHES.get((r.offering_year, r.project_name))
        if manual:
            hit = tot[(tot.kind == "agreement") & (tot.name == manual)]
            assert hit[["site_plan", "total_units", "project_mpdus"]].drop_duplicates().shape[0] == 1, manual
            h = hit.iloc[0]
            filled.append((h.total_units, h.project_mpdus, h.site_plan, f"agreement to build {h.year} (manual match)"))
            df.at[r.Index, "site_plan"] = None  # replaced by the matched row's plan below
        else:
            filled.append(find_totals(tot, r.site_plan, name_key(r.project_name), name_key(r.aka),
                                      r.offering_year, r.mpdus_in_offering))
    df["total_units"] = [f[0] for f in filled]
    df["project_mpdus"] = [f[1] for f in filled]
    df["totals_source"] = [f[3] for f in filled]
    # 2005 prints no site plans: take the one the name (or manual) match points to
    from_name = df.site_plan.isna() & pd.Series([bool(f[2]) for f in filled])
    df.loc[from_name, "site_plan"] = [f[2] for f, m in zip(filled, from_name) if m]
    df.loc[from_name, "note"] = df.loc[from_name, "note"].fillna("").map(
        lambda s: "; ".join(x for x in [s, "site plan from name match"] if x))

    for f in FIELDS:
        if f not in df:
            df[f] = None
    for f in NUMERIC:
        df[f] = df[f].astype("Int64")
    df["page"] = np.nan
    df["corrected"] = False
    df["check"] = row_checks(df)
    df = df[["offering_year", "offering_date"] + [f for f in FIELDS if f != "offering_date"]
            + ["file", "page", "row_on_page", "method", "corrected", "note", "check",
               "prelim_plan", "totals_source"]]
    df = df.sort_values(["offering_year", "offering_date", "row_on_page"]).reset_index(drop=True)
    write_dta(df, OUT_FILE)

    by = df.groupby("offering_year").agg(agreements=("file", "size"), mpdus=("mpdus_in_offering", "sum"))
    by["rental_mpdus"] = df[df.tenure == "Rental"].groupby("offering_year")["mpdus_in_offering"].sum()
    by["forsale_mpdus"] = df[df.tenure == "For-Sale"].groupby("offering_year")["mpdus_in_offering"].sum()
    by["with_totals"] = df.groupby("offering_year")["total_units"].count()
    val = OFFICIAL.merge(by.reset_index().rename(columns={"offering_year": "year"}), on="year", how="outer").fillna(0)
    val["ok"] = ((val.agreements == val.official_agreements) & (val.mpdus == val.official_mpdus)
                 & (val.rental_mpdus == val.official_rental_mpdus) & (val.forsale_mpdus == val.official_forsale_mpdus))

    print(f"\nwrote {len(df)} offerings to {OUT_FILE}")
    print(f"with project totals: {df.total_units.notna().sum()} / {len(df)}")
    print(df.totals_source.str.replace(r"\d{4}", "YYYY", regex=True).value_counts().to_string())
    print(f"rows with consistency flags: {(df['check'] != '').sum()}")
    print(val[["year", "agreements", "official_agreements", "mpdus", "official_mpdus", "rental_mpdus",
               "official_rental_mpdus", "forsale_mpdus", "official_forsale_mpdus", "with_totals", "ok"]]
          .astype({c: int for c in val.columns if c not in ("ok",)}).to_string(index=False))
    for y, note in VALIDATION_NOTES.items():
        print(f"  {y}: {note}")


def row_checks(df):
    flags = [[] for _ in range(len(df))]
    for i, r in enumerate(df.itertuples()):
        if pd.isna(r.mpdus_in_offering):
            flags[i].append("no MPDUs in offering")
        if pd.notna(r.mpdus_in_offering) and pd.notna(r.project_mpdus) and r.mpdus_in_offering > r.project_mpdus:
            flags[i].append("offering > project MPDUs")
        if pd.isna(r.total_units):
            flags[i].append("no project totals")
        if isinstance(r.site_plan, str) and not re.fullmatch(r"8\d{7}[0-9A-Z]", r.site_plan):
            flags[i].append("site plan format")
        if r.tenure is None:
            flags[i].append("no tenure")
    return ["; ".join(f) for f in flags]


VAR_LABELS = {
    "offering_year": "Calendar year of offering agreement",
    "offering_date": "Offering agreement date (DHCA: date MPDUs counted as built)",
    "project_name": "Project name",
    "aka": "Also known as",
    "site_plan": "Site plan number",
    "street_address": "Street address (not in FOIA reports)",
    "city": "City (not in FOIA reports)",
    "zip": "ZIP code (not in FOIA reports)",
    "total_units": "Total units in project (from pipeline/Agreement to Build)",
    "project_mpdus": "Total MPDUs in project (from pipeline/Agreement to Build)",
    "mpdus_in_offering": "MPDUs in this offering",
    "wfh_units": "Workforce housing units (not in FOIA reports)",
    "tenure": "Rental or For-Sale",
    "developer": "Builder name (2005-2007 only)",
    "unit_description": "Unit description (2005-2006 only)",
    "file": "Source spreadsheet (relative to mpdu_annual_reports)",
    "page": "Blank for spreadsheets",
    "row_on_page": "Excel row number",
    "method": "Extraction: xls",
    "corrected": "Always 0 (no hand corrections)",
    "note": "Note",
    "check": "Consistency flags",
    "prelim_plan": "Preliminary plan number",
    "totals_source": "Sheet and match used for total_units/project_mpdus",
}


def write_dta(df, path):
    out = df.copy()
    for f in NUMERIC + ["offering_year", "page", "row_on_page"]:
        out[f] = out[f].astype("float64")  # Stata missing for blanks
    out["corrected"] = out["corrected"].astype("int8")
    for c in out.columns:
        if out[c].dtype == object:
            out[c] = out[c].fillna("").astype(str)
    path.parent.mkdir(parents=True, exist_ok=True)
    out.to_stata(path, write_index=False, version=118, convert_dates={"offering_date": "td"},
                 data_label="MPDU offering agreements, DHCA annual reports 2005-2012 (FOIA)",
                 variable_labels=VAR_LABELS)


if __name__ == "__main__":
    main()
