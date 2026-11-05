# Montgomery County MPDU density bonus

Jacob Herbstman and Evan Soltas.

The layout is Evan's Dropbox folder `DensityBonus/Montgomery_MPDU`:

- `code/01_data_collection`, `code/02_data_cleaning`, `code/03_analysis`: numbered
  scripts. Each script's console output is saved next to it as `<script>.log`.
- `data/`: links to `data.nosync/`, which iCloud does not sync. It holds the
  downloads (`data/raw`) and intermediate files (`data/int`), about 5 GB, and is
  not in git except the hand-coded inputs and the download manifests (see
  `.gitignore`).
- `output/tables`, `output/figures`.
- `policy/`: the law and staff reports `rules.py` cites.
- `docs/`: `NOTES.md` (every check and hand-coded value, with sources),
  `descriptives.md`/`.pdf`, `judgment_calls.md`/`.pdf`.

The first commit is Evan's and Audrey's files as they were in the Dropbox on
29 Oct 2026 (copy at `~/mpdu_data/Montgomery_MPDU_snapshot_2026-10-29`). The
commits after it are ours. Their scripts are not edited; our checks are new
files (`06`-`10` in `03_analysis`, `02_data_cleaning/01_combine_reports.py`,
`01_data_collection/12_download_pb_staff_reports.py`, `run_all.py`) and
hand-coded inputs.

## Run

    conda activate mpdu
    cd code
    python run_all.py

`run_all.py` runs cleaning, the simulation and the analysis from `data/raw`. It
skips the downloads and, unless `--ocr` is passed, the OCR steps.

## Data on another machine

Copy the Dropbox's `data/raw` into `data.nosync/raw` without overwriting the
tracked files, which carry our additions (e.g. `manual_coding.csv`):

    rsync -a --ignore-existing <Dropbox>/DensityBonus/Montgomery_MPDU/data/raw/ data.nosync/raw/

The staff reports added to `data/raw/pb_archive_reports` after the snapshot come
from `code/01_data_collection/12_download_pb_staff_reports.py`.
