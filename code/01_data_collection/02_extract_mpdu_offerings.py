"""Extract MPDU Offering Agreements (Attachment B) from the DHCA annual reports.

Run 01_download_mpdu_reports.py first.

Each report's Attachment B lists every Offering Agreement executed that year:
project, site plan number, total units, project MPDUs, MPDUs in the offering,
workforce (WFH) units, rental/for-sale, offering date, developer. DHCA counts
an MPDU as "built" on its offering date.

The reports come in three physical formats, handled separately:
  * text PDFs (2018-19, 2021, 2023, 2024): tables read with PyMuPDF
    find_tables(); some are printed sideways and come out transposed.
  * scanned PDFs (2013-16, 2017, 2020, 2022): table grid detected with
    OpenCV, then each cell OCR'd with tesseract (digits-only for numeric
    columns).
  * 2025: the published PDF only contains a cropped middle slice of the
    table (no project name, developer, or year of the offering date).

OCR errors are fixed via data/raw/mpdu_annual_reports/manual_corrections.csv
(file, page, row_on_page, field, ocr_value, value, note), checked by eye
against the page images. A correction is applied only if the cell still holds
ocr_value, so a change in OCR output can't silently misapply it. Each year's extracted totals are
compared to the official totals printed in the report text.

Output: data/int/02_data_cleaning/00_ocr_reports.dta, one row per offering
agreement. The check against official totals is printed to the console.

Usage:
  python 02_extract_mpdu_offerings.py                   full run (OCR takes ~4-6 min)
  python 02_extract_mpdu_offerings.py --no-corrections  raw OCR output, e.g. to write new corrections

Requires: pymupdf, opencv-python, numpy, pandas, and the tesseract binary.
"""

import re
import subprocess
import tempfile
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
import pymupdf

pymupdf.no_recommend_layout()

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "mpdu_annual_reports"
OUT_FILE = ROOT / "data" / "int" / "02_data_cleaning" / "00_ocr_reports.dta"
CORRECTIONS = RAW / "manual_corrections.csv"

FIELDS = [
    "project_name", "aka", "site_plan", "street_address", "city", "zip",
    "total_units", "project_mpdus", "mpdus_in_offering", "wfh_units",
    "tenure", "offering_date", "developer", "unit_description",
]
NUMERIC = ["total_units", "project_mpdus", "mpdus_in_offering", "wfh_units"]

# Scanned column layouts, left to right.
SCAN_COLS_2013 = ["project_name", "aka", "site_plan", "total_units", "project_mpdus",
                  "mpdus_in_offering", "wfh_units", "tenure", "offering_date", "developer"]
SCAN_COLS_2020 = ["project_name", "aka", "site_plan", "total_units", "project_mpdus",
                  "mpdus_in_offering", "tenure", "offering_date", "developer"]
SCAN_COLS_2022 = SCAN_COLS_2013 + ["unit_description"]

# Attachment B pages. rot = quarter turns (np.rot90 k) to make a rendered scan upright.
REPORTS = [
    {"file": "annual_report_mpdu_2013-2016.pdf", "method": "ocr", "pages": [9, 10, 11, 12], "rot": 3, "cols": SCAN_COLS_2013},
    {"file": "annual_report_mpdu_2017.pdf", "method": "ocr", "pages": [5], "rot": 3, "cols": SCAN_COLS_2013, "row_mode": "anchor"},
    {"file": "annual_report_mpdu_2018-2019.pdf", "method": "text", "pages": [6, 7]},
    {"file": "annual_report_mpdu_2020.pdf", "method": "ocr", "pages": [7], "rot": 3, "cols": SCAN_COLS_2020},
    {"file": "annual_report_mpdu_2021.pdf", "method": "text", "pages": [9]},
    {"file": "annual_report_mpdu_2022.pdf", "method": "ocr", "pages": [10], "rot": 3, "cols": SCAN_COLS_2022},
    {"file": "annual_report_mpdu_2023.pdf", "method": "text", "pages": [12, 13]},
    {"file": "annual_report_mpdu_2024.pdf", "method": "text", "pages": [12]},
    {"file": "annual_report_mpdu_2025.pdf", "method": "clipped2025", "pages": [12], "year": 2025},
]

