*******************************************************************************
* 01_combine_reports.do
*
* Builds one offering-level MPDU file from the DHCA annual reports:
*   - 2013-2025: published report PDFs
*     (data/int/02_data_cleaning/00_ocr_reports.dta, written by
*     code/01_data_collection/02_extract_mpdu_offerings.py);
*   - 2005-2012: reports obtained by FOIA as spreadsheets
*     (data/int/02_data_cleaning/00_foia_reports.dta, written by
*     code/01_data_collection/08_extract_foia_offerings.py).
*
* Output: data/int/02_data_cleaning/01_mpdu_offerings_combined.dta
*
* Things to keep in mind when using the combined file:
*   1. offering_date is the executed Offering Agreement date and
*      mpdus_in_offering the number of MPDUs released in that offering, in
*      both series.
*   2. total_mpdus is the project's total MPDUs. It is a project attribute
*      repeated on every offering row of that project, so summing it over rows
*      overstates production. In the published reports it is printed on the
*      offering row; in the FOIA series it is looked up in the pipeline and
*      Agreement to Build sheets (see totals_source) and is missing for 18 of
*      103 offerings, mostly 2005-2006.
*   3. 2025 is incomplete (19 of 22 offerings; the published PDF is cropped).
*      2005 lists one more offering than the memo counts (Wheaton Forest, 15
*      rental MPDUs).
*   4. The county open data (Moderately_Priced_Dwelling_Units_20260928.csv)
*      used to fill years before 2013 was replaced by the FOIA reports; the
*      old do-file and the data are in code/_archive and data/raw/_archive.
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
	display as error "Unknown user `c(username)': set global root in 01_combine_reports.do"
	exit 198
}

global int  "$root/data/int/02_data_cleaning"

*------------------------------------------------------------------------------
* 1. Append the two report series
*------------------------------------------------------------------------------
use "$int/00_foia_reports.dta", clear
gen str9 report_series = "foia"
append using "$int/00_ocr_reports.dta"
replace report_series = "published" if report_series == ""

