# Judgment calls in the base dataset (Nov 3 2026; status Nov 4)

The dataset gives each project a **base**: the most units the site could have before any MPDU bonus. We then compare what was built to it. For example, Poplar Run built 773 units on a base of 634, so it used a 22% bonus. A different base moves a project between five positions: **below base, at base, between (some bonus), at 22% (the full bonus), above 22%**.

Most bases come straight from a stated number in a Planning Board document. The calls below are the places where we had to choose a reading. For each one:
- what we did;
- the other reading;
- whether the choice moves any project to a different position;
- the source;
- what you need to decide.

**Where the files are.** Links go to the Planning Board's own copies online, to the cited page where one is given; local copies of every cited document are in `sources/planning_board/` (outside git). "p." means the PDF page, not the printed page number. The originals are in `data/raw/pb_resolutions/` and `data/raw/pb_archive_reports/`.

**Where things stand (Nov 4).** 205 report projects; 198 have a measured base (`06`). The building-size table (`08`) has 184 rows, because phases that share one plan are counted as one. Bonus available: 116 (46 below base, 17 at base, 21 between, 30 at 22%, 2 above 22%). Unclear: 3. All calls are decided except 3 and 12, which are for Evan. The Nov 4 cleanup (flags on the put-back projects, Montgomery Village Center dropped, four missing dates) is in NOTES.md; numbers in the decided calls below are as of their date.

## What I need from you

Answer these in any form ("2: keep as written, 4: like TDR, ..."). I'll recode, rerun, and update the notes. Details and sources for each are in the call of the same number below.

**Decisions that move projects**

