# MPDU dataset, version 1: basic descriptives (Nov 4 2026, revised twice the same day; 850 Sligo Avenue moved and Whitehall Square grouped Nov 5)

Made by `09_descriptives.py` (run by `run_all.py` after `08`). Every number below is from its tables in `output/tables/descriptives_*.csv`, and the figures are `output/figures/descriptives.pdf`. No model and no filtering: the "choice" sample is shown for reference only.

## The samples

| Sample | What it is | Projects |
|---|---|---|
| report projects | every row of the annual reports, agreements and permits | 219 |
| | projects listed twice counted once (`project_fixes.csv`) | 206 |
| **all** | phases of one plan counted once; the MPDU-share sample (needs no base) | 189 (1 with unknown regime) |
| **base** | projects with a base read from a Planning Board resolution (`08`) | 181 |
| **bonus** | base projects whose rule let MPDUs buy units above base | 99 |
| **choice** | bonus projects with no subsidy, no 25% impact-tax flag and a 12.5% minimum | 72 |
| **wedge** | base projects that faced a known price for density (bonus available, height limit, lump at 15%, own schedule) and chose their own share: no subsidy except LIHTC after completion, no 25% impact-tax share (`08` `wedge_sample`) | 110 |

**Revision.** The first version counted the MPDU-share sample by report row (206). But 8 plans set their MPDU obligation for the whole plan and the reports list their phases or buildings separately. So a phase's share isn't a choice: Cabin Branch phases run from 5% to 25%, while the plan as a whole is at 14.4%. The "all" sample now sums each such plan into one project, as `08` does for the base: the 6 plan groups `08` already had (20 rows), plus two plans whose buildings share one cap, The Perry with Park Potomac Townhomes (75 MPDUs of 600, exactly 12.5%), and The Darcy with The Flats (27 of 250, 10.8%). That makes 206 rows into 190 projects, and the base sample 182. The "all" sample also keeps Wildwood Manor, which `06` drops because its report plan number belongs to another project; its units and MPDUs are fine.

**Second revision.** The choice sample had 14 projects at base, which looked like a second pile. I read the documents for each, and for the downtown (CBD/CR) choice projects 8-13% below base. 15 had another limit and leave the bonus sample:

- **Height limit (12, a new group).** At the zone's or plan's maximum height with no more than the base floor area built, so the bonus floor area had no room. At base: Eleven55 Ripley (200 ft), Flats 8300 and Argent (90 ft), Element 28 and Cameron (143 ft), 8415 Fenton Street (at the permitted height in all three zones), Guardian (an office conversion, 138 of 145 ft). Below base: 1200 East West Highway (142 of 143 ft), The Veridian (tapered to 143 ft under the South Silver Spring guidelines), The Premier (13 storeys, "the maximum height of 143 feet"), Fenwick (60 ft required and approved, at the CBD edge) and Heritage (90 ft, the CBD-1 and overlay maximum; source a description of the proposal, not a resolution).
- **Ceiling at base (2).** The Blairs (a Project Plan ceiling) and Bentley Park (a development plan cap of 248 units including MPDUs).
- **Other program (1).** The Core went over the floor-area cap through workforce housing.

Bonus available goes from 116 to 101 and choice from 89 to 74. In the choice sample, at base falls from 14 to 4 and below base from 31 to 26. Woodward Crossing, Wootton Crossing and Woodcrest show no other limit and stay at base. Sources are in `NOTES.md`.

