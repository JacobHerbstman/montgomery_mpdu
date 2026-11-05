"""Download Planning Board resolutions for the site plans in the MPDU data.

Resolutions (MCPB No. ...) state the zone, tract area, mapped density, and
the approved MPDU share, which together give the base density the MPDU
simulation needs. They are found through the WordPress media search of
montgomeryplanningboard.org, which indexes uploaded PDFs by file name.

Plan numbers come from
  * the annual-report offerings in data/int/02_data_cleaning/01_mpdu_offerings_combined.dta
    (composite entries like "820220190/820220120" are split), and
  * with --universe, also every site plan in the Montgomery Planning layer
    (data/raw/mcplanning/site_plans.geojson) with 20+ dwelling units
    (approved, else proposed) and a Planning Board date from 2008 on, not
    denied. Resolutions are online from about 2008.
Each plan is searched as written and, for amendments (e.g. 82006029A), also
by its 8-character stem.

Output: data/raw/pb_resolutions/
  <plan>__<original file name>.pdf   one per resolution found
  search_index.csv                   every media hit per plan, including
                                     staff reports that were not downloaded
  manifest.csv

Usage:
  python 04_download_pb_resolutions.py [--universe] [--force]
"""

import json
import re
import sys
import time
from urllib.parse import unquote, urlparse

import pandas as pd

from _download_utils import RAW, ROOT, Manifest, get, save_url

OUT_DIR = RAW / "pb_resolutions"
OFFERINGS = ROOT / "data" / "int" / "02_data_cleaning" / "01_mpdu_offerings_combined.dta"
SITE_PLANS = RAW / "mcplanning" / "site_plans.geojson"
UNIVERSE_MIN_UNITS = 20
UNIVERSE_START = "2008-01-01"
MEDIA_API = "https://montgomeryplanningboard.org/wp-json/wp/v2/media"


def plan_numbers():
    d = pd.read_stata(OFFERINGS)
    plans = set()
    for sp in d["site_plan"]:
        for p in str(sp).split("/"):
            p = p.strip().replace("-", "")
            if p:
                plans.add(p)
    return sorted(plans)


def universe_plans():
    """Site plans from the Planning layer: 20+ units, Planning Board date
    2008 or later, not denied."""
    feats = json.load(open(SITE_PLANS))["features"]
    p = pd.DataFrame([f["properties"] for f in feats])
    appr = p["APPR_DU_TOT"].fillna(0)
    units = appr.where(appr > 0, p["PROP_DU_TOT"].fillna(0))
    pb = pd.to_datetime(p["PBDATE"], unit="ms")
    keep = (units >= UNIVERSE_MIN_UNITS) & (pb >= UNIVERSE_START) & (p["DECISIONTYPE"] != "DENIED")
    return sorted(set(p.loc[keep, "APNO"].str.strip()))


SEARCH_CACHE = OUT_DIR / "search_cache.json"


def load_cache():
    return json.loads(SEARCH_CACHE.read_text()) if SEARCH_CACHE.exists() else {}


def search(term, cache, waits=(60, 300, 900)):
    """Media search for one term, cached in search_cache.json so an
    interrupted run resumes where it stopped. On connection failure (e.g. a
    network drop) waits and retries before giving up."""
    if term in cache:
        return cache[term]
    for k in range(len(waits) + 1):
        try:
            r = get(MEDIA_API, params={"search": term, "per_page": 100,
                                       "_fields": "id,date,source_url,title,mime_type"})
            break
        except Exception as e:
            if k == len(waits):
                raise
            print(f"  search {term} failed ({type(e).__name__}); retrying in {waits[k]}s", flush=True)
            time.sleep(waits[k])
    cache[term] = r.json()
    return cache[term]


def is_resolution(url, title):
    s = f"{url} {title}".upper()
    return "MCPB" in s or "RESOLUTION" in s


ARCHIVE_PAGES = [
    "https://montgomeryplanningboard.org/agendas/resolutions-archive/",
    "https://montgomeryplanningboard.org/agendas/resolutions/",
]


def normalize(s):
    """Uppercase with spaces, dashes and dots removed, so "8201 3022B",
    "8-20130220" and "820130220" compare equal."""
    return re.sub(r"[\s\-.]", "", s.upper())


