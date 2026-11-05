"""Extract text from the Planning Board resolution PDFs.

Run code/01_data_collection/04_download_pb_resolutions.py first.

76 of the 126 resolutions are scans with no text layer. Text PDFs are read
with pypdf; a page with fewer than 30 words of text is rendered at 300 dpi
with pypdfium2 and OCR'd with tesseract (--psm 4, which keeps the columns of
the development standards tables in reading order).

Output: data/int/02_data_cleaning/02_pb_resolution_text/<pdf name>.txt, pages separated by form
feeds, plus extraction_log.csv (pages, OCR'd pages, words per file). Files
already extracted are skipped unless --force is passed.

Also used for the pre-2008 staff reports (10_download_pb_archive_reports.py):
  --archive reads data/raw/pb_archive_reports/ and writes
  data/int/02_data_cleaning/02_pb_archive_text/, first ARCHIVE_MAX_PAGES pages
  only (the project data tables come first; the rest is plans and maps),
  always OCR'd (embedded text layers in some of these PDFs are out of order).

Usage:
  python 02_extract_resolution_text.py [--force] [--archive]

Requires: pypdf, pypdfium2, and the tesseract binary.
"""

import os
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import pandas as pd
import pypdfium2 as pdfium
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[2]
PDF_DIR = ROOT / "data" / "raw" / "pb_resolutions"
OUT_DIR = ROOT / "data" / "int" / "02_data_cleaning" / "02_pb_resolution_text"

ARCHIVE_PDF_DIR = ROOT / "data" / "raw" / "pb_archive_reports"
ARCHIVE_OUT_DIR = ROOT / "data" / "int" / "02_data_cleaning" / "02_pb_archive_text"
ARCHIVE_MAX_PAGES = 15

MIN_WORDS = 30
DPI = 300
WORKERS = 12


def tesseract_exe():
    exe = shutil.which("tesseract")
    if exe:
        return exe
    for p in [Path.home() / "AppData/Local/Programs/Tesseract-OCR/tesseract.exe",
              Path("C:/Program Files/Tesseract-OCR/tesseract.exe")]:
        if p.exists():
            return str(p)
    raise FileNotFoundError("tesseract binary not found")


def ocr_page(pdf, i, exe, tmpdir):
    img = pdf[i].render(scale=DPI / 72).to_pil().convert("L")
    path = Path(tmpdir) / "page.png"
    img.save(path)
    out = subprocess.run([exe, str(path), "-", "--psm", "4"],
                         capture_output=True, text=True, encoding="utf-8")
    return out.stdout


def extract(path, exe, tmpdir, max_pages=None, force_ocr=False):
    reader = PdfReader(path)
    pdf = pdfium.PdfDocument(path)
    pages, n_ocr = [], 0
    for i, page in enumerate(reader.pages[:max_pages]):
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""
        if force_ocr or len(text.split()) < MIN_WORDS:
            text = ocr_page(pdf, i, exe, tmpdir)
            n_ocr += 1
        pages.append(text)
    pdf.close()
    return pages, n_ocr


def process(path, force, out_dir=OUT_DIR, max_pages=None, force_ocr=False):
    """Extract one PDF (in a worker process); returns its log row."""
    dest = out_dir / (path.stem + ".txt")
    if dest.exists() and not force:
        pages, n_ocr = dest.read_text(encoding="utf-8").split("\f"), None
    else:
        with tempfile.TemporaryDirectory() as tmpdir:
            pages, n_ocr = extract(path, tesseract_exe(), tmpdir, max_pages, force_ocr)
        dest.write_text("\f".join(pages), encoding="utf-8")
    return {"file": path.name, "pages": len(pages), "ocr_pages": n_ocr,
            "words": sum(len(p.split()) for p in pages)}


def main(force=False, archive=False):
    pdf_dir, out_dir = (ARCHIVE_PDF_DIR, ARCHIVE_OUT_DIR) if archive else (PDF_DIR, OUT_DIR)
    max_pages = ARCHIVE_MAX_PAGES if archive else None
    # staff reports: always OCR. Some 2006-2007 PDFs carry a text layer from
    # the county's own OCR with the header's label and value columns read
    # one after the other ("REVIEW BASIS: ZONE: LOCATION: ... "), which
    # tesseract --psm 4 reads row by row.
    force_ocr = archive
    out_dir.mkdir(parents=True, exist_ok=True)
    tesseract_exe()  # fail early if missing
    pdfs = sorted(pdf_dir.glob("*.pdf"))
    # OCR is CPU-bound and one tesseract call per page; run files in parallel
    workers = max(1, min(WORKERS, (os.cpu_count() or 2) - 2))
    log = []
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futs = {pool.submit(process, p, force, out_dir, max_pages, force_ocr): p for p in pdfs}
        for k, fut in enumerate(as_completed(futs), 1):
            row = fut.result()
            log.append(row)
            print(f"[{k}/{len(pdfs)}] {row['file']}: {row['pages']} pages, "
                  f"{'cached' if row['ocr_pages'] is None else str(row['ocr_pages']) + ' OCR'}, "
                  f"{row['words']} words", flush=True)

    old = out_dir / "extraction_log.csv"
    new = pd.DataFrame(log)
    if old.exists():  # keep OCR page counts from earlier runs for cached files
        prev = pd.read_csv(old).set_index("file")["ocr_pages"]
        new["ocr_pages"] = new["ocr_pages"].fillna(new["file"].map(prev))
    new.to_csv(old, index=False)


if __name__ == "__main__":
    main(force="--force" in sys.argv, archive="--archive" in sys.argv)