# Official totals from each report (memo text, or the Attachment B totals row).
# DHCA's agreement counts include WFH-only offerings in some years but not others.
OFFICIAL = pd.DataFrame(
    [
        (2013, 30, 23, 576, 435, 141),
        (2014, 24, 18, 336, 167, 169),
        (2015, 27, 17, 335, 185, 150),
        (2016, 22, 19, 329, 245, 84),
        (2017, 26, 21, 364, 219, 145),
        (2018, 22, 16, 234, 122, 112),
        (2019, 16, 13, 306, 228, 78),
        (2020, 14, 13, 244, 162, 82),
        (2021, 24, 14, 320, 185, 135),
        (2022, 15, 11, 184, 122, 62),
        (2023, 14, 11, 325, 293, 32),
        (2024, 22, 15, 305, 227, 78),
        (2025, 22, 14, 521, 387, 134),
    ],
    columns=["year", "official_agreements", "official_developments", "official_mpdus",
             "official_rental_mpdus", "official_forsale_mpdus"],
)

VALIDATION_NOTES = {
    2017: "rows in the report's own table sum to 216 rental / 148 for-sale; its printed totals row says 219 / 145 (total 364 agrees)",
    2025: "published PDF contains only a cropped slice of Attachment B: 19 of 22 offerings, no project names or developers",
}

# Recurring OCR slips in the scanned reports' text columns.
OCR_TEXT_FIXES = [
    (r"^[\s'‘’\"|]+", ""),                    # stray marks at the left cell edge
    (r"[\s|!?\]\u2014_-]+$", ""),             # ... and at the right edge
    (r"\bHomes\.$", "Homes"),
    (r"\bE[VY] ?A\b", "EYA"),
    (r",\s*l?[Iil]n[ce]\.", ", Inc."),
    (r"\bMHP, Elm\b", "MHP/ Elm"),
    (r"(Lot 31)4A?\b", r"\1A"),
]

DATE_RE = re.compile(r"(\d{1,2})\s*/\s*(\d{1,2})\s*/\s*(\d{2,4})")


# ---------------------------------------------------------------- helpers

def clean(s) -> str:
    if s is None:
        return ""
    s = str(s).replace("‐", "-").replace("‑", "-").replace("\n", " ")
    return re.sub(r"\s+", " ", s).strip()


def to_int(s):
    s = clean(s).replace(",", "")
    m = re.fullmatch(r"\d+", s)
    return int(s) if m else None


def norm_tenure(s):
    s = clean(s).lower()
    if "rent" in s or "ental" in s:
        return "Rental"
    if "sale" in s or "sal" in s:
        return "For-Sale"
    return s or None


def parse_date(s):
    m = DATE_RE.search(clean(s).replace(" ", ""))
    if not m:
        return None
    mo, d, y = map(int, m.groups())
    if y < 100:
        y += 2000
    try:
        return pd.Timestamp(year=y, month=mo, day=d)
    except ValueError:
        return None


def map_header(h: str):
    h = clean(h).lower().replace("’", "'")
    if not h:
        return None
    if "wfh" in h or "workforce" in h:
        return "wfh_units"
    if "in offering" in h:
        return "mpdus_in_offering"
    if "offering" in h and "date" in h:
        return "offering_date"
    if h.startswith("project name"):
        return "project_name"
    if h == "aka":
        return "aka"
    if "site plan" in h:
        return "site_plan"
    if "street" in h:
        return "street_address"
    if h == "city":
        return "city"
    if "zip" in h:
        return "zip"
    if "total units" in h:
        return "total_units"
    if re.fullmatch(r"(total )?m[pd][dp]us", h):
        return "project_mpdus"
    if "rental" in h or h.endswith("sale"):
        return "tenure"
    if "developer" in h or "development name" in h:
        return "developer"
    if "unit desc" in h:
        return "unit_description"
    return None


