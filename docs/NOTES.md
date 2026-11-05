# Notes on Audrey's Montgomery_MPDU pipeline

Paths before 5 Nov 2026: the working copy `~/mpdu_data/full_run` is now this repo (`~/Desktop/montgomery_mpdu`), and the files once staged in `replication/` are in `code/`, `data/raw/` and `docs/`; its downloaded documents are in `sources/planning_board/` and `sources/subsidy/` (outside git).

## Kink bunching split at the October 2018 schedule change (Oct 31 2026)

- `07_kink_bunching_by_regime.py` (in `code/03_analysis` of the working copy, run last by `run_all.py`) redoes Audrey's kink counts and figure separately for each schedule. Audrey's `04_kink_bunching_figure.py` pools all years, and its comment dates the 20% tier to the 2014 rewrite; it came with ZTA 18-06 (Ord. 18-52, effective 29 Oct 2018).
- Old schedule (the Chapter 25A table that Bill 34-17 deleted): 1% bonus per 0.1% of MPDUs to 20% at 14.5%, then 22% at 15%, and nothing more above 15%. So 15% is where the bonus stops, and there is no 20% kink. Zones could cap the bonus lower: R-90, R-60, R-40 and most CR zones got no bonus (PHED memo, 20 Sep 2018, p. 2).
- Rule: Bill 34-17 Sec. 3 keeps applications accepted as complete before 31 Oct 2018 (amendments included) on the old rules unless the applicant elects the new ones. So regime = site plan acceptance date (`date_regime`) before or after 31 Oct 2018. Not observed: sketch-plan grandfathering and elections. No old project's base implies a bonus above 22% beyond rounding (Olney Springs 22.6%, Batchellors Forest 23.3%).
- 14 of the 16 projects without a site-plan match were dated from the GIS layer by name (in the script). Westside Shady Grove and Heritage Gardens stay unknown.
- Result: 183 old, 34 new, 2 unknown.
  - Old, 15%: 44 projects exactly at 15%, against about 9 per unit-step nearby. Old, 20%: 2, no bunching (as expected).
  - New, 15%: 14 at 15%, but 10 of them have a 15% minimum (high-income areas, Bethesda Downtown, SSDAC). Only 4 of the 21 new projects with a 12.5% minimum stop at the kink. New, 20%: 1.
  - New projects pile up at 25% (7, including Sligo/HOC, MHP-Nebel, Hillandale, Ashford Woods). Unexplained; check whether some other rule rewards 25%.

## Which projects could buy density with MPDUs before October 2018 (Nov 1 2026)

Needed for building-size bunching. A kink at base exists only where a unit bonus was available above base. Where base was a hard ceiling, a project sitting at base says nothing about the elasticity.

| Zone family, period | Rule | Source checked |
|---|---|---|
| R-30, R-20, R-10, RT, PD, TS-R/TS-M, CBD (pre-Oct 2014 code, and later reviews grandfathered under it) | Chapter 25A table: up to 22% bonus at 15% MPDUs. CBD and TS: "may be increased in proportion to any MPDU density bonus provided on-site" (59-C-6.215, 59-C-8.42(c)), added by Ord. 15-35, effective 1 Apr 2005. Before that the code had no express language. | Resolutions: CBD "22 percent density bonus for providing 15 percent MPDUs" (MCPB 12-071, 13-023; 820110020 offers 12.5% with no bonus or 15% with 22%); TS-R Hampden Lane 2.5 FAR without the bonus, 3.05 with 22%; PD-44 7001 Arlington Rd 44 du/ac, 53.68 with 22%; PD 59-C-7.14(c); `sources/law/0_zta_04-12_ord_15-35_cbd_ts_mpdu_bonus_2005.pdf`, `old_59-C-6_cbd_zones_2013.pdf` |
| R-200 | 22% before Oct 2014 (2.0 to 2.44 du/ac); 12% under the 2014 code | old-code 59-C-1.622; PHED memo on ZTA 18-06, 20 Sep 2018, p. 2 |
| R-90, R-60, R-40 | 22% before Oct 2014 (R-90 3.6 to 4.39, R-60 5.0 to 6.10); no bonus under the 2014 code (MPDU density below the 2014 standard density) | old-code 59-C-1.622; resolutions (Potomac Highlands R-90, Bethesda Mews R-60); PHED memo p. 2; Ord. 18-52 |
| CR, CRT (2010-2014 code, 59-C-15) | no density above mapped FAR (59-C-15.42(a)). Mar 2010 - Oct 2011 (Ord. 16-44): MPDUs above 12.5% earn "incentive density" at the 25A rate (14.5% earns 20% of the incentive FAR), counted toward the mapped maximum. From Oct 2011 (Ord. 17-09): 12 public-benefit points per 1% up to 15%, 2 per 1% above | `sources/law/0_zta_09-08_ord_16-44_cr_zones_2010.pdf`, `0_zta_11-01_ord_17-09_cr_crt_crn_2011.pdf`, `old_59-C-15_cr_zones_2012.pdf`; Hanover Shady Grove resolution (MCPB 13-06) |
| CR, CRT without a "T" (Oct 2014 - Oct 2018) | no unit bonus. MPDU floor area above 12.5% is exempt from FAR; at 15%+ all MPDU floor area is exempt | 2014 Chapter 59, Sec. 4.7.3.D.6.c (`sources/law/chapter59_2014_as_adopted.pdf`); deleted by Ord. 18-52; Strathmore Square resolution (MCPB 23-067) |
| CR "T" zones (Oct 2014 - Oct 2018; the parsed zone drops the T) | Chapter 25A bonus, in proportion | 2014 Sec. 4.5.2.C.2; Ripley East and Ripley II resolutions |
| RNC (pre-Oct 2014 code) | Chapter 25A bonus; MPDUs added to the zone by text amendment | Resolutions: Batchellors Forest (MCPB 09-95), Trotters Glen (MCPB 13-92), Danshes staff report |
| RMX (pre-Oct 2014 code) | master plan units + one per MPDU, up to 22% (59-C-10.3.7(c)) | `sources/law/0_zta_06-15_rmx_2c_tdr_2006.pdf` pp. 7-8; Buckingham staff report |
| C-2, I-3 residential (pre-Oct 2014 code) | not found; left unclear | |
| All zones after ZTA 18-06 (except the Bethesda Overlay Zone) | 0.88% / 0.16% / 0.1% schedule | Ord. 18-52 |

- **Non-T CR, 2014-18: a jump at 15%, not a kink at base.** Between 12.5% and 15%, each exempt MPDU only replaces market floor area, so market floor area does not grow. At 15%, market floor area can rise from 0.875 to 1.0 of the mapped FAR, with MPDUs at 17.6% of the larger building. So a project at base turned down one lump: +17.6% floor area, 29% of it MPDUs. That's about the price of the residential 22% bonus.
- **The 20 projects exactly at base, sorted by these rules:**
  - Bonus available, so the kink applies (7): Fenton Street, The Core, Element 28 and Flats 8300 (CBD); 2115 East Jefferson (CR, new schedule, 15% minimum); Wootton Crossing; Woodward Crossing.
  - Hard ceiling (10):
    - George, Hanover and Camden Shady Grove (CR 2010-14)
    - Travilah Station (CR standard method)
    - Solaire Wheaton (TS-R development plan: max 245 units including MPDUs)
    - The Darcy and Flats @ Bethesda Ave (G-850)
    - Quince Trace (G-839)
    - National Park Seminary (G-828)
    - Mt. Prospect (master plan + TDRs). PD zones let density exceed the cap for MPDUs (59-C-7.14(c)), so this one is unclear.
  - Lump option, non-T CR (2): The Elm, The Crescent at Chevy Chase.
  - Base set from approved units (1): Elms at Clarksburg.
- Several resolutions treat the bonus as all-or-nothing: 12.5% with no bonus, or 15% with 22%.
- Sources: a research agent found the old-code texts (Montgomery Planning pages archived on web.archive.org, and Council ordinances). I checked each quote above against the files, now in `sources/law/` (`0_*` and `old_*`). Its first report was wrong on one point: 59-C-15.857 is the Retained Building rule, not the MPDU points rule. Not found: a codified 59-C-7 (PD) or 59-C-8 (TS) after 2005.

## Building size relative to base, by bonus rule (Nov 1 2026)

- `08_building_size_bunching.py` (run last by `run_all.py`) sorts the 110 projects with a resolution base by the rule they faced: the table above, plus hand lists of plan caps and CR "T" zones. It then places each project against base and the 22% top (within one unit or 0.5% of base).
  - Output: `output/tables/building_size_bunching.csv` and `output/figures/building_size_bunching.pdf`.
- Two corrections to the table above, found while coding:
  - **R-90, R-60, R-200 before Oct 2014 did have a 22% bonus.** The old code's MPDU densities are standard × 1.22 (R-60 5.0 to 6.10; R-90 3.6 to 4.39; R-200 2.0 to 2.44). For example, Potomac Highlands (R-90, 2013) states a 22% bonus. The PHED memo's "no bonus" compares against the 2014 code's standard densities, so it holds only for Oct 2014 - Oct 2018.
  - **Six CR projects are "T" zones** (the resolutions say "H-145T" etc.; the parsed zone drops the T): Century, Fairchild, Guardian, Victory Haven, Solaire 8250, Solaire 8200 Dixon. They had the 25A bonus.
- Result on Nov 1, with 110 projects (positions: below base / at base / between / at 22% / above 22%):
  - Bonus available (70): 31 / 7 / 16 / 12 / 4. Ten of the 12 at 22% are resolutions that state "a 22 percent density bonus". All 4 above 22% are post-2018.
  - Ceiling at base (17: plan caps, CR 2010-14): 8 / 9 / 0 / 0 / 0.
  - CR lump at 15% (8): 6 / 2 / 0 / 0 / 0.
  - Bethesda Overlay 5, unclear 9 (RMX, RNC, CBD before Apr 2005, Mt. Prospect, no zone), base from approved units 1.
  - None of the 25 projects that could not buy units above base is above base, which supports the rules.
- Result on Nov 2, with 135 projects after the hand-coding below. Eight more plan caps were added to `PLAN_CAPS`: Clarksburg Town Center, Park Potomac, Gallery Park, Stonehall, Wisconsin Place, Chelsea Heights, Ashton Market, Park Montgomery.
  - Bonus available (81): 37 / 8 / 18 / 14 / 4. The new ones at 22% are Millstone at Kingsview and The Lauren; Eleven55 Ripley is new at base.
  - Ceiling at base (27): 9 / 18 / 0 / 0 / 0.
  - CR lump at 15% (8): 6 / 2 / 0 / 0 / 0.
  - Bethesda Overlay 5, unclear 13 (RMX, RNC, C-2, CBD before Apr 2005, Mt. Prospect, no zone), base from approved units 1.
  - Still none of the projects that could not buy units above base is above base.

## Corrections made in the working copy (`~/mpdu_data/full_run`)

- **Four misread resolutions** (Oct 31 2026), hand-coded in Audrey's `manual_coding.csv` format. The rows are in `manual_coding_additions.csv`; append them to `data/raw/pb_resolutions/manual_coding.csv` in a fresh copy. Each value is from the resolution text:
  - Linthicum West: 253 units, not 2, with a stated base of 165. The extra units come from TDRs, so the project fails the consistency check and its base is now inferred.
  - Willow Manor at Fairland: 121 units, not 19. It's still 48% below base: senior apartments at 7.6 du/acre where R-30 allows 14.5.
  - Arora Hills: 844 units, not 648 (the parse missed 196 multifamily). Now 0.8% above base.
  - Baum Property / Magruder's Overlook: 48 units, not 42 (the parse missed 6 MPDU duplexes). Now 6% below base, likely because units/acre is applied to gross acres.
- Linthicum's misread base (20,904 units) had made up 38% of the simulated frontier rows behind `03_tax_schedule_figure.py` (43,646 of 115,962), so that figure's bins changed. The kink bunching counts didn't change.
- Left as they are:
  - Century and Strathmore: Audrey takes the base ratio from one phase on purpose, and both are below base whichever resolution is used.
  - Wildwood Manor (agreement-to-build): the 2023 report lists Preston Place's plan number 820220180.
  - Maple Ridge: the report has 67 units against 59 approved, and no amendment text was found.
- **Bases checked against the resolution data tables** (Oct 31 2026), for the 26 below-base projects whose base came from a floor-area conversion or from gross acres. These are 19 more `base_units_permitted` rows plus two floor-area rows for The Elm, all in `manual_coding_additions.csv`. Rules used:
  - **A binding cap is the base** (Jacob agreed, Oct 31 2026). Where a development plan, master plan, overlay zone or covenant caps units below the zone default before any MPDU bonus, the cap is the base. Audrey did the same for North Bethesda Parcel H. This applies to Glenmont (50.1 du/ac), the Darcy/Flats (250), Mt. Prospect, National Park Seminary (G-828), Quince Trace (G-839), Ashford Woods (Clarksburg overlay, 3 du/ac) and North Quarter (private covenant, 109).
  - **Purchased TDR units count toward the base** (Mt. Prospect 170 + 17). Linthicum West's row was changed on Nov 2 from 165 to 165 + 56 TDRs = 221. It still fails the consistency check: its 32 MPDUs (12.6%) sit outside the TDR calculation, 14.5% above 221. So its base is still inferred, at 250.
  - **Where the text confirms the pipeline's base, it is recorded as a stated base** (Fenwick, 1200 East West Hwy, Bethesda Mews, Cloverly Forest, Maple Ridge, Grosvenor Place, Willow Manor), so the audit shows it as checked.
  - **No "bonus 0" rows.** The stated-bonus route would set base = approved units, even where the cap is higher.
