"""Parse Planning Board resolutions into a site-plan-level table.

Run 02_extract_resolution_text.py first.

Fields are read from the narrative text (opening paragraph and numbered
conditions). The development standards tables come out of pypdf/OCR with
their columns interleaved, so they are only used through labelled snippets.
Every extracted value keeps the sentence it came from (*_src columns) so it
can be checked against the PDF.

What the MPDU simulation needs, and where it comes from:
  * zone: CR-family zones (CR, CRT, CRF, CRN, CRNF, EOF, LSC) are written
    "CRT-1.0, C-0.5, R-0.5, H-55"; the R value is the mapped residential FAR,
    so mapped residential floor area = R x tract area, and res_gfa_ratio =
    (approved residential floor area - Bethesda Overlay Zone density) / mapped
    is 1 + the MPDU bonus used. Other zones (R-200, PD-n,
    RT-n, RNC, TS-R, RMX, CBD ...) are recorded as named; their base density in
    units is in the density snippets.
  * tract area (acres), approved units and residential floor area, MPDU share.
  * resolution_plan: the plan the resolution actually approves. Resolutions
    found by plan-number stem can be a later amendment (e.g. 81999002M for
    target 81999002H); plan_match flags this.

Pre-2008 staff reports (data/int/02_data_cleaning/02_pb_archive_text/, from
10_download_pb_archive_reports.py and 02_extract_resolution_text.py
--archive) are parsed the same way, as doc_type "staff_report". Their file
names carry only the plan stem, so each is tied to the sample projects
(annual-report offerings and Agreements to Build) whose site plan has that
stem (target_plan). An agenda item found by stem can be another plan with the
same number, so a staff report is usable only if it names the project or its
approved units are within 10% of the project's total units (doc_check).
Approved units and MPDUs come from the header's approval statement
("APPLYING FOR: Approval of 255 units ... inclusive of 32 MPDUs") where it
states them (header_units, header_mpdus). A staff report's base is used only
if its approved units come from that statement or are within 10% of the
project's (units_check; 04_build_base_density.py): the base is kept as a
ratio to approved units, and unit counts found elsewhere in the text are
often another phase's.

Hand-checked values in data/raw/pb_resolutions/manual_coding.csv
(file, field, value, note) override the parsed ones.

Output: data/int/02_data_cleaning/03_pb_resolutions_parsed.csv (one row per resolution PDF)

Usage:
  python 03_parse_resolutions.py
"""

import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
TEXT_DIR = ROOT / "data" / "int" / "02_data_cleaning" / "02_pb_resolution_text"
ARCHIVE_TEXT_DIR = ROOT / "data" / "int" / "02_data_cleaning" / "02_pb_archive_text"
OFFERINGS = ROOT / "data" / "int" / "02_data_cleaning" / "01_mpdu_offerings_combined.dta"
AGREEMENTS = ROOT / "data" / "int" / "02_data_cleaning" / "11_agreement_projects.csv"
MANUAL = ROOT / "data" / "raw" / "pb_resolutions" / "manual_coding.csv"
OUT_FILE = ROOT / "data" / "int" / "02_data_cleaning" / "03_pb_resolutions_parsed.csv"

NUM = r"\d{1,3}(?:,\d{3})+|\d+"          # 1,234 or 1234
DEC = r"\d+(?:\.\d+)?"


def num(s):
    return float(s.replace(",", "")) if s else np.nan


def clean(text):
    """Collapse whitespace and fix common OCR confusions in numbers/words."""
    t = text.replace("’", "'").replace("–", "-").replace("—", "-")
    t = re.sub(r"\s+", " ", t)
    t = re.sub(r"(?<=\d) \.(?=\d)|(?<=\d)\. (?=\d)", ".", t)   # "0. 5" -> "0.5"
    t = re.sub(r"\bmm1mum\b|\bminirnum\b|\bmmimum\b", "minimum", t)
    return t


def sentence(t, start, end, width=160):
    return t[max(0, start - width):min(len(t), end + width)].strip()


def first(pattern, t, flags=re.I, group=1):
    m = re.search(pattern, t, flags)
    return (m.group(group), sentence(t, m.start(), m.end())) if m else (None, None)


# ------------------------------------------------------------------------------
# Plan and resolution identifiers
# ------------------------------------------------------------------------------
PLAN_RE = r"Site Plan (?:Amendment )?(?:No\.?|Number)?\s*:?\s*(8\s?-?\s?\d{2}\s?\d{2}\s?\d{3}\s?[0-9A-Z])"


