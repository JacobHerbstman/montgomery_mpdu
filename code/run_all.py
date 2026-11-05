"""Run the Montgomery MPDU pipeline from data/raw to output/figures and output/tables.

Put this file in code/ (with 01_combine_reports.py in code/02_data_cleaning/,
which replaces the Stata step) and run it on a copy of the project folder.

Skipped: the download scripts in code/01_data_collection (01, 03-07, 09, 10, 12).
data/raw already holds what they fetched, and the county sites change.

OCR steps are skipped unless --ocr is passed: the scanned annual-report tables
(02_extract_mpdu_offerings.py -> 00_ocr_reports.dta) and the scanned
resolutions and staff reports (02_extract_resolution_text.py -> text files).
Their saved outputs were checked by hand against the page images. Tesseract
reads some cells differently on another machine, and the hand corrections only
apply where the OCR value is the one they were written for. With --ocr on this
Mac about 10 cells come out wrong, and 11_agreement_projects.py stops on a
project with total units but no MPDU count.

Each script's console output is saved next to it as <script>.log.

pandas' date conversion throws a spurious FloatingPointError at random on
Apple Silicon. A run that gets through gives the same output every time, so a
script is rerun (up to 5 times) on that error only; any other error stops.

Usage:
  python run_all.py [--ocr]
"""

import subprocess
import sys
from pathlib import Path

CODE = Path(__file__).resolve().parent

OCR_STEPS = [
    ["01_data_collection/02_extract_mpdu_offerings.py"],
    ["02_data_cleaning/02_extract_resolution_text.py", "--force"],
    ["02_data_cleaning/02_extract_resolution_text.py", "--force", "--archive"],
]
STEPS = [
    # extract tables from the FOIA spreadsheets and the text-layer report PDFs
    ["01_data_collection/08_extract_foia_offerings.py"],
    ["01_data_collection/11_extract_agreements_to_build.py"],
    # clean
    ["02_data_cleaning/01_combine_reports.py"],
    ["02_data_cleaning/03_parse_resolutions.py"],
    ["02_data_cleaning/04_build_base_density.py"],
    ["02_data_cleaning/05_hud_ami.py"],
    ["02_data_cleaning/06_tract_rents.py"],
    ["02_data_cleaning/07_site_plan_regime.py"],
    ["02_data_cleaning/08_resolution_projects.py"],
    ["02_data_cleaning/09_permit_mpdu_projects.py"],
    ["02_data_cleaning/10_dhca_mpdu_projects.py"],
    ["02_data_cleaning/11_agreement_projects.py"],
    # simulate and plot
    ["03_analysis/01_mpdu_simulation/main.py"],
    ["03_analysis/02_bunching_figure.py"],
    ["03_analysis/03_tax_schedule_figure.py"],
    ["03_analysis/04_kink_bunching_figure.py"],
    ["03_analysis/05_kink_distance_histogram.py"],
    # checks (not Audrey's): audit the resolution-based base density; kink
    # bunching split at the October 2018 schedule change; building size
    # relative to base, by whether a bonus was available
    ["03_analysis/06_base_density_audit.py"],
    ["03_analysis/07_kink_bunching_by_regime.py"],
    ["03_analysis/08_building_size_bunching.py"],
    ["03_analysis/09_descriptives.py"],
    # what each project's position reveals about its wedge, in units of the MPDU discount
    ["03_analysis/10_wedge_bounds.py"],
]


def run(script, *args):
    path = CODE / script
    log = path.with_name(path.stem + "".join("_" + a.strip("-") for a in args) + ".log")
    for attempt in range(1, 6):
        r = subprocess.run([sys.executable, path.name, *args], cwd=path.parent,
                           capture_output=True, text=True)
        log.write_text(r.stdout + r.stderr)
        if r.returncode == 0:
            print(f"ok      {script} {' '.join(args)}" + (f" (try {attempt})" if attempt > 1 else ""))
            return
        if "FloatingPointError" not in r.stderr:
            break
    print(f"FAILED  {script} {' '.join(args)}; last lines of {log}:")
    print("\n".join(r.stderr.strip().splitlines()[-5:]))
    sys.exit(1)


def main():
    steps = (OCR_STEPS if "--ocr" in sys.argv else []) + STEPS
    for step in steps:
        run(*step)
    print("done")


if __name__ == "__main__":
    main()
