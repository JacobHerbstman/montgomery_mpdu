"""Download Montgomery County DHCA MPDU annual reports.

The reports are listed on the DHCA "MPDU Program Information" page:
https://www.montgomerycountymd.gov/department-housing-community-affairs/moderately-priced-dwelling-units-mpdus/mpdu-program-information

Each report's Attachment B lists every MPDU Offering Agreement executed in the
calendar year(s) it covers. The county counts an MPDU as "built" on the date
of its Offering Agreement.

Output: data/raw/mpdu_annual_reports/<file>.pdf plus manifest.csv
(url, years covered, sha256, download time).
"""

import csv
import hashlib
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "data" / "raw" / "mpdu_annual_reports"

BASE = "https://assets.montgomerycountymd.gov/files/"

# (local file name, source URL, first year covered, last year covered)
# 2025 was posted under a different naming scheme than earlier years.
REPORTS = [
    ("annual_report_mpdu_2013-2016.pdf", BASE + "annual_report_mpdu-2013-2016.pdf", 2013, 2016),
    ("annual_report_mpdu_2017.pdf", BASE + "annual_report_mpdu-2017.pdf", 2017, 2017),
    ("annual_report_mpdu_2018-2019.pdf", BASE + "annual_report_mpdu-2018-2019.pdf", 2018, 2019),
    ("annual_report_mpdu_2020.pdf", BASE + "annual_report_mpdu-2020.pdf", 2020, 2020),
    ("annual_report_mpdu_2021.pdf", BASE + "annual_report_mpdu_2021.pdf", 2021, 2021),
    ("annual_report_mpdu_2022.pdf", BASE + "annual_report_mpdu-2022.pdf", 2022, 2022),
    ("annual_report_mpdu_2023.pdf", BASE + "annual_report_mpdu-2023.pdf", 2023, 2023),
    ("annual_report_mpdu_2024.pdf", BASE + "annual_report_mpdu_2024.pdf", 2024, 2024),
    ("annual_report_mpdu_2025.pdf", BASE + "2026-05/2025%20MPDU%20and%20WFH%20Annual%20Report.pdf", 2025, 2025),
]

HEADERS = {"User-Agent": "Mozilla/5.0 (research download; Princeton)"}


def download(url: str, dest: Path) -> bytes:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=120) as r:
        data = r.read()
    if not data.startswith(b"%PDF"):
        raise ValueError(f"not a PDF (server probably returned an error page): {url}")
    dest.write_bytes(data)
    return data


def main(force: bool = False) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    for fname, url, y0, y1 in REPORTS:
        dest = OUT_DIR / fname
        if dest.exists() and not force:
            data = dest.read_bytes()
            status = "exists"
        else:
            data = download(url, dest)
            status = "downloaded"
            time.sleep(1)
        rows.append({
            "file": fname,
            "url": url,
            "year_start": y0,
            "year_end": y1,
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
            "retrieved_utc": datetime.now(timezone.utc).isoformat(timespec="seconds") if status == "downloaded" else "",
        })
        print(f"{status:10s} {fname}")

    manifest = OUT_DIR / "manifest.csv"
    # keep the original retrieval time for files that were already present
    old = {}
    if manifest.exists():
        with manifest.open() as f:
            old = {r["file"]: r for r in csv.DictReader(f)}
    for r in rows:
        if not r["retrieved_utc"] and r["file"] in old:
            r["retrieved_utc"] = old[r["file"]]["retrieved_utc"]
    with manifest.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {manifest}")


if __name__ == "__main__":
    main(force="--force" in sys.argv)