def norm_plan(s):
    return re.sub(r"[\s\-]", "", s.upper()) if s else None


def parse_ids(t, fname):
    target = fname.split("__", 1)[0]
    plan, plan_src = first(PLAN_RE, t)
    plan = norm_plan(plan)
    # filename is cleaner than OCR when it carries the plan number
    fn_plan = re.search(r"(8\d{7}[0-9A-Z])", fname.split("__", 1)[1].replace("-", "").replace(".", ""))
    if fn_plan:
        plan = fn_plan.group(1)
    mcpb, _ = first(r"MCPB\s*(?:No\.?|Number)?\s*:?\s*(\d{2}\s?-\s?\d{2,3})", t)
    head = t[:3000].upper()
    kind = ("staging_allocation" if "STAGING ALLOCATION" in head
            else "correspondence" if "CORRESPONDENCE" in fname.upper()
            else "site_plan")
    return {
        "target_plan": target,
        "resolution_plan": plan,
        "plan_match": plan == target if plan else None,
        "same_project": plan[:8] == target[:8] if plan else None,
        "mcpb_no": mcpb.replace(" ", "") if mcpb else None,
        "doc_type": kind,
        "plan_src": plan_src,
    }


# ------------------------------------------------------------------------------
# Zone
# ------------------------------------------------------------------------------
CR_RE = (r"\b(CRNF|CRT|CRF|CRN|CR|EOF|LSC)\s*-?\s*(" + DEC + r")\s*,?\s*C\s*-?\s*(" + DEC +
         r")\s*,?\s*R\s*-?\s*(" + DEC + r")\s*,?\s*H\s*-?\s*(\d+)")
OTHER_ZONES = (r"R-?200|R-?150|R-?90|R-?60|R-?40|R-?30|R-?20|R-?10|R-?H|RE-?2C|RE-?2|RE-?1|"
               r"RT-?\d+(?:\.\d+)?|THD|TLD|TMD|PD-?\d+|RNC|RDT|RC|TS-?R|TS-?M|TOMX-?\d(?:\.\d)?|"
               r"TMX-?\d?|RMX-?\d[A-Z]?|MXPD|MXTC|MXN|CBD-?R?\d(?:\.\d)?|CBD-?0\.5|I-?1|I-?3|"
               r"O-?M|C-?[1-4]|C-?T|H-?M|MXTC/TDR|PNZ|R-?4plex|R-?MH")


def parse_zone(t):
    out = {}
    crs = list(re.finditer(CR_RE, t, re.I))
    if crs:
        # the most frequent CR zone string is the property's zone; earlier
        # zones in rezoning histories appear less often
        keys = [tuple(m.groups()) for m in crs]
        best = max(dict.fromkeys(keys), key=keys.count)   # ties: first occurrence
        m = crs[keys.index(best)]
        fam, tot, c, r, h = best
        out.update(zone=f"{fam.upper()}-{tot}, C-{c}, R-{r}, H-{h}", zone_family=fam.upper(),
                   cr_total_far=float(tot), cr_c_far=float(c), cr_r_far=float(r),
                   cr_height_ft=float(h), zone_src=sentence(t, m.start(), m.end()),
                   n_zone_strings=len(set(keys)))
        return out
    norm = lambda s: re.sub(r"(?<=[A-Z])-?(?=\d)", "-", s.upper())
    # the zone named in the property description ("... acres of PD-2 zoned-land",
    # "... in the R-200 zone") is the property's own zone
    own = re.search(r"(?:acres|square feet|sf)\s+(?:of\s+(?:land\s+)?)?(?:in\s+the\s+)?(" + OTHER_ZONES
                    + r")[\s-]*(?:zoned|zone\b)", t, re.I)
    zs = list(re.finditer(r"\b(" + OTHER_ZONES + r")\b(?=[\s/,]*(?:and [A-Z0-9\-/ ]+)?\s*(?:zone|zoned|zoning)|\s+Zone)",
                          t, re.I))
    zs += list(re.finditer(r"zoned\s+(" + OTHER_ZONES + r")\b", t, re.I))
    zs.sort(key=lambda g: g.start())
    if own:
        best, m = norm(own.group(1)), own
        keys = [norm(g.group(1)) for g in zs] or [best]
    elif zs:
        # most frequent, ties broken by first occurrence (deterministic)
        keys = [norm(g.group(1)) for g in zs]
        best = max(dict.fromkeys(keys), key=keys.count)
        m = zs[keys.index(best)]
    if own or zs:
        out.update(zone=best, zone_family=re.sub(r"[-\d.]+[A-Z]?$", "", best) or best,
                   zone_src=sentence(t, m.start(), m.end()), n_zone_strings=len(set(keys)))
    return out