**Nov 5.** 850 Sligo Avenue, the last choice project at base, moves to lump at 15%. Its density was set by Sketch Plan 320180090, filed 5 Jan 2018 under the 2014 CR rule, whose binding elements fix the maximum density at 82,941 sf (3.0 FAR, the mapped maximum) and the height at 60 ft (H-60, and the Sector Plan's limit east of Fenton Street), at 12.5% MPDUs. The site plan (MCPB 19-039), filed 8 days after ZTA 18-06, keeps both. Same rule as Knowles Manor. Bonus available 101 to 100, choice 74 to 73 (3 at base); the wedge sample stays 111.

**Nov 5, later.** White Oak (82005018C, 22 townhouses, 4 MPDUs) is Phase 2 of Whitehall Square (820050180, 106, 16) and is now one plan group with it. The Phase 2 staff report (Planning Board, 22 May 2014) sets density and MPDUs for the whole plan: "Max. Number of Dwelling Units 128 (29.34 ac X 4.39)" and "Min. Number of MPDUs at 15%: 20 (16 existing + 4 proposed)". Its 3.04 added acres alone would allow 13 units. Grouped: 128 units, 20 MPDUs (15.6%), base 105 (the phases' 87 + 18), at 22%, as each phase was alone. White Oak's base was Phase 1's ratio (`base_check` borrowed); the 2014 table checks it, so it is now checked. All 189, base 181, bonus 99, choice 72, wedge 110.

## Who is in it

| | all | base | bonus | choice |
|---|---|---|---|---|
| Projects | 189 | 181 | 99 | 72 |
| Units, total | 46,465 | 44,551 | 20,430 | 14,895 |
| Units, median (25th-75th pct) | 176 (71-312) | 180 (71-319) | 125 (55-252) | 112 (45-267) |
| MPDUs, total | 7,256 | 6,994 | 3,619 | 2,192 |
| MPDU share, median | 14.3% | 14.0% | 15.0% | 15.0% |
| At its required minimum | 51% | 53% | 41% | 40% |
| At exactly 15% (above a 12.5% minimum) | 21% | 20% | 32% | 43% |
| 15% minimum required | 10% | 9% | 9% | 0% |
| Rental / for-sale | 48% / 50% | 49% / 49% | 37% / 61% | 31% / 68% |
| First MPDU offering, median year (range) | 2016 (2005-2025) | 2017 | 2016 | 2014 |
| Under the new rules (ZTA 18-06) | 18% | 18% | 23% | 8% |
| Tract median gross rent 2019, median | $1,843 | $1,802 | $1,799 | $1,802 |

A plan group takes its first phase's tenure, rent and minimum, its earliest offering year, and the regime of its earliest site plan. The base sample loses little: 181 of 189 projects, and 96% of the units. The choice sample is smaller, older and more for-sale: 60 of its 72 projects had their site plans accepted before the October 2014 zoning rewrite.

## 1. MPDU share: the pile at 15%

"At x%" is counted in units: a project is at 15% when its MPDUs equal the fewest that reach 15% of its units, so rounding doesn't move it.

| MPDU share | Old schedule | New (ZTA 18-06) | Total |
|---|---|---|---|
| Fully affordable | 1 | 1 | 2 |
| Below its minimum | 6 | 0 | 6 |
| At its minimum (12.5%, or 15% where required) | 80 | 17 | 97 |
| Between the minimum and 15% | 18 | 0 | 18 |
| At 15% | 36 | 2 | 39 |
| 15-20% | 4 | 3 | 7 |
| At 20% | 2 | 1 | 3 |
| 20-25% | 1 | 0 | 1 |
| At 25% | 3 | 7 | 10 |
| Above 25% | 3 | 3 | 6 |
| **Total** | **154** | **34** | **189** (incl. 1 unknown) |

Under the old schedule the bonus stopped at 15% MPDUs. 36 projects stop exactly there, against 18 spread over the whole range from the minimum to 15% and 4 over 15-20%. Summing phases took "below its minimum" from 13 to 6: most were phases of plans whose MPDUs sit in other phases. Under the new rules there are only 34 projects. Their 15% pile is mostly the 15% minimum areas, and 7 of the 34 are at 25%, the impact-tax notch.

![MPDU share by regime](descriptives_figs/share.png)

### Only where the bonus was available

The old-schedule sample mixes projects that could buy units with MPDUs and projects whose base was a hard ceiling (group from `08`'s zone and date rules; 6 projects have no resolution, so no group).

| MPDU share, old schedule | Bonus available | *of which choice* | Ceiling at base | Height limit | Lump at 15% | Other groups | No resolution base | Total |
|---|---|---|---|---|---|---|---|---|
| Fully affordable | 1 | *0* | 0 | 0 | 0 | 0 | 0 | 1 |
| Below its minimum | 1 | *1* | 1 | 0 | 0 | 2 | 2 | 6 |
| At its minimum | 30 | *26* | 25 | 12 | 7 | 6 | 0 | 80 |
| Between the minimum and 15% | 7 | *7* | 7 | 0 | 1 | 2 | 1 | 18 |
| At 15% | 30 | *29* | 1 | 0 | 2 | 2 | 1 | 36 |
| Above 15% | 7 | *3* | 2 | 0 | 1 | 1 | 2 | 13 |
| **Total** | **76** | ***66*** | **36** | **12** | **11** | **13** | **6** | **154** |

This is the cleanest picture of the 15% pile. Where MPDUs bought units, 30 of 76 projects stop exactly at 15%. Where base was a ceiling, 1 of 36 does, though both faced the same 12.5% requirement. The ceiling projects pile at the minimum instead (25 of 36), and so do all 12 at a height limit. So the 15% pile is about the bonus, not a habit of offering 15%.

![MPDU share, bonus available against ceiling at base](descriptives_figs/share_by_group.png)

What this changes for any later use of the share:
- **The sample for the bonus schedule is about 66 to 76 projects, not 154.** That's 76 bonus-available old-schedule projects, 66 of them with no subsidy, impact-tax flag or 15% minimum.
- **The interior is thin.** Of the 18 projects between the minimum and 15%, only 7 could buy units, and four of those are small projects one MPDU over the minimum (Leaman Farm, Trotters Glen, Tapestry, Manor Oaks: 54-69 units, where one MPDU is 1.5-1.9 points of share). Only Arora Hills (12 over), Thayer & Spring (9) and Citron (3) are interior by more than rounding.
- **Ceiling-at-base projects above the minimum (7).** They give MPDUs that buy nothing under our rule: Cabin Branch (35 over the minimum, 14.4% plan-wide), Mallory Square (7), Hanover Shady Grove (4), Solaire Wheaton (3), and AVA Wheaton, Amalyn and Pike & Rose (1 each, rounding). Cabin Branch is worth a look at its development plan's MPDU condition; the rest are not checked.

### The 14.5-15% gap

The old table gives 20% at 14.5% MPDUs and 22% at 15%, nothing in between. So no one should stop strictly between. Counted in units, one project does: Thayer & Spring, 59 MPDUs of 399 (14.79%; 15% needs 60). It took the full 22% (base 327), so the Board treated it as meeting 15%. Its resolution is worth checking. Manor Oaks (8 of 54) and Tapestry (10 of 67) have the fewest MPDUs that reach 14.5% and took 20%, as the table says. Trotters Glen and Leaman Farm (10 of 69, 14.49%) took 19%, also as the table says.

The last step of the table is pricier than the rest: 2 points of bonus for 0.5 points of MPDUs, about 0.45 MPDUs per extra unit against about 0.27 just before. That makes 14.5% a second, small kink; the model sketch's straight line ignores it.

## 2. Building size: no bonus or the full bonus

Position is units built against the base (the most units before any MPDU bonus).

| Group | Below base | At base | Between | At 22% | Above 22% | Total |
|---|---|---|---|---|---|---|
| Bonus available | 41 | 6 | 21 | 29 | 2 | 99 |
| *of which choice* | *26* | *3* | *16* | *26* | *1* | *72* |
| Ceiling at base | 14 | 23 | 0 | 0 | 0 | 37 |
| Height limit (only CBD/CR at or just below base checked) | 5 | 7 | 0 | 0 | 0 | 12 |
| Lump at 15% (2014 CR rule) | 6 | 5 | 1 | 0 | 1 | 13 |
| Own schedule (Bethesda Overlay, Tregoning) | 0 | 0 | 3 | 0 | 7 | 10 |
| Other program | 0 | 1 | 1 | 0 | 4 | 6 |
| Unclear | 1 | 2 | 0 | 0 | 0 | 3 |
| Base from approved units | 0 | 1 | 0 | 0 | 0 | 1 |

Among the 72 choice projects, the pile is at the full 22% (26), with only 4 projects between +5% and +15%. At base there are now only 3, against 26 below: before the second revision the 14 at base looked like a second pile, but 11 of them were stopped by height, a plan cap, another program or the CR lump rule. So few projects that could use the bonus stop exactly at base; the downtown projects at or just below base were at a height limit, not refusing the bonus. Where base is a hard ceiling (right panel), 23 of 37 sit at it and none go above, as they shouldn't. The height-limit group is selected on position (only downtown projects at or just below base were checked), so it is not a comparison group. Of the 16 "between" projects, 10 are just short of the top, at 16-21%.

![Units over base](descriptives_figs/units_over_base.png)

## 3. The two margins line up

If the data are right, a project at 15% MPDUs should have taken the full bonus, and one at its minimum should be at or below base. For the 99 bonus-available projects:

| MPDU share | Below base | At base | Between | At 22% | Above 22% | Total |
|---|---|---|---|---|---|---|
| At its minimum | 29 | 5 | 5 | 2 | 0 | 41 |
| Minimum to 15% | 0 | 0 | 5 | 2 | 0 | 7 |
| At 15% | 3 | 0 | 7 | 22 | 0 | 32 |
| At 25% | 3 | 1 | 2 | 1 | 2 | 9 |
| Other | 6 | 0 | 2 | 2 | 0 | 10 |

Mostly they do. 22 of the 32 at 15% MPDUs are at 22%, and 34 of the 41 at the minimum are at or below base. The exceptions are explainable or worth a look:
- **At the minimum, but above base (7).** Three are small projects where the 12.5% minimum rounds up to 14-15% (4 MPDUs of 26-28 units: Kensington Overlook, Bethesda Crest, Hallman Grove), which earns part of the bonus. Two have a 15% minimum, whose bonus starts there (12710 Twinbrook Parkway, Strathmore Square). Olney Estates is call 12. Residences at Shady Grove (19 of 149, 12.75%) is 4.9% over base where its share earns about 2.5%, which is 3 units and close enough to be the base's rounding.
- **At 15%, but below base (3): worth checking.** Grosvenor Place (−23%), North Bethesda Market (−21%, a zone-table base on TS-M) and White Oak Apartments (−1%, essentially at base). Each paid for 15% MPDUs without using the bonus they buy, unless the base is too high.

The scatter shows the same thing against the two bonus schedules: the choice projects (filled) sit on the schedule or at its 22% top, or below base at the 12.5% minimum.

![MPDU share against units over base](descriptives_figs/share_vs_units.png)

## 4. Flags, by group

| Group | Projects | TDRs or transfer | Subsidy | 25% impact tax | 15% minimum | Other program | Base not checked |
|---|---|---|---|---|---|---|---|
| Bonus available | 99 | 15 | 15 | 5 | 9 | 0 | 1 |
| Ceiling at base | 37 | 3 | 2 | 1 | 0 | 0 | 0 |
| Height limit | 12 | 0 | 0 | 0 | 0 | 0 | 2 |
| Lump at 15% | 13 | 0 | 3 | 1 | 0 | 0 | 0 |
| Own schedule | 10 | 0 | 0 | 0 | 8 | 7 | 0 |
| Other program | 6 | 1 | 3 | 1 | 0 | 6 | 0 |
| Unclear, base from approved units | 4 | 0 | 0 | 0 | 0 | 0 | 0 |
| **Total** | **181** | **19** | **23** | **8** | **17** | **13** | **3** |

Subsidy excludes "LIHTC after completion" (The Argent, now in height limit), whose share the market developer set.

## 5. The choice sample, by period and tenure

| | Below base | At base | Between | At 22% | Above 22% | Total |
|---|---|---|---|---|---|---|
| Before Oct 2014 | 18 | 3 | 16 | 23 | 0 | 60 |
| Oct 2014 - Oct 2018 | 4 | 0 | 0 | 2 | 0 | 6 |
| From Oct 2018 | 4 | 0 | 0 | 1 | 1 | 6 |
| For-sale | 19 | 2 | 13 | 15 | 0 | 49 |
| Rental | 6 | 1 | 3 | 11 | 1 | 22 |
| Tenure unknown | 1 | 0 | 0 | 0 | 0 | 1 |

The building-size evidence is almost all pre-2014. The 2014-18 period is thin because most CR projects then faced the lump rule instead of the unit bonus. After 2018 it's thin because many new projects are in 15% minimum areas or subsidized. Rentals no longer sit at base more often than for-sale projects (1 of 22 against 2 of 49); the earlier gap (9 of 35 against 5 of 53) was the downtown rentals at their height limit.

![Projects by year](descriptives_figs/year.png)

## 6. The wedge sample, all together

The figures above each show one slice: the MPDU-share figures cover all 189 projects (no base needed), the building-size figures the bonus or choice samples. The wedge sample is the 110 base projects that faced a known price for density and chose their own share (`wedge_sample`): bonus available 79 (old 66, new 13), height limit 12, lump at 15% 9, own schedule 10; 90 under the old schedule and 20 under ZTA 18-06.

| Group | Below base | At base | Between | At 22% | Above 22% | Total |
|---|---|---|---|---|---|---|
| Bonus available | 29 | 5 | 17 | 27 | 1 | 79 |
| Height limit | 5 | 7 | 0 | 0 | 0 | 12 |
| Lump at 15% | 4 | 5 | 0 | 0 | 0 | 9 |
| Own schedule | 0 | 0 | 3 | 0 | 7 | 10 |
| **Total** | **38** | **17** | **20** | **27** | **8** | **110** |

The share piles at 12.5% (35 projects in the 12.5% bin) and 15% (36). In units over base, 27 are at the 22% top and 17 at base, 12 of those 17 at a height limit or under the 2014 CR lump rule. The 8 above 22% are mostly Bethesda Overlay projects, which buy density on their own schedule.

![Wedge sample: MPDU share and units over base](descriptives_figs/wedge_sample.png)

## What these don't show yet

- **Geography.** Planning area is carried in `08` but not tabulated here.
- **The 26 choice projects below base.** 7 of them are more than 30% below. Something else binds (height, parking, the market) or the base is too high. They need a look before anyone reads take-up from them. All five downtown ones just below base were at a height limit and are now in that group; the rest are outside downtown and not checked (the closest to base: Clarksburg Square, Meadows at Hurley Ridge, Magruder's Overlook, 4-6% below).
- **The choice projects still at base (3).** Woodward Crossing, Wootton Crossing and Woodcrest (no other limit found; Wootton Crossing's approval even lists the bonus density, 9.76 du/ac, and it built 7.98).
- **Open calls 3 and 12.** These are Evan's. Call 3 moves Clarksburg Village; call 12 drops Olney Estates if coded at 14.3%.
