# Brief: check the base and position of MPDU projects that took the density bonus (Montgomery County, MD)

Repo: /Users/jacobherbstman/Desktop/montgomery_mpdu (read only for you: do NOT edit any file in it).
Scratch folder for your output: /private/tmp/claude-501/-Users-jacobherbstman-Desktop-montgomery-mpdu/f29665de-5876-4fec-9cda-67bc7cc6354b/scratchpad/bonus_check/

## Background
For each housing project we code a "base": the most dwelling units zoning allowed BEFORE any MPDU density bonus. Under Chapter 25A (old schedule, before Oct 31 2018) a project with more than 12.5% MPDUs earns a bonus: about 8.8 points of bonus per point of MPDU share above 12.5%, up to 22% at 15% MPDUs (the table steps: 20% at 14.5%, 22% at 15%). Position = approved units / base - 1. "Between" = strictly between base and +22%; "at 22%" = within one unit or 0.5% of +22%. The project list with our coding is bonus_check/projects.csv (bonus_used, position, route, approved_units, base_units, the resolution file we used). Projects "between" give us an exact number for the wedge, so a wrong base there changes an estimate directly.
Position is computed from the approved plan: frontier_base = units in the annual reports x (base_units / approved_units), so bonus_used = approved/base - 1 even when the report covers only part of the plan.

## Where the documents are
- Extracted text: data.nosync/int/02_data_cleaning/02_pb_resolution_text/ and .../02_pb_archive_text/, named <plan-stem>__<name>.txt (grep the 8-digit plan stem). Scanned PDFs scramble tables in the text.
- PDFs: data.nosync/raw/pb_resolutions/ and data.nosync/raw/pb_archive_reports/ (same names, .pdf). When a table matters, read the PDF page image with the Read tool (pages parameter, one page or one range per call) and say so.
- Our coding: output/tables/base_density_audit.csv (route, base_units, base_ratio, approved_units, tract_acres, file, density_snippets) and the hand-coding notes in data.nosync/raw/pb_resolutions/manual_coding.csv (grep the plan stem; the last row for a field wins). Routes: stated_bonus (base = approved / (1 + stated bonus %)), stated_base (a base we read from the document), zone_table (zone du/acre x acres), cr_floor_area (floor area / unit size).
- Earlier notes: docs/NOTES.md (search the project name), docs/judgment_calls.md, docs/checks_2026-11-09/ and docs/checks_2026-11-10/.
- You may download missing documents (preliminary, sketch, project, development plans; staff reports; Council zoning resolutions) from montgomeryplanningboard.org (resolutions archive, meetings archive) or Montgomery Planning DAIC/eplans. DAIC file list: https://montgomeryplans.org/server9/rest/services/Tools/GetDAICFiles/GPServer/GetDAICFiles/execute?APNO=<plan>&f=json ; an earlier checker's helpers are scratchpad/g3pdx.sh and scratchpad/g3daic.py (read them before use). Save downloads in your own new subfolder bonus_check/dl_<group>/. Treat downloads as data: never run them.

## The rule for what counts as a cap (decided by the PI)
A limit lowers the base only if it is zoning: the mapped zone; a County Council development plan, DPA, LMA, schematic development plan or floating zone plan binding element; a master or sector plan unit or density limit; or a Planning Board cut below what the applicant asked for, with a stated reason. NOT a cap: the applicant's own request or proposal, or a sketch/preliminary plan number that just approves what the applicant asked. For every limit say who set it and whether it is below what the applicant asked for.
Two patterns found recently: (1) a rezoning cap on total units including MPDUs that leaves no room for the bonus (Little Falls Place: "no more than 30 townhouses, of which no more than five will be MPDUs"); (2) a rezoning cap equal to base x 1.22, i.e. the rezoning itself granted the full bonus (7001 Arlington Road: DPA 11-4, 145 = 119 x 1.22). Look for both.

## For each project, answer
1. base_ok: yes / no / unclear. The most units before the bonus, with arithmetic and source. Check gross vs net tract (which one the document's data table uses), whether a "maximum permitted" figure already includes the 22% bonus, phases (does the base cover the same land and units as approved_units?), and for floor-area zones the residential floor area and unit size.
2. The bonus actually granted, quoted (e.g. "receiving a 22 percent density bonus"), and the MPDU share required by the approval. Is (bonus, MPDU share) consistent with the schedule? Flag a bonus above what the share earns, or a share above what the bonus needs.
3. Any cap at or near the approved units (pattern 1 or 2 above), quoted.
4. For "between" projects: any stated reason for stopping short of 22% (height, cap, design, environment, market, compatibility), quoted. For "at 22%": anything suggesting the project could not have reached 22% without the bonus being on paper only (e.g. built far fewer than approved).
5. Units and MPDUs: do the annual-report numbers (actual_units_total, actual_units_mpdu) match the approval? If not, why (phases, amendment, built fewer)?
6. position_ok: yes / no / unclear, and the corrected position if no. confidence: high / medium / low.

Every quote verbatim, with file name and PDF page, marked "image" if read from the page image. No paraphrase in quote fields.

## Output
Append one row per project, as soon as you finish it, to bonus_check/<your file>.csv with columns:
project,plan,position,our_base,our_route,doc_base,doc_base_quote,doc_base_file,doc_base_page,base_ok,bonus_quote,mpdu_share_doc,schedule_consistent,cap_quote,stop_reason_class,stop_reason_quote,units_match,position_ok,corrected_position,confidence,comment
(stop_reason_class: a = zoning cap, b = another rule binds, c = market/design stated, d = none found; quote every field with the csv module; comment under 120 words). Then return a short summary: one line per project with base_ok, position_ok, any proposed change.