def archive_links():
    """Every PDF link on the resolution list pages (all paginated pages).

    The media search only indexes uploads from about 2017 on; older
    resolutions sit in /resolutions_archive/documents/ and are reachable only
    from these list pages. Link text reads like "Project, Site Plan No.
    820130220, MCPB No. 13-190".
    """
    rows = []
    for base in ARCHIVE_PAGES:
        page, seen_urls = 1, set()
        while True:
            url = base if page == 1 else f"{base}page-{page}/"
            try:
                html = get(url).text
            except Exception:
                break
            links = re.findall(r'<a[^>]+href="([^"]+\.pdf)"[^>]*>(.*?)</a>', html, re.S)
            new = [(u, t) for u, t in links if u not in seen_urls]
            if not new:
                break
            for u, t in new:
                seen_urls.add(u)
                rows.append({"list_page": url, "url": u,
                             "text": re.sub(r"<[^>]+>|\s+", " ", t).strip()})
            page += 1
            time.sleep(1)
    return pd.DataFrame(rows).drop_duplicates("url")


def main(force=False, universe=False):
    man = Manifest(OUT_DIR)
    plans = plan_numbers()
    if universe:
        plans = sorted(set(plans) | set(universe_plans()))
    print(f"site plans to search: {len(plans)}")

    index = []
    cache = load_cache()
    for n, plan in enumerate(plans, 1):
        terms = [plan] + ([plan[:8]] if len(plan) == 9 and not plan[-1].isdigit() else [])
        seen = set()
        for term in terms:
            fresh = term not in cache
            for m in search(term, cache):
                if m["id"] in seen or m.get("mime_type") != "application/pdf":
                    continue
                seen.add(m["id"])
                url = m["source_url"]
                title = re.sub(r"<[^>]+>", "", m["title"]["rendered"])
                index.append({
                    "plan": plan, "search_term": term, "media_id": m["id"],
                    "date": m["date"][:10], "title": title, "url": url,
                    "is_resolution": is_resolution(url, title),
                    # the plan number must appear in the file name, not just the text
                    "plan_in_filename": term in url.replace("-", "").replace(".", ""),
                })
        if fresh:
            time.sleep(0.5)
        if n % 25 == 0 or n == len(plans):
            SEARCH_CACHE.write_text(json.dumps(cache))
            print(f"  searched {n} / {len(plans)}", flush=True)

    idx = pd.DataFrame(index)
    idx.to_csv(OUT_DIR / "search_index.csv", index=False)
    man.add("search_index.csv", MEDIA_API, fresh=True,
            note="WordPress media search hits per site plan")

    todo = idx[idx["is_resolution"] & idx["plan_in_filename"]].drop_duplicates("url")

    # Older resolutions: match plan numbers against the archive list pages
    arch = archive_links()
    arch.to_csv(OUT_DIR / "archive_index.csv", index=False)
    man.add("archive_index.csv", ARCHIVE_PAGES[0], fresh=True,
            note=f"all PDF links on the resolution list pages; {len(arch)} links")
    key = (arch["url"].map(normalize) + " " + arch["text"].map(normalize))
    hits = [{"plan": p, "url": u}
            for p in plans for u, k in zip(arch["url"], key) if normalize(p) in k]
    hits = pd.DataFrame(hits, columns=["plan", "url"])
    print(f"archive links: {len(arch):,}; matching our plans: {len(hits)}")
    todo = pd.concat([todo[["plan", "url"]], hits]).drop_duplicates("url")

    for r in todo.itertuples(index=False):
        fname = f"{r.plan}__{unquote(urlparse(r.url).path.rsplit('/', 1)[-1])}"
        try:
            save_url(r.url, OUT_DIR, fname, man, force=force, note=f"resolution, plan {r.plan}")
        except Exception as e:
            print(f"FAILED     {fname}: {e}")
    man.write()

    found = set(todo["plan"])
    missing = [p for p in plans if p not in found]
    print(f"\nplans with a resolution: {len(found)} / {len(plans)}")
    print("no resolution found:", " ".join(missing))


if __name__ == "__main__":
    main(force="--force" in sys.argv, universe="--universe" in sys.argv)
