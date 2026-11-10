# Context for a reader new to the repo (Nov 10 2026)

A guide for someone reading this repo without the working conversations: where things are written down, the rules we work by, what is still open, and what is not in git.

## Read in this order

1. `README.md`: layout, and whose code is whose.
2. `docs/dataset_overview.pdf`: the dataset as of Nov 10 (main changes, samples, positions, figures, one row per project).
3. `docs/NOTES.md`: the record. Every check, every hand-coded value with its source, and the counts before and after each change. It is in date order, so the last sections are the current state.
4. `docs/judgment_calls.md`: the hand judgment calls, with what each moves and what is still open.
5. The docstrings of `code/03_analysis/08_building_size_bunching.py` (the rule each project faced), `10_wedge_bounds.py` (the bound on each project's wedge) and `12_wedge_distribution.py` (the fitted distribution).

## Whose code

- **Evan's and Audrey's** (first commit, the 29 Oct 2026 Dropbox snapshot): everything in `code/` except the files below. Never edited. A fix to their output goes in our scripts or in rows added to the hand-coded inputs.
- **Ours:**
  - `02_data_cleaning/01_combine_reports.py`;
  - `01_data_collection/12_download_pb_staff_reports.py`;
  - `03_analysis/06` to `12`;
  - `run_all.py`.

## Hand-coded inputs (tracked in git; each row carries a source note)

| File | What it holds |
|---|---|
| `data/raw/pb_resolutions/manual_coding.csv` | Values read from Planning Board documents (base units, bonus, tract). Append-only: rows 1-346 are Audrey's; ours are added below. A later row overrides an earlier one. |
| `data/raw/mpdu_annual_reports/project_fixes.csv` | Projects listed twice in the reports |
| `data/raw/mpdu_annual_reports/total_fixes.csv` | Unit counts where the documents disagree with the reports |
| `data/raw/mpdu_annual_reports/project_subsidy.csv`, `project_impact_tax.csv`, `project_tdr.csv` | Flags |
| `08`: `PLAN_CAPS`, `HEIGHT_CAPS`, `PLAN_GROUPS`, `RE1_STEP`, `RMX_BONUS`, `CR_LUMP`, ... | Rule calls, each with the document text quoted |
| `06`: `MIN_SHARE_FIXES`, `OTHER_PROGRAM`, `OTHER_RULE` | Minimum-share fixes; projects put back after `04` dropped them |

## Rules we work by

- **Keep every project and flag it; filter later.** Nothing is dropped for being messy. Subsidy, the 25% impact-tax share, TDRs, 15% minimum areas and other programs are columns, not exclusions.
- **Every base is checked against its document** before it is used. Recodes are made only after Jacob agrees, and NOTES records his words.
- **The estimand is the wedge** on the density limit by revealed preference: the value of one more permitted unit beyond the 12.5% MPDUs it owes anyway, in MPDU discounts d. Not the bunching elasticity at base.
- **Pool the two schedules.** There is no power to compare them: 32 post-2018 projects with a base, about 10 on each side within 2 years of the cutoff.
- **d is not in the data yet.** Rentals need market and MPDU rents. For-sale projects need sale prices (the SDAT match is a scratch exploration in NOTES). No dollar figures yet.

## Held and open decisions (details in NOTES and `judgment_calls.md`)

- **Held by Jacob ("dont change these yet"):**
  - Rezoning or plan caps equal to base x 1.22: 7001 Arlington, Reserve at Fair Hill, Brody, Avalon, Layhill Overlook.
  - Evan's rounding of the base to whole units: unrounded would move Manor Oaks, 2115 E Jefferson, Towns at Oak Hill.
- **Open:**
  - Evan's calls 3 and 12;
  - pricing on whole MPDUs (depends on the rounding);
  - 15% minimums for Twinbrook and 2115 E Jefferson;
  - Maizon Bethesda base (230, not 203) and The Camille (181 approved, not 200), both own schedule, no wedge.
- **Known, not changed:**
  - Audrey's `07` does not grandfather projects with an earlier sketch plan (no sample project affected);
  - Linthicum West's label in `08`.

## Where the estimation stands

- **`10`:** gives 88 of the 100 wedge-sample projects a range for w.
  - Pre-2018 projects are priced on the Chapter 25A table (Bill 34-17 pp. 19-20, existing law in single brackets), later ones on ZTA 18-06.
  - Not modeled (11): Bethesda Overlay (9; density bought with a Park Impact Payment per square foot, 15% MPDUs to qualify), Tregoning (RE-1 flat step) and Buckingham Station (RMX, each MPDU adds one unit).
  - Reserve at Fair Hill has no bound: it paid for 22% and built less.
- **`12`:** fits one distribution (mass at zero plus a lognormal) to those ranges.
  - It misses the between group: 9 observed, about 3 predicted.
  - It leans on reading those 9 as exact. See the last section of NOTES.

## Not in git

- **`sources/`** (law, Planning Board documents, literature; 382 MB): gitignored. The quotes in NOTES and the notes in `manual_coding.csv` are the record. `policy/` (staff reports, executive regulations) is tracked.
- **`data.nosync/`** (5 GB of downloads and intermediate files): only the manifests (file, url, sha256) and the hand-coded inputs are tracked. To run the pipeline, copy the Dropbox `data/raw` as in the README.
- **Jacob's own working files** in the folder (meeting notes, model sketch): gitignored, not part of the project.