# ------------------------------------------------------------------------------
# Area, units, floor area, MPDUs, method, density snippets
# ------------------------------------------------------------------------------
DECISION_RE = (r"NOW,? THEREFORE|BE IT (?:FURTHER )?RESOLVED|hereby approves|"
               r"Planning Board APPROVES|approves Site Plan")


def split_decision(t):
    """(recitals, decision). Amendments recite every earlier approval before
    the decision, so values are searched in the decision part first."""
    m = re.search(DECISION_RE, t, re.I)
    return (t[:m.start()], t[m.start():]) if m else ("", t)


def first_scoped(pattern, scopes, flags=re.I):
    for s in scopes:
        v, src = first(pattern, s, flags)
        if v is not None:
            return v, src
    return None, None


def parse_quantities(t):
    out = {}
    recitals, decision = split_decision(t)
    out["has_decision_clause"] = bool(recitals)
    scopes = [decision, t]

    # tract area: labelled first, then the opening "on X acres" phrase
    v, src = first(r"tract area[^.;]{0,60}?(" + DEC + r")\s*(?:ac\b|acres)", t)
    if v is None:
        v, src = first(r"tract area[^.;]{0,40}?(" + NUM + r")\s*(?:sq\.? ?ft|square feet|s\.f\.)", t)
        if v is not None:
            v = str(num(v) / 43560)
    if v is None:
        v, src = first(r"\bon (?:approximately |about )?(" + DEC + r")\s*(?:gross )?acres", t)
    if v is None:
        v, src = first(r"(" + DEC + r")\s*acres", t)
    out["tract_acres"], out["tract_acres_src"] = (float(v) if v else np.nan), src

    # approved dwelling units: the decision's opening sentence, then its
    # Density condition, then anywhere in the decision, then the recitals
    unit_pats = [
        r"(?:limited to|up to|maximum of|not (?:to )?exceed|total of|consisting of)\s+"
        r"(?:a maximum of\s+)?(" + NUM + r")\s+(?:new\s+)?(?:residential\s+|multi-?family\s+|"
        r"multiple-?family\s+|single-?family\s+|one-?family\s+|(?:attached|detached)\s+|"
        r"townhouse\s+|dwelling\s+)*(?:dwelling\s+)?(?:units|lots)",
        r"(" + NUM + r")\s+(?:new\s+)?(?:residential\s+|multi-?family\s+|one-?family\s+|"
        r"dwelling\s+)*(?:dwelling\s+)?(?:units|lots)\b",
    ]
    dens = re.search(r"\bDensity\b(?! &).{0,600}", decision, re.I)
    v = src = None
    for scope in [decision[:1500]] + ([dens.group(0)] if dens else []) + scopes:
        for p in unit_pats:
            for m in re.finditer(p, scope, re.I):
                if num(m.group(1)) >= 2 and not re.search(r"Phase|MCPB|Page", scope[max(0, m.start() - 60):m.start()]):
                    v, src = m.group(1), sentence(scope, m.start(), m.end())
                    break
            if v:
                break
        if v:
            break
    out["approved_units"], out["approved_units_src"] = (num(v) if v else np.nan), src

    # residential floor area
    v, src = first_scoped(r"(" + NUM + r")\s*(?:gross\s+)?(?:sq(?:uare)?\.?\s*f(?:ee)?t\.?|s\.f\.|SF)\s+of\s+"
                          r"(?:total\s+)?(?:multi-?family\s+)?residential", scopes)
    out["approved_res_gfa_sf"], out["approved_res_gfa_src"] = (num(v) if v else np.nan), src

    # MPDU share: every percentage attached to "MPDU"; the first one in the
    # decision is the approved share (the MPDU condition), recitals otherwise
    pcts = []
    for scope in scopes:
        for m in re.finditer(r"(" + DEC + r")\s*(?:%|percent|per cent)\s*(?:of\s+the\s+(?:total\s+)?"
                             r"(?:number\s+of\s+)?(?:dwelling\s+)?units\s+(?:as\s+)?)?(?:MPDU|Moderately)",
                             scope, re.I):
            p = float(m.group(1))
            if 5 <= p <= 100:
                pcts.append((p, sentence(scope, m.start(), m.end())))
        if pcts:
            break
    if pcts:
        vals = [p for p, _ in pcts]
        out["mpdu_pct"], out["mpdu_pct_src"] = pcts[0]
        out["mpdu_pct_all"] = ";".join(sorted({f"{p:g}" for p in vals}, key=float))
    v, src = first_scoped(r"(" + NUM + r")\s+(?:on-?site\s+)?(?:MPDUs|Moderately Priced Dwelling Units)", scopes)
    out["mpdu_count"], out["mpdu_count_src"] = (num(v) if v else np.nan), src

    out["optional_method"] = len(re.findall(r"optional method", t, re.I))
    out["standard_method"] = len(re.findall(r"standard method", t, re.I))

    # density language: kept as snippets for coding base density by hand
    snips = []
    for m in re.finditer(r"(?:base density|bonus density|density bonus|MPDU bonus|"
                         r"maximum (?:permitted |allowed )?density|units per acre|"
                         r"dwelling units per acre|du/ac|mapped density)", t, re.I):
        snips.append(sentence(t, m.start(), m.end(), 200))
    out["n_density_snippets"] = len(snips)
    out["density_snippets"] = " || ".join(dict.fromkeys(snips))[:4000]
    v, src = first(r"(" + DEC + r")\s*(?:dwelling\s+)?(?:units per acre|du/ac)", t)
    out["units_per_acre"], out["units_per_acre_src"] = (float(v) if v else np.nan), src
    v, src = first(r"(?:bonus density|density bonus)[^.]{0,80}?(" + DEC + r")\s*(?:%|percent)", t)
    out["bonus_pct"], out["bonus_pct_src"] = (float(v) if v else np.nan), src
    return out


