"""Download Planning Board staff reports from 2008 on, and the documents of
related plans, for the MPDU projects whose base is still inferred.

Run 10_download_pb_archive_reports.py and
code/03_analysis/01_mpdu_simulation/main.py first.

A resolution (04_download_pb_resolutions.py) often states only what was
approved. The density permitted is in the staff report's data table, or in
the preliminary, sketch or project plan that the site plan carries out.
10_download_pb_archive_reports.py gets staff reports for 2001-2007 only. This
script adds:
  * 2008-2016: the meetings archive's agenda pages (one per meeting,
    agenda/YYYY/agendaYYYYMMDD[e].html, laid out as in 2006-2007). Each
    agenda item ("Item 5") has a title naming its plans, then links to the
    staff report and its attachments. A link is indexed by the plan numbers
    in its own text (to the next link, as in 10); an attachment link, whose
    own text names no plan, by those in its agenda item.
  * 2017 on: staff reports, attachments and resolutions in the WordPress
    media library, searched as in 04. A hit is kept only if the plan number
    is in its file name; files 04 already saved are skipped.
  * 2001-2007: the items in 10's index for the related plans.
  * 2006: the April-August agenda pages, which end in .shtm, so 10's
    pattern (.htm, .html) skips them. Same layout as 10's other pages.
  * document_fills.csv (hand-made, optional): documents found by hand, by
    name or address, that the plan-number searches miss (site_plan, url, note).

Targets: the site plans of the projects whose base is inferred
(01_mpdu_simulation_results.csv), or the site plans given on the command
line (to check a base the parser found), and the preliminary (1-), sketch (3-) and
project (9-) plans their own documents cite (text already extracted to
02_pb_resolution_text and 02_pb_archive_text).

Files are saved to data/raw/pb_archive_reports/ as <site plan stem>__<file>.pdf,
the name 03_parse_resolutions.py uses to tie a staff report to its project,
so a related plan's documents are filed under the site plan that cites it.
Extract their text with 02_extract_resolution_text.py --archive.

Output: data/raw/pb_archive_reports/
  index_2008_2016.csv  every agenda link 2008-2016 with its plan numbers
  index_2006_shtm.csv  the same for the 2006 .shtm agenda pages
  media_index.csv      media library hits for the target plans
  <stem>__<file>.pdf   documents for the target plans
  manifest.csv

Usage:
  python 12_download_pb_staff_reports.py [--index-only] [site plan ...]
"""

import html
import json
import re
import sys
import time
from importlib import import_module
from urllib.parse import unquote, urljoin, urlparse

import pandas as pd

from _download_utils import RAW, ROOT, Manifest, get, save_url

archive = import_module("10_download_pb_archive_reports")   # stems(), plan-number formats

OUT_DIR = RAW / "pb_archive_reports"
RESOLUTIONS = RAW / "pb_resolutions"
RESULTS = ROOT / "data" / "int" / "03_analysis" / "01_mpdu_simulation_results.csv"
TEXT_DIRS = [ROOT / "data" / "int" / "02_data_cleaning" / "02_pb_resolution_text",
             ROOT / "data" / "int" / "02_data_cleaning" / "02_pb_archive_text"]
MEETINGS = "https://www.montgomeryplanningboard.org/meetings_archive/"
MEDIA_API = "https://montgomeryplanningboard.org/wp-json/wp/v2/media"
FIRST_YEAR, LAST_YEAR = 2008, 2016      # agenda pages; media library from 2017
RELATED_TYPES = ("1", "3", "9")         # preliminary, sketch and project plans
SEARCH_CACHE = OUT_DIR / "media_search_cache.json"
FILLS = OUT_DIR / "document_fills.csv"


def targets(plans=()):
    """{site plan stem: set of stems to look for} for the given site plans, or
    else the projects whose base is inferred: the site plan itself and the
    related plans its documents cite."""
    if not plans:
        res = pd.read_csv(RESULTS, dtype={"site_plan": str})
        plans = {p.strip() for v in res.loc[res["base_source"] == "inferred", "site_plan"].dropna()
                 for p in v.split("/") if re.fullmatch(r"8\d{7}[0-9A-Z]?", p.strip())}
    out = {}
    for plan in sorted(plans):
        stem = plan[:8]
        cited = set()
        for d in TEXT_DIRS:
            for f in list(d.glob(f"{plan}__*.txt")) + list(d.glob(f"{stem}__*.txt")):
                cited |= {s for s in archive.stems(f.read_text(encoding="utf-8"))
                          if s.startswith(RELATED_TYPES)}
        out[stem] = {stem} | cited
    return out


def agenda_pages(pattern):
    page = get(MEETINGS).text
    return sorted({urljoin(MEETINGS, u) for u in re.findall(pattern, page)})


def agenda_index(idx_file, pattern):
    """Every link on the agenda pages matching pattern, cached in idx_file."""
    if idx_file.exists():
        return pd.read_csv(idx_file, dtype=str).fillna("")
    rows = []
    for i, url in enumerate(agenda_pages(pattern), 1):
        try:
            rows += index_page(url)
        except Exception as e:
            print(f"  failed {url}: {type(e).__name__}")
        if i % 50 == 0:
            print(f"  indexed {i} agenda pages", flush=True)
        time.sleep(0.5)
    idx = pd.DataFrame(rows).drop_duplicates("pdf")
    idx.to_csv(idx_file, index=False)
    return idx


