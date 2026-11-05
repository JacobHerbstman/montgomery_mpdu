"""Copy ACS 2019 tract data and tract boundaries from the CityComparison project.

The Census API now requires a key (see 06_download_income_rents.py), so the
tract rent and value data come from Social Explorer extracts already in
Research/CityComparison instead:

  * ACS 2019 5-year, tract level (summary level 140), all US tracts:
    median household income, median gross rent, median home value, tenure.
    Social Explorer report R50079860: data file, Stata dictionary and do-file,
    copied unchanged.
  * 2019 TIGER tract boundaries (the 2010-vintage tracts the 2019 ACS uses).
    The national shapefile is 716 MB, so only Montgomery County, MD tracts
    (STATEFP 24, COUNTYFP 031) are written out, as GeoJSON in WGS84.

Output: data/raw/acs_tract/ plus manifest.csv (source path, sha256, time)

Usage:
  python 07_copy_citycomparison_census.py [--force]
"""

import shutil
import sys
from pathlib import Path

import pyogrio

from _download_utils import RAW, Manifest

OUT_DIR = RAW / "acs_tract"
CITYCOMP = Path(__file__).resolve().parents[3] / "Research" / "CityComparison" / "data"
ACS_DIR = CITYCOMP / "other" / "tract_characteristics"
TRACTS = CITYCOMP / "shapefiles" / "tracts_2019" / "tracts_2019.shp"

ACS_FILES = ["R50079860_SL140.txt", "ACS2019_5yr_R50079860.dct", "ACS2019_5yr_R50079860.do"]
TRACT_OUT = "tracts_2019_montgomery_md.geojson"


def main(force=False):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    man = Manifest(OUT_DIR)

    for f in ACS_FILES:
        dest = OUT_DIR / f
        fresh = force or not dest.exists()
        if fresh:
            shutil.copy2(ACS_DIR / f, dest)
        man.add(f, str(ACS_DIR / f), fresh=fresh,
                note="copied from CityComparison; Social Explorer ACS 2019 5-year, tract level")
        print(f"{'copied' if fresh else 'exists':10s} {f}")

    dest = OUT_DIR / TRACT_OUT
    fresh = force or not dest.exists()
    if fresh:
        g = pyogrio.read_dataframe(TRACTS, where="STATEFP = '24' AND COUNTYFP = '031'")
        g.to_crs(4326).to_file(dest, driver="GeoJSON")
        print(f"written    {TRACT_OUT} ({len(g)} tracts)")
    man.add(TRACT_OUT, str(TRACTS), fresh=fresh,
            note="subset of CityComparison tracts_2019 shapefile: STATEFP 24, COUNTYFP 031; reprojected to EPSG:4326")
    man.write()


if __name__ == "__main__":
    main(force="--force" in sys.argv)