OLD_PLAN_RE = r"\b(8)-(\d{2})(\d{3})([A-Z]?)\b"


def name_key(s):
    s = re.sub(r"\b(the|at|phase|ph|section)\b", " ", str(s or "").lower())
    return re.sub(r"[^a-z0-9]", "", s)


def sample_projects():
    """Site plan, name and total units of every sample project."""
    off = pd.read_stata(OFFERINGS)
    off = off[off["site_plan"] != ""]
    rows = [(sp.strip(), r.project_name, r.aka, r.total_units, r.total_mpdus)
            for r in off.itertuples() for sp in r.site_plan.split("/")]
    if AGREEMENTS.exists():
        ag = pd.read_csv(AGREEMENTS, dtype={"site_plan": str})
        ag = ag[ag["site_plan"].notna()]
        rows += [(r.site_plan, r.project_name, r.aka, r.total_units, r.mpdus) for r in ag.itertuples()]
    return pd.DataFrame(rows, columns=["site_plan", "name", "aka", "total_units", "total_mpdus"])


UNIT_WORDS = (r"(?:dwelling\s+units?|units?|townhouses?|town\s*homes?|"
              r"one[- ]family\s+(?:detached|attached)(?:\s+(?:dwelling\s+)?units?)?|"
              r"single[- ]family\s+(?:detached|attached)(?:\s+units?)?|multi-?family\s+(?:condominium\s+)?(?:dwelling\s+)?units?|"
              r"garden\s+apartments?|apartments?|condominiums?|duplex(?:es)?(?:\s+units)?|lots?)")


def staff_header(raw):
    """The approval requested in a staff report's header (APPLYING FOR,
    STAFF RECOMMENDATION, ...), first two pages."""
    h = clean(" ".join(raw.split("\f")[:2]))
    m = re.search(r"(?:APPLYING FOR|STAFF RECOMMENDATION|REQUEST)\s*:?\s*(.{0,400})", h, re.I)
    return m.group(1) if m else ""


NUMBER_WORDS = {w: i for i, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen "
    "sixteen seventeen eighteen nineteen twenty".split())}


def header_zone(raw):
    """Zone named on the header's ZONE line."""
    h = clean(" ".join(raw.split("\f")[:2]))
    m = re.search(r"\bZONE\s*:\s*(.{0,60})", h)
    if not m:
        return None
    seg = m.group(1)
    cr = re.search(CR_RE, seg, re.I)
    if cr:
        return None   # CR zones: leave to parse_zone, which reads their FARs
    z = re.search(rf"\b({OTHER_ZONES})\b", seg, re.I)
    if not z:
        return None
    # TDR overlays ("R-200 TDR-6", "R-200/TDR") take density from TDRs: keep the marker
    tdr = re.match(r"\s*[/ ]\s*TDR", seg[z.end():], re.I)
    return z.group(1).upper() + ("/TDR" if tdr else "")


