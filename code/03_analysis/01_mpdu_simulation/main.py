"""Build MPDU choice frontiers and place each observed project on its frontier.

Montgomery County analog of San Diego code/02_simulation/main.py.

Input:  data/int/02_data_cleaning/01_mpdu_offerings_combined.dta (annual-report offerings)
        data/int/02_data_cleaning/04_base_density_by_plan.csv   (optional; observed base density)
Output: data/int/03_analysis/01_mpdu_simulation_results.csv  one row per project
        data/int/03_analysis/01_mpdu_full_frontier.csv       one row per project x option

Base units come from the Planning Board resolution where a consistent one
exists (base_source = "resolution"), and are otherwise inferred from total
units and MPDUs (base_source = "inferred"); both are kept for comparison.

MPDU rents use each project's own-year HUD AMI for Montgomery County
(05_hud_ami.py) and a rent-to-AMI ratio calibrated to DHCA's MPDU rents.
Market rent is a single standardized value (rules.RENT_MKT_STANDARD) until
the market-rent approach is settled; set rules.USE_TRACT_RENT = True to use
tract median rents instead. rent_roll and atr are illustrative only; the unit
columns (base units, bonus, MPDUs) do not depend on prices.

Usage:
  python main.py
"""

import numpy as np
import pandas as pd

import rules
import utils

RESULTS_FILE = utils.ANALYSIS_DIR / "01_mpdu_simulation_results.csv"
FRONTIER_FILE = utils.ANALYSIS_DIR / "01_mpdu_full_frontier.csv"


def main():
    # ---- 1. Projects ----
    df = utils.load_projects()
    df = utils.attach_regime(df)
    df = utils.attach_ami(df)
    df = utils.attach_market_rent(df)
    print(f"Projects: {len(df):,} ({df['source'].value_counts().to_dict()})")

    # ---- 2. Base units and frontier position ----
    # Inferred base: reverse-engineered from (total units, MPDUs) alone.
    inferred = [
        utils.infer_base_units(h, m, s)
        for h, m, s in zip(df["actual_units_total"], df["actual_units_mpdu"], df["min_share"])
    ]
    df["inferred_base_units"] = [b for b, _, _ in inferred]
    df["inferred_base_units_max"] = [b for _, b, _ in inferred]
    df["inferred_label"] = [lab for _, _, lab in inferred]

    # Observed base: from Planning Board resolutions (04_build_base_density.py).
    # Used wherever available; the inferred base fills the rest.
    df = utils.attach_observed_base(df)
    has_obs = df["obs_base_units"].notna()
    df["base_source"] = np.where(has_obs, "resolution", "inferred")
    df["frontier_base_units"] = df["obs_base_units"].where(has_obs, df["inferred_base_units"]).astype(int)
    obs_pos = [rules.classify_position(h, m, b, s) if o else (None, np.nan)
               for h, m, b, s, o in zip(df["actual_units_total"], df["actual_units_mpdu"],
                                        df["frontier_base_units"], df["min_share"], has_obs)]
    df["mpdus_required"] = [r for _, r in obs_pos]
    df["strategy_label"] = np.where(has_obs, [lab for lab, _ in obs_pos], df["inferred_label"])

    # ---- 3. Frontiers, one per (base units, minimum share, lowest h, AMI) ----
    # With an observed base the frontier also covers totals below base, since
    # projects can build under their base density.
    cache = {}
    parts = []
    for row in df.itertuples(index=False):
        h_min = min(row.frontier_base_units, row.actual_units_total)
        k = (row.frontier_base_units, row.min_share, h_min, row.ami, row.rent_mkt)
        if k not in cache:
            cache[k] = rules.calculate_frontier(k[0], min_share=k[1], h_min=k[2], ami=k[3], rent_mkt=k[4])
        f = cache[k].copy()

        # Chosen option: the observed total if it is on the frontier,
        # otherwise the frontier point with the closest MPDU count at the
        # closest total (Approximate Match / Below Minimum).
        gap = (f["units_total"] - row.actual_units_total).abs() * 1000 \
            + (f["units_mpdu"] - row.actual_units_mpdu).abs()
        chosen_idx = gap.idxmin()
        f["is_actual_choice"] = False
        f.loc[chosen_idx, "is_actual_choice"] = True

        f["rent_roll_smooth"] = utils.concave_upper_envelope(
            f["units_total"].to_numpy(float), f["rent_roll"].to_numpy(float))
        f.insert(0, "id", row.id)
        parts.append(f)

    frontier = pd.concat(parts, ignore_index=True)

    chosen = frontier.loc[frontier["is_actual_choice"],
                          ["id", "units_total", "units_mpdu", "pct_bonus", "atr", "mtr"]]
    chosen = chosen.rename(columns={"units_total": "matched_units_total",
                                    "units_mpdu": "matched_units_mpdu",
                                    "pct_bonus": "matched_pct_bonus"})
    df = df.merge(chosen, on="id", how="left")
    df["took_bonus"] = df["matched_pct_bonus"] > 0
    # Inferred bases only: because MPDU counts round up, many projects are also
    # consistent with no bonus at all (inferred_base_units_max == total units).
    # The bonus is only certain when even the largest consistent base is below
    # the total. With an observed base the bonus is observed directly.
    df["bonus_certain"] = np.where(df["base_source"].eq("resolution"), df["took_bonus"],
                                   df["inferred_base_units_max"] < df["actual_units_total"])

    # ---- 4. Summary ----
    print(f"\nBase source: {df['base_source'].value_counts().to_dict()}")
    print("\nFrontier position:")
    print(pd.crosstab(df["strategy_label"], df["base_source"]).to_string())

    core = df[~df["is_fully_affordable"] & (df["strategy_label"] != "Below Minimum")]
    print(f"\nExcluding fully affordable and below-minimum (n={len(core):,}):")
    for src, g in core.groupby("base_source"):
        print(f"  [{src}, n={len(g)}] took any bonus: {g['took_bonus'].mean():.1%}; "
              f"bonus certain: {g['bonus_certain'].mean():.1%}; "
              f"median bonus | bonus>0: {g.loc[g['took_bonus'], 'matched_pct_bonus'].median():.1%}")
    obs = core[core["base_source"].eq("resolution")]
    print(f"  observed vs inferred base (n={len(obs)}): inferred base within its consistent range "
          f"{((obs['frontier_base_units'] >= obs['inferred_base_units']) & (obs['frontier_base_units'] <= obs['inferred_base_units_max'])).mean():.0%}; "
          f"observed base above actual total (not binding): {(obs['frontier_base_units'] > obs['actual_units_total']).mean():.0%}")
    bins = [0, 0.124, 0.13, 0.149, 0.155, 0.20, 0.50]
    print("  MPDU share distribution:")
    print(pd.cut(core["actual_sh_mpdu"], bins).value_counts().sort_index().to_string())

    # ---- 5. Export ----
    RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(RESULTS_FILE, index=False)
    frontier.to_csv(FRONTIER_FILE, index=False)
    print(f"\n[saved] {RESULTS_FILE}")
    print(f"[saved] {FRONTIER_FILE}  ({len(frontier):,} option rows)")


if __name__ == "__main__":
    main()
