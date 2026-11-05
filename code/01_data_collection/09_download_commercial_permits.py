"""Download dataMontgomery Commercial Permits (i26v-w6bd), all rows.

Multifamily buildings are permitted as commercial construction, and some
permit descriptions name the MPDUs in the building ("... including 15
MPDUs"), which can add projects to the annual-report sample. The MPDU rows
are picked out in code/02_data_cleaning (search the description), so the
full export is kept here.

Output: data/raw/permits/commercial_permits_i26v-w6bd.csv (+ manifest.csv)

Usage:
  python 09_download_commercial_permits.py [--force]
"""

import sys

from _download_utils import RAW, Manifest, save_url

PERMIT_DIR = RAW / "permits"
URL = "https://data.montgomerycountymd.gov/api/views/i26v-w6bd/rows.csv?accessType=DOWNLOAD"


def main(force=False):
    PERMIT_DIR.mkdir(parents=True, exist_ok=True)
    man = Manifest(PERMIT_DIR)
    save_url(URL, PERMIT_DIR, "commercial_permits_i26v-w6bd.csv", man, force=force,
             note="dataMontgomery Commercial Permits, all rows")
    man.write()


if __name__ == "__main__":
    main(force="--force" in sys.argv)
