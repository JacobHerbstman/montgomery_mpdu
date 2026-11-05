*******************************************************************************
* 01_append_open_data.do
*
* Builds one offering-level MPDU file:
*   - spine: offering agreements extracted from the DHCA annual reports
*     (data/int/02_data_cleaning/00_ocr_reports.dta, written by code/01_data_collection/02_extract_mpdu_offerings.py)
*     for every year the reports cover;
*   - appended: a cleaned version of the county open data
*     (data/raw/Moderately_Priced_Dwelling_Units_20260928.csv) for years the
*     reports do not cover.
*
* Output: data/int/02_data_cleaning/01_mpdu_offerings_combined.dta
*
* Things to keep in mind when using the combined file:
*   1. Report years are taken from 00_ocr_reports.dta itself (currently
*      2013-2025). 2025 is incomplete in the reports (19 of 22 offerings; the
*      published PDF is cropped) but is still treated as a report year.
*   2. The two sources do not measure the same thing:
*        - reports: offering_date is the executed Offering Agreement date and
*          mpdus_in_offering is the number of MPDUs released in that offering;
*        - open data: "Offering Date" is undocumented and, where it can be
*          matched to the reports, is often 1-3 years EARLIER than the actual
*          offering; there is no per-offering MPDU count, so
*          mpdus_in_offering is missing.
*      Use `source' to separate them.
*   3. total_mpdus is the project's total MPDUs, available from both sources.
*      It is a project attribute repeated on every offering row of that
*      project, so summing it over rows overstates production.
*   4. Open-data offering dates after the data were pulled (28 Sep 2026) are
*      kept but flagged projected_date = 1.
*******************************************************************************

version 17
clear all
set more off

* Project root -- add a branch if running on a new machine
if "`c(username)'" == "aw0578" {
	global root "C:/Users/aw0578/Princeton Dropbox/Audrey Wang/MarylandMPDU"
}
else if "`c(username)'" == "audreywang" {
	global root "/Users/audreywang/Library/CloudStorage/Dropbox-Princeton/Audrey Wang/MarylandMPDU"
}
else {
	display as error "Unknown user `c(username)': set global root in 01_append_open_data.do"
	exit 198
}

global int  "$root/data/int/02_data_cleaning"
global raw   "$root/data/raw"

local open_csv   "$raw/Moderately_Priced_Dwelling_Units_20260928.csv"
local pull_date  = td(28sep2026)

*------------------------------------------------------------------------------
* 1. Spine: offerings from the annual reports
*------------------------------------------------------------------------------
use "$int/00_ocr_reports.dta", clear

rename project_mpdus total_mpdus

* WFH-only offerings leave the project's MPDU column blank in the reports; take
* it from the same project's other offerings in the same report
bysort file site_plan project_name: egen double _fill = max(total_mpdus)
count if missing(total_mpdus) & !missing(_fill)
display as text "total_mpdus filled from same project in same report: " r(N)
replace total_mpdus = _fill if missing(total_mpdus)
drop _fill

gen str11 source = "report"
gen byte projected_date = 0

levelsof offering_year, local(report_years)
display as text "Years covered by the annual reports: `report_years'"

tempfile reports
save `reports'


*------------------------------------------------------------------------------
* 2. Clean the open data
*------------------------------------------------------------------------------
import delimited using "`open_csv'", varnames(1) stringcols(_all) ///
    bindquote(strict) encoding("utf-8") clear

* expected columns: planningarea totalunits totalmpdu totalworkforce
*                   rentalindicator offeringdate
confirm variable planningarea totalunits totalmpdu totalworkforce ///
    rentalindicator offeringdate

local n0 = _N

* exact duplicate rows (147 in the 2026-09-28 pull, mostly blank records)
duplicates drop
local n_dup = `n0' - _N

destring totalunits totalmpdu totalworkforce, replace

rename planningarea   planning_area
rename totalunits     total_units
rename totalmpdu      total_mpdus
rename totalworkforce open_total_workforce

* "Rental Indicator" is "For-Sale & Rental" on every row: no information
drop rentalindicator

* records with no units are not projects (0 or missing units; these rows are
* also where MPDUs > total units occurred)
count if missing(total_units) | total_units <= 0
local n_nounits = r(N)
drop if missing(total_units) | total_units <= 0

* offering date; undated rows cannot be placed in a year
gen offering_date = date(offeringdate, "MDY")
format offering_date %td
count if missing(offering_date)
local n_nodate = r(N)
drop if missing(offering_date)
drop offeringdate

gen offering_year = year(offering_date)

* keep only years the reports do not cover
gen byte in_report_years = 0
foreach y of local report_years {
    replace in_report_years = 1 if offering_year == `y'
}
count if in_report_years
local n_overlap = r(N)
drop if in_report_years
drop in_report_years

gen str11 source = "open_data"
gen byte projected_date = offering_date > `pull_date'

tempfile open
save `open'

*------------------------------------------------------------------------------
* 3. Combine
*------------------------------------------------------------------------------
use `reports', clear
append using `open'

* placeholder text ("N/A", "NA", "none", "TBD", "-", ...) means missing
ds, has(type string)
foreach v of varlist `r(varlist)' {
    quietly count if ustrregexm(strtrim(`v'), "^(n\s*/?\s*a|none|null|tbd|unknown|not applicable|-+)$", 1)
    if r(N) > 0 display as text "`v': " r(N) " placeholder values set to blank"
    quietly replace `v' = "" if ustrregexm(strtrim(`v'), "^(n\s*/?\s*a|none|null|tbd|unknown|not applicable|-+)$", 1)
}

