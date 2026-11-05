"""MPDU program rules and frontier construction (analog of San Diego rents.py).

Montgomery County's MPDU program differs from California density bonus law in
one structural way: the affordable set-aside is MANDATORY. Every development of
20+ units owes at least 12.5% (15% in some areas) MPDUs, and only the MPDU
share ABOVE 12.5% is voluntary, bought with bonus density. So R(h) carries a
flat tax from the first unit, plus an optional bonus stretch above base.

Sources (text copies of the PDFs in policy/):
  [SR24]  MPDU Staff Report, Planning Board, 18 Jan 2024
          (policy/MPDU-Staff-Report-01-18-2024-w-template_1-11-24_Final.pdf)
  [ER11]  Executive Regulation 11-23 (HIF payments for 11-19 unit buildings)

Anything marked VERIFY is an assumption not confirmed from the policy files.
"""

import math

import numpy as np
import pandas as pd

# ----------------------------------------------------------------------
# Requirement (Chapter 25A)
# ----------------------------------------------------------------------
# [SR24 p.3] Applies to new development with 20 or more units. The minimum is
# 12.5% to 15% "of the total number of units in the development", i.e. the
# share is of TOTAL units including bonus units, not of base units.
MPDU_THRESHOLD_UNITS = 20
MIN_SHARE_DEFAULT = 0.125
MIN_SHARE_HIGH = 0.15

# [SR24 p.4] 11-19 unit developments pay 0.5% of each unit's price to the
# Housing Initiative Fund instead of providing MPDUs. Not modeled in R(h) yet:
# the observed sample is all 20+ unit projects with MPDUs.
HIF_SHARE_11_19 = 0.005

# [SR24 p.9] Bill 38-17 (effective October 2018): 15% minimum in Planning
# Areas designated annually by the Planning Board (45% of tract acreage with
# median household income >= 150% of the county median). The requirement is
# set when the Planning Board accepts the application as complete.
HIGH_INCOME_AREA_START = pd.Timestamp("2018-10-01")
# [SR24 p.12] 2024 designation. VERIFY: the list changes every year (e.g.
# Poolesville was on it in 2023); earlier lists are not in policy/ yet.
HIGH_INCOME_AREAS_2024 = {
    "Bethesda/Chevy Chase", "Darnestown", "Lower Seneca",
    "North Bethesda", "Potomac", "Travilah",
}
# [SR24 p.6] Also 15% by master plan / overlay: Bethesda Overlay Zone and the
# 2022 Silver Spring Downtown and Adjacent Communities Plan (optional method).
# Not coded: needs parcel location, which the report rows do not have.


def min_share_for(date, planning_area=None):
    """Minimum MPDU share for a project, given its date and planning area.

    Falls back to 12.5% when the planning area is unknown, which is the case
    for every annual-report offering. VERIFY: `date` should be the date the
    application was accepted, but only the offering date is observed.
    """
    if (planning_area in HIGH_INCOME_AREAS_2024
            and pd.notna(date) and pd.Timestamp(date) >= HIGH_INCOME_AREA_START):
        return MIN_SHARE_HIGH
    return MIN_SHARE_DEFAULT


# ----------------------------------------------------------------------
# Bonus density (Chapter 59), outside the Bethesda Overlay Zone
# ----------------------------------------------------------------------
# [SR24 p.7] Residential density may be increased above mapped FAR by:
#   1. 0.88% per 0.1% of MPDUs above 12.5%, up to and including 15%;
#   2. 22% plus 0.16% per 0.1% above 15%, up to and including 20%;
#   3. 30% plus 0.1% per 0.1% above 20%.
# No cap. The Bethesda Overlay Zone uses a different schedule (17.5% plus 0.1%
# per 0.1% above 17.5%) and is not coded.
# VERIFY: the bonus is assumed to apply to the full share above 12.5% even
# where 15% is required ([SR24 p.8] says this holds for public benefit
# points; bonus density is not stated explicitly).
_KNOTS_SHARE = np.array([0.125, 0.15, 0.20])
_KNOTS_BONUS = np.array([0.00, 0.22, 0.30])
_SLOPES = np.array([8.8, 1.6, 1.0])  # bonus per unit of MPDU share, by tier


