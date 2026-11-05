"""Download county permit, DHCA rental, and state property-assessment data.

  * DHCA MPDU rental list (current MPDU rents by building), HTML as served:
    data/raw/dhca_mpdu_rentals/
  * dataMontgomery Residential Permits (m88u-pqki), all rows, full export:
    data/raw/permits/
  * Maryland Real Property Assessments (opendata.maryland.gov, ed4q-f8tm),
    Montgomery County parcels only, a subset of columns (identifiers,
    location, zoning, land use, last three sales, values, structure):
    data/raw/sdat/

Usage:
  python 05_download_county_state_data.py [--force]
"""

import io
import sys
import time

import pandas as pd

from _download_utils import RAW, Manifest, get, save_url

DHCA_DIR = RAW / "dhca_mpdu_rentals"
PERMIT_DIR = RAW / "permits"
SDAT_DIR = RAW / "sdat"

DHCA_PAGES = [
    ("mpdu_rental_list_print.html", "https://apps.montgomerycountymd.gov/DHCA-MPDU/Rental/PrintRentalList"),
    ("mpdu_rental_list.html", "https://apps.montgomerycountymd.gov/dhca-mpdu/Rental/List"),
]

PERMITS_URL = "https://data.montgomerycountymd.gov/api/views/m88u-pqki/rows.csv?accessType=DOWNLOAD"

SDAT_URL = "https://opendata.maryland.gov/resource/ed4q-f8tm.csv"
SDAT_WHERE = "jurisdiction_code_mdp_field_jurscode='MONT'"
SDAT_COLS = [
    "account_id_mdp_field_acctid",
    "mdp_longitude_mdp_field_digxcord_converted_to_wgs84",
    "mdp_latitude_mdp_field_digycord_converted_to_wgs84",
    "mdp_street_address_mdp_field_address",
    "mdp_street_address_city_mdp_field_city",
    "mdp_street_address_zip_code_mdp_field_zipcode",
    "premise_address_condominium_unit_no_sdat_field_28",
    "subdivision_code_mdp_field_subdivsn_sdat_field_37",
    "plat_number_mdp_field_plat_sdat_field_38",
    "zoning_code_mdp_field_zoning_sdat_field_45",
    "land_use_code_mdp_field_lu_desclu_sdat_field_50",
    "record_key_owner_occupancy_code_mdp_field_ooi_sdat_field_6",
    "sales_segment_1_transfer_date_yyyy_mm_dd_mdp_field_tradate_sdat_field_89",
    "sales_segment_1_consideration_mdp_field_considr1_sdat_field_90",
    "sales_segment_1_how_conveyed_ind_mdp_field_convey1_sdat_field_87",
    "sales_segment_2_transfer_date_yyyy_mm_dd_sdat_field_109",
    "sales_segment_2_consideration_sdat_field_110",
    "sales_segment_2_how_conveyed_ind_sdat_field_107",
    "sales_segment_3_transfer_date_yyyy_mm_dd_sdat_field_129",
    "sales_segment_3_consideration_sdat_field_130",
    "sales_segment_3_how_conveyed_ind_sdat_field_127",
    "current_cycle_data_land_value_mdp_field_names_nfmlndvl_curlndvl_and_sallndvl_sdat_field_164",
    "current_cycle_data_improvements_value_mdp_field_names_nfmimpvl_curimpvl_and_salimpvl_sdat_field_165",
    "c_a_m_a_system_data_year_built_yyyy_mdp_field_yearblt_sdat_field_235",
    "c_a_m_a_system_data_number_of_dwelling_units_mdp_field_bldg_units_sdat_field_239",
    "c_a_m_a_system_data_number_of_stories_mdp_field_bldg_story_sdat_field_240",
    "c_a_m_a_system_data_structure_area_sq_ft_mdp_field_sqftstrc_sdat_field_241",
    "c_a_m_a_system_data_land_area_mdp_field_landarea_sdat_field_242",
    "c_a_m_a_system_data_land_unit_of_measure_mdp_field_luom_sdat_field_243",
    "mdproperty_view_edition_year_mdp_field_existing",
]
SDAT_PAGE = 50_000


def download_sdat(man, force):
    fname = "sdat_montgomery_parcels.csv"
    dest = SDAT_DIR / fname
    if dest.exists() and not force:
        man.add(fname, SDAT_URL, fresh=False)
        print(f"exists     {fname}")
        return
    parts, offset = [], 0
    while True:
        r = get(SDAT_URL, params={
            "$select": ",".join(SDAT_COLS), "$where": SDAT_WHERE,
            "$order": "account_id_mdp_field_acctid",
            "$limit": SDAT_PAGE, "$offset": offset,
        })
        part = pd.read_csv(io.StringIO(r.text), dtype=str)
        parts.append(part)
        print(f"  sdat rows {offset:,}-{offset + len(part):,}")
        if len(part) < SDAT_PAGE:
            break
        offset += SDAT_PAGE
        time.sleep(1)
    df = pd.concat(parts, ignore_index=True)
    df.to_csv(dest, index=False)
    man.add(fname, SDAT_URL, fresh=True,
            note=f"$where {SDAT_WHERE}; {len(SDAT_COLS)} of 186 columns; {len(df)} rows")
    print(f"downloaded {fname} ({len(df):,} rows)")


def main(force=False):
    for d in (DHCA_DIR, PERMIT_DIR, SDAT_DIR):
        d.mkdir(parents=True, exist_ok=True)

    man = Manifest(DHCA_DIR)
    for fname, url in DHCA_PAGES:
        save_url(url, DHCA_DIR, fname, man, force=force, note="DHCA MPDU rental list, current")
    man.write()

    man = Manifest(PERMIT_DIR)
    save_url(PERMITS_URL, PERMIT_DIR, "residential_permits_m88u-pqki.csv", man, force=force,
             note="dataMontgomery Residential Permit, all rows")
    man.write()

    man = Manifest(SDAT_DIR)
    download_sdat(man, force)
    man.write()


if __name__ == "__main__":
    main(force="--force" in sys.argv)