def finalize(rec: dict, source: dict) -> dict:
    out = {f: clean(rec.get(f)) or None for f in FIELDS}
    for f in NUMERIC:
        out[f] = to_int(rec.get(f))
    out["tenure"] = norm_tenure(rec.get("tenure"))
    # site plan cells sometimes pick up overflow text from the AKA column
    plans = re.findall(r"8-?\d{6,7}[0-9A-Z]", (out["site_plan"] or "").replace(" ", ""))
    out["site_plan"] = "/".join(plans) or ((out["site_plan"] or "").replace(" ", "") or None)
    for f in ["project_name", "aka", "developer"]:
        if out[f] and source.get("method") == "ocr":
            for pat, fix in OCR_TEXT_FIXES:
                out[f] = re.sub(pat, fix, out[f])
            out[f] = out[f] or None
    out.update(source)
    return out


# ---------------------------------------------------------------- text PDFs

def extract_text_pdf(cfg):
    doc = pymupdf.open(RAW / cfg["file"])
    rows = []
    for pg in cfg["pages"]:
        page = doc[pg - 1]
        for tab in page.find_tables(strategy="lines").tables:
            grid = [[clean(c) for c in r] for r in tab.extract()]
            # sideways tables come out transposed: header labels down the first column
            if not any(map_header(c) == "offering_date" for c in grid[0]):
                grid = [list(col) for col in zip(*grid)]
            hdr_i = next((i for i, r in enumerate(grid) if any(map_header(c) == "offering_date" for c in r)), None)
            if hdr_i is None:
                continue
            fields = [map_header(c) for c in grid[hdr_i]]
            n = 0
            for r in grid[hdr_i + 1:]:
                rec = {f: v for f, v in zip(fields, r) if f}
                if parse_date(rec.get("offering_date")) is None:
                    continue  # year headers, blank spacer rows, totals
                n += 1
                rows.append(finalize(rec, {"file": cfg["file"], "page": pg, "row_on_page": n, "method": "text"}))
    return rows


# ---------------------------------------------------------------- scanned PDFs

def render_gray(doc, pg, dpi=300):
    pm = doc[pg - 1].get_pixmap(dpi=dpi, colorspace=pymupdf.csGRAY)
    return np.frombuffer(pm.samples, np.uint8).reshape(pm.height, pm.width).copy()


def line_positions(mask, axis, minfrac, gap=6):
    prof = (mask > 0).sum(axis=axis)
    idx = np.where(prof > prof.max() * minfrac)[0]
    groups = []
    for i in idx:
        if groups and i - groups[-1][-1] <= gap:
            groups[-1].append(i)
        else:
            groups.append([i])
    return [int(np.mean(g)) for g in groups]