def bonus_pct(share):
    """Bonus density (fraction of base) earned by an MPDU share."""
    s = np.asarray(share, dtype=float)
    tier = np.clip(np.searchsorted(_KNOTS_SHARE, s, side="right") - 1, 0, 2)
    b = _KNOTS_BONUS[tier] + _SLOPES[tier] * (s - _KNOTS_SHARE[tier])
    return np.where(s <= _KNOTS_SHARE[0], 0.0, b)


def share_for_bonus(bonus):
    """Inverse of bonus_pct: smallest MPDU share earning a given bonus."""
    x = np.asarray(bonus, dtype=float)
    tier = np.clip(np.searchsorted(_KNOTS_BONUS, x, side="left") - 1, 0, 2)
    s = _KNOTS_SHARE[tier] + (x - _KNOTS_BONUS[tier]) / _SLOPES[tier]
    return np.where(x <= 0, _KNOTS_SHARE[0], s)


# VERIFY: MPDU counts round fractions up, and bonus units round down (the
# bonus is a maximum density, so a fractional unit cannot be built).
_EPS = 1e-9


def mpdus_required(h, h_base, min_share=MIN_SHARE_DEFAULT):
    """Fewest MPDUs that make a development of h total units legal on a site
    with h_base base units.

    Below the 20-unit threshold at base density, no MPDUs are owed. Any unit
    above base needs the bonus, and the bonus needs MPDUs above 12.5%.
    """
    h = np.asarray(h, dtype=float)
    need_bonus = np.maximum(h / h_base - 1.0, 0.0)
    share = np.maximum(share_for_bonus(need_bonus), min_share)
    m = np.ceil(share * h - _EPS)
    exempt = (h < MPDU_THRESHOLD_UNITS) & (h <= h_base)
    return np.where(exempt, 0.0, m)


# ----------------------------------------------------------------------
# Prices
# ----------------------------------------------------------------------
# AMI: HUD median family income (4-person) for Montgomery County, MD, by
# fiscal year, from data/int/02_data_cleaning/05_hud_ami_montgomery.csv (05_hud_ami.py); the
# simulation passes each project's own-year value. AMI_DEFAULT (FY2023) is
# only used when no year is available.
AMI_DEFAULT = 152_100.0           # $/year, HUD FY2023
# MPDU rents are set by DHCA each year as a share of AMI (garden apartments
# for households up to 65% AMI, high-rise up to 70%), but the regulation text
# is not in policy/. Calibrated instead to DHCA's current MPDU rents: 83
# buildings, 3,055 MPDUs (data/raw/mcplanning/mpdu_rental_buildings.geojson).
# Unit-weighted mean rent $1,600/month = 0.117 x FY2025 AMI / 12. By bedroom
# (median of building rents / FY2025 monthly AMI): studio 0.10, 1BR 0.107,
# 2BR 0.127 (garden) - 0.131 (high-rise), 3BR 0.13-0.15.
# VERIFY: assumes the rent-to-AMI ratio is stable over time, which holds if
# DHCA indexes rents to AMI as the program pages describe.
MPDU_RENT_TO_MONTHLY_AMI = 0.117
MPDU_RENT_TO_MONTHLY_AMI_BY_BR = {0: 0.100, 1: 0.107, 2: 0.129, 3: 0.140}
# Market rent: a single standardized value for every project and year, until
# the market-rent approach is settled (to discuss with Evan). With
# USE_TRACT_RENT = True, utils.attach_market_rent instead uses the tract
# median gross rent (ACS 2019 5-year, 06_tract_rents.py) indexed by AMI and
# scaled by NEW_CONSTRUCTION_PREMIUM; tract medians understate new-building
# rents, so that premium would need a source (CoStar, rental listings).
USE_TRACT_RENT = False
RENT_MKT_STANDARD = 2500.0        # $/unit/month
NEW_CONSTRUCTION_PREMIUM = 1.0
RENT_MKT_PLACEHOLDER = RENT_MKT_STANDARD


