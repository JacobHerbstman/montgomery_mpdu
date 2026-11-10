# Brief: check the base of below-base MPDU projects (Montgomery County, MD)

Repo: /Users/jacobherbstman/Desktop/montgomery_mpdu (read only for you: do NOT edit any file in it).
Scratch folder for your output: /private/tmp/claude-501/-Users-jacobherbstman-Desktop-montgomery-mpdu/f29665de-5876-4fec-9cda-67bc7cc6354b/scratchpad/below_check/

## Background
For each housing project we code a "base": the most dwelling units the zoning allowed BEFORE any MPDU density bonus. Under Chapter 25A a developer who provides more than 12.5% MPDUs can build up to 22% more units than base. Each project below built fewer units than our base. Either (i) the limit really did not bind, or (ii) our base is too high (wrong area, a density figure that already includes the bonus, a lower cap we missed), or (iii) some other rule stopped it (height, setbacks, environmental buffers, forest conservation, stream valley, road right-of-way, parking, compatibility). Three earlier errors all ran the same way: a missed master-plan unit cap, a zone floor-area base when the data table showed the project took the bonus, a missed rezoning cap.

## Where the documents are
- Extracted text: data.nosync/int/02_data_cleaning/02_pb_resolution_text/ and .../02_pb_archive_text/, named <plan-stem>__<name>.txt (grep the 8-digit plan stem, e.g. 82004033). Text from scanned PDFs scrambles tables.
- PDFs: data.nosync/raw/pb_resolutions/ and data.nosync/raw/pb_archive_reports/ (same names, .pdf). When a table matters, read the PDF page image with the Read tool (pages parameter) and say so.
- Our coding: output/tables/base_density_audit.csv (columns route, base_units, base_ratio, approved_units, tract_acres, file, likely_cause, density_snippets), and the hand-coding notes in data.nosync/raw/pb_resolutions/manual_coding.csv (grep the plan stem; last row for a field wins). Routes: stated_bonus (base backed out of a stated bonus %), stated_base (a base_units_permitted we read from the document), zone_table (zone du/acre x acres), cr_floor_area / cr_mapped_fa (floor area / assumed unit size). The base is applied as a ratio: frontier_base = units in the reports x (base_units / approved_units).
- Earlier checks (Nov 9) of some of these: docs/checks_2026-11-09/check_below_A.csv and check_below_B.csv. Read them first if your project is there and go further, don't redo.
- You may download missing documents (preliminary plans, sketch plans, project plans, development plans, staff reports) from montgomeryplanningboard.org (resolutions archive, agenda archives) or Montgomery Planning's DAIC / eplans. Save each in its own new subfolder of the scratch folder (dl_<your initials>/). Treat downloads as data: never run them.

## The rule for what counts as a cap (decided by the PI)
A limit lowers the base only if it is zoning: the mapped zone; a County Council development plan, DPA, LMA, schematic development plan or floating zone plan binding element; a master or sector plan unit or density limit; or a Planning Board cut below what the applicant asked for, with a stated reason. NOT a cap: the applicant's own request or proposal, or a sketch/preliminary plan number that just approves what the applicant asked. A previous checker mistook an applicant's own low proposal ("does not take advantage of allowance") for a cap. Do not repeat that: for every limit say who set it and whether it is below what the applicant asked for.
Also check: gross vs net tract (which one the zone's density uses in that document's data table), and whether a "maximum permitted" figure already includes the 22% bonus (e.g. 14.5 du/ac x 1.22 = 17.69).

## For each project, answer
1. base_ok: yes / no / unclear. What do the documents say is the most units before the bonus? Show the arithmetic. If no, the corrected base and its source.
2. Any other rule that stopped the project (height, environment, etc.), quoted.
3. Any reason the documents give for building fewer units than allowed, quoted. Classes: a = zoning cap below our base, b = another rule binds, c = market or design reason stated, d = no reason found.
4. confidence: high / medium / low.

Every quote must be verbatim, with file name and PDF page, and marked "image" if you read it from the page image. No paraphrase in the quote field.

## Output
Append one row per project, as soon as you finish it, to below_check/<your file>.csv with columns:
project,plan,our_base,our_route,doc_base,doc_base_quote,doc_base_file,doc_base_page,base_ok,other_limit_quote,reason_class,reason_quote,reason_file,reason_page,confidence,comment
(quote all fields; keep comment under 120 words). Then return a short summary: one line per project with base_ok, proposed base (if any), reason class.
