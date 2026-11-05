"""Download Montgomery Planning GIS layers used to place MPDU projects.

From Montgomery Planning's public ArcGIS REST services (MCAtlas and the
Planning hub):
  * site plans (8-) and preliminary plans (1-): plan number (APNO), acceptance
    and Planning Board dates, proposed/approved units, site polygon;
  * zoning blocks and overlay zones. Current zoning only: the service (and
    the county's Zoning file geodatabase) has no retired blocks, so every
    ENDDATE is empty and pre-2014 zones must come from the resolutions;
  * zoning history annotations: map labels for the zoning cases that set each
    area's zone (G- local map amendments, E- sectional map amendments, BA
    Board of Appeals cases). Labels only, no dates or prior zones;
  * planning areas, and the 15% MPDU high-income planning areas for each
    designation year 2019-2026 plus the 15% master-plan areas;
  * DHCA MPDU rental buildings (current MPDU rents by bedroom) and MPDU
    ownership projects.

Layers are saved as GeoJSON in WGS84 (outSR=4326); dates are epoch
milliseconds, as served.

Output: data/raw/mcplanning/*.geojson plus manifest.csv

Usage:
  python 03_download_planning_gis.py [--force]
"""

import sys

from _download_utils import RAW, Manifest, save_arcgis_layer

OUT_DIR = RAW / "mcplanning"

MCATLAS = "https://mcmaps.org/server11/rest/services/Overlays"
MCPLANS = "https://montgomeryplans.org/server/rest/services/Overlays"
HUB = "https://services1.arcgis.com/HbzrdBZjOwNHp70P/arcgis/rest/services"

# (file name, layer URL, note)
LAYERS = [
    ("site_plans.geojson", f"{MCATLAS}/MCAtlas_Development_Review/MapServer/3",
     "Site Plans (8-); APNO = site plan number"),
    ("preliminary_plans.geojson", f"{MCATLAS}/MCAtlas_Development_Review/MapServer/1",
     "Preliminary Plans (1-)"),
    ("zoning_blocks.geojson", f"{MCATLAS}/MCAtlas_Zoning/MapServer/4",
     "Zoning blocks (current zoning; BEGINDATE/BEGINREASON = case that set the zone, ENDDATE always empty)"),
    ("zoning_history_annotations.geojson", f"{MCATLAS}/MCAtlas_Zoning/MapServer/0",
     "Zoning history annotations: case-number labels (G-, E-, BA-) placed on the zoning map"),
    ("overlay_zones.geojson", f"{MCATLAS}/MCAtlas_Zoning/MapServer/3",
     "Overlay zones (incl. Bethesda Overlay Zone) with begin/end dates"),
    ("planning_areas.geojson", f"{MCPLANS}/Planning_Areas/MapServer/0",
     "Planning Areas (current boundaries)"),
    ("planning_areas_boz_ssdac.geojson", f"{HUB}/MPDURequirement203_WebMap/FeatureServer/0",
     "Planning areas with Bethesda Overlay Zone and SSDAC 15% areas"),
    ("mpdu_15pct_master_plans.geojson", f"{HUB}/2025_MPDU_Update/FeatureServer/0",
     "Master plans with a 15% MPDU requirement"),
    ("mpdu_rental_buildings.geojson", f"{MCPLANS}/MPDU/MapServer/0",
     "DHCA MPDU rental buildings: MPDU counts and rents by bedroom (current)"),
    ("mpdu_ownership_projects.geojson", f"{MCPLANS}/MPDU/MapServer/1",
     "DHCA MPDU ownership projects"),
]

# 15% high-income planning areas, one layer per designation year, from the
# "15% MPDU Requirements (All Years)" web map (item 3d405bcacf524f378a1f7e6c8dd41659)
HIGH_INCOME_AREAS = {
    2019: f"{HUB}/HistoricalMPDUReq/FeatureServer/5",
    2020: f"{HUB}/HistoricalMPDUReq/FeatureServer/4",
    2021: f"{HUB}/HistoricalMPDUReq/FeatureServer/3",
    2022: f"{HUB}/HistoricalMPDUReq/FeatureServer/2",
    2023: f"{HUB}/HistoricalMPDUReq/FeatureServer/1",
    2024: f"{HUB}/15PercentMPDUAreas2024/FeatureServer/1",
    2025: f"{HUB}/2025_MPDU_Update/FeatureServer/1",
    2026: f"{HUB}/15PercentMPDUAreas2026/FeatureServer/0",
}


def main(force=False):
    man = Manifest(OUT_DIR)
    layers = LAYERS + [
        (f"high_income_planning_areas_{y}.geojson", url,
         f"15% MPDU high-income planning areas, {y} designation")
        for y, url in HIGH_INCOME_AREAS.items()
    ]
    failed = []
    for fname, url, note in layers:
        try:
            save_arcgis_layer(url, OUT_DIR, fname, man, geometry=True, force=force, note=note)
        except Exception as e:  # keep going; report at the end
            print(f"FAILED     {fname}: {e}")
            failed.append(fname)
    man.write()
    if failed:
        print("failed:", ", ".join(failed))


if __name__ == "__main__":
    main(force="--force" in sys.argv)
