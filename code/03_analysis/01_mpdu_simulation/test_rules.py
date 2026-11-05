"""Hand-checked tests for rules.py and utils.infer_base_units.

Run with pytest, or directly: python test_rules.py
"""

import numpy as np

import rules
import utils


# ---- Bonus schedule [SR24 p.7] ----
def test_bonus_knots():
    assert np.isclose(rules.bonus_pct(0.125), 0.0)
    assert np.isclose(rules.bonus_pct(0.15), 0.22)   # 25 steps of 0.1% x 0.88%
    assert np.isclose(rules.bonus_pct(0.20), 0.30)   # 22% + 50 x 0.16%
    assert np.isclose(rules.bonus_pct(0.25), 0.35)   # 30% + 50 x 0.1%
    assert np.isclose(rules.bonus_pct(0.10), 0.0)


def test_bonus_within_tiers():
    assert np.isclose(rules.bonus_pct(0.135), 0.088)  # 10 steps x 0.88%
    assert np.isclose(rules.bonus_pct(0.16), 0.236)   # 22% + 10 x 0.16%


def test_share_for_bonus_inverts():
    for s in [0.125, 0.13, 0.15, 0.17, 0.20, 0.40]:
        assert np.isclose(rules.share_for_bonus(rules.bonus_pct(s)), s)
    assert np.isclose(rules.share_for_bonus(0.0), 0.125)


# ---- Required MPDUs ----
def test_no_bonus_minimum():
    # 100 units at base: ceil(12.5) = 13
    assert rules.mpdus_required(100, 100) == 13
    assert rules.mpdus_required(100, 100, min_share=0.15) == 15
    assert rules.mpdus_required(40, 40) == 5


def test_threshold():
    assert rules.mpdus_required(19, 19) == 0
    assert rules.mpdus_required(20, 20) == 3   # ceil(2.5)


def test_full_22_pct_bonus():
    # base 100 -> 122 units needs 15% of 122 = 18.3 -> 19 MPDUs
    assert rules.mpdus_required(122, 100) == 19


def test_frontier_shape():
    f = rules.calculate_frontier(100)
    assert f["units_total"].iloc[0] == 100
    assert f["units_total"].iloc[-1] == 210          # 110% bonus at 100% MPDUs
    assert f["units_mpdu"].is_monotonic_increasing
    assert np.all(f["sh_mpdu"] >= 0.125 - 1e-12)
    assert f["atr"].iloc[0] > 0                       # taxed at base density


# ---- Base-unit inference ----
def test_infer_round_trip():
    for base in [20, 45, 100, 333]:
        f = rules.calculate_frontier(base)
        for h, m in zip(f["units_total"], f["units_mpdu"]):
            b, b_max, lab = utils.infer_base_units(h, m)
            assert lab == "Dominant"
            assert b <= base <= b_max


def test_infer_below_minimum():
    assert utils.infer_base_units(100, 10)[2] == "Below Minimum"


# ---- Frontier below base and position with a known base ----
def test_frontier_below_base():
    f = rules.calculate_frontier(100, h_min=60)
    assert f["units_total"].iloc[0] == 60
    assert f.loc[f["units_total"] == 60, "units_mpdu"].iloc[0] == 8   # ceil(0.125 * 60)
    assert f.loc[f["units_total"] == 60, "units_bonus"].iloc[0] == -40


def test_classify_position():
    # 453 units at 15% needs base ~371 for a 22% bonus; 68 MPDUs is the
    # requirement at base 372, one unit from the rounded base 371
    assert rules.classify_position(453, 68, 371)[0] == "Dominant"
    assert rules.classify_position(100, 13, 100)[0] == "Dominant"
    assert rules.classify_position(100, 20, 100)[0] == "Above Required"
    assert rules.classify_position(122, 13, 100)[0] == "Below Required"   # 22% bonus needs 19


if __name__ == "__main__":
    tests = [v for k, v in dict(globals()).items() if k.startswith("test_")]
    for t in tests:
        t()
    print(f"{len(tests)} tests passed")