* the series must not overlap in years
levelsof offering_year if report_series == "foia", local(foia_years)
foreach y of local foia_years {
    assert report_series == "foia" if offering_year == `y'
}

rename project_mpdus total_mpdus

* WFH-only offerings leave the project's MPDU column blank in the reports; take
* it from the same project's other offerings in the same report
bysort file site_plan project_name: egen double _fill = max(total_mpdus)
count if missing(total_mpdus) & !missing(_fill)
display as text "total_mpdus filled from same project in same report: " r(N)
replace total_mpdus = _fill if missing(total_mpdus)
drop _fill

* placeholder text ("N/A", "NA", "none", "TBD", "-", ...) means missing
ds, has(type string)
foreach v of varlist `r(varlist)' {
    quietly count if ustrregexm(strtrim(`v'), "^(n\s*/?\s*a|none|null|tbd|unknown|not applicable|-+)$", 1)
    if r(N) > 0 display as text "`v': " r(N) " placeholder values set to blank"
    quietly replace `v' = "" if ustrregexm(strtrim(`v'), "^(n\s*/?\s*a|none|null|tbd|unknown|not applicable|-+)$", 1)
}

*------------------------------------------------------------------------------
* 2. Link offerings of the same project across reports
*------------------------------------------------------------------------------
* The 2024 report prints no site plan numbers, the (cropped) 2025 report
* prints no project names, and the 2005 FOIA sheet prints no site plans, so
* offerings of one project can carry different partial keys. Fill them in
* from other offerings of the same project.
* Original values are kept in site_plan_orig / project_name_orig.

gen str site_plan_orig    = site_plan
gen str project_name_orig = project_name
label variable site_plan_orig    "Site plan as extracted, before cross-report linking"
label variable project_name_orig "Project name as extracted, before cross-report linking"

* name key for matching: lowercase alphanumerics, "phase" -> "ph"
gen str name_key = ustrlower(project_name)
replace name_key = ustrregexra(name_key, "phase", "ph")
replace name_key = ustrregexra(name_key, "[^a-z0-9]", "")

* 2a. Site plan from offerings with the same name and totals. Takes the modal
* site plan when it is unique; this also overrides a site plan that disagrees
* with the other offerings of the same name and totals.
egen _g = group(name_key total_units total_mpdus) if name_key != ""
bysort _g site_plan: gen _cnt = _N if !missing(_g) & site_plan != ""
bysort _g: egen _maxcnt = max(_cnt)
gen byte _top = !missing(_cnt) & _cnt == _maxcnt
egen byte _toptag = tag(_g site_plan) if _top
bysort _g: egen _ntop = total(_toptag)
gen str _topsp = site_plan if _top
bysort _g (_topsp): replace _topsp = _topsp[_N]
count if !missing(_g) & _ntop == 1 & site_plan != _topsp
display as text "2a. site plan filled/overridden from same name and totals: " r(N)
replace site_plan = _topsp if !missing(_g) & _ntop == 1 & site_plan != _topsp
drop _g _cnt _maxcnt _top _toptag _ntop _topsp

* 2b. Remaining offerings with a name but no site plan, matched to offerings
* with a site plan but no name on (total units, total MPDUs, tenure). Only
* one-to-one matches are used: one site plan among the unnamed offerings and
* one name among the offerings without a site plan.
gen byte _recip = site_plan == "" & name_key != "" & !missing(total_units)
gen byte _donor = site_plan != "" & name_key == ""
egen _g = group(total_units total_mpdus tenure) if _recip | _donor
egen byte _sptag = tag(_g site_plan) if _donor
egen byte _nmtag = tag(_g name_key) if _recip
bysort _g: egen _nsp = total(_sptag)
bysort _g: egen _nnm = total(_nmtag)
gen str _sp = site_plan if _donor
bysort _g (_sp): replace _sp = _sp[_N]
count if _recip & _nsp == 1 & _nnm == 1
display as text "2b. site plan filled from unnamed offerings with the same totals: " r(N)
replace site_plan = _sp if _recip & _nsp == 1 & _nnm == 1
drop _recip _donor _g _sptag _nmtag _nsp _nnm _sp

* 2c. Name and developer for unnamed offerings, from the most recent named
* offering with the same site plan and totals.
egen _g = group(site_plan total_units total_mpdus) if site_plan != ""
foreach v in project_name developer {
    gen byte _nohas = `v' == ""
    gen double _negdate = -offering_date
    bysort _g (_nohas _negdate): gen str _fill = `v'[1] if !missing(_g)
    count if !missing(_g) & `v' == "" & _fill != ""
    display as text "2c. `v' filled from same site plan and totals: " r(N)
    replace `v' = _fill if !missing(_g) & `v' == "" & _fill != ""
    drop _nohas _negdate _fill
}
drop _g name_key

gen byte key_linked = (site_plan != site_plan_orig) | (project_name != project_name_orig)
label variable key_linked "Site plan or name filled/changed by cross-report linking (section 2)"

label variable report_series     "Report series: published (2013-2025 PDFs) or foia (2005-2012 spreadsheets)"
label variable offering_date     "Offering Agreement date (DHCA counts MPDUs as built on this date)"
label variable total_mpdus       "Total MPDUs in the project (repeated per offering)"
label variable mpdus_in_offering "MPDUs released in this offering"
label variable file              "Source report (relative to data/raw/mpdu_annual_reports)"

notes total_mpdus: Project total, repeated on every offering row of a project; do not sum across rows. Sum mpdus_in_offering for MPDUs built.
notes total_mpdus: FOIA series (2005-2012): looked up in the pipeline / Agreement to Build sheets; see totals_source.

order report_series offering_year offering_date project_name aka site_plan ///
      prelim_plan street_address city zip total_units total_mpdus ///
      mpdus_in_offering wfh_units tenure developer unit_description
sort offering_date report_series

assert inlist(report_series, "published", "foia")
assert !missing(offering_year) & !missing(offering_date)

label data "MPDU offerings: DHCA annual reports 2005-2012 (FOIA) and 2013-2025 (published)"
compress
save "$int/01_mpdu_offerings_combined.dta", replace

tab offering_year report_series, missing