def header_counts(s):
    """(total units, MPDUs, acres) from e.g. 'Approval of 255 units: 145 single
    family detached and 110 townhouses inclusive of 32 MPDUs on 47 acres'.
    Lots count only when no dwelling units are named."""
    s = re.split(r"(?i)\b(?:PROJECT NAME|REVIEW BASIS|with the following|subject to)\b", s)[0]
    words = "|".join(NUMBER_WORDS)
    mp = re.search(rf"\(?({NUM}|{words})\)?\s*(?:moderately priced dwelling units|MPDU\W{{0,2}}s?)\b", s, re.I)
    mp = (num(mp.group(1)) if mp.group(1)[0].isdigit() else NUMBER_WORDS[mp.group(1).lower()]) if mp else np.nan
    pct = re.search(r"(\d{1,2}(?:\.\d)?)\s*%\s*(?:\(\d+\)\s*)?(?:moderately priced|MPDU)", s, re.I)
    pct = float(pct.group(1)) if pct else np.nan
    ac = re.search(rf"(\d*\.\d+|{DEC})\s*(?:gross\s+|net\s+)?acres", s, re.I)
    ac = float(ac.group(1)) if ac else np.nan
    parts = [(num(n), w.lower()) for n, w in re.findall(rf"\(?({NUM})\)?\s+(?:new\s+)?({UNIT_WORDS})", s, re.I)]
    units = [n for n, w in parts if not w.startswith("lot")] or [n for n, w in parts]
    if not units:
        return np.nan, mp, ac, pct
    # "255 units: 145 SFD and 110 TH" -> 255 (the parts add up to the first);
    # "6 SFD, 139 SFA and 45 MF" -> their sum
    total = units[0] if len(units) > 1 and sum(units[1:]) == units[0] else (
        units[0] if len(units) == 1 else max(units[0], sum(units)))
    return total, mp, ac, pct


def parse_archive(projects):
    """Staff report rows, one per sample project sharing the file's plan stem."""
    rows = []
    for path in sorted(ARCHIVE_TEXT_DIR.glob("*.txt")):
        raw = path.read_text(encoding="utf-8")
        t = clean(raw)
        stem, pdf = path.stem[:8], path.stem + ".pdf"
        head = t[:4000]
        plan = first(PLAN_RE, head)[0]
        plan = norm_plan(plan) if plan else None
        if not plan:
            m = re.search(OLD_PLAN_RE, head)
            if m:   # 8-03010A -> 82003010A
                yy = int(m.group(2))
                plan = f"8{'19' if yy >= 50 else '20'}{m.group(2)}{m.group(3)}{m.group(4) or '0'}"
        base = {"file": pdf, "n_pages": raw.count("\f") + 1, "n_words": len(t.split()),
                "resolution_plan": plan, "mcpb_no": None, "doc_type": "staff_report", "plan_src": None}
        base.update(parse_zone(t))
        base.update(parse_quantities(t))
        # the header's approval statement beats the general search, whose
        # unit counts in staff reports often come from other plans or phases
        hdr = staff_header(raw)
        h_units, h_mpdus, h_acres, h_pct = header_counts(hdr)
        h_zone = header_zone(raw)
        base.update(header=hdr[:200], header_units=h_units, header_mpdus=h_mpdus,
                    header_acres=h_acres, header_zone=h_zone)
        if pd.notna(h_units):
            base["approved_units"] = h_units
            if pd.notna(h_mpdus):
                base["mpdu_count"] = h_mpdus
                base["mpdu_pct"] = 100 * h_mpdus / h_units
            elif pd.notna(h_pct):
                base["mpdu_pct"] = h_pct
        # the header's acreage and zone describe the application itself; the
        # general search can pick up other parcels and rezoning histories
        if pd.notna(h_acres):
            base["tract_acres"] = h_acres
        if h_zone:
            base["zone"] = h_zone
            base["zone_family"] = re.match(r"[A-Z]+", h_zone).group(0)
        text_key = name_key(head)
        for _, pr in projects[projects["site_plan"].str[:8] == stem].drop_duplicates("site_plan").iterrows():
            names = [k for k in (name_key(pr["name"]), name_key(pr["aka"])) if len(k) >= 5]
            named = any(k in text_key for k in names)
            units_ok = (pd.notna(base.get("approved_units")) and pd.notna(pr["total_units"])
                        and abs(base["approved_units"] - pr["total_units"]) <= 0.1 * pr["total_units"])
            rows.append({**base, "target_plan": pr["site_plan"],
                         "plan_match": plan == pr["site_plan"] if plan else None,
                         "same_project": plan[:8] == stem if plan else None,
                         "doc_check": "name" if named else "units" if units_ok else "",
                         "units_check": bool(units_ok) or pd.notna(h_units),
                         "project_mpdu_pct": (100 * pr["total_mpdus"] / pr["total_units"]
                                              if pd.notna(pr["total_units"]) and pr["total_units"] else np.nan)})
    return pd.DataFrame(rows)


