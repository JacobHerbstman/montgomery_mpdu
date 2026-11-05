"""Download HUD income limits and ACS tract rents/values.

  * HUD Section 8 income limits, FY2004-FY2026: national files with each
    area's median family income and 30/50/80% limits by household size.
    MPDU eligibility and controlled prices key off the DC-metro median.
    data/raw/hud_income_limits/
  * ACS 5-year tract estimates for Montgomery County (state 24, county 031),
    2009-2024, from the Census API, saved as served (JSON): median gross rent
    (overall and by bedrooms), median home value, median household income,
    tenure counts. data/raw/acs_tract/ Needs a Census API key in the
    CENSUS_API_KEY environment variable; skipped otherwise.

Usage:
  python 06_download_income_rents.py [--force]
"""

import os
import sys

from _download_utils import RAW, Manifest, save_url

HUD_DIR = RAW / "hud_income_limits"
ACS_DIR = RAW / "acs_tract"

HUD = "https://www.huduser.gov/portal/datasets"
# Paths as linked from https://www.huduser.gov/portal/datasets/il.html. FY2014
# has no Section 8 link on that page, so a few likely names are tried.
HUD_FILES = {
    2004: ["IL/IL04/Section8.xls"],
    2005: ["il/il05/Section8FY2005.xls"],
    2006: ["il/il06/Section8FY2006.xls"],
    2007: ["il/il07/Section8-rev.xls"],
    2008: ["il/il08/Section8_FY08.xls"],
    2009: ["il/il09/Section8.xls"],
    2010: ["il/il10/Section8.xls"],
    2011: ["il/il11/Section8_v3.xls"],
    2012: ["il/il12/Section8.xls"],
    2013: ["il/il13/Section8.xls"],
    2014: ["il/il14/Section8.xls", "il/il14/Section8_Rev.xls", "il/il14/Section8-FY14.xls",
           "il/il14/Section8_Rev.xlsx"],
    2015: ["il/il15/Section8_Rev.xlsx"],
    **{y: [f"il/il{y % 100:02d}/Section8-FY{y % 100:02d}.xlsx"] for y in range(2016, 2027)},
}

ACS_API = "https://api.census.gov/data/{year}/acs/acs5"
ACS_VARS = [
    "NAME",
    "B25064_001E",                                  # median gross rent
    *[f"B25031_{i:03d}E" for i in range(1, 8)],     # median gross rent by bedrooms
    "B25077_001E",                                  # median home value
    "B19013_001E",                                  # median household income
    "B25003_001E", "B25003_002E", "B25003_003E",    # tenure: total, owner, renter
]
ACS_YEARS = range(2009, 2025)


def main(force=False):
    man = Manifest(HUD_DIR)
    for year, paths in HUD_FILES.items():
        for path in paths:
            ext = path.rsplit(".", 1)[-1]
            try:
                save_url(f"{HUD}/{path}", HUD_DIR, f"section8_il_fy{year}.{ext}", man,
                         force=force, note=f"HUD Section 8 income limits FY{year}")
                break
            except Exception as e:
                print(f"miss       FY{year} {path}: {e}")
        else:
            print(f"FAILED     FY{year}: no candidate URL worked")
    man.write()

    # The Census API requires a key (free: https://api.census.gov/data/key_signup.html)
    key = os.environ.get("CENSUS_API_KEY")
    if not key:
        print("SKIPPED    ACS: set CENSUS_API_KEY to download the tract tables")
        return
    man = Manifest(ACS_DIR)
    for year in ACS_YEARS:
        params = {"get": ",".join(ACS_VARS), "for": "tract:*", "in": "state:24 county:031",
                  "key": key}
        try:
            save_url(ACS_API.format(year=year), ACS_DIR, f"acs5_{year}_montgomery_tracts.json",
                     man, force=force, params=params,
                     note=f"ACS 5-year {year}; get={','.join(ACS_VARS)}")
        except Exception as e:
            print(f"FAILED     ACS {year}: {e}")
    man.write()


if __name__ == "__main__":
    main(force="--force" in sys.argv)