def text_of(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def index_page(url):
    """(plan stems, pdf url, text) for each link on one agenda page."""
    s = get(url).content.decode("latin-1")
    starts = [m.start() for m in re.finditer(r"Item\s*\*?\s*\d+", s)] + [len(s)]
    rows = []
    for m in re.finditer(r'<a[^>]+href="([^"]+\.pdf)"[^>]*>', s, re.I):
        nxt = re.search(r"<a[^>]+href=", s[m.end():], re.I)
        own = text_of(s[m.end(): m.end() + (nxt.start() if nxt else 600)])[:400]
        a = max([p for p in starts if p < m.start()], default=0)
        item = text_of(s[a: min(p for p in starts if p > m.start())])[:1000]
        rows.append({"agenda": url, "pdf": urljoin(url, m.group(1)), "text": own, "item": item,
                     "stems": " ".join(sorted(archive.stems(own) or archive.stems(item)))})
    return rows


def search(term, cache):
    """Media library search for one term, cached so a rerun does not repeat it."""
    if term not in cache:
        cache[term] = get(MEDIA_API, params={"search": term, "per_page": 100,
                                             "_fields": "id,date,source_url,title,mime_type"}).json()
        time.sleep(0.5)
    return cache[term]


def main(index_only=False, plans=()):
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # 2008-2016 agenda pages, and the 2006 pages 10 skips
    years = "|".join(map(str, range(FIRST_YEAR, LAST_YEAR + 1)))
    idx = agenda_index(OUT_DIR / "index_2008_2016.csv", rf'href="([^"]*agenda/(?:{years})/[^"]+\.html?)"')
    print(f"agenda links 2008-2016: {len(idx)}; with a plan number: {(idx['stems'] != '').sum()}")
    idx06 = agenda_index(OUT_DIR / "index_2006_shtm.csv", r'href="([^"]*06_meeting_archive/[^"]+\.shtm)"')
    print(f"agenda links 2006 (.shtm): {len(idx06)}; with a plan number: {(idx06['stems'] != '').sum()}")
    if index_only:
        return

    want = targets(plans)
    print(f"target site plans: {len(want)}; related plans cited: "
          f"{sum(len(v) - 1 for v in want.values())}")
    owner = {}                       # stem looked for -> site plan stems it is filed under
    for site, looks in want.items():
        for s in looks:
            owner.setdefault(s, set()).add(site)

    # agenda items, 2001-2007 (10's index) and 2008-2016
    old = pd.read_csv(OUT_DIR / "index.csv", dtype=str).fillna("")
    items = pd.concat([old[["pdf", "text", "stems"]], idx06[["pdf", "text", "stems"]], idx[["pdf", "text", "stems"]]])
    todo = []
    for r in items.itertuples(index=False):
        for s in r.stems.split():
            for site in owner.get(s, ()):
                todo.append({"site": site, "url": r.pdf, "found_as": s, "note": r.text[:200]})

    # media library, 2017 on
    cache = json.loads(SEARCH_CACHE.read_text()) if SEARCH_CACHE.exists() else {}
    saved = set(pd.read_csv(RESOLUTIONS / "manifest.csv", dtype=str)["url"])
    hits = []
    for term in sorted(owner):
        for m in search(term, cache):
            url = m["source_url"]
            if m.get("mime_type") != "application/pdf" or term not in re.sub(r"[\s\-.]", "", url):
                continue
            title = re.sub(r"<[^>]+>", "", m["title"]["rendered"])
            hits.append({"term": term, "media_id": m["id"], "date": m["date"][:10], "title": title, "url": url})
            if url not in saved:
                for site in owner[term]:
                    todo.append({"site": site, "url": url, "found_as": term, "note": title[:200]})
    SEARCH_CACHE.write_text(json.dumps(cache))
    pd.DataFrame(hits).to_csv(OUT_DIR / "media_index.csv", index=False)

    # documents found by hand
    if FILLS.exists():
        fills = pd.read_csv(FILLS, dtype=str)
        for r in fills.itertuples(index=False):
            todo.append({"site": r.site_plan[:8], "url": r.url, "found_as": "hand", "note": r.note[:200]})
        print(f"hand-found documents: {len(fills)} for {fills['site_plan'].nunique()} site plans")

    todo = pd.DataFrame(todo).drop_duplicates(["site", "url"])
    print(f"documents to download: {len(todo)} for {todo['site'].nunique()} site plans")
    man = Manifest(OUT_DIR)
    for r in todo.itertuples(index=False):
        fname = f"{r.site}__{unquote(urlparse(r.url).path.rsplit('/', 1)[-1])}"
        try:
            save_url(r.url, OUT_DIR, fname, man, note=f"found as {r.found_as}: {r.note}")
        except Exception as e:
            print(f"  failed {r.url}: {type(e).__name__}")
    man.write()

    found = set(todo["site"]) & set(want)
    print(f"\nsite plans with a document: {len(found)} / {len(want)}")
    print("none found:", " ".join(sorted(set(want) - found)))


if __name__ == "__main__":
    main(index_only="--index-only" in sys.argv, plans=[a for a in sys.argv[1:] if not a.startswith("--")])