- Can't tell from the text (OCR lost the data table, or the text has no limits): AVA Wheaton, The Blairs, Wentworth House, Veridian, Bainbridge Bethesda, Heritage at Silver Spring, The Premier, Cabin John Village, Fairland View, Bentley Park. These need the staff reports.
- Adding The Elm's residential floor area shifts the median sf-per-unit used by `04_build_base_density.py`, so Wentworth House and Persei move by one unit.
- Result: 53 of 110 resolution-based projects are below base (64 of 111 in Audrey's run); the median bonus used goes from -4.2% to 0. The kink bunching counts don't change.

## Bases hand-coded for projects with documents but no base (Nov 2 2026)

109 of the 219 projects had no measured base, so their base was inferred from their MPDU count. That base can't be used to look at building size relative to base: it assumes the answer. Why each of the 109 had none:
- 64: a resolution or staff report is in the data, but the parser got no base from it (32), the document was set aside as not matching the project (17), or the base failed Audrey's consistency check (15).
- 34: a site plan number, but no document downloaded.
- 11: no site plan number.

This round covers the 64. Four readers went through the documents (PDF page images where the text lost the tables), with the rules above plus three more:
- In TDR zones, base = base density + TDR density.
- In old-code R zones, a stated "maximum with MPDUs" divided by 1.22 is the base.
- Where approved units exceed the base because of something other than the MPDU bonus or TDRs, the base is coded as stated and left to fail the check.

Every row cites its passage: each quote was matched word for word against the text file, and I checked the four values that come only from PDF images (Hallman Grove p. 11, Buckingham Station p. 16, Piedmont/Shady Grove Crossing p. 16, Millstone p. 28). The rows are appended to `manual_coding_additions.csv` (73 rows, after the earlier 26), with the source and arithmetic in each note.

- **Result: 31 of the 64 coded. 25 now get a measured base, so 135 of 219 projects have one** (was 110).
- **Six are coded but fail the consistency check** (approved units exceed base by more than the MPDU share earns), so they stay inferred. The documents say where the extra units come from:
  - Jefferson at Inigo's Crossing: the PD zone's own bonus.
  - Preserve at Rock Creek (2 report projects): an Upper Rock Creek master plan bonus, 0.2 to 0.4 du/ac.
  - 7340 Wisconsin: Bethesda Overlay density.
  - Hillandale Gateway / Sligo: the ZTA 21-07 floor-area exemption for income-restricted housing.
  - Linthicum West: TDRs, with MPDUs outside the TDR count.
- **Can't tell (33):**
  - Phase of a larger plan with only plan-wide limits (12): six Cabin Branch phases (one cap of 1,886 du across 535 acres), Black Hill, Northpark at Montrose, Clarksburg Village (2), Meridian at Grosvenor, Lionsgate.
  - Documents not about this project's housing (5): Citron, Regency at Leisure World, Montgomery Row, Meadows at Hurley Ridge, The Henri.
  - The limit isn't in what we have (16): Aurora, Westside at Shady Grove (2), The Daley and Laureate, Woodcrest, Gateway Commons, Solaire/1150 Ripley, Bloom Montgomery Village (2), 900 Thayer, Summerfield Crossing, Eton Square, The Rae, Tregoning (2024 code states only the maximum with MPDUs), Woodfield Commons.
    - Woodfield: the data table's 1.0 FAR = 384,200 sf doesn't fit the 3.88-acre site (169,013 sf), so its base is left out. Its approved units (84, parsed 11) and MPDU share are corrected.
- Not used: corrections to Aurora's approved units (341 for amendment A). Audrey's rows give the original plan's 327, there is no base either way, and I didn't override her coding.
- Added by me:
  - Gallery Park's and Hallman Grove's bases are put on their amendment resolutions as well, since the pipeline prefers a resolution over a staff report.
  - Silver Spring Library's resolution gets same_project = True: its parsed plan number was the mailing date.
  - Hallman Grove's zone is R-200, taken from its staff report.
- **Judgment calls to revisit:**
  - **Caps that may already include the bonus.** Gallery Park's development plan cap (290 incl 40 MPDUs) is about the PD-11 standard (262) plus the bonus its MPDU share earns. It is coded as the base under the cap rule, so the project is 12% below base; with 262 it would be 2% below. Park Potomac's master plan 600 is 423 base + 102 TDRs + 75 MPDUs, also coded as a cap.
  - **Buckingham Station:** coded at the Master Plan's 500 units before the bonus, not the 610 cap (= 500 × 1.22). It took a 20.5% bonus.
  - **MHP-Nebel:** base from mapped residential floor area (256 units). Its sketch plan approved 188,500 sf (178 units); with that as the cap the base is 178. Below base either way.
  - **Amalyn Bethesda (R-90, accepted 2017):** the 2014 code's 4.39 du/ac maximum is the base, with no ÷1.22.
  - **Silver Spring Library:** the report project (a building-permit record) has 139 MPDUs in 149 units, close to fully affordable. The resolution has 155 du with 12.5% MPDUs + 32 workforce units, 41% below base.
- **Leads, not checked:**
  - **The 25% pile.** Sligo/Hillandale and probably other projects in it used ZTA 21-07 (income-restricted housing exempt from FAR). That may explain the pile.
  - **Shifted report names.** The report's "4725 Cheltenham Drive" carries Park Montgomery's plan number (820220020), and "7340 Wisconsin Avenue" carries 4725 Cheltenham's (820220060). Units match on plan number, so they were coded by plan number.
- **Left for the next round:** the 34 with a plan number but no document (find the resolution or staff report on Planning's site), the 11 with no plan number, and the zone rules for RMX, RNC and C-2 (13 projects are still "unclear" in `08`).

## Staff reports from 2008 on, and a second hand-coding round (Nov 2 2026)

- **New download script, `12_download_pb_staff_reports.py`** (in `code/01_data_collection` of the working copy; run by hand like the other download scripts, then `02_extract_resolution_text.py --archive`). It follows 04 and 10 and adds three sources:
  - 2008-2016 meeting agendas from the Board's meetings archive. These have the same layout as the 2006-2007 pages that 10 reads, and 10 stops at 2007.
  - The media library for 2017 on, keeping the staff reports and attachments that 04 found but didn't save.
  - The preliminary, sketch and project plans that each project's own documents cite.
- Files go to `data/raw/pb_archive_reports/` named by the site plan they belong to, which is how `03_parse_resolutions.py` ties a staff report to its project.
- The run downloaded 312 documents for 54 of the 62 site plans with an inferred base. Still none for Leaman Farm, Rock Creek Overlook, Orchards of Sandy Spring, Olney Estates, The Argent, The Cameron, Germantown Park and Elizabeth House III.
- Audrey's parser alone then found bases for 7 more projects. Checked by hand:
  - 3 confirmed: Galaxy, Layhill Overlook, Symphony Park (the last corrected slightly, to usable acres).
  - 4 wrong, and corrected:
    - Fairwood Crossing: the parser used the neighbouring R-20 zone. The R-90/TDR base is 52, not 250.
    - Montgomery Row: the document was another project's (Smalls Nursery). The 2014 joint staff report gives 179.
    - Mateny Hill: split-zoned, and the resolution states a base of 50.
    - Fraley's Green: the document covers only Phase I. Set to unusable.
- **Second hand-coding round**, same rules and checks as the first. All 102 quotes were found word for word, and I checked the image-only tables for Clarksburg Village (PDF p. 80) and Gateway Commons (p. 40) myself. 98 rows were added to `manual_coding_additions.csv`.
- **Plan level (Jacob, Nov 2 2026): where the density limit and MPDU obligation are set for a whole plan, the plan is the observation.** Each phase is coded with the plan-wide base and plan-wide approved units, so all phases share one ratio. `08` (`PLAN_GROUPS`) sums the phases into one row.
  - **Cabin Branch** (6 report projects): G-806 / Preliminary Plan 12003110 caps the community at 1,886 du including MPDUs, and 1,886 are approved, so it is at base. It is in `PLAN_CAPS`.
    - Alternative reading: G-806 also describes the 1,886 as 1,676 market + 210 MPDUs. With 1,676 as the base, the bonus used would be 12.5%.
  - **Clarksburg Village Phases I-II** (3 report projects): Phase II's TDR table gives 2,653 du approved, 15% MPDUs, and "Non-Density Bonus Units: 2,653 / 1.22 = 2,175" (1,562 base + 613 TDR units), so it took the full 22%. Two of the three report projects (997 and 973 du) may be the same Phase I at two stages; the plan-level row sums them.
  - **Shady Grove Station-Westside** (5 report projects): base 960 + 192 TDR units = 1,152, with 1,521 du approved. It fails the consistency check because 116 workforce units are on top, so it is dropped (Jacob, Nov 2: drop projects that go over base for reasons other than the MPDU bonus, as Audrey's check does). The same applies to the six dropped in round 1.
- **Result: 166 of 219 projects have a measured base** (Audrey's run 111; 135 after round 1). `08` has 159 observations once plan groups are counted once:
  - Bonus available (97): 42 / 9 / 20 / 22 / 4.
  - Ceiling at base (32): 12 / 20 / 0 / 0 / 0.
  - CR lump at 15% (9): 6 / 3 / 0 / 0 / 0.
  - Bethesda Overlay 5, unclear 15, base from approved units 1.
  - Still no project without a unit bonus is above base.
  - New in `PLAN_CAPS`: Leesborough (G-798, 201), Villa Cortese (DPA 07-1, 48), Aurora (G-801, 500), Black Hill (Project Plan, 1,229), Cabin Branch.
  - New in `T_ZONES`: Woodfield Commons (H-55T).
- **Calls to revisit:**
  - **Tregoning** (2024, RE-1 MPDU optional method): left out. The resolution states only the maximum with MPDUs, 1.22 du/ac = 46 units. Treating that as the base (as for Amalyn) puts it at base; 1.0 du/ac (37.85) fails the check.
  - **Black Hill and Northpark at Montrose:** "at base" only because the plan's own approval equals its cap (1,229; 745 on exactly the mapped floor area).
  - **Aurora:** a row sets approved units to 341 on the 82008011A resolution, which overrides Audrey's 327 (the original plan's count). 341 is the amendment the report project matches, and it is the approval the G-801 base of 500 is compared with.
  - **Woodfield Commons:** base 273.5 from 1.0 FAR on the 8.82-acre gross tract, which includes 4.94 acres dedicated earlier (staff report p. 16 and 22). That puts it 69% below base.
  - **Montgomery Row:** the 179 comes from the applicant's letter in the staff report; it matches staff's 8 du/ac table.
- **Still open:**
  - 53 inferred bases:
    - 11 dropped on purpose (other density programs: the 6 from round 1 and Shady Grove Station-Westside's 5)
    - Tregoning, left out (above)
    - 17 cannot tell from the documents (e.g. Bloom Montgomery Village, Eton Square, Lionsgate, The Henri, Grandview)
    - 13 with no document (8 of them listed above)
    - 11 with no plan number in the MPDU reports. 9 of those plans were found by name in the GIS layer in `07_kink_bunching_by_regime.py`; their bases need the plan number attached to the report project first.
  - North Bethesda Market II (82012004C): its resolution is in the data under 82012004A but isn't linked to this project.

## Plan numbers for the 2024-report projects, and a third hand-coding round (Nov 2 2026)
- **Why they had no base.** The 2024 annual report prints no site plan numbers, and its projects that no other report lists never got one from Audrey's linking steps. So `04` had no resolution to read.
- **Fix: `data/raw/mpdu_annual_reports/site_plan_fills.csv`**, a hand-made file (file, project_name, site_plan, note). Each plan number was found by name, aka and units in the Planning GIS site plan layer, then checked against the resolution's approved units.
  - `01_combine_reports.py` applies it as step d., after Audrey's linking, and only to offerings that still have no plan. It flags them in `site_plan_hand`. Without the file the port still reproduces Audrey's `.dta`.
  - 12 offerings on 9 report projects were filled: Armstrong Property 820160110, 7607 Old Georgetown Road 820190030, Bloom MV Areas (2 offerings) 820170130, Strathmore Square 820220070, 8787 Georgia 820180100, Westside Shady Grove 820130220 (name match only; that plan is dropped anyway), St. Elmo 82017003A, 8015 Old Georgetown Road 820200130, 4909 Auburn Avenue 820190100.
  - Heritage Gardens is left out. It has Preliminary Plan 120230070 (63 du) and no site plan.
- **Documents.** `12_download_pb_staff_reports.py` now also takes site plans on the command line, for checking a base the parser found. Run for the 8 plans, it downloaded their staff reports and sketch and preliminary plans.
- **The parser's floor-area bases were wrong for all 8 plans.** These are CR-family zones, and its `cr_floor_area` route mixed up tract and site area or whole-plan and phase floor area. It also read 8015 Old Georgetown's residential floor area as 500 sf. All 8 were hand-coded from the data tables. The 13 rows are in `manual_coding_additions.csv`; all quotes were found, and I checked the image-only tables for Armstrong (PDF p. 7) and 4915 Auburn (p. 10) myself. The arithmetic is base = approved units × residential floor area allowed before any bonus / residential floor area approved:
  - Armstrong Property: 55 × 177,997 / 160,200 = 61.1, so 10% below base. Its zone is CRT ... H-55 T, so it is added to `T_ZONES`.
  - 8787 Georgia: 400 × 591,032 / 413,821 = 571.3, 30% below base. **Call:** Sketch Plan 320170060 caps residential at the 413,821 sf approved, so under the binding-cap rule the base would be 400 and the project at base. This is the same question as MHP-Nebel.
  - Strathmore Square, **plan level**: Preliminary Plan 120190180 sets 1,746,451 sf base residential plus 384,219 sf of bonus for 15% MPDUs on the whole 14.58 acres, for 2,218 du. Base = 2,218 × 1,746,451 / 2,130,670 = 1,818, so it is at 22% by construction. **Call:** Phase 1 by itself (220 du, the only phase in the reports) is entirely within mapped density.
  - Bloom Montgomery Village, **plan level** (it was "cannot tell" in round 2): TLD Areas II-VI, 1,163 permitted / 1.22 = 953.3, plus CRN Area I, 111 × 0.5 / 0.23 = 241.3, gives 1,194.6 against 494 approved. That is 59% below base. The 9.76 du/ac = 8.0 × 1.22 reading of the TLD maximum is ours; no Bloom document states it.
  - Dropped, because they go over base with Bethesda Overlay Zone density rather than the MPDU bonus (they fail the check): St. Elmo (base 139.5 of 279), 8015 Old Georgetown (180.1 of 297), 4915 Auburn (81.3 of 175), 7607 Old Georgetown (81.2 of 200).
- **Result: 173 of 219 projects have a measured base. `08` has 166 observations**:
  - Bonus available: 43 / 9 / 20 / 23 / 4.
  - Ceiling at base: 12 / 20 / 0 / 0 / 0.
  - Lump at 15%: 11 / 3 / 0 / 0 / 0.
  - Own schedule 5, unclear 14, base from approved units 1.
- **New problem: one plan can appear as several report projects.** Bloom is now 4 rows in `08`: the 514- and 494-du totals from the 2021 and 2022 reports, and the 2024 report's 43- and 86-du areas. The same happens elsewhere, from Audrey's project list: North Bethesda Market (397 / 424), Clarksburg Town Center (1,206 / 1,106), Clarksburg Square / Garnkirk Farms (392 / 392), Grosvenor Place (43 / 46). Others are real separate buildings on one plan (Park Potomac, Darcy / Flats, Glenmont, Chevy Chase Lake, Wildwood / Preston Place). This needs one rule for what a project is before the descriptives.

## Documents found by hand, the 2006 agenda gap, and a fourth hand-coding round (Nov 2 2026)
- **Why 30 projects still had no base.** Their approvals were never downloaded, or the documents we had were another project's. Searching Planning's sites by name, address and developer (not just plan number) found them for 27 of the 30. The causes:
  - **10 skipped part of 2006.** Its pattern takes `.htm`/`.html` agenda pages, and 15 meetings from April to August 2006 end in `.shtm`. Leaman Farm, The Argent, The Cameron, Rock Creek Overlook, Olney Estates and Citron were approved at those meetings.
  - **Renamed projects.** The approvals use other names: 1200 Blair Mill Road (The Argent), Cameron House, Rock Creek Woods (Rock Creek Overlook), Danshes Property (Orchards of Sandy Spring), Martens Property (Meadows at Hurley Ridge), Downtown Silver Spring 8-99002F (Citron), Tevis Place (E20250010).
  - **Wrong plan numbers in the county reports.** Meadows at Hurley Ridge is 820030110, not 820030100 (Cloverly Commercial). The Astrid is Pooks Hill 81982098F (originally 820160080), not 82016008C. Elizabeth House III is its own site plan 820160160 inside Elizabeth Square 820170140. Sandy Spring Village's 8198806A is 81988060A.
  - **Staff reports split into parts.** For Eton Square, Lionsgate and Woodlake we had only part 1. The data tables are in parts A/B.
- **Changes to `12_download_pb_staff_reports.py`:**
  - It also indexes the 2006 `.shtm` agenda pages (`index_2006_shtm.csv`: 15 pages, 478 links, 225 with a plan number).
  - It reads an optional hand-made `data/raw/pb_archive_reports/document_fills.csv` (site_plan, url, note). It has 82 documents for 25 site plans. Each is filed under the **report project's** plan stem, even where that number is wrong, so `03` ties it to the report project. The note says what the document is for.
  - The run downloaded 283 documents: 52 from the hand list and the rest from the 2006 pages and the plans they cite.
- **The parser alone then gave bases for 10 more projects.** All 10 were checked by hand. Leaman Farm and The Argent are right. The other 8 were wrong (wrong acreage, misread unit counts, or the MPDU share read as the bonus) and were recoded.
- **Fourth hand-coding round.** Same rules and checks as before: all 54 quotes were found word for word. I checked the image-only tables myself for Cameron (Item 3, PDF p. 6), Meadows (item3_050103 p. 22) and Eton Square (ITEM13A p. 5). 57 rows were added to `manual_coding_additions.csv`. That includes `same_project` = True on the right document for the wrong-number cases (Meadows, Woodlake, Sandy Spring Village, The Astrid).
  - At or near a cap: Rock Creek Overlook (G-822, 30 of 30), Germantown Park (G-878, 104 of 105), Woodcrest (86 of 86 on the R-200 part), The Cameron (325 of 326), The Argent (96, 125 du/ac CBD-1). Rock Creek Overlook and Germantown Park are added to `PLAN_CAPS` in `08`.
  - Using the bonus: Leaman Farm (58 base, 19%), Orchards of Sandy Spring (master plan 33, 21%), Citron (199 + a stated 12% bonus), Tevis Place (137.4 base, 12% MPDU bonus, all 154 units MPDUs), Chevy Chase Lake (10.5% over the plan's base).
  - Below base: Fraley's Green (72 base, 53 approved), Sandy Spring Village (57.6, 56), The Astrid (644, 562), North Bethesda Market II (633 base, 280 approved).
- **New plan-level groups in `08`:**
  - **Pike & Rose (Sketch Plan 320110010):** The Henri (Phase II) and Persei/Pallas (Phase I). The residential cap of 1,726,642 sf is spread over 1,544 du, so both phases are at base by construction, as with Black Hill. Persei/Pallas had a phase-level base of 504.
  - **Chevy Chase Lake (32014003A / 120150130):** The Lindley and the Townhomes. One mapped residential density covers both: 262 du on 429,000 sf against 388,833 sf mapped, with 19% MPDUs.
  - **Grandview (ELP Bethesda):** the plan's 1,300 senior units equal its cap, so it is at base. Phase 2 has since been approved.
  - **Woodlake:** the RH density limit is computed on the whole 1971 site (1,017 "with MPDUs" against 534 existing + 59 new). The base is 1,017 / 1.22 = 834 by analogy with the old R-zone rule; I couldn't get the old RH zone text.
- **Result: 191 of 219 projects have a measured base** (Audrey 111, then 135, 166, 173). `08` has 182 observations with plan groups counted once.
  - Bonus available: 44 / 13 / 21 / 23 / 4.
  - Ceiling at base: 13 / 22 / 0 / 0 / 0.
  - Lump at 15%: 13 / 3 / 2 / 0 / 0.
  - Own schedule 5, unclear 18, base from approved units 1.
- **The 28 still without a base:**
  - **Dropped on purpose (17):** they go over base with non-MPDU density. Jefferson at Inigo's, Preserve at Rock Creek (2), Shady Grove Westside (6), 7340 Wisconsin, Hillandale, Linthicum West, the four Bethesda Overlay projects, and Elizabeth House III (Elizabeth Square adds a 10% workforce housing bonus on top of the 22% MPDU bonus, putting it 32% over base).
  - **Coded but failing the check on MPDU-law density (3), a call for Jacob:**
    - **Meadows at Hurley Ridge** (R-200/TDR): base 171 + 113 TDRs = 284, with the 41 MPDUs (12.6%) on top for 325.
    - **Eton Square** (R-60/TDR): base 54 + 52 TDRs bought = 106, with 16 MPDUs (12.5%) on top for 122. Coded at 106 under the purchased-TDR rule. With the zone's full TDR density (54 + 76 = 130, incl MPDUs) as a cap, it would be 6% below base instead.
    - **Olney Estates** (RNC): base 35. Sec. 25A-5(d)(2) let this 20-49 unit project convert one MPDU into a market unit, so it has 20% more units with 14.3% MPDUs.
    - Linthicum West (round 1) is the same TDR pattern. In TDR zones, MPDUs seem to sit on top of base + TDRs at 12.5%, which the bonus schedule (no bonus at 12.5%) doesn't cover. If that is the MPDU law's own density, these projects shouldn't be dropped.
  - **No usable document (4):** Summerfield Crossing (the 2002 preliminary plan opinion isn't online), Lionsgate (the 158-unit redesign was an administrative amendment), Regency at Leisure World (2001, before the online archive), Meridian at Grosvenor (PD-25 development plan not online).
  - **Out of scope (4):**
    - Woodlake 871011A: a second listing of 8-71011A. Its 7-character plan number can't tie to a document.
    - Hampden Lane: from the permit records. `03` ties staff reports only to report and agreement projects, and its 82007010C resolution isn't online.
    - Heritage Gardens: a conditional-use senior care facility with no site plan.
    - Tregoning: still the open call above.

## TDR zones: the base is the zone's maximum TDR density (Jacob, Nov 2 2026)
- **The rule in TDR zones (old code, Sec. 59-C-1.395).** "TDRs must be purchased for all market rate units above the base density. MPDUs are excluded from the calculations" (Linthicum West, MCPB 22-026 p. 13). The 12.5% MPDU requirement is taken on all units. The Chapter 25A bonus is calculated on base density as raised by TDRs (2014 code Sec. 4.9.15.B.1.d.ii). Norbeck Crossing shows it: 61 base + 154 TDRs = 215, + 22% for 15% MPDUs = 262.
- **Why the old rule failed three projects.** Under "base + TDRs bought" (rule 2 above), a project that bought fewer TDRs than allowed shows its 12.5% MPDUs as units over base. That is about 14% at a share the bonus schedule rewards with nothing. Meadows at Hurley Ridge, Eton Square and Linthicum West all failed the check this way.
- **Decision (Jacob, Nov 2 2026, "for now"; worth raising with Evan):** in TDR zones the base is the zone's maximum TDR density (designation x acres) before any MPDU bonus. TDRs are density the developer buys, up to that maximum. This replaces rule 2 for TDR zones. The documents show each of the three stopped short of the maximum for reasons other than the bonus:
  - **Meadows:** bought only the 2/3 minimum. The preliminary plan's 326-unit APF condition equals the units applied for.
  - **Eton Square:** "not maximizing it's potential ... due to site constraints such as the master-planned roadway in the center of the site, dedication of roadway along MD 355 and grading concerns" (staff report p. 5).
  - **Linthicum West:** the Board allowed fewer than 2/3 of the TDRs because of environmental resources and park dedication (p. 14).
- **APF (traffic) limits are not caps.** Every preliminary plan states one ("limited to N dwelling units"), and it is normally the number applied for. Count it as a binding cap only where a document shows it was set below what the applicant asked for. This is consistent with Summerfield Crossing.
- **Recoded (6 rows, both copies of each plan's file):**

  | Project | Old base (base + TDRs bought) | New base (zone maximum) | Approved | Position |
  |---|---|---|---|---|
  | Meadows at Hurley Ridge (plan level) | 284 | 342 (4 du/ac x 85.5 ac) | 325 | 5% below base |
  | Eton Square | 106 | 130 (12 du/ac x 10.88 ac) | 122 | 6% below base |
  | Linthicum West | 221 | 330 (2 du/ac x 165.25 ac) | 253 | 23% below base |
  | Clarksburg Village (plan level) | 2,175 | 2,255.3 | 2,653 | 17.6% over base (was 22%) |
  | Manor Oaks | 45 | 45.96 | 55 | no change in use (the stated-bonus route already gives 46.0) |

  - Clarksburg Village's zone maximum is the "Permitted Density with Density Bonus" total from its TDR table, 2,751.14 / 1.22 (Phase II staff report PDF p. 80).
- **Already at the zone maximum (bought every TDR allowed):** Orchard Run (75), Gateway Commons (241.6), Fairwood Crossing (52), Millstone (245), Norbeck Crossing (215), Bradford's Landing (about 198-200).
- **Not affected:**
  - Cabin Branch and Park Potomac / The Perry: TDRs sit inside a binding plan cap.
  - Mt. Prospect: master-plan cap plus 17 TDRs.
  - Shady Grove Westside: its TDR density is a fixed 20% (192 of 960), so its base doesn't change, and it stays dropped for workforce housing.
- **Result: 194 of 219 projects have a measured base. `08` has 185 observations.**
  - Bonus available: 47 / 13 / 22 / 22 / 4.
  - The other groups are unchanged.
  - Olney Estates (the small-development MPDU conversion) is still left out pending Jacob's call.

## Olney Estates kept at the 22% top (Jacob, Nov 2 2026)
- **The project.** Base 35 (Olney master plan 0.33 du/ac x 107.35 ac, RNC). The full 22% bonus gives 42 units (35 x 1.22 = 42.7, rounded down) and needs 15% MPDUs, which is 7.
- **What was built.** 42 units with 6 MPDUs (14.3%). The applicant converted one required MPDU into a market unit under the small-development provision for 20-49 units. Staff disputed that reading (staff report pp. 9-10) but recommended approval.
- **Why it failed the check.** At 14.3% the schedule earns about 16%, short of the 20% it took.
- **Decision.** `mpdu_pct` is coded at 15%, the share the bonus was calculated on, and the note records that 6 MPDUs were built. It now passes the check and sits at 22% in `08`. Its group is "unclear" because `08` has no RNC zone rule yet.
- **Result: 195 of 219 projects have a measured base. `08` has 186 observations.**
- **Still without a base (24):**
  - 16 dropped for non-MPDU density. Linthicum West is back in under the TDR rule.
  - 4 with no usable document: Summerfield Crossing, Lionsgate, Regency at Leisure World, Meridian at Grosvenor.
  - 4 out of scope: the Woodlake duplicate listing, Hampden Lane (permit records), Heritage Gardens (conditional use), and Tregoning (an open call).

## Tregoning and Amalyn rechecked against the 2014 code (Nov 2 2026)
- **What the 2014 code says.** Optional method MPDU Development "is permitted where moderately priced dwelling units (MPDUs) are included in a development above the minimum required by Chapter 25A" (Sec. 4.4.1, PDF p. 146). The densities in `chapter59_2014_as_adopted.pdf`:

  | Zone | Standard method | MPDU Development | Cluster |
  |---|---|---|---|
  | RE-1 | 1.09 du/ac (p. 154) | 1.22 (p. 156) | 1.0 |
  | R-90 | 4.84 (p. 162) | 4.39 (p. 164) | 3.6 |

  - Ord. 18-52 (ZTA 18-06) changed R-200 through the townhouse zones (R-90 MPDU Development becomes 5.90, with the 0.88 / 0.16 / 0.1% schedule) but not RE-1.
- **Amalyn Bethesda (R-90, accepted Oct 2017): no change.** I had suspected its base should be the 3.6 cluster density. That was wrong: 3.6 is the cluster option, not the base. Under the 2014 code the R-90 MPDU density (4.39) is below the standard-method 4.84, so there is no unit bonus. That is the zone-rule table above ("no bonus zone"). Its 309 units at 4.39 (12.5% + 1 MPDU) sit in "ceiling at base" either way.
- **Tregoning (RE-1, 2024): base coded, left out.**
  - Base = standard 1.09 du/ac x 37.85 ac = 41.26. Approved 46 = 44 du on 17.81 ac + 2 development rights retained on 20.04 ac (resolution PDF p. 8), with 13% MPDUs (6). The preliminary plan was amended from 12.5% to 13% MPDUs, just above the minimum.
  - So it took RE-1's MPDU-method step: 11.5% over base, from any MPDU share above 12.5%. That is not the 25A sliding schedule. At 13% the schedule earns 4.4%, so it fails the check.
  - Left out as its own schedule. It is a single project, and putting it on the sliding schedule would mean misstating its MPDU share. RE-1 2014-code projects are an all-or-nothing step, like the non-T CR lump at 15%.
- **Label to fix in `08`:** Linthicum West (RE-1/TDR-2, reviewed under the pre-2014 code) is labelled "ZTA 18-06". It is below base under any rule.
- **Result unchanged: 195 of 219 with a measured base.** Tregoning moves from "open call" to "own schedule, left out". The 24 without a base are 16 dropped for non-MPDU density, Tregoning, 4 with no usable document, and 3 out of scope (Woodlake duplicate, Hampden Lane, Heritage Gardens).

## Bases no person had checked, a fifth hand-coding round (Nov 2 2026)
- **Which ones.** 45 of the 195 measured bases came from the parser alone: 30 with no hand-coded row at all, and 15 on files where Audrey coded only the zone, `usable` or floor areas, not the base. In rounds 3-4 the parser was wrong in 8 of 10 bases checked, so all 45 were read against their data tables. Same rules as above. 61 rows, all quotes found word for word. I checked AVA Wheaton's image-only table (MCPB 14-114 p. 12) and the CR standard-method cap (2014 code Sec. 4.5.3: "the greater of 0.5 FAR or 10,000 SF") myself. The rows are in `manual_coding_additions.csv`.
- **The parser's errors:** the MPDU share read as the bonus (Poplar Run, Portico, Victory Haven, Knowles Manor, Flats at Knowles Station, 12710 Twinbrook, Hillandale Gateway); net instead of gross tract (Fairchild, Guardian Building, 850 Sligo, Crescent); a 200 du/ac unit limit the data table gives as n/a (Bainbridge Bethesda, The Blairs); a split-zoned site at one zone's FAR (Chevy Chase Lake Block B); Bethesda Overlay floor area subtracted from approved floor area (The Edge, Metro Tower); the mapped 1.0 FAR for a standard-method project capped at 0.5 (PSTA); another project's document (id 183's 820220190 is The Claiborne).
- **Biggest changes** (position relative to base, before -> after): Bainbridge Bethesda -11% -> +22%; Poplar Run +15% -> +22%; Whitehall Square +12% -> +22%; Hillandale Gateway +25% -> +35% (stated 35% bonus for 25% MPDUs); The Blairs -33% -> 0 (plan level); PSTA -50% -> 0; Springvale Terrace (id 216) +23% -> 0; Residences at Forest Glen +25% -> -6% (the "35% bonus" was a clerical error the Board corrected); Victory Haven +14% -> +3% (stated 3.1% bonus); Century -27% -> -64%; AVA Wheaton -39% -> -49%.
- **Edits to the readers' rows:**
  - Portico: the reader coded the bonus used (16.15%) as `bonus_pct`; that is computed, not stated, so the field is cleared instead and the stated base (130) is used.
  - Id 183 (2025 report, 501 du / 76 MPDU): it is Grandview (id 203, 512 / 77, agreement 2023), the same ELP Phase 1A building listed twice. The reader gave it a base by setting Audrey's `usable` = 0 on the Phase 1B resolution to 1. Not used: it is left without a base, for the project-definition step.
  - Century: the reader's 1,359 = 488 x 2,513,798 / 902,530 is kept. Site Plan 82003007B approved all of Phase I on the full 57.6 ac, so tract and approved floor area have the same scope, and Audrey's 488 stays. Plan-level alternative with Phase I-C: 721 x 2,513,798 / 1,248,970 = 1,451.
- **Now without a measured base (4):**
  - The Edge and Metro Tower: Bethesda Overlay density above base (138,083 and 188,506 sf), so dropped.
  - Knowles Manor: base 69,195 sf + 30,805 sf "MPDU bonus density" = 44.5% at 30% MPDUs, above the ZTA 18-06 schedule (about 40%). The bonus equals the MPDUs' floor area. Left out by the check.
  - Id 183, the Grandview duplicate.
- **Can't tell; the parser's base stays, unverified (4):** Wentworth House (Parcel E of G-801; the 500 du per parcel cap is stated only for Parcels F and G), Veridian (the approved 2005 report has no data table; the superseded 2004 report is now `usable` = 0), Heritage at Silver Spring (no data table), White Oak (Whitehall Square Phase 2, amendment 82005018C, not online; it takes Phase 1's ratio).
- **Calls to review:**
  - AVA Wheaton: Sketch Plan 320140020 approved 460,492 sf residential. As a cap the base would be 426, not 637 (same question as MHP-Nebel and 8787 Georgia).
  - The Blairs: plan level (2,800 cap incl 1,110 existing units, at base) against phase level (692, 27% below).
  - Transferred density inside the base: Bainbridge Bethesda (CBD density transfer from Woodmont Triangle lots) and Flats at Knowles Station (33,666 sf from neighbouring properties under the sketch plan). The MPDU bonus is calculated on base plus transfer, as with TDRs. Without the transfer Flats at Knowles Station would be far over base.
  - PSTA: the 0.5 FAR standard-method cap is from the 2014 code text; I didn't check it against the 2021 code.
  - Bentley Park: the DPA 09-1 binding element (248 incl 31 MPDUs) is the base. It is at the cap.
- **Report names fixed:** the report's "Sligo Apartments" (820190130) is Hillandale Gateway, the other half of the swap noted in round 1. The unnamed 2025 rows: 180 PSTA, 181 Metro Tower, 182 White Oak Apartments (2220 Broadbirch), 214 2115 East Jefferson, 216 Springvale Terrace.
- **More duplicates for the project-definition step:** id 183 = Grandview; Clarksburg Square = Garnkirk Farms (same 392 units; Garnkirk's 24 MPDUs may be only the townhouse share); The Claude is probably one of Chevy Chase Lake Block B's three buildings.
- **Result: 191 of 219 projects have a measured base. `08` has 182 observations.**
  - Bonus available: 44 / 18 / 16 / 27 / 2 (was 47 / 13 / 22 / 22 / 4). Several projects in "between" moved to at base or at 22%.
  - Ceiling at base 13 / 22; lump at 15% 11 / 5 / 2; own schedule 2; unclear 7 / 4 / 5 / 3; base from approved units 1.
  - Every measured base now has a hand-coded or hand-confirmed row except the 4 above.

## What a project is: duplicates counted once (Nov 2 2026)
- **Why there are duplicates.** `utils.load_projects` makes a project of each (site plan, total units, total MPDUs). When a report revises a project's totals, or lists it under another plan number, name or source (report vs Agreement to Build), the same units become two projects. Sometimes a later report also lists one building or area of a plan already listed whole.
- **The rule.** A project is one set of units with one MPDU obligation, counted once. Two rows are the same project when they describe the same units. Keep one row:
  1. the row covering the whole, not a part (a building or area of it);
  2. the row whose plan number ties to the approval the base is coded from;
  3. the row whose totals match that approval;
  4. otherwise the latest report.
- **Not duplicates:** separate buildings or phases on one plan, each with its own units: Park Potomac Townhomes / The Perry, The Darcy / The Flats, Glenmont Metrocentre 1.1 / 1.3 / The Atelier, the Cabin Branch phases, Clarksburg Village Phases 1, 2 and 3 (Encore), Whitehall Square / White Oak Phase 2, Preserve at Rock Creek (two builders' sections) and the Westside at Shady Grove phases. Where their density is set plan-wide they already share the plan's ratio (`PLAN_GROUPS` in `08`). The units-only matches (similar size, different plan, name and place, e.g. Mt. Prospect and The Claude, both 186 / 24) are coincidences.
- **`data/raw/mpdu_annual_reports/project_fixes.csv`**, hand-made (site_plan, total_units, total_mpdus, source, fix, same_as, note). `06` leaves out every listed row. `08` reads `06`'s table. `07` leaves out the duplicates and parts. Audrey's scripts, the simulation and her figures (02-05) still count every row. Each script asserts that every listed row is in the results, so a stale list stops the run.

  | Left out | Kept | Why |
  |---|---|---|
  | Clarksburg Town Center 819980010 1,040 / 149 (2005) and 820070220 1,106 / 139 (2023) | 820070220 1,206 / 151 | Site Plan 820070220 re-approved the whole town center, 1,213 du incl 152 MPDUs, built units included |
  | Clarksburg Village 820030020 997 / 108 (2005) | Phase 1 82003002B 973 / 132 | Phase 1 + Phase 2 = 973 + 1,680 = the plan's 2,653. `08` had summed 3,650 |
  | Arora Hills 82004022A 844 / 118 | 820040220 844 / 118 | same totals, two forms of the plan number |
  | North Bethesda Market 397 / 60 (2010) | 424 / 64 (2022) | White Flint Crossing; 440 approved |
  | Woodlake 871011A | 8-71011A | same 59 TH |
  | Garnkirk Farms 392 / 24 | Clarksburg Square 392 / 49 | same plan and units; 49 MPDUs approved |
  | Grosvenor Place 43 / 7 | 46 / 7 | 46 approved |
  | Bloom 514 / 114 (2021); Areas 3A (43 / 10) and II (86 / 21) | Bloom 494 / 109 | the 2022 and 2025 reports and the coded approval have 494 / 109 |
  | The Claude 186 / 24 | Chevy Chase Lake Block B 531 / 69 | The Claude is building B-1; Block B's offerings (45 + 24) are its 69 MPDUs |
  | 2025 report 820220190/820220120 501 / 76 | Grandview 820210190 512 / 77 | same ELP Phase 1A building; the report's numbers are The Claiborne and Phase 1B |

- **Wildwood Manor Shopping Center** (agreement, 301 / 46) carries Preston Place's plan number 820220180, so its "measured" base was Preston Place's ratio. It is not Site Plan 82008024C (72 senior units), and its own plan isn't in the data. Listed as `other project's plan`: left out of `06`/`08`, kept in `07`.
- **Result: 206 projects (219 less 13 listed twice).** 179 have a measured base: the 191 rows, less 11 duplicates or parts that had one, less Wildwood Manor. All 179 are in `06`. `08` has 171 observations with plan groups counted once.
  - Bonus available: 40 / 18 / 15 / 27 / 2.
  - Ceiling at base: 13 / 21.
  - Lump at 15%: 8 / 4 / 2.
  - Own schedule 2; unclear 6 / 4 / 5 / 3; base from approved units 1.
  - Kink bunching (`07`): old 172 projects, 43 at the 15% kink; new 33, 13 at 15%; Heritage Gardens unknown.
- **Possible, not listed:** Westside at Shady Grove's Stanley Martin townhouse rows (180 / 6 in 2021, 38 / 6 in 2024) may overlap. Both are dropped for workforce housing anyway.

## Northpark at Montrose rechecked against the 2025 plan (Nov 3 2026)
- **The problem.** Northpark was coded at plan level on Preliminary Plan 120200140 (2020): 745 units (107 townhouses + 638 multifamily) on the full 1,025,789 sf of mapped residential density, so at base by construction. In 2025, Sketch Plan amendment 32019007A (MCPB 25-025) dropped the commercial space and kept mapped density at 1,030,662 sf, now residential only. Preliminary Plan amendment 12020014A (MCPB 25-144, condition 1) then limited the plan to "625,594 square feet of residential uses for a maximum of 279 dwelling units": Phase I's 141 (unchanged) plus a Phase II of 138 townhouses (Site Plan 820250100). The high-rise multifamily is gone.
- **Scope.** Density is set for the whole 16.64-acre site, and Phase I has no allocation of its own: Phase I staff report Table 1 (p. 27) gives each zone's density for the entire site, and Phase I uses 325,924 sf, "approximately 32%" of it. So the plan-level rule stands, with the plan as it is now, as for Clarksburg Village and Cabin Branch.
- **Recoded** (our two plan-level rows replaced in both copies; Audrey's Phase I row is unchanged): base = 279 x 1,030,662 / 625,594 = 459.65 for 279 approved. The 279-unit limit is what was applied for, so it is not a cap (judgment call 1). Phase I (141 units, 22 MPDUs) moves from at base to 39% below base.
- **Result.** `08` bonus available: 41 / 17 / 15 / 27 / 2 (was 40 / 18). Otherwise unchanged: 206 projects, 179 with a measured base, 171 rows in `08`.

## Plan maximums: one rule, checked on all five plans (Nov 3 2026)
- **The rule** (judgment call 1). A limit is the base only if it is the site's zoning: the mapped zone, a Council development plan or its binding elements, a master or sector plan limit, or a Planning Board cut below the request with a stated reason. A Board "up to X" that equals the developer's own proposal is not a cap. Public-benefit points don't limit density: the CR optional method needs at least 100 points whatever density is asked for.
- **Read against each sketch, project and sector plan:**
  - The Blairs: the 2000 Silver Spring CBD Sector Plan (p. 69) caps the site at 2,800 units under the optional method (2013 Project Plan staff report, p. 19). A cap, so it stays at base.
  - Black Hill: the 1,227 units were the applicant's own cut from 1,618 (2016 staff report p. 7, note 1), so they are not a cap. The 2009 Germantown sector plan (p. 63) limits the Lerner site to 0.7 FAR in total, with no limit on units. (The staff report's "40% of the 0.7 FAR" is the plan's rule for site NE-1.) Residential 1,851,560 sf is all of the 0.7 FAR left after the 1,432,440 sf commercial, so it stays at base under the CR "total less commercial" test. Only the coding note changed.
  - 8787 Georgia (Sketch Plan 320170060), AVA Wheaton (320140020) and MHP-Nebel (320210110): each staff report gives the sketch plan's floor area as the applicant's proposal, approved as asked, with nothing in the sector plans limiting units. Not caps; all three stay below base (30%, 49%, 36%).
- **Not ruled out:** physical limits. 8787 Georgia would need about 4.2 FAR on its lot under the 90-foot height, and MHP-Nebel's lot is mostly stream valley buffer. "Below base" means below what zoning allowed.
- **Sources** saved in `sources/planning_board/`: the Blairs 2013 staff report, the AVA Wheaton and MHP-Nebel sketch plan staff reports, and pp. 62-63 of the Germantown sector plan.
- **Result:** no value changes; counts as in the Northpark entry.

## TDR flag (Nov 3 2026)
- **Why.** In a TDR area a developer can buy density two ways: provide more MPDUs (the bonus) or buy farmland development rights. MPDUs also need no TDRs, which makes them cheaper relative to market units. So TDR projects face a different price for density, and the analysis may want to drop them or look at them separately.
- **`project_tdr.csv`**, hand-made, copied to `data/raw/mpdu_annual_reports/` (site_plan, project_name, tdr, tdrs, note). `06` adds `tdr` (used / available, not used / none) and `tdrs` (rights bought, where given); `08` carries `tdr`. No other value changes.
- **How it was found.** Every project with a measured base whose zone, documents (all text files for its plan) or coding notes mention TDRs: 40 projects. Each mention was read.
  - **Used (21):** Orchard Run, Linthicum West, Eton Square, Meadows at Hurley Ridge, Park Potomac Townhomes and The Perry (I-3 under the Potomac master plan, not a TDR zone), the six Cabin Branch phases, Mt. Prospect (PD-2), Gateway Commons, Clarksburg Village Phases 1 and 2, Manor Oaks, Fairwood Crossing, Millstone at Kingsview, Norbeck Crossing, Bradford's Landing.
  - **Available, not used (2):** Hallman Grove (split R-200 and R-200/TDR-3, built under the R-200 MPDU option) and Reserve at Damascus (CRT with a TDR 1.16 overlay, standard method, no TDR condition).
  - **Passing mentions only (17):** a neighbouring property's zone, a plan checklist line ("MPDU, TDR, and recreation facility calculations"), "TDRs: No" in a data table, or master plan text. Woodcrest's 42 hits were all in Clarksburg documents filed under its plan prefix; its own reports don't mention TDRs.
- **Where they sit** (`08`, plan groups once): bonus available 11 used + 2 not used (used: 4 below base, 2 between, 5 at 22%); ceiling at base 3 (Park Potomac x2, Cabin Branch); unclear 1 (Mt. Prospect).
- **Not covered:** the 27 projects without a measured base, and documents that exist only as scanned images with no text. Zone names catch the TDR zones in either case.
- Also fixed `08`'s PLAN_CAPS note for Black Hill to the 0.7 FAR reading (call 1); the group is unchanged.

## Call 2 decided: caps that include MPDUs stay as written (Nov 3 2026, Jacob)
- **Park Potomac: 600.** The Potomac master plan's 600 covers both site plans (450 MF + 150 TH) and includes the 75 MPDUs (12.5% of 600). The 102 TDR units are what is left above the 423 base; MPDUs need no TDRs.
- **Cabin Branch: 1,886.** The master plan sets 1,886 "including all MPDU's" (12003110B staff report, 2008, p. 11). G-806's 1,676 + 210 split only counts TDRs; MPDUs above 12.5% reduce a site plan's TDR share and add no units (MCPB 18-021, pp. 9, 12).
- No value changes.

## Call 4 decided: transferred density counts in the base, flagged (Nov 3 2026, Jacob)
- **The Monty (Bainbridge Bethesda)** and **Flats at Knowles Station** took floor area from neighbouring lots under recorded easements. Both documents add the transfer before the MPDU bonus: The Monty's density exhibit (2007 project plan staff report, PDF p. 33: base residential 165,974 sf + 22% MPDU bonus) and Flats' data table (MCPB 23-042 p. 5, fn 4: 25,263 base + 33,666 transferred + 19,338 MPDU bonus). Kept as coded (at 22% and +33%).
- Flagged `tdr = density transfer` in `project_tdr.csv` (the column now means density from a source other than the MPDU bonus). Counts in `06`: none 154, used 21, available not used 2, density transfer 2. No other value changes.
- The Monty's 106-unit chart (2007 report PDF p. 42) is DHCA's bedroom-mix check on an early draft, not a density figure. The 2009 site plan (MCPB 09-077, p. 6) allows 200 units in the same 210,188 sf.

## Call 8 decided: Strathmore Square at plan level (Nov 3 2026, Jacob)
- Preliminary Plan 120190180 (MCPB 19-065, condition 3) approves up to 2,218 du on 1,746,451 sf mapped residential plus 384,219 sf MPDU bonus for 15% MPDUs. Phase 1 (Site Plan 820220070, 220 du, 33 MPDUs) uses 313,569 sf of mapped density and none of the bonus, which the site plan data table carries to future phases (MCPB 22-032 pp. 16-17; fn 6: the bonus is based on building the full mapped density).
- Kept at plan level: base 1,818 for 2,218 approved, so Phase 1 sits at 22% (base 180 for 220). Phase 1 alone would be at base.
- **Watch:** about 90% of the plan is unbuilt. If a later amendment cuts it (as Northpark's did in 2025), recode to the plan as it then stands. No value changes.
- **The bonus applies even where 15% is required.** Strathmore is in North Bethesda, a high-income planning area (15% minimum from Oct 2018; `07_site_plan_regime.csv`: designation 2021, min_share 0.15). Its site plan data table lists "MPDU requirement (min) 15%" and still grants 384,219 sf "of bonus MPDU density for providing 15% MPDUs" (MCPB 22-032 pp. 16-18), 22% of mapped residential. This confirms, for one project, the VERIFY in `rules.py` ("the bonus is assumed to apply to the full share above 12.5% even where 15% is required"). In 15% areas the full 22% comes with the requirement, so a project there at 15% / 22% has not chosen the kink. 9 bonus-available projects in `08` have a 15% minimum: 4 below base, 3 at base, 1 between, 1 at 22% (Strathmore).
- **No real choice; kept for now (Jacob, Nov 3).** Projects with a 15% minimum did not choose 15% or the 22% bonus that comes with it. All are kept in the dataset for now; the plan is to filter later to projects that made a real choice. `08` now carries `min_share` so they can be found: 0.15 for 11 rows (9 bonus available, 2 own schedule), 0.125 for the other 160. No other value changes.

## Call 10 decided: Buckingham Station at base 500, bonus available (Nov 3 2026, Jacob)
- The base stays at the Germantown Master Plan's 500 units for Fairfield at Germantown. Preliminary Plan 1-02068's 610 is 500 × 1.22, the cap with the bonus. Sources: the 2003 staff report (`82003003__item7_011603.pdf` p. 16: "optional method of development for the R-MX zone to increase density by 91 MPDUs"; p. 17: "Residential - MPDU NTE 22% of MP guide") and the 2005 amendment (`82003003__item10_031705_opt.pdf` p. 13: reduced from 610 to 604; 91 MPDUs at 15%; Phase 2 = 30 MPDUs).
- `08` had it as "unclear" (RMX has no general rule). It is now "25A bonus" through `RMX_BONUS` in `08_building_size_bunching.py`, a one-plan override that rests on the staff report's statement of the bonus, so it moves to **bonus available**, still **between** (200 units, base 166, +20.5%, 15% MPDUs). Bonus-available positions: below base 41, at base 17, between 16, at 22% 27, above 22% 2. Unclear: 17. No other value changes.

## Call 13 decided: Knowles Manor kept in the lump group, flagged LIHTC (Nov 3 2026, Jacob)
- **Why it was dropped.** Base 69,195 sf (R-2.0 x 34,597 sf) + 30,805 sf MPDU bonus = 100,000 sf, 94 du incl 29 MPDUs: 44.5% over base. `04_build_base_density.py` checks every base against the ZTA 18-06 schedule (40% at 30% MPDUs, +3 points) and dropped it.
- **The rule.** Sketch Plan 320180210 (accepted 13 Jun 2018, before ZTA 18-06), condition 1: "up to 30,805 square feet of MPDUs ... which is exempt from the calculation of FAR pursuant to Section 59.4.7.3.D.6.c.iii" (2014 code: with at least 15% MPDUs, all MPDU floor area is exempt from FAR); data table "Exempted MPDUs 30,805 sq. ft." (`320180210-Kensington-Manor-Staff-Report-FINAL.pdf`, online). The site plan (MCPB 19-102 p. 7) rewrote the condition in ZTA 18-06 terms: "The density limitation remains the same". So the 44.5% is the 2014 CR lump, which beats the ZTA schedule above about 27% MPDUs.
- **Not a market project.** Now Silver Creek Senior Living: all 94 units income-restricted (10 at 30% AMI, 69 at 60%, 15 at 80%), seniors 62+, LIHTC equity, $8.9m Housing Initiative Fund loan, CDA and HUD 221(d)(4) loans (Montgomery County press release, 8 Apr 2022). `is_fully_affordable` is False in the pipeline because the agreement lists 29 MPDUs of 94. The Town of Kensington's R-07-2020 is the developer's $100,000 contribution for traffic enforcement under a neighbours' settlement, not a subsidy.
- **Coded.** `06_base_density_audit.py`: `CR_EXEMPT` puts it back with the hand-coded base (frontier_base_units 65, rounded as in `utils.attach_observed_base`); new column `subsidy` from the hand-made `data/raw/mpdu_annual_reports/project_subsidy.csv` (LIHTC 1, none 179). `08_building_size_bunching.py`: `CR_LUMP` codes it "CR lump at 15%", ahead of the ZTA date rule; `subsidy` carried. Result: 180 projects in `06`, 172 rows in `08`; lump at 15% now 15 (Knowles above 22%). No other row changed.
- **To do:** check the other high-share projects for LIHTC or nonprofit financing (MHP-Nebel, Silver Spring Library Residential, Sligo Apartments, 4010 Randolph Road, and the rest at 25% MPDUs or more) and fill in `project_subsidy.csv`.

## Call 14 decided: Tregoning kept, own schedule (Nov 3 2026, Jacob)
- RE-1 under the 2014 code (not amended by ZTA 18-06): standard method 1.09 du/ac x 37.85 ac = 41.26; MPDU optional method 1.22 du/ac = 46, for any MPDUs (Sec. 4.4.6.B and D). Tregoning has the minimum: the MCPB 24-091 data table lists MPDUs "12.5% (6 DUs)" allowed/required and "13% (6 DUs)" approved (p. 8). A flat step, so no choice of share.
- `04_build_base_density.py` drops it (11.5% over base against 4.4% on the sliding schedule at 13%). `06_base_density_audit.py` now puts it back through `OTHER_RULE` (renamed from `CR_EXEMPT`; it holds Knowles Manor and Tregoning). `08_building_size_bunching.py`: new rule "RE-1 MPDU step" (`RE1_STEP`) in the "own schedule" group.
- Result: base 39 for the report's 44 units (the other 2 of the 46 are development rights retained on 20.04 ac), +12.8%, between. Own schedule now 3 (2 Bethesda Overlay + Tregoning). 181 projects in `06`, 173 rows in `08`. No other row changed.

## Subsidized projects flagged; 2023 report labels fixed; the 25% impact-tax notch (Nov 3 2026)
- **Search.** Candidates: every project in `06` with 20% MPDUs or more, a nonprofit or HOC developer, a HUD LIHTC property within 100 m of its site plan (HUD LIHTC ArcGIS layer, 96 Montgomery County properties, placed in service through about 2019; `sources/subsidy/hud_lihtc_montgomery.geojson`), or a name match in DHCA's Multi-Family Home Loans list (data.montgomerycountymd.gov n724-uy7d; `sources/subsidy/dhca_multifamily_loans_n724-uy7d.csv`). About 30 projects, each read against its Planning Board documents and financing announcements (county and HOC releases, CDA bond statements, DHCA's FY2026 Q4 pipeline report, developer pages). Local quotes checked word for word; Victory Haven, Willow Manor and The Argent web sources checked by hand.
- **Coded** in `data/raw/mpdu_annual_reports/project_subsidy.csv` (21 rows; `subsidy`, `restricted_units`, quote and source): LIHTC 16 (Knowles Manor, Springvale Terrace, 4010 Randolph Road, MHP Nebel, Residences at Forest Glen, Hillandale Gateway, Victory Haven, 900 Thayer, Silver Spring Library, Willow Manor, The Galaxy, National Park Seminary (66 historic apartments only), Sandy Spring Village, Woodfield Commons, Sligo Artspace, Park Montgomery); LIHTC planned 1 (Tevis Place); LIHTC after completion 1 (The Argent, built as a market condo, converted 2010); HOC without tax credits 1 (The Lindley, in the Chevy Chase Lake plan group); public land 2 (PSTA, 30% "a requirement of Montgomery County for the disposition of public land"; Olney Springs, county school site, 30% MPDUs + 30% workforce by agreement).
- **Nothing found:** Solaire Wheaton, The Citron (county loan entries equal their MPDUs), The George, The Exchange (HUD's Wheaton Metro Kiss & Ride is HOC's MetroPointe, a different building), Thayer & Spring (neighbour of 900 Thayer).
- **2023 report labels.** `annual_report_mpdu_2023.pdf` p. 11 (agreements to build) shifts names and developers against plan numbers and counts: 820220020 217/34 is Park Montgomery (named "4725 Cheltenham Drive"), 820220060 110/17 is 4725 Cheltenham Drive (named "7340 Wisconsin Avenue"), 820210080 141/22 is Northpark at Montrose Phase I (named "Park Montgomery"), 820220170 98/25 is Sligo Apartments (named "Hillandale Gateway"), 820190130 463/116 is Hillandale Gateway (named "Sligo Apartments"). Plan numbers and counts agree with the resolutions, so bases and positions were right; `06` now fixes the two names in its table (`NAME_FIXES`: Park Montgomery, Hillandale Gateway). The others are not in `06` (inferred bases or merged).
- **Result.** No count or position changed. `08` bonus available: 13 of 103 flagged (10 LIHTC, 1 after completion, 2 public land). Plan groups list their phases' subsidies.
- **The 25% notch (open, call 25).** Staff reports for Dowden's Station (82016006A), Century (82003007E), Axiom at Cabin Branch (820180060), Bloom Montgomery Village (82017013C) and Bradford's Landing (MCPB 17-054) say the share went to 25% to get the development impact tax exemption (Ch. 52, Sec. 52-41(g)(5), 52-54(c)(5)). Bloom cut back to 22% once its Opportunity Zone area was exempt anyway. Ashford Woods and Reserve at Damascus are at exactly 25% with no stated reason. Not coded yet.

## Calls 23 and 25 decided: unverified bases and the impact-tax notch flagged, all kept (Nov 3 2026, Jacob)
- **Call 23.** `06_base_density_audit.py` has `BASE_UNVERIFIED`; new column `base_check` (carried to `08`): unverified for Wentworth House (820050340), The Veridian (82005001A), Heritage at Silver Spring (820060380); borrowed for White Oak (82005018C, Phase 1's ratio). Checked for the other 177. All kept.
- **Call 25.** New hand-made `data/raw/mpdu_annual_reports/project_impact_tax.csv`; column `impact_tax` in `06` and `08`: stated 5 (Dowden's Station, Century, Axiom at Cabin Branch, Bloom Montgomery Village, Bradford's Landing), likely 2 (Ashford Woods, Reserve at Damascus: exactly 25%, no reason stated). Law: Ch. 52, Sec. 52-41(g)(5) and 52-54(c)(5), cited by the 2017-2019 staff reports; Bill 8-15 (2015 Council packet, `20150505_74.pdf`) proposed the 25% exemption for rentals. Start date of the version that covers for-sale projects not found; flags rest on each project's documents.
- `08` plan groups list their phases' flags (Cabin Branch shows impact_tax stated, from Axiom). No count or position changed.

## Call 11 decided: PSTA keeps the 0.5 FAR standard-method cap (Nov 3 2026, Jacob)
- PSTA (820220050, CR-1.0 C-0.5 R-1.0 H-150, standard method, approved Apr 2022): base = the CR standard-method cap, the lesser of mapped FAR or the greater of 0.5 FAR or 10,000 sf = 1,048,244 sf total; approved 1,040,876 sf (0.497 FAR). As coded: base 634 for 630.
- The cap stood in 2022: Planning staff's report on ZTA 22-08 (1 Sep 2022, pp. 1-3; `sources/planning_board/ZTA-22-08-Planning-staff-report_2022-09-01.pdf`) quotes Sec. 4.5.3.C as then in force ("CR Density, FAR: The lesser of: mapped FAR or the greater of 10,000 SF or 0.5 FAR") and says CR projects reach the MPDU provisions only through the optional method. The county's ZTA list (data.montgomerycountymd.gov 3hex-pk9g) shows no change to CR standard-method density from 2014 to 2022. MCPB 22-037's "up to 2,096,488 sf" is the mapped FAR. No value changes.

## Calls 1, 6 and 7 decided: kept as coded (Nov 3 2026, Jacob)
- Call 1: a plan maximum is the base only if it is zoning (mapped zone, Council DP/DPA or binding element, master or sector plan limit, or a Board cut below the request with a reason).
- Call 6: APF (traffic) unit limits are not caps unless the Board set one below the request.
- Call 7: old-code R zones, base = "maximum with MPDUs" / 1.22 (Woodlake and Bloom by analogy; neither moves).
- No value changes. Open: call 5 (the 19 projects over base through non-MPDU programs, dropped; keep-everything rule may call for keeping them flagged) and calls 3 and 12 for Evan.

## Call 5 decided: projects over base through other programs kept, flagged (Nov 3 2026, Jacob)
- `06_base_density_audit.py`: `OTHER_PROGRAM` puts back the 18 report rows whose base `04` drops because they went over base through a non-MPDU program (base as in `utils.attach_observed_base`); column `other_program`: Bethesda Overlay 7 (The Edge 820180170, Metro Tower 820190110, 7607 Old Georgetown 820190030, St. Elmo 82017003A, 8015 Old Georgetown 820200130, 4909 Auburn 820190100, 4725 Cheltenham Drive 820220060), workforce housing 7 (Shady Grove Station-Westside rows on 820130220 / 82013022A / 82013022E, incl. The Daley and Laureate; Elizabeth House III on Elizabeth Square 820170140), master plan bonus 2 (Preserve at Rock Creek 820060110), PD zone bonus 1 (Jefferson at Inigo's Crossing 820040230), ZTA 21-07 1 (Sligo Apartments 820220170). Knowles Manor (the 19th) was put back under call 13.
- `08_building_size_bunching.py`: Bethesda Overlay rows take the "Bethesda Overlay" rule (own schedule; St. Elmo had fallen to "CR lump at 15%" because its regime row has no Bethesda Downtown Plan tag); the others get the new rule and group "other program". PLAN_GROUPS adds Shady Grove Station-Westside (820130220, 82013022A, 82013022E) and Preserve at Rock Creek (820060110); their rows share one ratio, so possible overlap among Westside's Stanley Martin rows does not move the position.
- `project_subsidy.csv`: Sligo Apartments added (LIHTC, 98 of 98 restricted; ZTA 21-07 requires 100% income-restricted; MCPB 22-073).
- `NAME_FIXES` now also names 4725 Cheltenham Drive (820220060), Sligo Apartments (820220170) and 11 rows the 2025 report lists without a name, from their resolutions.
- Result: 199 projects in `06` (put back: OTHER_RULE 2, OTHER_PROGRAM 18), 185 rows in `08`. Own schedule 10, other program 5. Bonus available unchanged: below base 41, at base 17, between 16, at 22% 27, above 2.


## Zone rules for the 17 "unclear" projects (Nov 3 2026)
- **RNC before Oct 2014 → 25A bonus (5).** The resolutions state the bonus: Batchellors Forest (MCPB 09-95, "22 percent density bonus for providing 15 percent MPDUs"), Trotters Glen (MCPB 13-92, "density bonus of 1.19 for providing 14.49 percent MPDUs"), Orchards of Sandy Spring (Danshes staff report: the Council amended the RNC zone after the master plan "to provide MPDU's", and the extra MPDUs earn "a density bonus of one market rate unit"). Olney Estates (call 12) and Reserve at Fair Hill sit at or near 22%, as the bonus predicts.
- **RMX → new rule "RMX bonus", group bonus available (3).** Old 59-C-10.3.7(c), quoted in ZTA 06-15 (`sources/law/0_zta_06-15_rmx_2c_tdr_2006.pdf` pp. 7-8): master plan units "may be increased by a number equal to the number of moderately priced dwelling units ... provided that the total increase does not exceed 22 percent". This is not the 25A table: each MPDU adds one unit, so a project at the master plan count with 12.5% MPDUs left units unbuilt. Positions are still measured against `04`'s base. Waterford Hills (below base) and Buckingham (between; was "25A bonus" through `RMX_BONUS`, which now only carries the note).
- **Clarksburg Town Center (820070220) → plan cap.** Same Project Plan 9-94004 (max 1,300 du) already in `PLAN_CAPS` for 819980010; MCPB 09-015 re-approved the whole town center at 1,213 du incl. 152 MPDUs. Below base either way.
- **Mt. Prospect (820170160) → plan cap.** MCPB 18-017 condition 12: "limited to 187 total dwelling units ... including 24 MPDUs and 17 TDRs"; the master plan's 170 + 17 TDRs, assumed by LMA G-884. Was in `UNCLEAR_CAPS`; at base, now ceiling at base.
- **RH (Woodlake) → 25A bonus.** The staff report's data table has a "Density Maximum Units (w/ MPDU's)" line under 59-C-2.411b, so the zone gave MPDU density (call 7). Below base.
- **Residences at Forest Glen → ZTA 18-06.** Zone not parsed, but it is CRTF (MCPB 21-017) and accepted Sep 2020, so the date rule applies. `bonus_rule` now calls a missing zone unclear only before Oct 2018. Below base; LIHTC.
- **CBD before Ord. 15-35.** The PHED Committee found in Nov 2004 that the CBD and TS zones "do not now have language that expressly allows the maximum residential density ... to be increased to accommodate the MPDU density bonus" (Ord. 15-35 preamble; adopted 30 Nov 2004, effective 1 Apr 2005). By hearing date:
  - Heard after adoption → 25A bonus (`CBD_HEARD`): Portico (31 Mar 2005, "22 percent density bonus for providing 15 percent MPDUs"), Citron (site plan 81999002H heard 13 Jul 2006; "12% density bonus for providing 13.7% MPDUs"; its 1998 date_regime is the project plan), The Veridian (re-heard 17 Mar 2005; 4.66 FAR of 5.0, 12.5% MPDUs; below base).
  - Heard before adoption → new rule "CBD before Ord. 15-35", group ceiling at base: The Crescent (21 Oct 2004; staff: "the permitted maximum density for this site under the optional method of development is 5.0 FAR"; 12.5% MPDUs, at base).
- **Still unclear (3), with a note (`UNCLEAR`).** Upstairs at Bethesda Row (C-2, 2004, at base), The Rae (C-2, 2009, at base), Montgomery Row at Rock Spring (I-3, 1989, below base). Residential in C-2 came from 59-C-4.35 (ZTA 01-08), whose text I could not get (amlegal blocks downloads; no Council PDF online); neither staff report mentions a bonus, and MCPB 09-123 notes parts of 59-C-4.35 "were invalidated by a recent court case".
- **Call 26 decided (Jacob, Nov 3):** The Crescent stays ceiling at base. No change to the code.
- **Result.** Only these 17 rows changed (`bonus_rule`, `group`, `note`). Bonus available: below base 45, at base 17, between 20, at 22% 30, above 22% 2. Ceiling at base: at base 23, below 14. Unclear: 3.

## Cleanup and stock-take (Nov 4 2026)
- **Reproduces.** A clean `run_all.py` in `full_run` (20 ok, first try) gives byte-identical output tables. Evan's and Audrey's code is untouched; ours is new files only (`06`, `07`, `08`, `12_download_pb_staff_reports.py`, `run_all.py`, `01_combine_reports.py`) plus hand-made inputs (`manual_coding_additions.csv` appended to Audrey's `manual_coding.csv`; `document_fills.csv`, `site_plan_fills.csv`, `project_fixes.csv`, `project_tdr.csv`, `project_subsidy.csv`, `project_impact_tax.csv`). `full_run`'s `manual_coding.csv` = the snapshot's + `manual_coding_additions.csv`, checked.
- **Fixed: plan-group bonus.** `08` took a plan group's `bonus_used` from its first phase; it is now the group's units over its base (Shady Grove Westside +31.0% → +32.1%, Chevy Chase Lake +10.50% → +10.55%; no position moved). Plan groups now also list their phases' `tdr`.
- **Fixed: flags on the call-5 put-backs.** The TDR and subsidy checks ran before these 18 rows were back in.
  - Shady Grove Station-Westside (820130220, 82013022A, 82013022E): TDRs used, 64 (MCPB 13-190 condition 4: 19 + 18 + 15 + 12 for Buildings A-D).
  - Laureate (id 157): HOC, no LIHTC (Bozzuto/EYA/HOC; HOC's Housing Production Fund, which does not use tax credits; 81 of 268 affordable), and impact_tax likely (exactly 25%). It shares plan 82013022A with The Daley (market), so `project_subsidy.csv` and `project_impact_tax.csv` now take an optional `id` column; `06` matches on id where given, else on site_plan (`by_id_or_plan`).
  - Elizabeth House III (820170140): LIHTC, 238 restricted (HOC; $35.2m LIHTC equity, $55m HOC bonds; 106 RAD replacement units).
  - The others (Bethesda Overlay rows, Preserve at Rock Creek, Inigo's Crossing, Tregoning, Knowles Manor, Sligo) have no TDR, subsidy or 25% notch beyond what was coded.
- **Fixed: Montgomery Village Center (820180020) dropped from the base table.** Audrey marked the "-1" copy of MCPB 18-038 `usable` 0 ("site capacity not comparable to the 104-unit report project": a 32-unit building on an 18.78-acre center, so the site-wide base was 23x the building's units), but the identical copy without "-1" stayed usable and supplied the base (-96%). One row in `manual_coding_additions.csv` extends her `usable` 0 to it. The same leak is in her snapshot run; no other `usable` 0 file has a usable twin (Olney Estates' opt-3/opt-4 are different parts). Side effect: the average unit size `04` estimates from floor-area projects shifts, so floor-area bases move about 0.6% (e.g. North Bethesda Market 534 → 537, Wentworth House 465 → 468); no position moved. `mpdu_tax_schedule_bins.csv` moves up to 2.5% per bin for the same reason.
- **Fixed: missing site plan dates.** Four report plan numbers have no GIS record, so `date_regime` was missing; `08`'s date tests then fell through, putting The Astrid, Sandy Spring Village and Tevis Place in "CR lump at 15%" by default. `08` now has `DATE_FIXES` (from the documents) and calls any remaining missing date unclear. Convention, shared with `07`'s `REGIME_DATES`: an amendment takes the original plan's date unless it created the units. Woodlake 18 Jan 2005 (the 59 townhouses), The Astrid 19 Feb 2016 (81982098C; the 2020 amendment only cut density), Sandy Spring Village 5 May 2021 (amendment turned two 1988 office buildings into the 56 units; `07` had 1988), Tevis Place 12 Feb 2025. Result: Sandy Spring Village and Tevis Place move from lump at 15% to bonus available (ZTA 18-06); in `07` Sandy Spring Village moves from old to new regime.
- **Checked, no change:** no duplicate ids or plan + units pairs; MPDU share and bonus_used recompute from units; six rows have fewer MPDUs than the minimum share (Maple Ridge, The Core, Park Potomac Townhomes, The Flats @ Bethesda Ave, Inigo's Crossing), as the reports give them; the two Park Potomac and Darcy/Flats rows are parts of plans whose MPDUs may sit in other buildings (not checked); two rows have no parsed zone (Forest Glen, dated 2020; Gallery Park, a plan cap), neither needs one.
- **Now:** 205 report projects after `project_fixes.csv`; 198 with a resolution base in `06`; 184 rows in `08` (plan groups once). Groups (below / at / between / at 22% / above): bonus available 116 (46 / 17 / 21 / 30 / 2), ceiling at base 37 (14 / 23 / 0 / 0 / 0), lump at 15% 12 (6 / 4 / 1 / 0 / 1), own schedule 10, other program 5, unclear 3, base from approved units 1.
- **Real-choice subset, for reference (not a filter yet).** Bonus available with no subsidy (except LIHTC after completion), no 25% impact-tax flag and a 12.5% minimum: 89 (31 / 14 / 16 / 27 / 1). Also with a checked base and no TDRs: 72 (24 / 14 / 13 / 21 / 0).

## Descriptives, dataset v1 (Nov 4 2026)

New `09_descriptives.py`, run by `run_all.py` after `08` (a full run is now 21 "ok" lines; the Nov 4 run reproduced every earlier table). It reads the results, `project_regime.csv` (now written by `07`), `building_size_bunching.csv` and `project_fixes.csv`, and writes `output/tables/descriptives_*.csv` and `output/figures/descriptives.pdf` (PNGs in `output/figures/descriptives/`). Four samples: all 206 (MPDU share), base 184, bonus available 116, real choice 89 (no subsidy except LIHTC after completion, no 25% impact-tax flag, 12.5% minimum). Share categories are counted in units, "at x%" meaning the fewest MPDUs that reach x%. The write-up is `descriptives.md` / `.pdf`. The MPDU-share sample is 206, not 205: `07` keeps Wildwood Manor, which `06` drops.

## MPDU-share sample: checks for the model (Nov 4 2026)

- **14.5-15% gap (old table buys nothing there).** One project is strictly inside it in units: Thayer & Spring, 59 of 399 (14.79%; 15% needs 60). It took the full 22% (base 327), so the Board treated it as 15%; check the resolution. Manor Oaks (8 of 54) and Tapestry (10 of 67) sit at the fewest MPDUs reaching 14.5% and took 20% (19.6%), as the table says. Trotters Glen and Leaman Farm (10 of 69, 14.49%) took 19%, which is also as the table says. The table's last step (20% to 22% for 0.5 points) costs about 0.45 MPDUs per unit against about 0.27 just before, so 14.5% is a second, small kink.
- **The old-schedule share sample mixes schedules.** Of 171 old-regime projects: bonus available 91, ceiling at base 34, lump at 15% 10, not an own row in `08` 26 (20 phases of the 6 plan groups, 6 with no base), other 10. At 15%: 30 of 91 bonus available against 1 of 34 ceiling at base. Between the minimum and 15%: 7 bonus available, 7 ceiling at base, 4 other.
- **Phases.** The share sample counts the 20 phase rows of the 6 `PLAN_GROUPS` separately; 8 of the 13 "below its minimum" rows are such phases (Cabin Branch phases at 5-6%, Westside 3%). Plan-wide shares: Cabin Branch 14.4%, Chevy Chase Lake 15.3%, Clarksburg Village 15.0%, Pike & Rose 12.6%, Preserve at Rock Creek 15.1%, Westside 14.6%.
- **Two more splits not in `PLAN_GROUPS`.** The Perry (61 of 450) and Park Potomac Townhomes (14 of 150) share 82004015A: 75 of 600, exactly 12.5% at the 600 cap. The Darcy (13 of 88) and The Flats @ Bethesda Ave (14 of 162) share 820070180: 27 of 250, 10.8% (other buildings not checked).
- **Ceiling at base above the minimum.** Mallory Square (+7 MPDUs over the minimum), Hanover Shady Grove (+4), Solaire Wheaton (+3), AVA Wheaton and Amalyn (+1 each) give MPDUs that buy nothing under our rule. Not checked.
- **Fixed (same day).** `08` adds Park Potomac (82004015A: The Perry + Park Potomac Townhomes) and Darcy/Flats (820070180) to `PLAN_GROUPS` and writes `output/tables/project_group.csv` (each report project's plan group and group). `09` sums plan groups in the MPDU-share sample too (earliest acceptance date sets the regime) and adds `descriptives_share_by_group.csv` and a share-by-group figure. Now: 206 report rows → 190 projects in the share sample (155 old, 34 new, 1 unknown); 182 in the base sample (ceiling at base 37 → 35); bonus available 116 and choice 89 unchanged. Old schedule at 15%: 31 of 92 bonus available, 1 of 34 ceiling at base. The 8 projects with no resolution (6 under the old schedule) have no group (no zone source: the site plan GIS layer has no zoning field).

## Old-schedule choice projects at base: another limit? (Nov 4 2026)

Why: the old-schedule choice sample (82) has 13 at base against 3 in the first 10% above, more than a smooth model can give at any elasticity. 9 of the 13 are CBD/CR (CBD/CR: 8 below / 9 at / 2 between / 10 at 22%; elsewhere 19 / 4 / 14 / 16). After Ord. 15-35 the 22% bonus also raises residential FAR (59-C-6.215(b); Cheval, Ripley East, Ripley II footnotes), so a FAR cap alone does not rule the bonus out; height or a plan cap can. Sources: the resolutions (`data/raw/pb_resolutions`), staff reports for the 2006 plans, `manual_coding.csv` notes. Height rules quoted in other resolutions: CBD-1 60 ft, up to 90 ft (59-C-6.235(b)); CBD-2 and CBD-R2 143 ft, up to 200 ft; Woodmont Triangle 143 ft, 174 ft with the 22% MPDU bonus.
- **Eleven55 Ripley (82006025A, CBD-2).** MCPB 10-65 data table: 5.0 FAR at the cap, 385 du, 1155 Ripley tower 200 ft (the CBD-2 maximum). Height.
- **Flats 8300 (82006036B, CBD-1).** MCPB 12-83: 3.0 FAR (CBD-1 optional maximum), 90 ft (the CBD-1 maximum). Height.
- **Argent (820060280, CBD-1).** 2006 staff report: 125 du/ac x 0.77 ac = 96, 90 ft. Height; also all 96 units restricted (LIHTC).
- **Element 28 (820130240, CBD-2, Bethesda Metro Core).** MCPB 13-137: 5.0 FAR at the cap, 143 ft; "most are limited to 143 feet, with the limited opportunity to reach 200 feet". Height, per the sector plan.
- **8415 Fenton Street (820130050, CBD-1/CBD-0.5/R-60, Fenton Village Overlay).** MCPB 13-26 data table: height permitted / approved 75/75 (CBD), 60/60 (FVOZ), 35/35 (R-60); density 257,002 sf permitted, 260,921 approved. Height.
- **Guardian Building (820170100, CR-5.0 R-4.75 H-145T).** Conversion of an existing office building (5 storeys added to 6); 4.75 FAR at the cap, 138 ft of 145 (less than a floor left). Height and the existing structure.
- **The Blairs F1-F2 (820140170).** Base is Project Plan 920130050's ceiling for the whole 30.4-ac site (2,800 du incl. 1,110 existing, 2.89 FAR, below the CBD-R2 5.0): a plan cap, which `08` puts in ceiling at base elsewhere (Black Hill). Not in `PLAN_CAPS`.
- **The Core (82011006A, CBD-2).** 292 du at 5.5 FAR: the 0.5 FAR over the 5.0 cap and the height from 143 to 161 ft are the workforce housing allowance (59-A-6.18, 17 WFHUs). Went over base through another program: belongs in other program, not at base.
- **Cameron (820060370, CBD-2).** Unclear. 143 ft, 15 storeys, 4.82 FAR of 5.0; the 200 du/ac unit limit (326) binds, and the amendment added 13 units in the same floor area to reach it. 143 ft is below the CBD-2 200 ft maximum; no Silver Spring sector-plan height found.
- **Not checked:** the 4 non-CBD projects at base (Woodward Crossing RT-10, Bentley Park PD-2, Woodcrest R-200, Wootton Crossing RT-8); the CBD/CR projects just below base (Heritage, 1200 East West Highway, The Premier, Veridian, Fenwick), which may also be height-limited.
- **Effect (console).** Without the 8: 74 projects, 27 / 5 / 16 / 26, at base 5 against 3 just above (a ratio the model can fit). The rough bunching elasticity on the MPDU price falls from 0.17 to 0.07 (0.06 without Cameron).
- **Coded (Jacob, same day: "flag them").** `08`: new `HEIGHT_CAPS` (Eleven55 Ripley, Flats 8300, Argent, Element 28, 8415 Fenton Street, Guardian) with bonus_rule "height cap", group "height at base"; The Blairs added to `PLAN_CAPS` (ceiling at base). `06`: The Core added to `OTHER_PROGRAM` as workforce housing (other program; its base of 292 still includes the workforce density, so it shows at base). `09`: "height at base" in `GROUP_ORDER`. The height group is selected on position (only at-base CBD/CR projects were checked), so it is not a comparison group. Rerun: 21 ok; only these 8 rows changed in `building_size_bunching.csv` (bonus_rule, group, note, other_program) and The Core's other_program in `base_density_audit.csv`. Now: bonus available 108 (46 / 9 / 21 / 30 / 2), ceiling at base 36 (14 / 22), height at base 6 (all at base), other program 6; choice 81 (31 / 6 / 16 / 27 / 1), old-schedule choice 74. `descriptives.md` / `.pdf` updated.

## Downtown choice projects just below base: height? (Nov 4 2026)

The five old-schedule CBD/CR choice projects 8-13% below base. If height stopped them below the base floor area, they are not projects where zoning doesn't bind, and they inflate the density just below base.
- **1200 East West Highway (820060140, CBD-2), -10.2%.** 2005 staff report data table: Max. Building Height 143 permitted, 142 approved (14 storeys); 4.51 FAR of 5.0 (base 275 from the 5.0 FAR). Height. Coded in `HEIGHT_CAPS`.
- **The Veridian (82005001A, CBD-2), -12.6%.** March 2005 staff report: heights taper at 2:1 from 90 ft on East West Highway to 143 ft, "consistent with the Master Plan urban design guidelines of South Silver Spring"; 4.66 FAR of 5.0. Height, on the guidelines rather than a data-table limit (weaker). Coded in `HEIGHT_CAPS`.
- **The Premier (82008023A, CBD-2), -8.0%.** Office building approved in 2008 (152,740 sf, 4.0 FAR of 5.0), converted to 160 residential units in 2011 with "building density and heights ... unchanged". The limit is the approved office shell, not shown to be zoning. Not coded.
- **Fenwick (820120080, CBD-1), -12.7%.** MCPB 12-48: 60 ft (the CBD-1 standard; optional method allows up to 90), 310 of 355 du at 125 du/ac; "under all the standards allowed". No sector-plan height found. Not coded.
- **Heritage at Silver Spring (820060380, CBD-1), -10.6%.** The local documents (2007 minor amendment, 2012 amenity resolution) give no height or floor area; the base is 125 du/ac x 1.88 ac. Not coded.
- **Group renamed** "height at base" → "height limit" (the two are below base). Still selected on position: only at-base and just-below CBD/CR choice projects were checked.
- **Rerun.** 21 ok; in `building_size_bunching.csv` only the 6 earlier height rows (group label) and the 2 new ones changed. Now: bonus available 106 (44 / 9 / 21 / 30 / 2), height limit 8 (2 below, 6 at base; Veridian's base is unverified), choice 79 (29 / 6 / 16 / 27 / 1), old-schedule choice 72 (25 / 5 / 16 / 26). Rough bunching elasticity on the MPDU price (console): 0.07 with the 10% window below base (11 projects, unchanged, as both new ones sit just outside it), 0.09 with a 15% window (13).

## The four choice projects at base outside downtown (Nov 4 2026)

- **Bentley Park (82005006A, PD-2).** Base 248 is a written binding element of DPA 09-1 (Council Res. 16-1105, already in `manual_coding.csv`): after the M-NCPPC acquisition of the Northern Portion, "the maximum number of dwelling units in the Southern Portion of G-813 Part I will be 248 units, including a maximum of 31 MPDU's". A plan cap including MPDUs, like the other G-plan caps. Coded in `PLAN_CAPS` (ceiling at base).
- **Woodward Crossing (820070250, RT-10, Mainhart Property).** MCPB 09-143: 32 townhouses on 3.28 ac (base 32.8 at 10 du/ac). SDPA 09-2's binding elements protect Woodwards Store Road, specimen trees and noise; none caps density. No other limit found. Stays at base.
- **Wootton Crossing (820100070, RT-8, Darnestown at Travilah).** MCPB 10-112 data table: maximum density 9.76 du/ac (8 x 1.22, the MPDU density), 39 lots on 4.89 ac net (7.98 du/ac); condition 5 limits development to the 39 units in the traffic study. SDP G-849's 3 binding elements not found (not local, not online). Bonus density was allowed and not used. Stays at base.
- **Woodcrest (820050090, R-200, Clarksburg).** 2004 staff report data table: 2 du/ac on 43.3 ac R-200 = 86 permitted, 86 proposed; townhouses 34 of the 40% maximum (34.4). The 86-unit limit is a transportation condition at the requested count. Before Oct 2014 R-200 MPDU density was 2.44 du/ac, so the bonus was available. Stays at base.
- **Rerun.** 21 ok; only Bentley Park changed (bonus_rule plan cap, group ceiling at base, note). Now: bonus available 105 (44 / 8 / 21 / 30 / 2), ceiling at base 37 (14 / 23), choice 78 (29 / 5 / 16 / 27 / 1), old-schedule choice 71 (25 / 4 / 16 / 26). Of the 14 choice projects at base before these checks, 9 had another limit; the 5 left are Cameron (unclear), Woodward Crossing, Wootton Crossing, Woodcrest and 850 Sligo Avenue (new rules, not checked). Rough bunching elasticity on the MPDU price (console): 0.055 (10% window, 11 below), 0.07 (15% window, 13).

## The four left: The Premier, Fenwick, Heritage, Cameron (Nov 4 2026)

Rule used throughout: in CBD-2 and CBD-R2, 143 ft is the optional-method maximum unless the Board finds that the sector plan supports up to 200 ft; in CBD-1, 60 ft unless it finds for up to 90 (59-C-6.235(b), as quoted in other resolutions). A building at that height and at or below its base floor area is height-limited. New documents downloaded to the session scratchpad, not to the project: MCPB 11-105 and 11-033 (resolutions archive), and the 19 Jan 2006 staff report for Project Plan 920050020 (`meetings_archive/06_meeting_archive/agenda_011906/8711 Georgia _ocr.pdf`).
- **Fenwick (820120080), -12.7%.** Project Plan 920110010 (MCPB 11-105) data table: Max. Building Height 60 ft required, "60 ft, as measured from Spring Street" approved; 109 of 125 du/ac (310 du). Condition 2 limits the building to 60 ft; the plan stresses the transition to the one-family neighborhood at the CBD edge. Height.
- **The Premier (82008023A), -8.0%.** Project Plan 920050020 staff report (19 Jan 2006): "a 13-story (143 feet) building", condition 2 "shall not exceed the maximum height of 143 feet"; development ceiling 152,740 sf (4.0 FAR of 5.0 on 0.88 ac), on a 90 x 185 ft footprint abutting the Crowne Plaza. MCPB 11-33 (2011 conversion to 160 du) keeps density and height. Height.
- **Cameron (820060370), at base.** 2006 staff report: 15 storeys, 143 ft, condition 3 "shall not exceed 143 feet"; 4.82 FAR of 5.0, at the 200 du/ac unit limit. No finding for more than 143 ft. Height (same rule as Element 28 and The Premier).
- **Heritage at Silver Spring (820060380), -10.6%.** No resolution or data table found (2006 agendas for the project and site plans are no longer online). The Downtown Silver Spring listing (silverspringdowntown.com/go/8021-georgia-avenue) describes the proposal: CBD-1 and South Silver Spring Overlay Zone, "approximately 210 dwelling units (including 27 MPDUs) ... in a 90' tall building", preserving parts of two Locational Atlas buildings. 90 ft is the CBD-1 and overlay maximum. Height (weaker source).
- **Coded.** All four in `HEIGHT_CAPS`.
- **Rerun.** 21 ok; only these 4 rows changed (bonus_rule, group, note). Now: bonus available 101 (41 / 7 / 21 / 30 / 2), height limit 12 (5 below, 7 at base), choice 74 (26 / 4 / 16 / 27 / 1), old-schedule choice 67 (22 / 3 / 16 / 26). Of the 14 choice projects at base before these checks, 10 had another limit; left: Woodward Crossing, Wootton Crossing, Woodcrest, 850 Sligo Avenue (new rules, not checked). Every downtown choice project at or within 13% below base is now in height limit. Rough bunching elasticity on the MPDU price (console): 0.05 with the 10% window (10 projects below base); the next project below is 21% under base, so wider windows only lower the density (0.07 at 15%, 0.09 at 20%).

## Wedge sample: decision (Jacob, Nov 4 2026)

The wedge is measured by revealed preference on the density (unit / floor-area) limit: each project's position on the price schedule it faced bounds its wedge (below base 0; at base 0 to 0.11d; interior exact; at 22% at least 0.16d, old schedule). No elasticity needed. Sample: every project that faced a known price for density and chose its own share (no subsidy except LIHTC after completion, no 25% impact-tax share): bonus available 81 (old 67, new 14 incl. 7 with a 15% minimum), height limit 12, CR lump at 15% 8, own schedule 10 = 111. Out: ceiling at base 37 (no price), subsidy or impact tax about 30, other program and unclear about 7.
- **Height limit stays in (Jacob: "Keep them in").** Their density limit did not bind, so their density wedge is at most 0.11d (most are at or below base). Their height wedge is not priced by MPDUs and is not measured.
- **Coded (same day).** `08` writes `wedge_sample` (`WEDGE_GROUPS` and the subsidy and impact-tax tests) in `building_size_bunching.csv`; `09` counts it in `descriptives_sample.csv`. Rerun: 21 ok; only the new column and the new sample row changed. 111 = bonus available 81 (old 67, new 14), height limit 12, lump at 15% 8, own schedule 10 (old 91, new 20). Positions: below base 38, at base 17, between 20, at 22% 28, above 22% 8.
- **Figure (same day).** `09` adds figure 6, `wedge_sample`: the 111 together, MPDU share and units over base, old and new rules stacked. `descriptives.md` section 6 shows it with the position-by-group table.

## 850 Sligo Avenue (Nov 5 2026)

- **Why checked.** The last choice project at base (80 units, 10 MPDUs, base 80; CR-3.0 C-2.0 R-2.75 H-60T, Fenton Village Overlay). Coded ZTA 18-06 because the site plan was filed 8 Nov 2018, 8 days after the new rules.
- **What the documents say.** Sketch Plan 320180090 (MCPB 18-025; filed 5 Jan 2018, approved by resolution 3 May 2018, under the 2014 CR rule) makes "maximum density and height" binding elements: 82,941 sf total, 76,029 sf residential (3.0 and 2.75 FAR, the mapped maxima), 12.5% MPDUs, new construction limited to 60 ft. Site Plan 820190050 (MCPB 19-039, scanned, OCR'd) "conforms to all binding elements" of the sketch plan and repeats both conditions; its data table shows permitted = approved for FAR (3.0) and height (60 ft). The 2000 Sector Plan limits residential buildings east of Fenton Street to 60 ft, and the building steps down to 35 ft by the houses on Gist Avenue. Amendment 82019005A (MCPB 19-120) only removed the age restriction. Sketch plan resolution and the 2019 staff report from montgomeryplanningboard.org; site plan resolutions in `data/raw/pb_resolutions`.
- **Coded.** `CR_LUMP` in `08` (the Knowles Manor rule: a CR plan after Oct 2018 whose density was set by an earlier sketch plan under the 2014 lump rule). It is also at its height limit, so either way it isn't a refusal of the unit bonus.
- **Rerun.** 21 ok; only this row changed (bonus_rule, group, note). Bonus available 100 (41 / 6 / 21 / 30 / 2), lump at 15% 13, choice 73 (26 / 3 / 16 / 27 / 1). Wedge sample still 111 (bonus 80, height 12, lump 9, own 10). Every choice project at base has now been read: Woodward Crossing, Wootton Crossing and Woodcrest are the 3 left. Rough bunching elasticity (console, 10-20% windows): 0.05-0.09 old schedule only, 0.04-0.075 with the new-rules projects.

## Wedge bounds in units of d (Nov 5 2026)

- **New script `10_wedge_bounds.py`** (run last by `run_all.py`; 22 ok, no other output changed). For each of the 111 wedge-sample projects it gives the bound its position reveals on w, the value of one more permitted unit beyond the minimum share's MPDUs, in units of the MPDU discount d. Rule: MPDUs carried by one more unit MC(n) = s(n) + n s'(n) on `rules.share_for_bonus`, w = MC - s_min; below base 0; at base [0, 0.114]; interior exact; at 22% at least 0.164 (old schedule, no upper bound) or [0.164, 0.79] (ZTA 18-06). 15% minimum: w = 0 below 22% (the minimum earns the 22% bonus in `rules.mpdus_required`; VERIFY). Lump: at base, average w over the notch band at most 1/6. Height limit at base: unbounded. Own schedule: not modeled.
- **Result.** 41 zero (below base, or a 15% minimum below 22%), 3 at most 0.114 (Woodward Crossing, Woodcrest, Wootton Crossing), 5 lump at base with an average at most 1/6, 17 exact (16 between, all 0.116-0.160; Flats at Knowles Station 1.44), 26 at least 0.164, 2 intervals at 22% under ZTA 18-06 (Avalon Residential, Strathmore Square), 7 height-limited unbounded, 10 own schedule. Within d, the schedule only prices density between 0.114d and 0.164d, so every finite threshold sits in that band.
- **Worth a look.** Flats at Knowles Station: 21 MPDUs of 84 (25%) at 33% over base, the only project on ZTA 18-06's third segment; 25% is also the impact-tax share, but it has no impact-tax flag.
- **d is not in the data.** Rentals: market rent (RentHub; `rules.RENT_MKT_STANDARD` is a $2,500 placeholder, ACS tract medians are old stock) minus the MPDU rent (`rules.mpdu_rent`, 0.117 x monthly AMI). For-sale (57 of 111): market sale price minus the DHCA MPDU price; the SDAT parcel file (`sdat_montgomery_parcels.csv`: last three sales per parcel, with price and how conveyed) is in the snapshot and the Dropbox but was not copied into `full_run`.

## SDAT match for the for-sale wedge projects (Nov 5 2026, exploration; no prices used yet)

- **Data.** `data/raw/sdat/sdat_montgomery_parcels.csv` copied from the snapshot into `full_run` (sha256 matches the manifest): Maryland Real Property Assessments, Montgomery County, 355,368 parcels, last three sales per parcel with price and conveyance code. Site plan polygons from `mcplanning/site_plans.geojson` (APNO = site plan number; amendments are their own records).
- **Method (scratch script, not in the pipeline).** For the 58 for-sale wedge projects: plan number -> GIS polygon (exact APNO; two fixes: Meadows at Hurley Ridge 820030110, the report's 820030100 is Cloverly Commercial; Woodlake 81971011A); residential (R) and condo (U) parcel points inside it; keep parcels built from the year before the site plan on; first sale = earliest arm's-length improved sale (code 1, price > 0) from the year before to two years after the parcel's year built, dropping bulk sales (same price and date on 3+ parcels of the plan); "low" sales = under 0.6 x the project's median first sale.
- **Tiers** (rules: parcels built since the plan within 90-110% of units; first sales for at least 75% of units; low sales within 25% (or 2) of the MPDUs expected among the sales found, and the lowest market sale at least twice the highest low sale):
  - **A clean (21):** Armstrong Property, Avalon Residential, Batchellors Forest, Bethesda Crest, Fairland View, Fairwood Crossing, Grosvenor Heights, Hallman Grove, Layhill Overlook, Leaman Farm, Little Falls Place, Mateny Hill, Olney Estates, Orchard Run, Orchards of Sandy Spring, Shady Grove Crossing, Symphony Park, Tapestry, Towns at Oak Hill, Woodcrest, Wootton Crossing. Positions: 8 at 22%, 2 at base, 6 below, 5 between.
  - **B MPDU prices not separable (8):** Arora Hills, Eton Square, Manor Oaks, Meadows at Hurley Ridge, Norbeck Crossing, Poplar Run, Towns of Tanglewood, Woodlake. Mostly mixed products (condos, townhouses, houses) whose price ranges overlap. Eton Square (14 low vs 14 expected), Meadows (39 vs 35) and Tanglewood (4 vs 5) fail only the gap rule (1.7-1.9).
  - **B no MPDU-priced sales (5):** Bethesda Mews, Cabin John Village, Magruder's Overlook, Potomac Highlands, Trotters Glen. Parcels and market sales match, but no sale near MPDU prices; the MPDUs may be elsewhere, sold through HOC, or not conveyed arm's length. Not checked.
  - **B first sales thin (4):** Cloverly Forest, Gateway Commons, Kensington Overlook, The Lauren (first sales lost to resales, or code 3/4 transfers).
  - **C parcels do not match units (11):** Buckingham Station (polygon is all of Fairfield at Germantown, 604 du, 1,207 parcels), Cheval Bethesda (condo records with no year built; 172 records for 71 units), Clarksburg Square, Clarksburg Village (plan group; polygon is phase 2), Creekside at Cabin Branch and Northpark at Montrose (still being built), Grosvenor Place, Maple Ridge, Reserve at Fair Hill, Residences at Shady Grove, Waterford Hills / Alta Liberty Mills.
  - **C polygon shared (2): White Oak (82005018C, 22 units) and Whitehall Square (820050180, 106 units).** The polygons share all 130 parcels; GIS gives the amendment 128 du = 106 + 22. These look like one plan listed as two projects with separate bases in `08` (both at 22%). Grouped in `08` on Nov 5 (see below); for SDAT they are now one project with one polygon.
  - **D no parcels (7):** 12710 Twinbrook Parkway, 2115 East Jefferson, 4910-4920 Strathmore, Linthicum West, Preston Place and Lake Apartments, Westwood Shopping Center (2024-25 agreements; not yet residential parcels in SDAT), The Argent (its 97 SDAT records are coded Commercial Condominium, so the residential filter dropped them; see below).
- **Not done yet.** Separating MPDUs from market units by something other than price (DHCA's ownership list in `mcplanning/mpdu_ownership_projects.geojson` gives each project's MPDU streets); unit size (SDAT square feet) for comparing like with like; the 52 rental projects.

### White Oak / Whitehall Square and The Argent (researched Nov 5 2026; White Oak grouped, Argent unchanged)

- **White Oak (82005018C) is Phase 2 of Whitehall Square's plan (820050180), and its density was set for the whole plan.**
  - 2005 site plan (staff report `82005018__item5_021005_opt.pdf`, OCR'd; Audrey's row): 106 townhouses incl. 16 MPDUs; density 24.2 ac x 4.39 du/ac = 106 (R-90 MPDU option); base 87.08.
  - 2014 amendments (Planning Board 22 May 2014, item 2: Preliminary Plan Amendment 11991099A and Site Plan Amendment 82005018C; staff report `WhiteOakStaffReports.FINAL.pdf` from montgomeryplanningboard.org, 83 pp.): the applicant bought five parcels (P56, P82, P108, P110, P158; 3.04 ac) and added 22 townhouses incl. 4 MPDUs. Table 5 computes the limit for the whole plan: "Max. Number of Dwelling Units 128 (29.34 ac X 4.39)" and "Min. Number of MPDUs at 15%: 20 (16 existing + 4 proposed)". The 3.04 ac alone give 13 units at 4.39; the 22 use the plan's remaining density (the 2014 table counts the original 26.30 ac, where 2005 used 24.2).
  - GIS: 820050180 / A / B 106 du on 26.8 ac; C and D 128 du on 30.0 ac, containing the whole original polygon.
  - So it meets the `PLAN_GROUPS` test in `08` (density limit and MPDU obligation set for the whole plan). NOTES round 4 listed it under "not duplicates ... where their density is set plan-wide they already share the plan's ratio"; it does share the ratio (`base_check` borrowed) but is not summed.
  - If grouped: 128 units, 20 MPDUs (15.6%); plan base 29.34 x 3.6 = 105.6 (sum of phase bases 87.08 + 18.07 = 105.2); 128 is within one unit of 22% over base, so at 22%. The wedge sample goes 111 -> 110, at 22% 28 -> 27, bonus available 100 -> 99, choice 73 -> 72. Separately, White Oak alone looks like a project at 22% with 18% MPDUs; grouped, the plan sits at the 15% count the table requires.
  - Also: White Oak's `date_regime` is 2004-12-02 (the original plan's), though amendment C (accepted 23 May 2013) created its units. Old code either way, so no change in rule.
- **The Argent: "For-Sale" is right for when it was offered; it became a LIHTC rental after completion, as `project_subsidy.csv` already records.**
  - SDAT has 97 records at 1200 Blair Mill Rd (96 units plus one other unit), all Commercial Condominium, each with a single recorded transfer: 29 Jul 2010, $24.7m, "arm's-length, multiple parcel". No unit ever sold separately, consistent with a condo that never sold and went back to the lender.
  - Press: built 2009 as luxury condos, sales stalled, Pallas bought it in 2010 for about $24.8m and reopened it in Sept 2010 as 96 affordable rentals with LIHTC and bond financing (86 units under 60% AMI, 10 under 50%; county press release, Gazette 11 Aug 2010, DCmud Sept 2010, Housing Finance).
  - So the 2009 MPDU offerings were for-sale MPDUs in a market condo, and the share was the market developer's. It is in the height limit group at base, so its wedge is not bounded either way. SDAT gives no unit sale prices for it.

### Whitehall Square grouped (Nov 5 2026, Jacob's OK)

- `08` `PLAN_GROUPS`: 820050180 and 82005018C -> "Whitehall Square (820050180)", with a comment citing the 2014 Table 5. `06` `BASE_UNVERIFIED`: White Oak's "borrowed" entry removed (the 2014 table checks the plan-wide density), so `base_check` is checked; the docstrings of `06` and `08` no longer list "borrowed", which had no other project.
- Grouped row: 128 units, 20 MPDUs (15.6%), base 105 (87 + 18, the phases' bases summed; the 2014 table's 29.34 x 3.6 = 105.6), bonus_used 0.219, at 22%, old code (date_regime 2004-12-02), For-Sale, offering year 2006 (the earliest). Wedge bound: lower, 0.164 (as each phase had alone).
- Rerun (22 ok). Changed tables: base_density_audit (one base_check), project_group (two plan_group), building_size_bunching 182 -> 181 rows, wedge_bounds 111 -> 110, and the descriptives. No other row changed. Counts: all 190 -> 189, base 182 -> 181, bonus 100 -> 99, choice 73 -> 72, wedge 111 -> 110 (bonus available 80 -> 79, old 91 -> 90); at 22% 30 -> 29 (bonus), 27 -> 26 (choice), 28 -> 27 (wedge); at 15% MPDUs 37 -> 36 old schedule (both phases were "at 15%" in units: 16 of 106 and 4 of 22 are the fewest MPDUs reaching 15%, as 20 of 128 is); base not checked 4 -> 3. `descriptives.md`/`.pdf` updated.

### SDAT match rerun after the Whitehall grouping (Nov 5 2026, exploration; no prices used)

- **Method change.** The scratch match keyed each project to one site plan number (`plan`). A plan-group row carries only its first phase's number, so the match now keys a plan group to all its phases' plans (`project_group.csv` + `base_density_audit.csv`) and dissolves their polygons into one. Everything else (R/U parcels, year built >= plan year - 1, first arm's-length sale, bulk rule, tiers) is unchanged.
- **Projects affected (2; all other 55 rows identical):**
  - **Whitehall Square (820050180 + 82005018C): C shared polygon -> B MPDU prices not separable.** 141 parcels, 124 built 2007-09 and 2017-18 (128 units); 111 first sales; 15 below 0.6 x median against 17.3 expected. It fails only the gap rule (1.84 < 2). Not the two phases mixed: split by build year, Phase 1 alone has 92 sales, 13 low (13.9 expected), gap 1.84; Phase 2 alone 19 sales, 2 low (3.5 expected), gap 2.41. Phase 1's sales run 2007-2010; not checked why its gap is narrow.
  - **Clarksburg Village Phases I-II (82003002B + 820050410): still C parcels do not match units**, now on both phases' polygons: new parcels 1,283 -> 2,234 for 2,653 units (0.84), first sales 1,081 -> 1,828, gap 1.01. (`PLAN_GROUPS` also lists 820030020, which is no project row, so it adds no polygon.)
- **Tiers: 58 -> 57 projects.** A clean 21 (unchanged), B 17 -> 18 (not separable 8 -> 9), C 13 -> 11 (shared polygon 2 -> 0), D 7. Outputs (scratchpad): `sdat_match_check.csv`, `sdat_first_sales.csv`; the earlier ones kept as `*_pre_wo.csv`.
