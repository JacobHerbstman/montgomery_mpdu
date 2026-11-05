"""Montgomery County, MD area median income by HUD fiscal year.

Run code/01_data_collection/06_download_income_rents.py first.

Reads the HUD Section 8 income limit files (FY2004-FY2026) and keeps the row
for Montgomery County, Maryland (state 24, county 31), which HUD places in the
Washington-Arlington-Alexandria HUD Metro FMR Area. MPDU eligibility and
controlled prices are set as shares of this median (DHCA: garden apartments
up to 65% AMI, high-rise 70%).

Column names change across years (median2008 / median2016 / median2026;
fips / fips2010; Metro_Area_Name / hud_area_name), so each file is matched by
pattern. The FY2023 file has malformed document metadata that openpyxl
rejects; it is re-read with the metadata part removed.

Output: data/int/02_data_cleaning/05_hud_ami_montgomery.csv
  fy, ami (4-person median family income), l50_4 (very low income limit,
  4 persons), l80_4 (low income limit, 4 persons, where reported), hud_area

Usage:
  python 05_hud_ami.py
"""

import io
import re
import zipfile
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
HUD_DIR = ROOT / "data" / "raw" / "hud_income_limits"
OUT_FILE = ROOT / "data" / "int" / "02_data_cleaning" / "05_hud_ami_montgomery.csv"

STATE, COUNTY = 24, 31


def read_sheet(path):
    try:
        return pd.read_excel(path)
    except ValueError:
        # drop docProps/core.xml (bad timestamp) and read from memory
        buf = io.BytesIO()
        with zipfile.ZipFile(path) as zin, zipfile.ZipFile(buf, "w") as zout:
            for item in zin.infolist():
                if item.filename != "docProps/core.xml":
                    zout.writestr(item, zin.read(item.filename))
        buf.seek(0)
        return pd.read_excel(buf, engine="openpyxl")


def col(d, pattern):
    hits = [c for c in d.columns if re.fullmatch(pattern, str(c), re.I)]
    return hits[0] if hits else None


def main():
    rows = []
    for path in sorted(HUD_DIR.glob("section8_il_fy*.xls*")):
        fy = int(re.search(r"fy(\d{4})", path.name).group(1))
        d = read_sheet(path)
        st, co = col(d, r"state"), col(d, r"county")
        r = d[(pd.to_numeric(d[st], errors="coerce") == STATE) & (pd.to_numeric(d[co], errors="coerce") == COUNTY)]
        if len(r) != 1:
            print(f"FY{fy}: {len(r)} rows for Montgomery County, MD; skipped")
            continue
        r = r.iloc[0]
        med = col(d, rf"median{fy}") or col(d, r"median(?!1999)\d{4}")
        area = col(d, r".*area_name")
        rows.append({
            "fy": fy,
            "ami": r[med],
            "l50_4": r[col(d, r"l50_4")],
            "l80_4": r[col(d, r"l80_4")] if col(d, r"l80_4") else None,
            "hud_area": r[area] if area else None,
        })
    out = pd.DataFrame(rows).sort_values("fy")
    out.to_csv(OUT_FILE, index=False)
    print(out.to_string(index=False))
    print(f"[saved] {OUT_FILE}")


if __name__ == "__main__":
    main()
