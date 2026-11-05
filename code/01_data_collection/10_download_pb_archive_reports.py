"""Download pre-2008 Planning Board staff reports for the MPDU projects.

Planning Board resolutions are online from about 2008
(04_download_pb_resolutions.py). Earlier decisions survive as the staff
reports posted with each meeting's agenda, in the Board's meetings archive:
  * 2001-2005: monthly agenda pages,
      meetings_archive/0Y_meeting_archive/agenda_MMYYYY/agenda_MMYYYY.htm
  * 2006-2007: one page per meeting, agenda/YYYY/agendaYYYYMMDD[e].html
Each agenda item names its plan ("Site Plan Review No. 8-04033, Eton Square",
"Preliminary Plan Review No. 120060040 (Formerly 1-06004)") and links its
staff report PDF. Staff reports state the zone, tract area, approved units
and MPDUs, which give the base density the simulation needs.

Every agenda item is indexed by the plan numbers in its text (old format
8-04033 converted to 820040330). Items for the target plans are downloaded:
the site plans and preliminary plans (8-character stems) of the
annual-report projects whose base is inferred (no consistent resolution) or
whose totals are missing.

Output: data/raw/pb_archive_reports/
  index.csv          every agenda item 2001-2007 with its plan numbers and PDF
  <stem>__<file>.pdf staff reports for target plans
  manifest.csv

Usage:
  python 10_download_pb_archive_reports.py [--index-only]
"""

import html
import re
import sys
import time
from urllib.parse import urljoin

import pandas as pd

from _download_utils import RAW, ROOT, Manifest, get, save_url

OUT_DIR = RAW / "pb_archive_reports"
ARCHIVE = "https://www.montgomeryplanningboard.org/meetings_archive/"
LAST_YEAR = 2007          # resolutions are online from 2008
OFFERINGS = ROOT / "data" / "int" / "02_data_cleaning" / "01_mpdu_offerings_combined.dta"
RESULTS = ROOT / "data" / "int" / "03_analysis" / "01_mpdu_simulation_results.csv"

# plan numbers as written on agendas: 820040330, 82004033A, 8-04033, 1-06004A
NEW_NO = re.compile(r"\b([1-9])(19|20)(\d{2})(\d{3})([0-9A-Z])\b")
OLD_NO = re.compile(r"\b([1-9])-(\d{2})(\d{3})([A-Z]?)\b")


def stems(text):
    """8-character plan stems (type digit, 4-digit year, 3-digit sequence)."""
    out = {m.group(1) + m.group(2) + m.group(3) + m.group(4) for m in NEW_NO.finditer(text)}
    for m in OLD_NO.finditer(text):
        yy = int(m.group(2))
        out.add(m.group(1) + ("19" if yy >= 50 else "20") + m.group(2) + m.group(3))
    return out


def agenda_pages():
    page = get(ARCHIVE).text
    links = set(re.findall(r'href="((?:0\d_meeting_archive|/agenda/200[67])[^"]+\.html?)"', page))
    return sorted(urljoin(ARCHIVE, u) for u in links)


def index_page(url):
    """(plan stems, pdf url, item text) for each agenda item on one page."""
    s = get(url).content.decode("latin-1")
    rows = []
    for m in re.finditer(r'<a[^>]+href="([^"]+\.pdf)"[^>]*>', s, re.I):
        # the item's text runs from this link to the next one
        nxt = re.search(r"<a[^>]+href=", s[m.end():], re.I)
        chunk = s[m.end(): m.end() + (nxt.start() if nxt else 600)]
        text = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", chunk))).strip()[:400]
        rows.append({"agenda": url, "pdf": urljoin(url, m.group(1)), "text": text,
                     "stems": " ".join(sorted(stems(text)))})
    return rows


def target_stems():
    """Site and preliminary plan stems of report projects with an inferred
    base or no totals."""
    off = pd.read_stata(OFFERINGS)
    res = pd.read_csv(RESULTS, dtype={"site_plan": str})
    inferred = {p.strip() for v in res.loc[res["base_source"] != "resolution", "site_plan"]
                for p in str(v).split("/")}
    no_totals = off["total_units"].isna()
    rows = off[off["site_plan"].isin(inferred) | no_totals]
    plans = set(rows["site_plan"]) | set(rows.get("prelim_plan", pd.Series(dtype=str)))
    return {p.strip()[:8] for v in plans for p in str(v).split("/") if re.fullmatch(r"[1-9]\d{7}", p.strip()[:8])}


def main(index_only=False):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    idx_file = OUT_DIR / "index.csv"
    if idx_file.exists():
        idx = pd.read_csv(idx_file, dtype=str).fillna("")
    else:
        rows = []
        for i, url in enumerate(agenda_pages(), 1):
            try:
                rows += index_page(url)
            except Exception as e:
                print(f"  failed {url}: {type(e).__name__}")
            if i % 25 == 0:
                print(f"  indexed {i} agenda pages", flush=True)
            time.sleep(0.5)
        idx = pd.DataFrame(rows).drop_duplicates("pdf")
        idx.to_csv(idx_file, index=False)
    print(f"agenda items: {len(idx)}; with a plan number: {(idx['stems'] != '').sum()}")
    if index_only:
        return

    targets = target_stems()
    hits = idx.assign(stem=idx["stems"].str.split()).explode("stem")
    hits = hits[hits["stem"].isin(targets)]
    print(f"target plan stems: {len(targets)}; found on agendas: {hits['stem'].nunique()}; "
          f"items to download: {len(hits)}")
    man = Manifest(OUT_DIR)
    for _, h in hits.iterrows():
        fname = f"{h['stem']}__{h['pdf'].rsplit('/', 1)[-1]}"
        try:
            save_url(h["pdf"], OUT_DIR, fname, man, note=h["text"][:200])
        except Exception as e:
            print(f"  failed {h['pdf']}: {type(e).__name__}")
    man.write()


if __name__ == "__main__":
    main(index_only="--index-only" in sys.argv)
