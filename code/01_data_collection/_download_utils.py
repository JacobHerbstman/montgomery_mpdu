"""Shared helpers for the 03-06 download scripts.

Every file is written under data/raw/ and logged in that folder's
manifest.csv (file, url, bytes, sha256, retrieval time). Files already on disk
are skipped unless --force is passed, and keep their original retrieval time.
"""

import csv
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"

HEADERS = {"User-Agent": "Mozilla/5.0 (research download; Princeton)"}
SESSION = requests.Session()
SESSION.headers.update(HEADERS)


def get(url, *, params=None, data=None, tries=4, timeout=180):
    """GET (or POST when data is given) with retries; returns the response."""
    for k in range(tries):
        try:
            if data is None:
                r = SESSION.get(url, params=params, timeout=timeout)
            else:
                r = SESSION.post(url, data=data, timeout=timeout)
            r.raise_for_status()
            return r
        except requests.RequestException:
            if k == tries - 1:
                raise
            time.sleep(3 * (k + 1))


class Manifest:
    """Per-folder manifest.csv; call add() for each file, then write()."""

    def __init__(self, folder: Path):
        self.folder = folder
        folder.mkdir(parents=True, exist_ok=True)
        self.path = folder / "manifest.csv"
        self.old = {}
        if self.path.exists():
            with self.path.open(newline="", encoding="utf-8") as f:
                self.old = {r["file"]: r for r in csv.DictReader(f)}
        self.rows = {}

    def add(self, fname, url, *, fresh, note=""):
        data = (self.folder / fname).read_bytes()
        when = datetime.now(timezone.utc).isoformat(timespec="seconds") if fresh \
            else self.old.get(fname, {}).get("retrieved_utc", "")
        self.rows[fname] = {
            "file": fname, "url": url, "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
            "retrieved_utc": when, "note": note,
        }

    def write(self):
        rows = {**self.old, **self.rows}
        with self.path.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["file", "url", "bytes", "sha256", "retrieved_utc", "note"])
            w.writeheader()
            for r in rows.values():
                w.writerow({k: r.get(k, "") for k in w.fieldnames})
        print(f"wrote {self.path}")


def save_url(url, folder, fname, manifest, *, force=False, params=None, note=""):
    """Download url to folder/fname unless it exists; log it. Returns True if saved."""
    dest = folder / fname
    if dest.exists() and not force:
        manifest.add(fname, url, fresh=False, note=note)
        print(f"exists     {fname}")
        return True
    r = get(url, params=params)
    # servers often answer a bad request with a 200 HTML page; only .html
    # targets may be HTML
    head = r.content[:200].lstrip().lower()
    if not fname.endswith(".html") and (head.startswith(b"<!doctype html") or head.startswith(b"<html")):
        raise ValueError(f"got an HTML page instead of data: {r.url}")
    dest.write_bytes(r.content)
    manifest.add(fname, url, fresh=True, note=note)
    print(f"downloaded {fname} ({len(r.content) / 1e6:.1f} MB)")
    time.sleep(1)
    return True


# ------------------------------------------------------------------------------
# ArcGIS REST layers
# ------------------------------------------------------------------------------
def arcgis_layer(layer_url, *, geometry, where="1=1", batch=500):
    """All features of an ArcGIS MapServer/FeatureServer layer.

    Pages by object id, which works whether or not the server supports
    resultOffset. With geometry=True returns a GeoJSON FeatureCollection in
    WGS84; otherwise a list of attribute dicts.
    """
    ids = get(f"{layer_url}/query", params={
        "where": where, "returnIdsOnly": "true", "f": "json"}).json()
    if "error" in ids:
        raise RuntimeError(f"{layer_url}: {ids['error']}")
    oid_field = ids["objectIdFieldName"]
    oids = sorted(ids.get("objectIds") or [])

    feats = []
    for i in range(0, len(oids), batch):
        chunk = oids[i:i + batch]
        params = {
            "objectIds": ",".join(map(str, chunk)),
            "outFields": "*",
            "returnGeometry": "true" if geometry else "false",
            "f": "geojson" if geometry else "json",
        }
        if geometry:
            params["outSR"] = "4326"
        d = get(f"{layer_url}/query", data=params).json()
        if "error" in d:
            raise RuntimeError(f"{layer_url}: {d['error']}")
        feats.extend(d["features"])
        time.sleep(0.5)

    if geometry:
        return {"type": "FeatureCollection", "features": feats}
    return [f["attributes"] for f in feats], oid_field


def save_arcgis_layer(layer_url, folder, fname, manifest, *, geometry, force=False, note=""):
    """Save a layer as GeoJSON (geometry=True) or CSV (attributes only)."""
    import pandas as pd

    dest = folder / fname
    if dest.exists() and not force:
        manifest.add(fname, layer_url, fresh=False, note=note)
        print(f"exists     {fname}")
        return
    if geometry:
        fc = arcgis_layer(layer_url, geometry=True)
        dest.write_text(json.dumps(fc), encoding="utf-8")
        n = len(fc["features"])
    else:
        rows, _ = arcgis_layer(layer_url, geometry=False)
        pd.DataFrame(rows).to_csv(dest, index=False)
        n = len(rows)
    manifest.add(fname, layer_url, fresh=True, note=(note + f"; {n} features").lstrip("; "))
    print(f"downloaded {fname} ({n} features)")