| # | Decide | Options | Moves | Source |
|---|---|---|---|---|
| Call 2 | ~~Caps that already include the MPDUs~~ **Decided Nov 3: keep the caps as written** | Park Potomac 600, Cabin Branch 1,886 | none (both stay at base) | [82004015__item3_031804_opt.pdf](https://www.montgomeryplanningboard.org/meetings_archive/04_meeting_archive/agenda_031804/item3_031804_opt.pdf#page=15) pp. 15-16; [Cabin Branch 2008 staff report](https://www.montgomeryplanningboard.org/agenda/2008/documents/20080403_CabinBranch_print.pdf#page=11) p. 11; [MCPB 18-021](https://montgomeryplanningboard.org/wp-content/uploads/2018/05/Cabin-Branch-Multi-Family-Site-Plan-No.-820180060-MCPB-No.-18-021.pdf#page=9) pp. 9, 12 |
| Call 4 | ~~Density moved in from neighbouring lots~~ **Decided Nov 3: counts in the base, flagged** | The Monty and Flats at Knowles Station stay in | none (at 22% and +33%) | [monty_pp_2007.pdf](https://www.montgomeryplanningboard.org/agenda/2007/documents/20070531_Monty.pdf#page=33) p. 33; [MCPB 23-042](https://montgomeryplanningboard.org/wp-content/uploads/2025/08/Flats-at-Knowles-Station-Site-Plan-Amend-82021003A-MCPB-No-23-042-no-list.pdf#page=5) footnote 4 |
| Call 8 | ~~Strathmore Square~~ **Decided Nov 3: plan level** | whole plan, at 22% | none | [MCPB 22-032](https://montgomeryplanningboard.org/wp-content/uploads/2022/04/Strathmore-Square-Site-Plan-820220070-MCPB-NO-22-032-03172022.pdf#page=16) pp. 16-17 |
| Call 10 | ~~Buckingham Station~~ **Decided Nov 3: base 500, bonus available** | base 500, not the 610 cap | none (stays between, +20.5%); moves from unclear to bonus available | [82003003__item7_011603.pdf](https://www.montgomeryplanningboard.org/meetings_archive/03_meeting_archive/agenda_011603/item7_011603.pdf#page=16) p. 16 |
| Call 13 | ~~Knowles Manor~~ **Decided Nov 3: kept, lump at 15%, flagged LIHTC** | the 2014 CR rule explains the 44.5% | Knowles Manor back in (above 22%, lump group) | [MCPB 19-102](https://montgomeryplanningboard.org/wp-content/uploads/2019/07/Knowles-Manor-Site-Plan-No.-820190080-MCPB-No.-19-102-07112019.pdf) condition 1 |
| Call 14 | ~~Tregoning~~ **Decided Nov 3: kept, own schedule (RE-1 MPDU step)** | flat 1.22 du/ac step, no choice of share | Tregoning back in (+12.8%, own schedule) | [MCPB 24-091](https://montgomeryplanningboard.org/wp-content/uploads/2024/10/Tregoning-Property-Site-Plan-No.-820240080-MCPB-No-24-091.pdf#page=8) p. 8 |
| Call 23 | ~~Four bases nobody could check~~ **Decided Nov 3: keep all four, flagged** | `base_check` = unverified (3) or borrowed (White Oak) | none | no data table online |
| Call 11 | ~~PSTA's 0.5 FAR standard-method cap~~ **Decided Nov 3: keep 0.5 FAR** | the cap still stood in 2022 | none (634 base for 630) | [MCPB 22-037](https://montgomeryplanningboard.org/wp-content/uploads/2025/03/PSTA-820220050-MCPB-No-22-037-04072022.pdf#page=15) pp. 15-16 |

**Quick yes or no** (calls 1, 6, 7 decided Nov 3: keep as they are)
- ~~**Call 1:**~~ **Kept.** A plan maximum counts as the base only if it is zoning or a plan limit, not just the developer's request. Nothing moves.
- ~~**Call 5:**~~ **Decided Nov 3: kept, flagged** (`other_program`). The 19 projects that went over base through other programs are back in; Knowles Manor was already back (call 13).
- ~~**Call 6:**~~ **Kept.** Traffic (APF) limits are not caps.
- ~~**Call 7:**~~ **Kept.** Old-code R zones: "maximum with MPDUs" ÷ 1.22.

**For Evan, not you**
- **Call 3:** the TDR rule (you chose it "for now"). The other reading drops 3 projects and moves Clarksburg Village to 22%.
- **Call 12:** Olney Estates coded at 15%. At 14.3% it is dropped.

**Spot-check if you have time:** the 13 duplicate rows in [project_fixes.csv](../data/raw/mpdu_annual_reports/project_fixes.csv) (call 9). Only Clarksburg Town Center changes anything (at base → 15% below).

**New, from the subsidy check (Nov 3)**
- **Call 25:** most projects at exactly 25% MPDUs chose it for the county's development impact tax exemption (County Code Ch. 52, Sec. 52-41(g)(5) and 52-54(c)(5): the whole project is exempt at 25% MPDUs or more), not for the density bonus. Staff reports say so for Dowden's Station, Century, Axiom at Cabin Branch and Bloom Montgomery Village, and Bradford's Landing cites "development tax relief". It is a second notch at 25%. **Decided Nov 3 (Jacob): flag them** (`impact_tax`: stated 5, likely 2). See section E.

**New, from the zone rules (Nov 3)**
- ~~**Call 26:**~~ **Decided Nov 3 (Jacob): The Crescent stays ceiling at base** (CBD-2, heard Oct 2004, before the Council adopted the CBD bonus language). See section F.

**Next (no input needed):** version 1 of the dataset and the descriptives.

## Summary

| # | Call | Projects | Moves a project? |
|---|---|---|---|
| 1 | Is a plan's approved maximum the base? (one rule; decided: keep) | 5 checked | No |
| 2 | A cap that includes MPDUs is still the base (decided: keep) | 24 rows in `08` | No |
| 3 | TDR zones: base = the zone's maximum TDR density | 5 | **Yes** |
| 4 | Density moved from neighbouring lots counts in the base (decided: keep, flag) | 2 | No |
| 5 | Projects over base through other programs (decided: keep, flagged) | 19 | Back in, own groups |
| 6 | Traffic (APF) limits are not caps (decided: keep) | 1 known | No |
| 7 | Old-code R zones: "maximum with MPDUs" ÷ 1.22 (decided: keep) | about 20 | No |
| 8 | Phases of one plan share the plan's ratio (decided: plan level) | 6 plans | No (Northpark fixed) |
| 9 | Duplicate listings counted once | 13 rows | Small |
| 10 | Buckingham Station (decided: base 500, bonus available) | 1 | No |
| 13 | Knowles Manor (decided: kept in the lump group, flagged LIHTC) | 1 | Back in |
| 14 | Tregoning (decided: kept, own schedule) | 1 | Back in |
| 11 | PSTA (decided: 0.5 FAR cap) | 1 | No |
| 12 | Single project that moves: Olney Estates (for Evan) | 1 | **Yes** |
| 15-22 | Single projects that stay put either way | 1 each | No |
| 23 | Four bases nobody could check (decided: keep, flagged) | 4 | No |
| 25 | The 25% impact-tax notch (decided: flagged) | 7 | No |
| 26 | The Crescent: CBD before Ord. 15-35 (decided: ceiling at base) | 1 | Group only |

---

## A. Rules that touch several projects

### 1. Is a plan's approved maximum the base? **(Checked Nov 3: one rule, no project moves; decided: keep)**
- **The issue.** Sketch plans, project plans and preliminary plans often approve "up to X square feet" or "up to N units", below what the zone allows. If that limit is just what the developer asked for, it is not a cap: the developer could have had more by asking. Our traffic rule (call 6) already works this way.
- **The rule.** A limit is the base only if it is the site's zoning: the mapped zone, a Council development plan (G-number, DPA) or its binding elements, a master or sector plan limit, or a Planning Board cut below the request with a stated reason. A Board "up to X" that equals the developer's own proposal is not a cap. Public-benefit points don't limit density either: the CR optional method needs at least 100 points whatever density is asked for (8787 Georgia sketch plan condition 3; MHP-Nebel 82022015A staff report).
- **The five plans, read against their own sketch, project and sector plans:**
  - **The Blairs: a cap, stays at base.** The 2000 Silver Spring CBD Sector Plan (p. 69) "sets a cap of 2,800 dwelling units under the optional method", quoted in the 2013 Project Plan staff report (p. 19), and the rezoning was tied to a ZTA holding that cap. The site plan's 507 units are the first phase of the 2,800.
  - **Black Hill: the 1,229 units are not a cap, but it stays at base.** In 2016 the applicant asked to cut the 2012 plan's 1,618 units to 1,227 (staff report p. 7, note 1), so the unit count is its own choice. The real limit is 0.7 FAR for the whole site: the 2009 Germantown Employment Area Sector Plan (p. 63) allows the Lerner property up to 1.5 million sf of employment space plus a hotel and retail, "provided the total density for the site does not exceed 0.7 FAR". (The staff report's "40% of the 0.7 FAR" line is the plan's rule for the next site, NE-1, not this one.) The 1,851,560 sf of residential (0.39 FAR) is all that is left under 0.7 FAR after the 1,432,440 sf of commercial (0.31), so with the project's own unit size the base is 1,229 and Black Hill is at base. That is the same "total less commercial" test we use in the CR zones. The base in units depends on unit size: the 2012 plan fit 1,618 smaller units into the same floor area.
  - **8787 Georgia: not a cap, stays 30% below base.** Sketch Plan 320170060 staff report: "The Sketch Plan application (Project) proposes to redevelop the Property with up to 413,821 total square feet" (p. 4), and staff's alternative design "maintains the same density as that proposed by the Applicant" (p. 7). The Board approved the request as it stood, and nothing in the Sector Plan limits the site's units. Zoning allows 591,032 sf of residential (R-2.75 on the 4.93-acre tract).
  - **AVA Wheaton: not a cap, stays 49% below base.** Sketch Plan 320140020 staff report: "The Project proposes to develop up to approximately 460,492 square feet of residential development" (p. 8), and "the proposed density and height are within the envelope established by the Sector Plan" (p. 18). The sector plan only recommends rezoning to CR-4.0 R-3.5 H-100 (sector plan p. 50, quoted on p. 17). The 50-foot height limit is binding too, but the applicant asked for it (a 4- to 5-story building on an H-100 zone).
  - **MHP-Nebel: not a cap, stays 36% below base.** Sketch Plan 320210110 staff report: "The Applicant proposes to develop the North Parcel ... into a multi-family building of up to 188,500 square feet" (p. 6) at 1.63 FAR and 80 feet, on a zone allowing 271,332 sf of residential and 200 feet.
- **What the documents do not rule out.** These limits are legal, not physical. 8787 Georgia would need about 4.2 FAR on its 3.24-acre lot to reach 591,032 sf under the zone's 90-foot height and the step-backs required next to Woodside Park. Most of MHP-Nebel's lot is stream valley buffer (1.9 of 2.66 acres). Both may have been unable to build their full base. "Below base" means below what zoning allowed, not below what the site could hold. That is the same measure we use for every other project.
- **No conflict:** Pike & Rose, Grandview and Northpark. Their plan maximum equals the zone's mapped density, so both readings give the same base. (Northpark's 2025 limit of 279 units is what was applied for, so it is not a cap; see NOTES.)
- **Sources** (`sources/planning_board/` holds the four downloaded documents):
  - Blairs: MCPB 14-108 ([820140170__14-108_..._theblairs.pdf](https://montgomeryplanningboard.org/resolutions_archive/documents/14-108_20141113_11132014_820140170_theblairs.pdf#page=15)), p. 15; Project Plan 920130050 staff report, Oct 24 2013 ([project_plan_920130050_blairs_staff_2013.pdf](https://www.montgomeryplanningboard.org/agenda/2013/documents/20131024TheBlairsReport_FINAL.pdf#page=19)), p. 19.
  - Black Hill: MCPB 16-024 ([820150060__BlackHillSitePlanNo.820150060MCPBNo.16-02603102016.pdf](https://montgomeryplanningboard.org/resolutions_archive/documents/BlackHillSitePlanNo.820150060MCPBNo.16-02603102016.pdf)), data table; staff report [82015006__BlackHill3_10_16.pdf](https://www.montgomeryplanningboard.org/agenda/2016/documents/BlackHill3_10_16.pdf), pp. 7, 12, 32-34; sector plan [germantown_sector_plan_2009_pp62-63.pdf](https://www.montgomeryplanning.org/community/germantown/documents/GermantownMasterPlanApprovedandAdopted_web.pdf#page=63).
  - 8787 Georgia: MCPB 18-112 ([820180100__8787-Georgia-Avenue-...18-112.pdf](https://montgomeryplanningboard.org/wp-content/uploads/2018/11/8787-Georgia-Avenue-Site-Plan-No.-820180100-MCPB-No.-18-112.pdf#page=10)), p. 10; sketch plan staff report [82018010__8787-Georgia-Avenue-Sketch-Plan-No-320170060.pdf](https://montgomeryplanningboard.org/wp-content/uploads/2017/07/8787-Georgia-Avenue-Sketch-Plan-No-320170060.pdf).
  - AVA Wheaton: MCPB 14-114 ([820140190__14-114_..._avawheaton.pdf](https://montgomeryplanningboard.org/resolutions_archive/documents/14-114_2014121-04_12042014_820140190_avawheaton.pdf#page=12)), p. 12; [sketch_320140020_ava_wheaton_staff.pdf](https://www.montgomeryplanningboard.org/agenda/2014/documents/revisedFINALStaffReport_320140020_AVAWheaton.pdf).
  - MHP-Nebel: MCPB 22-075 corrected ([820220150__MHP-Nebel-Street-CORRECTED-...22-075.pdf](https://montgomeryplanningboard.org/wp-content/uploads/2022/10/MHP-Nebel-Street-CORRECTED-Site-Plan-No-820220150-MCPB-No-22-075.pdf#page=11)), p. 11; [sketch_320210110_mhp_nebel_staff.pdf](https://montgomeryplanningboard.org/wp-content/uploads/2021/07/320210110-MHP-Nebel-Street-FINAL-V2.pdf#page=6).
- **What to decide:** Whether you agree with the rule. With it, all five stay where they were.

### 2. A cap that already includes the MPDUs is still the base
- **What we did.** Where a development plan or master plan caps total units "including MPDUs", we used the cap as the base. 24 rows in `08` are in this group, for example Cabin Branch, Gallery Park, Park Potomac and Rock Creek Overlook.
- **The other reading.** Part of such a cap may itself be the MPDU bonus:
  - **Park Potomac** (Townhomes and The Perry): the Potomac master plan's 600 units for both site plans (450 multifamily on 8-04015 + 150 townhouses on 8-04012) = 423 base (8 du/ac x 52.9 ac) + 102 TDR units (51 TDRs) + 75 MPDUs. The order on paper: Preliminary Plan 1-03029 (2003) approved the 600 total; MPDUs are 12.5% of that total (75); the TDR units are what is left above base (600 - 423 - 75), and the TDRs are verified only before plats are recorded (staff report pp. 4, 10, 13). So the 75 MPDUs are the required minimum inside the cap, not a bonus on top. Using 525 as the base moves both from **at base to +14% (between)**, but that would be a 14% bonus at exactly 12.5% MPDUs plan-wide (61 + 14 of 600), where the old schedule gives none. **Decided Nov 3 (Jacob): keep 600, at base.** Source: 2004 staff report [82004015__item3_031804_opt.pdf](https://www.montgomeryplanningboard.org/meetings_archive/04_meeting_archive/agenda_031804/item3_031804_opt.pdf#page=15), data table pp. 15-16.
  - **Cabin Branch** (6 phases, one row): the master plan "specifies 1,886 for the Cabin Branch Property", a maximum "including all MPDU's" ([12003110B staff report, 2008](https://www.montgomeryplanningboard.org/agenda/2008/documents/20080403_CabinBranch_print.pdf#page=11), p. 11), and the preliminary plan is limited to 1,886. Development Plan G-806 splits it as 1,676 market + 210 MPDUs only to count TDRs: the MPDUs "are deducted from providing TDRs" ([MCPB 18-021](https://montgomeryplanningboard.org/wp-content/uploads/2018/05/Cabin-Branch-Multi-Family-Site-Plan-No.-820180060-MCPB-No.-18-021.pdf#page=9), p. 9), and "site plans approving more than 12.5% MPDUs can deduct the excess MPDUs from their pro-rata share of TDRs" (p. 12): extra MPDUs cut the TDR bill, they add no units. 12003110B then set the MPDUs at 12.5% of the full 1,886 (236), inside the cap. Using 1,676 would move it from **at base to +12.5% (between)**. **Decided Nov 3 (Jacob): keep 1,886, at base.** Also cited in the coding note on [82006029A__11-125_..._cabinbranchcommunity.pdf](https://montgomeryplanningboard.org/resolutions_archive/documents/11-125_20111201_06282012_82006029A_correctedwinchesterphaseIcabinbranchcommunity.pdf).
  - **Gallery Park:** Development Plan G-824 allows 290 incl 40 MPDUs, while the PD-11 standard is 262. It is **12% below base** with 290 and **2% below base** with 262, so it doesn't move. Source: [82005038__20070208_Eastside.pdf](https://www.montgomeryplanningboard.org/agenda/2007/documents/20070208_Eastside.pdf#page=15), Tables 1-2, pp. 15-16.
- **Decided Nov 3 (Jacob):** keep caps as written. In both documented cases the MPDU part is the required minimum inside the cap, and the split exists only to count TDRs.

### 3. TDR zones: the base is the zone's maximum TDR density (you chose this "for now")
- **What we did.** In TDR zones, the base is the most units the zone allows with TDRs (designation × acres), before the MPDU bonus.
- **The other reading:** base = base density + the TDRs actually bought. Under that reading:
  - Meadows at Hurley Ridge, Eton Square and Linthicum West go over base and get **dropped** (now 5%, 6% and 23% below base).
  - Clarksburg Village moves from **+17.6% (between) to +22% (at 22%)**.
  - Manor Oaks doesn't change.
- **Sources:**
  - Meadows: [82003010__item3_050103.pdf](https://www.montgomeryplanningboard.org/meetings_archive/03_meeting_archive/agenda_050103/item3_050103.pdf) p. 22.
  - Eton: [82004033__ITEM13A-072204_opt.pdf](https://www.montgomeryplanningboard.org/meetings_archive/04_meeting_archive/agenda_072204/ITEM13A-072204_opt.pdf#page=5) p. 5 (site constraints).
  - Linthicum: [MCPB 22-026](https://montgomeryplanningboard.org/wp-content/uploads/2022/03/Linthicum-West-Site-Plan-No.-820210010-MCPB-No.-22-026-03032022.pdf), pp. 13-14 (the Board allowed fewer TDRs).
  - Clarksburg Village: [82005041__20090205_clarksburg_village_phase_II.pdf](https://montgomeryplanningboard.org/agenda/2009/documents/20090205_clarksburg_village_phase_II.pdf#page=80) p. 80.
  - The law: old code Sec. 59-C-1.395, quoted in [Linthicum](https://montgomeryplanningboard.org/wp-content/uploads/2022/03/Linthicum-West-Site-Plan-No.-820210010-MCPB-No.-22-026-03032022.pdf) p. 13.
- **TDR flag (Nov 3).** Every project now carries `tdr` (used / available, not used / none) in `06` and `08`, from `project_tdr.csv`: 21 used TDRs, 2 sat in TDR zones but built without them. TDR projects can buy density without MPDUs, so the analysis can drop them or look at them separately. Details in [NOTES.md](NOTES.md).
- **What to decide:** Confirm with Evan.

### 4. Density moved in from neighbouring lots counts as base
- **What we did.** Two projects bought floor area from nearby lots before applying the MPDU bonus. We counted it as part of the base, the same way as TDRs.
  - **Bainbridge Bethesda (The Monty):** 165,974 sf base incl the transferred area, + 22% bonus = 202,488 sf. It sits **at 22%**. Source: [monty_pp_2007.pdf](https://www.montgomeryplanningboard.org/agenda/2007/documents/20070531_Monty.pdf#page=33) (Project Plan staff report, 2007), p. 33.
  - **Flats at Knowles Station:** 25,263 sf own + 33,666 sf transferred + 19,338 sf MPDU bonus. It sits at **+33% (above 22%**, which the post-2018 schedule allows at 25% MPDUs). Source: MCPB 23-042 ([82021003A__Flats-at-Knowles-Station-...23-042.pdf](https://montgomeryplanningboard.org/wp-content/uploads/2025/08/Flats-at-Knowles-Station-Site-Plan-Amend-82021003A-MCPB-No-23-042-no-list.pdf#page=5)), data table footnote 4.
- **The other reading:** leave the transfer out of the base. Both would then be far over base and **dropped**. Without the transfer, Flats' base is 27 units against 84 built.
- **Decided Nov 3 (Jacob):** count the transfer in the base, as the county did (both documents apply the MPDU bonus to base + transfer), and flag both projects `tdr = density transfer` in `project_tdr.csv`. The Monty's unit count changed with smaller units in the same floor area (106 in a March 2007 draft, 133 in the 2007 project plan, 200 in the 2009 site plan, MCPB 09-077, max 210,188 sf); the 22% bonus is in floor area, so its base is 200 / 1.22 = 164.

### 5. Projects over base through a non-MPDU program (decided: kept, flagged)
- **What we did.** We dropped projects whose units above base came from something other than the MPDU bonus: 19 projects.
  - **Bethesda Overlay Zone (7):** 7340 Wisconsin, St. Elmo, 8015 and 7607 Old Georgetown, 4909 Auburn, The Edge, Metro Tower.
  - **Workforce housing (7):** Westside at Shady Grove (6 rows) and Elizabeth House III.
  - **A master plan or PD-zone bonus (3):** Preserve at Rock Creek (2) and Jefferson at Inigo's Crossing.
  - **The ZTA 21-07 exemption for income-restricted housing (1):** Sligo Apartments (listed in the report as "Hillandale Gateway"; round 1 found the two names are swapped).
  - **A bonus above the schedule (1):** Knowles Manor (call 13).
- **Sources:** each project's note in [NOTES.md](NOTES.md), rounds 1-5.
- **Decided Nov 3 (Jacob): keep them, flagged.** `06` puts the 18 back (`OTHER_PROGRAM`; Knowles Manor was already back under call 13) with column `other_program`. Their position mixes the MPDU bonus with the other program, so it is not the MPDU bonus alone; none of them is in the bonus-available group:
  - **Bethesda Overlay (7)** go to "own schedule" with the two Bethesda projects already there: The Edge, Metro Tower, 7607 and 8015 Old Georgetown Road, St. Elmo, 4909 Auburn Avenue, 4725 Cheltenham Drive (the 2023 report's "7340 Wisconsin Avenue"). All above 22% (+64% to +185%).
  - **New group "other program" (5 rows):** Shady Grove Station-Westside (6 report rows summed at plan level, workforce housing, +31%), Elizabeth House III (workforce housing, +32%), Preserve at Rock Creek (2 rows summed, master plan bonus, +100%), Jefferson at Inigo's Crossing (PD zone bonus, +13%, between), Sligo Apartments (ZTA 21-07, a 100% income-restricted LIHTC building, base 12 for 98).
  - Westside's and Preserve's report rows share one plan ratio, so summing them leaves their position unchanged even if two Westside rows overlap.
  - Also filled: names for 11 projects the 2025 report lists without one (from their resolutions). Result: 199 projects in `06`, 185 rows in `08`; bonus available unchanged (41 / 17 / 16 / 27 / 2).

### 6. Traffic (APF) limits are not caps
- **What we did.** Nearly every preliminary plan says "limited to N units" for traffic. That is normally the number applied for, so we don't count it as a cap unless a document shows the Board set it below the request.
- **Effect.** If APF limits did count, Meadows at Hurley Ridge (APF limit 326, 325 built) would move from 5% below base to at base. Wootton Crossing is at base either way.
- **Source:** Meadows preliminary plan condition, in [82003010__item3_050103.pdf](https://www.montgomeryplanningboard.org/meetings_archive/03_meeting_archive/agenda_050103/item3_050103.pdf).
- **Decided Nov 3 (Jacob): keep.** APF limits are not caps unless a document shows the Board set one below the request.

### 7. Old-code R zones: "maximum with MPDUs" ÷ 1.22 = base
- **What we did.** Before Oct 2014, R zones listed a maximum density "with MPDUs" equal to the standard density × 1.22. Where a document gave only that maximum, we divided by 1.22. For example, Poplar Run: 773 ÷ 1.22 ≈ 634, which matches 2.0 × 297.56 ac + 3.6 × 10.80 ac.
- **Projects:** about 20 coded rows, including Poplar Run, Whitehall Square, Grosvenor Place, Hallman Grove, Chelsea Heights, Tanglewood and Clarksburg Village.
- **Two stretches:**
  - **Woodlake** (an RH zone, not an R zone; done by analogy). It is **29% below base**, or 42% below without the ÷1.22, so it doesn't move. Source: [8-71011A__item2b_050505_opt.pdf](https://www.montgomeryplanningboard.org/meetings_archive/05_meeting_archive/agenda_050505/item2b_050505_opt.pdf#page=3) p. 3.
  - **Bloom's** TLD zone: we read its 9.76 du/ac as 8.0 × 1.22. No Bloom document says so. It is **59% below base**, or 65% below without the ÷1.22, so it doesn't move. Source: [82017013D resolution](https://montgomeryplanningboard.org/wp-content/uploads/2025/03/Bloom-MV-I-IV-Site-Plan-82017013D-MCPB-22-041.pdf#page=5) resolution table p. 5 and the coding note on [820170130__Bloom-...17-111.pdf](https://montgomeryplanningboard.org/wp-content/uploads/2017/12/Bloom-Montgomery-Village-Site-Plan-No.820170130-MCPB-No.-17-111.pdf).
- **Decided Nov 3 (Jacob): keep.** Old-code "maximum with MPDUs" ÷ 1.22, including the Woodlake and Bloom stretches (neither moves).

### 8. Phases of one plan share the plan's ratio
- **What we did.** Where density and MPDUs are set for a whole plan, every phase gets the plan's base ratio, and `08` sums the phases into one row:
  - Cabin Branch.
  - Clarksburg Village: 2,653 units against a base of 2,255, **+17.6%**.
  - Pike & Rose and Chevy Chase Lake: **at base** and **+10.5%**.
  - Strathmore Square and Grandview are also coded at plan level.
- **Where it moves something:**
  - **Strathmore Square:** the plan as a whole is **at 22%**. Phase 1 (the only phase in the reports, 220 units) sits entirely inside mapped density; the bonus floor area is listed as "available for future phases". Phase by itself it would be **at or below base**. Source: MCPB 22-032 ([820220070__Strathmore-Square-...22-032...pdf](https://montgomeryplanningboard.org/wp-content/uploads/2022/04/Strathmore-Square-Site-Plan-820220070-MCPB-NO-22-032-03172022.pdf#page=16)), data table pp. 16-17, and Preliminary Plan [MCPB 19-065](https://montgomeryplanningboard.org/wp-content/uploads/2019/07/Strathmore-Square-Preliminary-Plan-No.-120190180-MCPB-No.-19-065.pdf), condition 2.b.
  - **Northpark at Montrose (fixed Nov 3).** It was coded at base on the 2020 plan (745 units on the full mapped density). In 2025 the plan was cut to 279 units on 625,594 sf, while mapped density stayed at 1,030,662 sf. Density is set for the whole site; Phase I has no share of its own. Recoded to the plan as it stands now: base = 279 × 1,030,662 / 625,594 = 460 for 279. Phase I (141 units, the only phase in the reports) moves from **at base to 39% below base**. Sources:
    - Preliminary Plan 12020014A, MCPB 25-144 ([82021008__Wilgus-II-Northpark-Preliminary-Plan-No.-12020014A-MCPB-No.-25-144.pdf](https://montgomeryplanningboard.org/wp-content/uploads/2026/02/Wilgus-II-Northpark-Preliminary-Plan-No.-12020014A-MCPB-No.-25-144.pdf)), condition 1.
    - Sketch Plan 32019007A, MCPB 25-025 ([82021008__Wilgus-II-at-Northpark-Sketch-Plan-No.-32019007A-MCPB-No.-25-025.pdf](https://montgomeryplanningboard.org/wp-content/uploads/2025/04/Wilgus-II-at-Northpark-Sketch-Plan-No.-32019007A-MCPB-No.-25-025.pdf)), the mapped-density table.
    - Phase I staff report Table 1 ([82021008__6_17_StaffReport_NorthparkatMontrosePhaseI_SitePlan820210080_FINAL-Copy.pdf](https://montgomeryplanningboard.org/wp-content/uploads/2021/06/6_17_StaffReport_NorthparkatMontrosePhaseI_SitePlan820210080_FINAL-Copy.pdf)), p. 27.
- **Decided Nov 3 (Jacob): plan level.** The 15% MPDU share and the 22% bonus were set for the whole 2,218-unit plan ([MCPB 19-065](https://montgomeryplanningboard.org/wp-content/uploads/2019/07/Strathmore-Square-Preliminary-Plan-No.-120190180-MCPB-No.-19-065.pdf), condition 3), and the bonus is earned on building the plan's mapped density (MCPB 22-032 p. 17, fn 6), so Phase 1 shares the plan's ratio and sits at 22%. **No real choice:** Strathmore is in North Bethesda, a high-income planning area, so 15% MPDUs was the minimum, and the 22% bonus comes with 15% (its data table lists both). Its "at 22%" is the requirement, not a response to the kink. Kept for now, with `min_share` = 0.15 in `08`; a later sample of real choices would drop it and the other 15%-minimum projects (9 in bonus available, 2 in own schedule). Caveat: about 90% of the plan (1,998 units) is unbuilt, so its position is the approved plan's. When a plan is cut after a phase is approved, we recode to the plan as it then stands (as for Northpark in 2025, and Clarksburg Village and Cabin Branch).

### 9. Duplicate listings counted once
- **What we did.** We counted 13 repeated rows once (full list in [project_fixes.csv](../data/raw/mpdu_annual_reports/project_fixes.csv), with a note on each). When two rows were the same units, we kept the one that matches the approval.
- **The one that changes something.** The dropped 2005 Clarksburg Town Center row was **at base** under the original 1998 plan. The kept row (1,206 units under the 2009 re-approval) is **15% below base**. Source: MCPB 09-015 ([820070220__09-015_..._clarksburgtowncenter.pdf](https://www.montgomeryplanningboard.org/resolutions_archive/documents/09-015_20081211_07092009_820070220_clarksburgtowncenter.pdf)): "1,213 residential dwelling units, including 152 MPDUs" for the whole town center.
- **What to decide:** Spot-check the list.

---

## B. Single projects where the call moves the project

### 10. Buckingham Station: base 500 or 610?
- **What we did.** The Germantown Master Plan's 500 units is the base, so the project is at **+20.5% (between)**.
- **Other reading:** the preliminary plan cap of 610 (= 500 × 1.22) as the base puts it **1% below base**.
- **Source:** [82003003__item7_011603.pdf](https://www.montgomeryplanningboard.org/meetings_archive/03_meeting_archive/agenda_011603/item7_011603.pdf#page=16) p. 16, and the [8-03003A staff report (2005)](https://www.montgomeryplanningboard.org/meetings_archive/05_meeting_archive/agenda_031705/item10_031705_opt.pdf) data table ("NTE 22% of MP guide").
- **Decided Nov 3 (Jacob): base 500, and the bonus counts as available.** The 610 cap is the master plan's 500 plus the 22% bonus, so it is not the base. Buckingham was "unclear" only because `08` has no general rule for RMX zones; its staff report states the bonus outright (p. 16: "optional method of development for the R-MX zone to increase density by 91 MPDUs"; p. 17: "Residential - MPDU NTE 22% of MP guide"). `08` now codes it "RMX bonus" (the RMX zone rule of section F; `RMX_BONUS` keeps its note), so it moves from unclear to **bonus available** and stays **between** (200 units on a base of 166, +20.5%, with 15% MPDUs). The other RMX projects stay unclear until their documents are read.

### 11. PSTA: does the 0.5 FAR standard-method cap apply?
- **What we did.** The project used the standard method in a CR zone. The 2014 code caps the standard method at "the greater of 0.5 FAR or 10,000 SF", and the approved 0.497 FAR sits just under that. So it is **at base**.
- **Other reading:** the mapped 1.0 FAR gives **50% below base**.
- **Sources:** MCPB 22-037 ([820220050__PSTA-820220050-MCPB-No-22-037-04072022.pdf](https://montgomeryplanningboard.org/wp-content/uploads/2025/03/PSTA-820220050-MCPB-No-22-037-04072022.pdf#page=15)), Table 1, pp. 15-16; 2014 code [Sec. 4.5.3](https://codelibrary.amlegal.com/codes/montgomerycounty/latest/montgomeryco_md_zone2014/0-0-0-3068) table (current version online). I did not check the 2021 version of the code.
- **Checked and decided Nov 3 (Jacob): keep the 0.5 FAR cap.** Planning staff's August 2022 report on ZTA 22-08 quotes the code then in force: "CR Density, FAR: The lesser of: mapped FAR or the greater of 10,000 SF or 0.5 FAR", and adds that "a CR zoned project would be an optional method project before Section 4.5.2.C kicks in because all CR zones are mapped at or above the allowed maximum FAR for standard method development" ([staff report](https://montgomeryplanningboard.org/wp-content/uploads/2022/08/ZTA-22-08-Commercial-Residential-Zones-MPDU_9-1-22_Final.pdf) pp. 1-3; local copy in `sources/planning_board/`). The county's list of zoning text amendments has no change to CR standard-method density between 2014 and 2022. The Board's "up to 2,096,488 sf" (p. 16) is the mapped FAR, reachable only by the optional method. PSTA stays at base 634 for 630 (0.6% under), and is flagged public land (30% MPDUs set by the county's land sale).

### 12. Olney Estates: coded at 15% MPDUs (your call)
- **What we did.** The project built 6 MPDUs of 42 units (14.3%). The bonus was calculated on 15%, and the applicant then converted one MPDU into a market unit under the small-project rule. We coded 15%, so it stays **at 22%**.
- **Other reading:** code 14.3%; then it fails the check and is **dropped**.
- **Source:** [82006019__Item_7_A_07-20-06_opt.pdf](https://www.montgomeryplanningboard.org/meetings_archive/06_meeting_archive/agenda_072006/Item_7_A_07-20-06_opt.pdf#page=8) pp. 8-11.
- **Decide:** Confirm with Evan.

### 13. Knowles Manor: dropped for a 44.5% bonus
- **The project.** Base 69,195 sf + 30,805 sf "MPDU bonus density" = 100,000 sf, with 30% MPDUs. That is a 44.5% bonus, while the post-2018 schedule gives about 40% at 30% MPDUs. The 30,805 sf equals the MPDUs' own floor area, so this may be a "MPDU floor area doesn't count" provision rather than the bonus schedule. Dropped because it fails the check.
- **Other reading:** keep it at **+44.5% (above 22%)**.
- **Source:** MCPB 19-102 ([820190080__Knowles-Manor-...19-102...pdf](https://montgomeryplanningboard.org/wp-content/uploads/2019/07/Knowles-Manor-Site-Plan-No.-820190080-MCPB-No.-19-102-07112019.pdf)), condition 1.
- **Found (Nov 3): the 2014 CR rule, not the ZTA schedule.** The sketch plan (320180210, accepted 13 Jun 2018) set the density before ZTA 18-06: condition 1 allows "up to 30,805 square feet of MPDUs ... which is exempt from the calculation of FAR pursuant to Section 59.4.7.3.D.6.c.iii", and its data table lists "Exempted MPDUs 30,805 sq. ft." ([sketch plan staff report](https://montgomeryplanningboard.org/wp-content/uploads/2018/09/320180210-Kensington-Manor-Staff-Report-FINAL.pdf)). With 15% MPDUs or more, all MPDU floor area is exempt, so the bonus is the MPDUs' own floor area: 30,805 / 69,195 = 44.5%. The 2019 site plan restated it in ZTA 18-06 terms; "The density limitation remains the same" (MCPB 19-102 p. 7). `04` checks every base against the ZTA schedule (40% at 30% MPDUs), so it dropped the project.
- **Not a market project.** All 94 units are income-restricted senior housing (10 at 30% AMI, 69 at 60%, 15 at 80%), financed with LIHTC equity, an $8.9m county Housing Initiative Fund loan, and State CDA and HUD 221(d)(4) loans; 29 of them are counted as MPDUs ([county press release, 8 Apr 2022](https://www.montgomerycountymd.gov/news/montgomery-county-supports-affordable-housing-seniors-silver-creek-senior-living-apartments)). Its 30% is not a response to the bonus.
- **Decided Nov 3 (Jacob): keep, with a flag.** `06` puts it back with its hand-coded base (`CR_EXEMPT`; base 65 for 94), `08` codes it "CR lump at 15%" (`CR_LUMP`), so it sits in the lump group at **+44.6% (above 22%)**. New column `subsidy` = LIHTC, from the hand-made `project_subsidy.csv`; a later sample of real choices would drop it. Other high-share projects (MHP-Nebel, Silver Spring Library, Sligo Apartments, 4010 Randolph Road) have not yet been checked for subsidy.

### 14. Tregoning: own schedule (decided: kept)
- **The project.** RE-1 zone under the 2014 code. The MPDU option there is a flat step (1.09 → 1.22 du/ac) for any MPDU share above 12.5%, not the sliding schedule. It has 13% MPDUs and is 11.5% over its base of 41.26, so it fails the check.
- **Other reading:** keep it at **+11.5% (between)**.
- **Source:** MCPB 24-091 ([820240080__Tregoning-Property-...24-091-1.pdf](https://montgomeryplanningboard.org/wp-content/uploads/2024/10/Tregoning-Property-Site-Plan-No.-820240080-MCPB-No-24-091.pdf#page=8)), p. 8.
- **Decided Nov 3 (Jacob): keep, flagged as its own schedule.** The RE-1 MPDU optional method gives a flat 1.22 du/ac for any MPDUs; Tregoning has the minimum 6 (12.5% of 46, rounded up; the data table lists 6 as both required and approved). Against the standard method's 41 units it gets 5 more units for about 1 more MPDU, so it made no choice of share. `06` puts it back with its hand-coded base (`OTHER_RULE`), `08` codes it "RE-1 MPDU step" (`RE1_STEP`) in the **own schedule** group, with the Bethesda Overlay projects. The report lists 44 built (the other 2 of the 46 are development rights kept on the remaining land), so on the report's units it is base 39 for 44, **+12.8% (between)**.

---

## C. Single projects where the call doesn't move anything

Each of these is a real choice, but both readings leave the project in the same position.

| # | Project | What we did | Other reading | Source |
|---|---|---|---|---|
| 15 | AVA Wheaton | mapped floor area: 49% below base | sketch plan cap: 24% below | [MCPB 14-114](https://montgomeryplanningboard.org/resolutions_archive/documents/14-114_2014121-04_12042014_820140190_avawheaton.pdf#page=12) p. 12 (also in call 1) |
| 16 | MHP-Nebel | mapped floor area: 36% below | sketch plan: 8% below | [MCPB 22-075 corrected](https://montgomeryplanningboard.org/wp-content/uploads/2022/10/MHP-Nebel-Street-CORRECTED-Site-Plan-No-820220150-MCPB-No-22-075.pdf#page=11), p. 11 (call 1) |
| 17 | Gallery Park | cap 290: 12% below | PD-11 standard 262: 2% below | [82005038__20070208_Eastside.pdf](https://www.montgomeryplanningboard.org/agenda/2007/documents/20070208_Eastside.pdf#page=15) pp. 15-16 |
| 18 | Woodfield Commons | 1.0 FAR on the 8.82-ac gross tract the staff report uses: 69% below | on the 3.88-ac site: 30% below | staff report [82015009__PreliminaryandSitePlanFinalDraft...pdf](https://www.montgomeryplanningboard.org/agenda/2015/documents/PreliminaryandSitePlanFinalDraft120315_RAW_KRR12-4-15.pdf#page=16) pp. 16, 22 |
| 19 | Century | Phase I on its 57.6-ac site plan: 64% below | Phases I + I-C together: 50% below | [MCPB 19-078](https://montgomeryplanningboard.org/wp-content/uploads/2019/07/Century-Site-Plan-No.-82003007E-MCPB-No.-19-078.pdf) condition 14; [MCPB 23-092](https://montgomeryplanningboard.org/wp-content/uploads/2025/07/Century-Site-Plan-No-82003007F-MCPB-no-23-092.pdf#page=14) p. 14 |
| 20 | Aurora | 341 units (amendment A) against the 500 cap: 32% below | Audrey's 327: 35% below | [82008011__20080522_north_bethesda_print.pdf](https://www.montgomeryplanningboard.org/agenda/2008/documents/20080522_north_bethesda_print.pdf) data table; [MCPB 11-090](https://montgomeryplanningboard.org/resolutions_archive/documents/11-090_20110922_11102011_82008011A_northbethesdacenterparcelsFIJ.pdf) |
| 21 | Woodlake, Bloom | ÷1.22 (call 7) | no ÷1.22 | call 7 |
| 22 | Bentley Park | Development Plan binding element, 248 incl 31 MPDUs: at base | PD-2 standard 260.9: 5% below | [dpa_09-1_fairland.pdf](https://assets.montgomerycountymd.gov/files/dpa_09-1_fairland.pdf#page=20) p. 20 |

Bentley Park does move (at base → below base), but it follows call 2's rule directly, so it needs no separate decision.

---

## E. Subsidized projects and the 25% notch (checked Nov 3)

### Subsidy flag (done; no input needed)
- **What we checked.** Every project with 20% MPDUs or more, a nonprofit or HOC developer, a HUD LIHTC property within 100 m ([HUD LIHTC layer](https://services.arcgis.com/VTyQ9soqVukalItT/arcgis/rest/services/LIHTC/FeatureServer/0), placed in service through about 2019), or a county Housing Initiative Fund loan ([DHCA multifamily loans](https://data.montgomerycountymd.gov/d/n724-uy7d)). Local copies in `sources/subsidy/`.
- **Coded** in `project_subsidy.csv` (column `subsidy`, with `restricted_units` and a quote and source per row): LIHTC 16, LIHTC planned 1 (Tevis Place), LIHTC after completion 1 (The Argent: a market condo converted in 2010, so its MPDU share was the market developer's), HOC without tax credits 1 (The Lindley), public land 2 (PSTA, Olney Springs: the county set the share when it sold the land).
- **In `08`'s bonus-available group:** 13 of 103 were flagged on Nov 3 (10 LIHTC, 1 after completion, 2 public land). After the zone rules and the Nov 4 cleanup: 16 of 116 (12 LIHTC, 1 planned, 1 after completion, 2 public land). The Nov 4 cleanup also flagged Elizabeth House III (LIHTC) and the Laureate (HOC, no LIHTC), both put back under call 5 after this check.
- **Checked, nothing found:** Solaire Wheaton and The Citron (their county loan entries count only the MPDUs), The George and The Exchange (near HOC's MetroPointe, not it), Thayer & Spring (a neighbour of 900 Thayer).
- **Report labels fixed.** The 2023 report's agreements table (p. 11) pairs some plan numbers and counts with the next row's name: our "4725 Cheltenham Drive" is Park Montgomery and our "Sligo Apartments" is Hillandale Gateway. Counts and plan numbers agree with the resolutions, so only the names change (`NAME_FIXES` in `06`).

### 25. The 25% impact-tax notch
- **What it is.** At 25% MPDUs or more a project pays no development impact tax for transportation and schools (Ch. 52, Sec. 52-41(g)(5), 52-54(c)(5)). The quotes:
  - Dowden's Station amendment 82016006A ([staff report](http://montgomeryplanningboard.org/wp-content/uploads/2018/06/Dowdens-Station-82016006A-7_12_18.pdf) p. 1): "increases MPDUs onsite from 13.3% ... to 25% ... which will exempt the project from the payment of development impact taxes".
  - Century 82003007E ([staff report](https://montgomeryplanningboard.org/wp-content/uploads/2019/06/Century_82003007E.pdf) p. 1): the same words, from 12.5% to 25%.
  - Axiom at Cabin Branch (2018 staff report p. 14): "a minimum of 25% of the units as MPDUs allowing them to take advantage of Bill 36-17 which would exempt this development from impact taxes".
  - Bloom Montgomery Village (82017013C staff report pp. 1-2): approved "with 25% MPDUs to allow an exemption from impact taxes"; when its Opportunity Zone area became exempt anyway, the developer replaced 21 MPDUs with market units.
  - Bradford's Landing (MCPB 17-054 p. 11): "providing 25% of the units as MPDUs, which allows development tax relief and a 22% density bonus".
  - Likely but not stated: Ashford Woods, Reserve at Damascus (both exactly 25%).
- **Other high shares:** Flats at Knowles Station chose 25% for a 35% CR bonus and 150 points; Grosvenor Place has one MPDU above the minimum for the R-30 optional method; Millstone at Kingsview's 33% looks like the whole Kingsview subdivision's obligation put on one parcel (not confirmed).
- **Decided Nov 3 (Jacob): flag them, keep them all.** Column `impact_tax` in `06` and `08`, from the hand-made `project_impact_tax.csv` (quote per row): stated 5 (Dowden's Station, Century, Axiom at Cabin Branch, Bloom Montgomery Village, Bradford's Landing), likely 2 (Ashford Woods, Reserve at Damascus). In `08`: 6 in bonus available (3 below base, 2 between, 1 at 22%), Cabin Branch (via Axiom) at base, Bloom in the lump group. The exemption's start date is not pinned: Bill 8-15 (2015) proposed it for rentals of developments with 25% affordable units ([Council packet, 5 May 2015](https://assets.montgomerycountymd.gov/files/council/resources/files/bill/2015/packets/20150505_74.pdf)); the staff reports from 2017 on cite Sec. 52-41(g)(5) and 52-54(c)(5). So the flags rest on what each document says, not on a date rule.

## F. Zone rules for the 17 "unclear" projects (done Nov 3)

Before this, 17 projects had no rule for whether MPDUs could buy units above base. Now 14 have one. Only their `bonus_rule`, `group` and `note` changed.

| Projects | Rule now | Evidence |
|---|---|---|
| RNC before 2014: Batchellors Forest, Trotters Glen, Orchards of Sandy Spring, Olney Estates, Reserve at Fair Hill | bonus available (25A) | the resolutions state it: Batchellors "22 percent density bonus for providing 15 percent MPDUs" (MCPB 09-95); Trotters Glen "density bonus of 1.19 for providing 14.49 percent MPDUs" (MCPB 13-92) |
| RMX: Waterford Hills (and Buckingham, already in) | bonus available, new rule "RMX bonus" | old 59-C-10.3.7(c): master plan units "may be increased by a number equal to the number of moderately priced dwelling units", up to 22% (quoted in ZTA 06-15, `sources/law/0_zta_06-15_rmx_2c_tdr_2006.pdf` pp. 7-8) |
| Woodlake (RH) | bonus available | the data table's "Density Maximum Units (w/ MPDU's)" line (call 7) |
| Residences at Forest Glen | bonus available (ZTA 18-06) | accepted Sep 2020; the zone just wasn't parsed (CRTF) |
| Portico, Citron, The Veridian (CBD) | bonus available | heard after the Council adopted Ord. 15-35 (30 Nov 2004); Portico and Citron state the bonus |
| The Crescent (CBD) | ceiling at base (call 26) | heard 21 Oct 2004, before Ord. 15-35 |
| Clarksburg Town Center 820070220, Mt. Prospect | ceiling at base (plan cap) | Project Plan 9-94004, 1,300 du; MCPB 18-017 condition 12, "limited to 187 total dwelling units ... including 24 MPDUs" |
| Upstairs at Bethesda Row, The Rae (C-2), Montgomery Row (I-3) | still unclear | old C-2 residential text (59-C-4.35) not online; staff reports mention no bonus |

### 26. The Crescent: was the CBD bonus available before Ord. 15-35? **(Decided Nov 3: ceiling at base)**
- **The question.** Ord. 15-35 added the CBD and TS language "the maximum dwelling unit density or residential FAR may be increased in proportion to any MPDU density bonus provided on-site". Was a bonus available in a CBD before that?
- **Against.** The Council committee found in Nov 2004 that these zones "do not now have language that expressly allows the maximum residential density or residential FAR ... to be increased to accommodate the MPDU density bonus" ([Ord. 15-35](../sources/law/0_zta_04-12_ord_15-35_cbd_ts_mpdu_bonus_2005.pdf), preamble). The Crescent's staff report calls 5.0 FAR "the permitted maximum density for this site under the optional method".
- **For.** Portico got its 22% bonus on 31 Mar 2005, after adoption but the day before the ordinance took effect. So the Board granted the bonus once the Council had acted, and it isn't clear it was refused before.
- **Decided Nov 3 (Jacob): ceiling at base.** The Crescent (heard 21 Oct 2004, 12.5% MPDUs, at base) stays in the ceiling-at-base group, as coded. The other reading would have added one at-base project to bonus available (17 → 18). No other project depends on this.

## D. Gaps

### 23. Four bases nobody could check
These still use the parser's number because their documents don't include the data table:
- **Wentworth House:** 34% below base. The 500-units-per-parcel cap is stated only for the neighbouring parcels.
- **The Veridian:** 13% below base.
- **Heritage at Silver Spring:** 11% below base.
- **White Oak (Whitehall Square Phase 2):** it borrows Phase 1's ratio, so it is +22%. Its own amendment isn't online.

**Decided Nov 3 (Jacob): keep all four, flagged.** Column `base_check` in `06` and `08` (`BASE_UNVERIFIED` in `06`): unverified for Wentworth House, The Veridian and Heritage at Silver Spring; borrowed for White Oak (Phase 1's ratio, +22%). Every other base is "checked". No value changes.

### 24. Projects with no measured base (26), for reference
- **Dropped for non-MPDU density:** 18 (call 5).
- **Knowles Manor** (call 13) and **Tregoning** (call 14).
- **No document online (4):** Summerfield Crossing, Regency at Leisure World, Lionsgate, Meridian at Grosvenor.
- **Out of scope (2):** Hampden Lane (from permit records) and Heritage Gardens (no site plan).
- **Wildwood Manor** is also left out of the base tables: the report gives it Preston Place's plan number, and we don't have its own plan.

---

## If you only check five things
1. ~~**Call 1**~~ (plan maximums): decided Nov 3, keep the rule.
2. ~~**Call 2**~~ (caps that include MPDUs): decided Nov 3, keep the caps.
3. ~~**Call 4**~~ (density transfers): decided Nov 3, count and flag.
4. ~~**Call 8**~~ (Strathmore): decided Nov 3, plan level.
5. **Call 3** (the TDR rule) for Evan.