def mpdu_rent(ami, rent_mkt, bedrooms=None):
    """Controlled monthly rent of an MPDU, capped at market rent.

    Without a bedroom count, uses the unit-weighted average ratio."""
    ratio = (MPDU_RENT_TO_MONTHLY_AMI if bedrooms is None
             else MPDU_RENT_TO_MONTHLY_AMI_BY_BR[min(int(bedrooms), 3)])
    return np.minimum(ratio * ami / 12.0, rent_mkt)


# ----------------------------------------------------------------------
# Frontier
# ----------------------------------------------------------------------
# Highest MPDU share offered on the frontier. There is no legal cap on bonus
# density; at 100% MPDUs the bonus is 110% of base.
SHARE_MAX = 1.0


def calculate_frontier(base_units, *, min_share=MIN_SHARE_DEFAULT, h_min=None,
                       rent_mkt=RENT_MKT_PLACEHOLDER, ami=AMI_DEFAULT):
    """Rent-roll-maximizing frontier for a site with `base_units` base units.

    Unlike San Diego, there is no need to enumerate mixes: MPDUs are one
    category, so at each total h the best option is the fewest legal MPDUs.
    Returns one row per h from h_min (default: base_units) up to the maximum
    bonus. h_min below base covers projects built under their base density,
    which is possible once base units come from zoning rather than inference.
    """
    if base_units is None or base_units < 1:
        raise ValueError("base_units must be a positive integer.")
    base_units = int(base_units)
    h_min = base_units if h_min is None else max(1, min(int(h_min), base_units))

    h_max = int(math.floor(base_units * (1.0 + float(bonus_pct(SHARE_MAX))) + _EPS))
    h = np.arange(h_min, h_max + 1, dtype=float)
    m = mpdus_required(h, base_units, min_share)
    keep = m <= h
    h, m = h[keep], m[keep]

    df = pd.DataFrame({
        "frontier_base_units": base_units,
        "units_total": h,
        "units_mpdu": m,
        "units_mkt": h - m,
    })
    df["units_bonus"] = df["units_total"] - base_units
    df["sh_mpdu"] = df["units_mpdu"] / df["units_total"]
    df["pct_bonus"] = df["units_bonus"] / base_units

    r_mpdu = mpdu_rent(ami, rent_mkt)
    df["rent_roll"] = rent_mkt * df["units_mkt"] + r_mpdu * df["units_mpdu"]
    df["all_mkt_revenue_potential"] = rent_mkt * df["units_total"]
    df["atr"] = 1.0 - df["rent_roll"] / df["all_mkt_revenue_potential"]
    # Marginal tax rate between adjacent h, as in San Diego rents.py
    df["mtr"] = 1.0 - (df["rent_roll"].diff(-1) / df["all_mkt_revenue_potential"].diff(-1))

    df["min_share"] = min_share
    df["rent_mkt"] = float(rent_mkt)
    df["ami"] = float(ami)
    return df


def classify_position(h, m, base_units, min_share=MIN_SHARE_DEFAULT, base_tol=1):
    """Where an observed (h total units, m MPDUs) sits relative to the fewest
    legal MPDUs at h given known base units.

    Dominant: m equals the requirement; Above Required: more MPDUs than the
    density needs (voluntary, or required by rules not modeled); Below
    Required: fewer MPDUs than the density needs.

    Observed bases carry rounding (e.g. 453 units / 1.22 bonus = 371.3 base
    units), so m counts as Dominant if it equals the requirement for any base
    within +/- base_tol units.
    """
    req = int(mpdus_required(h, base_units, min_share))
    reqs = [int(mpdus_required(h, b, min_share))
            for b in range(max(1, int(base_units) - base_tol), int(base_units) + base_tol + 1)]
    if min(reqs) <= m <= max(reqs):
        return "Dominant", req
    return ("Above Required" if m > max(reqs) else "Below Required"), req


def build_master_cache(max_units, **kwargs):
    """Frontiers for every base-unit count 1..max_units."""
    return {b: calculate_frontier(b, **kwargs) for b in range(1, int(max_units) + 1)}