def apply_manual(df):
    if not MANUAL.exists():
        df["manual"] = False
        return df
    man = pd.read_csv(MANUAL, dtype=str)
    df["manual"] = False
    for r in man.itertuples(index=False):
        i = df.index[df["file"] == r.file]
        if len(i) == 0:
            raise ValueError(f"manual_coding.csv: no parsed row for {r.file}")
        v = r.value  # an empty value clears a wrongly parsed field
        if r.field not in df.columns:
            df[r.field] = np.nan
        if pd.isna(v):
            v = np.nan
        elif pd.api.types.is_numeric_dtype(df[r.field]):
            try:
                v = float(v)
            except ValueError:
                df[r.field] = df[r.field].astype(object)
        df.loc[i, r.field] = v
        df.loc[i, "manual"] = True
    return df


def main():
    rows = []
    for path in sorted(TEXT_DIR.glob("*.txt")):
        raw = path.read_text(encoding="utf-8")
        t = clean(raw)
        pdf = path.stem + ".pdf"
        row = {"file": pdf, "n_pages": raw.count("\f") + 1, "n_words": len(t.split())}
        row.update(parse_ids(t, pdf))
        row.update(parse_zone(t))
        row.update(parse_quantities(t))
        rows.append(row)
    df = pd.DataFrame(rows)
    arch = parse_archive(sample_projects()) if ARCHIVE_TEXT_DIR.exists() else pd.DataFrame()
    df = pd.concat([df, arch], ignore_index=True)

    # usable: the resolution speaks to the project's residential program;
    # hand coding sets 0 for parking, public-space, amenity-fund, enforcement
    # and similar amendments. Staff reports: only if checked against the project.
    df["usable"] = ((df["doc_type"] == "site_plan")
                    | ((df["doc_type"] == "staff_report") & df.get("doc_check", "").fillna("").ne(""))
                    ).astype(float)
    df["max_units_permitted"] = np.nan    # zone maximum incl. MPDU bonus, where stated
    df["base_units_permitted"] = np.nan   # maximum before any MPDU bonus, where stated
    df["boz_density_sf"] = np.nan         # Bethesda Overlay Zone density allocated
    df = apply_manual(df)
    # mapped residential floor area for CR-family zones, using the hand-coded
    # tract area and zone where they override the parsed ones. Bethesda
    # Overlay Zone density is bought separately, so it is taken out before
    # comparing approved to mapped residential floor area (the MPDU bonus).
    df["mapped_res_gfa_sf"] = df["cr_r_far"] * df["tract_acres"] * 43560
    df["res_gfa_ratio"] = ((df["approved_res_gfa_sf"] - df["boz_density_sf"].fillna(0))
                           / df["mapped_res_gfa_sf"])

    src_cols = [c for c in df.columns if c.endswith("_src") or c == "density_snippets"]
    df = df[[c for c in df.columns if c not in src_cols] + src_cols]
    df.to_csv(OUT_FILE, index=False)

    print(f"documents parsed: {len(df)} (staff report rows: {(df['doc_type'] == 'staff_report').sum()}, "
          f"usable: {int(df.loc[df['doc_type'] == 'staff_report', 'usable'].sum())})")
    print(f"  doc types: {df['doc_type'].value_counts().to_dict()}")
    print(f"  plan matches target: {df['plan_match'].eq(True).sum()}  "
          f"(same project, other amendment: {(df['same_project'].eq(True) & df['plan_match'].eq(False)).sum()})")
    for c in ["zone", "cr_r_far", "tract_acres", "approved_units", "approved_res_gfa_sf",
              "mpdu_pct", "mpdu_count", "units_per_acre", "bonus_pct"]:
        print(f"  {c:22s} {df[c].notna().sum():4d} / {len(df)}")
    print(f"[saved] {OUT_FILE}")


if __name__ == "__main__":
    main()