def rule_masks(img):
    bw = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 25, 15)
    hmask = cv2.morphologyEx(bw, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, (img.shape[1] // 25, 1)))
    vmask = cv2.morphologyEx(bw, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, (1, img.shape[0] // 40)))
    return bw, hmask, vmask


def deskew(img):
    """Rotate so the table's long horizontal rules are level."""
    _, hmask, _ = rule_masks(img)
    segs = cv2.HoughLinesP(hmask, 1, np.pi / 3600, threshold=200, minLineLength=img.shape[1] // 4, maxLineGap=30)
    if segs is None:
        return img
    angles = [np.degrees(np.arctan2(y2 - y1, x2 - x1)) for x1, y1, x2, y2 in segs[:, 0]]
    angle = float(np.median(angles))
    if abs(angle) < 0.05:
        return img
    h, w = img.shape
    rot = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
    return cv2.warpAffine(img, rot, (w, h), flags=cv2.INTER_CUBIC, borderValue=255)


def table_grid(img):
    _, hmask, vmask = rule_masks(img)
    ys = line_positions(hmask, 1, 0.15)
    xs = line_positions(vmask, 0, 0.2)
    # scanned rules can be faint: split any row taller than ~1.6x the typical height
    heights = np.diff(ys)
    typical = np.median(heights[heights > 20]) if (heights > 20).any() else 0
    out = [ys[0]]
    for y0, y1 in zip(ys, ys[1:]):
        k = int(round((y1 - y0) / typical)) if typical else 1
        if typical and (y1 - y0) > 1.6 * typical and k > 1:
            out += [int(y0 + (y1 - y0) * j / k) for j in range(1, k)]
        out.append(y1)
    lines = cv2.dilate(cv2.bitwise_or(hmask, vmask), np.ones((5, 5), np.uint8))
    return out, xs, lines


def glyphs_only(cell, target_h=40):
    """Binarize, drop leftover rule fragments and specks, crop to the
    characters and scale them to a height tesseract reads reliably."""
    _, bw = cv2.threshold(cell, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    n, lab, st, _ = cv2.connectedComponentsWithStats(bw, 8)
    keep = np.zeros_like(bw)
    for i in range(1, n):
        _, _, w, h, area = st[i]
        if h >= 0.3 * cell.shape[0] and w < 0.8 * cell.shape[1] and area > 8:
            keep[lab == i] = 255
    ys, xs = np.where(keep > 0)
    if len(ys) == 0:
        return None
    crop = 255 - keep[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    s = target_h / crop.shape[0]
    crop = cv2.resize(crop, None, fx=s, fy=s, interpolation=cv2.INTER_CUBIC)
    return cv2.copyMakeBorder(crop, 30, 30, 30, 30, cv2.BORDER_CONSTANT, value=255)


def ocr_cell(cell, kind, tmpdir):
    if (cell < 140).sum() < 15:
        return ""
    path = Path(tmpdir) / "cell.png"
    whitelist = {"number": "0123456789,", "date": "0123456789/",
                 "siteplan": "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"}.get(kind)
    if whitelist is None:
        cell = cv2.copyMakeBorder(cv2.resize(cell, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC),
                                  20, 20, 20, 20, cv2.BORDER_CONSTANT, value=255)
        cv2.imwrite(str(path), cell)
        args = ["tesseract", str(path), "-", "--psm", "6"]
        return clean(subprocess.run(args, capture_output=True, text=True).stdout)
    plain = cv2.copyMakeBorder(cv2.resize(cell, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC),
                               20, 20, 20, 20, cv2.BORDER_CONSTANT, value=255)
    glyphs = glyphs_only(cell)
    # isolated glyphs read best for short numbers; the plain upscaled cell for
    # dates and site plans (the glyph filter can drop slashes and letters)
    variants = [glyphs, plain] if kind == "number" else [plain, glyphs]
    want = {"number": r"\d[\d,]*", "date": r"\d{1,2}/\d{1,2}/\d{2,4}", "siteplan": r"[0-9A-Z]{6,}"}[kind]
    first = ""
    for img in variants:
        if img is None:
            continue
        cv2.imwrite(str(path), img)
        for psm in ("7", "8", "13", "10"):
            args = ["tesseract", str(path), "-", "--psm", psm, "-c", f"tessedit_char_whitelist={whitelist}"]
            txt = clean(subprocess.run(args, capture_output=True, text=True).stdout)
            first = first or txt
            if re.fullmatch(want, txt.replace(" ", "")):
                return txt
    return first


def kind_of(field):
    if field in NUMERIC:
        return "number"
    return {"offering_date": "date", "site_plan": "siteplan"}.get(field, "text")


def text_bands(strip, min_h=12):
    """Vertical extents of text lines in a (line-free) image strip."""
    ink = (strip < 140).sum(axis=1) > 2
    bands, start = [], None
    for y, on in enumerate(np.append(ink, False)):
        if on and start is None:
            start = y
        elif not on and start is not None:
            if y - start >= min_h:
                bands.append((start, y))
            start = None
    return bands


def row_spans(clean_img, ys, xs, di, cfg, tmpdir):
    """Row extents (y0, y1) for each offering, per column.

    Default: rows are the spaces between horizontal rules. With
    row_mode="anchor" (scans without row rules), each text line in the date
    column that reads as a date anchors a row of the typical line pitch."""
    ncol = len(cfg["cols"])
    if cfg.get("row_mode") != "anchor":
        spans = [(y0, y1) for y0, y1 in zip(ys, ys[1:]) if y1 - y0 >= 20]
        return [[s] * ncol for s in spans]
    x0, x1 = xs[di] + 3, xs[di + 1] - 2
    anchors = []
    for b0, b1 in text_bands(clean_img[:, x0:x1]):
        txt = ocr_cell(clean_img[max(b0 - 6, 0):b1 + 6, x0:x1], "date", tmpdir)
        if parse_date(txt):
            anchors.append((b0 + b1) / 2)
    pitch = float(np.median(np.diff(anchors))) if len(anchors) > 1 else 50.0
    return [[(int(a - pitch / 2), int(a + pitch / 2))] * ncol for a in anchors]


def extract_scanned_pdf(cfg):
    doc = pymupdf.open(RAW / cfg["file"])
    rows = []
    with tempfile.TemporaryDirectory() as tmpdir:
        for pg in cfg["pages"]:
            img = deskew(np.ascontiguousarray(np.rot90(render_gray(doc, pg), cfg["rot"])))
            ys, xs, lines = table_grid(img)
            clean_img = img.copy()
            clean_img[lines > 0] = 255
            ncol = len(cfg["cols"])
            if len(xs) - 1 != ncol:
                print(f"  WARNING {cfg['file']} p{pg}: found {len(xs) - 1} columns, expected {ncol}")
            xs = xs[: ncol + 1]
            di = cfg["cols"].index("offering_date")
            n = 0
            for spans in row_spans(clean_img, ys, xs, di, cfg, tmpdir):
                # date first: rows without an offering date are headers/totals/spacers
                cells = {}
                y0, y1 = spans[di]
                cells["offering_date"] = ocr_cell(clean_img[y0 + 2:y1 - 1, xs[di] + 2:xs[di + 1] - 1], "date", tmpdir)
                if parse_date(cells["offering_date"]) is None:
                    continue
                for j, f in enumerate(cfg["cols"]):
                    if f == "offering_date":
                        continue
                    y0, y1 = spans[j]
                    cells[f] = ocr_cell(clean_img[y0 + 2:y1 - 1, xs[j] + 2:xs[j + 1] - 1], kind_of(f), tmpdir)
                n += 1
                rows.append(finalize(cells, {"file": cfg["file"], "page": pg, "row_on_page": n, "method": "ocr"}))
    return rows


# ---------------------------------------------------------------- 2025 (clipped)

def extract_2025(cfg):
    """The 2025 PDF only contains a cropped slice of Attachment B. Columns are
    identified by content, since the header row is not on the page."""
    # The page is printed sideways, so find_tables returns one table row per
    # field and one table column per offering, in this fixed field order.
    field_order = ["tenure", "wfh_units", "mpdus_in_offering", "project_mpdus", "total_units",
                   "site_plan", "zip", "city", "street_address"]
    doc = pymupdf.open(RAW / cfg["file"])
    rows = []
    for pg in cfg["pages"]:
        page = doc[pg - 1]
        tab = max(page.find_tables(strategy="lines").tables, key=lambda t: t.row_count * t.col_count)
        grid = tab.extract()
        tenure_cells = tab.rows[0].cells
        # the (truncated) offering dates lie outside the ruled table; match them to
        # offerings by position across the page
        date_words = [w for w in page.get_text("words") if re.fullmatch(r"\d{1,2}/\d{0,2}/?\d?", w[4])]
        n = 0
        for j, bbox in enumerate(tenure_cells):
            rec = {f: grid[i][j] for i, f in enumerate(field_order)}
            if norm_tenure(rec["tenure"]) not in ("Rental", "For-Sale") or bbox is None:
                continue
            x0, _, x1, _ = bbox
            frag = next((w[4] for w in date_words if x0 <= (w[0] + w[2]) / 2 <= x1), "")
            m = re.match(r"(\d{1,2})/(\d{1,2})", frag)
            rec["offering_date"] = f"{m.group(1)}/{m.group(2)}/{cfg['year']}" if m else ""
            n += 1
            out = finalize(rec, {"file": cfg["file"], "page": pg, "row_on_page": n, "method": "text_clipped"})
            out["note"] = "2025 PDF is cropped: no project name/developer; offering year assumed 2025"
            rows.append(out)
    return rows


# ---------------------------------------------------------------- main

def as_text(v) -> str:
    """Cell value as it appears in manual_corrections.csv ('' for blank)."""
    if v is None or (isinstance(v, float) and np.isnan(v)) or v is pd.NA:
        return ""
    if isinstance(v, (int, np.integer)) or (isinstance(v, float) and v.is_integer()):
        return str(int(v))
    return str(v)


def apply_corrections(df):
    if not CORRECTIONS.exists():
        return df
    corr = pd.read_csv(CORRECTIONS, dtype=str, comment="#", keep_default_na=False)
    skipped = 0
    for _, c in corr.iterrows():
        m = (df["file"] == c["file"]) & (df["page"] == int(c["page"])) & (df["row_on_page"] == int(c["row_on_page"]))
        if m.sum() != 1:
            print(f"  WARNING correction matched {m.sum()} rows: {dict(c)}")
            skipped += 1
            continue
        current = as_text(df.loc[m, c["field"]].iloc[0])
        if current != c["ocr_value"]:
            # OCR output changed since the correction was written: the row may
            # have shifted, so don't apply blindly
            print(f"  WARNING {c['file']} p{c['page']} row {c['row_on_page']} {c['field']}: "
                  f"expected OCR value {c['ocr_value']!r}, found {current!r}; correction not applied")
            skipped += 1
            continue
        val = c["value"] or None
        if c["field"] in NUMERIC:
            val = to_int(val)
        elif c["field"] == "tenure":
            val = norm_tenure(val)
        df.loc[m, c["field"]] = val
        df.loc[m, "corrected"] = True
    print(f"applied {len(corr) - skipped} of {len(corr)} manual corrections")
    return df


def main(use_corrections=True):
    rows = []
    for cfg in REPORTS:
        print(f"{cfg['file']} ({cfg['method']})")
        fn = {"text": extract_text_pdf, "ocr": extract_scanned_pdf, "clipped2025": extract_2025}[cfg["method"]]
        got = fn(cfg)
        print(f"  {len(got)} rows")
        rows += got
    df = pd.DataFrame(rows)
    for f in NUMERIC:
        df[f] = df[f].astype("Int64")

    df["corrected"] = False
    if use_corrections:
        df = apply_corrections(df)
    df["offering_date"] = df["offering_date"].map(parse_date)
    df["offering_year"] = df["offering_date"].dt.year.astype("Int64")
    if "note" not in df:
        df["note"] = None
    df = df[["offering_year", "offering_date"] + [f for f in FIELDS if f != "offering_date"]
            + ["file", "page", "row_on_page", "method", "corrected", "note"]]
    df = df.sort_values(["offering_year", "offering_date", "file", "page", "row_on_page"]).reset_index(drop=True)
    df["check"] = row_checks(df)
    write_dta(df, OUT_FILE)

    # DHCA's agreement counts sometimes include WFH-only offerings and sometimes
    # not, so report both
    mp = df[df["mpdus_in_offering"].fillna(0) > 0]
    by = df.groupby("offering_year").agg(rows=("file", "size")).join(
        mp.groupby("offering_year").agg(
            agreements=("mpdus_in_offering", "size"),
            mpdus=("mpdus_in_offering", "sum"),
            developments=("site_plan", "nunique"),
        ))
    by["rental_mpdus"] = mp[mp.tenure == "Rental"].groupby("offering_year")["mpdus_in_offering"].sum()
    by["forsale_mpdus"] = mp[mp.tenure == "For-Sale"].groupby("offering_year")["mpdus_in_offering"].sum()
    val = OFFICIAL.merge(by.reset_index().rename(columns={"offering_year": "year"}), on="year", how="outer")
    val = val.fillna({c: 0 for c in ["rows", "agreements", "mpdus", "rental_mpdus", "forsale_mpdus", "developments"]})
    val["ok"] = (((val.agreements == val.official_agreements) | (val.rows == val.official_agreements))
                 & (val.mpdus == val.official_mpdus)
                 & (val.rental_mpdus == val.official_rental_mpdus) & (val.forsale_mpdus == val.official_forsale_mpdus))

    print(f"\nwrote {len(df)} offerings to {OUT_FILE}")
    print(f"rows with consistency flags: {(df['check'] != '').sum()}")
    print(val[["year", "rows", "agreements", "official_agreements", "mpdus", "official_mpdus",
               "rental_mpdus", "official_rental_mpdus", "forsale_mpdus", "official_forsale_mpdus", "ok"]].to_string(index=False))
    for y, note in VALIDATION_NOTES.items():
        print(f"  {y}: {note}")


VAR_LABELS = {
    "offering_year": "Calendar year of offering agreement",
    "offering_date": "Offering agreement date (DHCA: date MPDUs counted as built)",
    "project_name": "Project name",
    "aka": "Also known as",
    "site_plan": "Site plan number",
    "street_address": "Street address (2024-25 reports only)",
    "city": "City (2024-25 reports only)",
    "zip": "ZIP code (2024-25 reports only)",
    "total_units": "Total units in project",
    "project_mpdus": "Total MPDUs in project",
    "mpdus_in_offering": "MPDUs in this offering",
    "wfh_units": "Workforce housing units in this offering",
    "tenure": "Rental or For-Sale",
    "developer": "Developer name",
    "unit_description": "Unit description (2022-24 reports only)",
    "file": "Source report PDF",
    "page": "PDF page of Attachment B",
    "row_on_page": "Offering row on page (top to bottom)",
    "method": "Extraction: text, ocr, or text_clipped (2025)",
    "corrected": "1 if any field hand-corrected (manual_corrections.csv)",
    "note": "Note",
    "check": "Consistency flags (values as printed in reports may differ)",
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
                 data_label="MPDU offering agreements, DHCA annual reports 2013-2025",
                 variable_labels=VAR_LABELS)


def row_checks(df):
    """Flag values that are probably misread: blank or implausible numbers, odd
    site plan numbers, and project figures that disagree with other offerings
    of the same site plan."""
    flags = [[] for _ in range(len(df))]
    for i, r in enumerate(df.itertuples()):
        if pd.isna(r.mpdus_in_offering) and pd.isna(r.wfh_units):
            flags[i].append("no MPDUs or WFH in offering")
        if pd.notna(r.mpdus_in_offering) and pd.notna(r.project_mpdus) and r.mpdus_in_offering > r.project_mpdus:
            flags[i].append("offering > project MPDUs")
        if pd.notna(r.project_mpdus) and pd.notna(r.total_units) and r.project_mpdus > r.total_units:
            flags[i].append("project MPDUs > total units")
        if isinstance(r.site_plan, str) and not re.fullmatch(r"8-?\d{6,7}[0-9A-Z](/8\d{7}[0-9A-Z])*", r.site_plan):
            flags[i].append("site plan format")
        if pd.isna(r.offering_date):
            flags[i].append("no date")
        else:
            years = [int(y) for y in re.findall(r"20\d\d", r.file)]
            if not min(years) <= r.offering_date.year <= max(years):
                flags[i].append("date outside years the report covers")
    for col in ["total_units", "project_mpdus"]:
        mode = df.groupby("site_plan")[col].agg(lambda s: s.mode().iloc[0] if s.notna().any() else np.nan)
        for i, r in enumerate(df.itertuples()):
            v, m = getattr(r, col), mode.get(r.site_plan, np.nan)
            if pd.notna(v) and pd.notna(m) and v != m:
                flags[i].append(f"{col} differs from other offerings of site plan ({m:g})")
    return ["; ".join(f) for f in flags]


if __name__ == "__main__":
    import sys
    main(use_corrections="--no-corrections" not in sys.argv)