*------------------------------------------------------------------------------
* 4. Link report offerings of the same project across reports
*------------------------------------------------------------------------------
* The 2024 report prints no site plan numbers and the (cropped) 2025 report
* prints no project names, so offerings of one project can carry different
* partial keys. Fill them in from other offerings of the same project.
* Original values are kept in site_plan_orig / project_name_orig.

gen str site_plan_orig    = site_plan
gen str project_name_orig = project_name
label variable site_plan_orig    "Site plan as extracted, before cross-report linking"
label variable project_name_orig "Project name as extracted, before cross-report linking"

* name key for matching: lowercase alphanumerics, "phase" -> "ph"
gen str name_key = ustrlower(project_name)
replace name_key = ustrregexra(name_key, "phase", "ph")
replace name_key = ustrregexra(name_key, "[^a-z0-9]", "")

* 4a. Site plan from offerings with the same name and totals. Takes the modal
* site plan when it is unique; this also overrides a site plan that disagrees
* with the other offerings of the same name and totals.
egen _g = group(name_key total_units total_mpdus) if source == "report" & name_key != ""
bysort _g site_plan: gen _cnt = _N if !missing(_g) & site_plan != ""
bysort _g: egen _maxcnt = max(_cnt)
gen byte _top = !missing(_cnt) & _cnt == _maxcnt
egen byte _toptag = tag(_g site_plan) if _top
bysort _g: egen _ntop = total(_toptag)
gen str _topsp = site_plan if _top
bysort _g (_topsp): replace _topsp = _topsp[_N]
count if !missing(_g) & _ntop == 1 & site_plan != _topsp
display as text "4a. site plan filled/overridden from same name and totals: " r(N)
replace site_plan = _topsp if !missing(_g) & _ntop == 1 & site_plan != _topsp
drop _g _cnt _maxcnt _top _toptag _ntop _topsp

* 4b. Remaining offerings with a name but no site plan, matched to offerings
* with a site plan but no name on (total units, total MPDUs, tenure). Only
* one-to-one matches are used: one site plan among the unnamed offerings and
* one name among the offerings without a site plan.
gen byte _recip = source == "report" & site_plan == "" & name_key != ""
gen byte _donor = source == "report" & site_plan != "" & name_key == ""
egen _g = group(total_units total_mpdus tenure) if _recip | _donor
egen byte _sptag = tag(_g site_plan) if _donor
egen byte _nmtag = tag(_g name_key) if _recip
bysort _g: egen _nsp = total(_sptag)
bysort _g: egen _nnm = total(_nmtag)
gen str _sp = site_plan if _donor
bysort _g (_sp): replace _sp = _sp[_N]
count if _recip & _nsp == 1 & _nnm == 1
display as text "4b. site plan filled from unnamed offerings with the same totals: " r(N)
replace site_plan = _sp if _recip & _nsp == 1 & _nnm == 1
drop _recip _donor _g _sptag _nmtag _nsp _nnm _sp

* 4c. Name and developer for unnamed offerings, from the most recent named
* offering with the same site plan and totals.
egen _g = group(site_plan total_units total_mpdus) if source == "report" & site_plan != ""
foreach v in project_name developer {
    gen byte _nohas = `v' == ""
    gen double _negdate = -offering_date
    bysort _g (_nohas _negdate): gen str _fill = `v'[1] if !missing(_g)
    count if !missing(_g) & `v' == "" & _fill != ""
    display as text "4c. `v' filled from same site plan and totals: " r(N)
    replace `v' = _fill if !missing(_g) & `v' == "" & _fill != ""
    drop _nohas _negdate _fill
}
drop _g name_key

gen byte key_linked = (site_plan != site_plan_orig) | (project_name != project_name_orig)
label variable key_linked "Site plan or name filled/changed by cross-report linking (section 4)"

label variable source               "Data source: report (DHCA annual report) or open_data"
label variable projected_date       "Open data: offering date after data pull (28 Sep 2026)"
label variable planning_area        "Planning area (open data only)"
label variable open_total_workforce "Open data: project total workforce units"
label variable offering_date        "Offering date (report: agreement date; open data: see notes)"
label variable total_mpdus          "Total MPDUs in the project (both sources; repeated per offering)"
label variable mpdus_in_offering    "MPDUs released in this offering (reports only)"

notes offering_date: For source report, the executed Offering Agreement date (DHCA counts MPDUs as built on this date).
notes offering_date: For source open_data, the county open data Offering Date; undocumented and often earlier than the actual offering.
notes total_mpdus: Project total, repeated on every offering row of a project in both sources; do not sum across rows. Sum mpdus_in_offering (reports) for MPDUs built.
notes mpdus_in_offering: Missing for source open_data (not in the open data).

order source offering_year offering_date projected_date project_name aka ///
      site_plan planning_area street_address city zip total_units ///
      total_mpdus mpdus_in_offering wfh_units open_total_workforce tenure ///
      developer unit_description
sort offering_date source

assert inlist(source, "report", "open_data")
assert !missing(offering_year)

label data "MPDU offerings: DHCA annual reports (2013-2025) + open data (other years)"
compress
save "$int/01_mpdu_offerings_combined.dta", replace

tab offering_year source, missing
