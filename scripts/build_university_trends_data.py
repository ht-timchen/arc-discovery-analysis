#!/usr/bin/env python3
"""Per-grant compact export for the university-by-year trends page (DP + fellowships, with FoR).

FoR codes switch from ANZSRC 2008 (divisions 01-22) to ANZSRC 2020 (divisions 30-52)
around 2022/23. Each grant gets the set of FoR 2020 divisions its codes map to, using the
approximate division-level crosswalk below, so a 2-digit filter spans 2010-2026.
This is NOT the official ABS field-level concordance.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))

import paths as P  # noqa: E402
from build_yearly_funding_stats import SCHEME_ORDER  # noqa: E402

# FoR 2008 division (or 4-digit group, checked first) -> nearest FoR 2020 division.
FOR_2008_TO_2020: Dict[str, str] = {
    "01": "49",  # Mathematical Sciences
    "02": "51",  # Physical Sciences
    "03": "34",  # Chemical Sciences
    "04": "37",  # Earth Sciences
    "05": "41",  # Environmental Sciences
    "06": "31",  # Biological Sciences
    "07": "30",  # Agricultural and Veterinary -> Agricultural, Veterinary and Food
    "08": "46",  # Information and Computing Sciences
    "09": "40",  # Engineering
    # 10 Technology splits across 2020 divisions
    "1001": "30",  # Agricultural Biotechnology
    "1002": "41",  # Environmental Biotechnology
    "1003": "31",  # Industrial Biotechnology
    "1004": "32",  # Medical Biotechnology
    "1005": "40",  # Communications Technologies
    "1006": "40",  # Computer Hardware
    "1007": "40",  # Nanotechnology
    "1099": "40",  # Other Technology
    # 11 Medical and Health Sciences splits into 32 Biomedical/Clinical and 42 Health
    "11": "32",
    "1104": "42",  # Complementary and Alternative Medicine
    "1106": "42",  # Human Movement and Sports Science
    "1110": "42",  # Nursing
    "1117": "42",  # Public Health and Health Services
    "12": "33",  # Built Environment and Design
    "13": "39",  # Education
    "14": "38",  # Economics
    "15": "35",  # Commerce, Management, Tourism and Services
    "16": "44",  # Studies in Human Society -> Human Society
    "17": "52",  # Psychology and Cognitive Sciences -> Psychology
    "18": "48",  # Law and Legal Studies
    "19": "36",  # Creative Arts and Writing
    "20": "47",  # Language, Communication and Culture
    "21": "43",  # History and Archaeology -> History, Heritage and Archaeology
    "22": "50",  # Philosophy and Religious Studies
}

UNKNOWN_ORG = "(not recorded)"

# Group of Eight. "Adelaide University" (UofA + UniSA merger, Go8 member from 2026) is counted as Go8;
# the ARC portal applies that name to some 2024-26 grants.
GO8 = {
    "The Australian National University",
    "The University of Melbourne",
    "The University of Sydney",
    "The University of New South Wales",
    "The University of Queensland",
    "Monash University",
    "The University of Western Australia",
    "The University of Adelaide",
    "Adelaide University",
}

# State/territory of each administering organisation (head office for multi-state bodies,
# e.g. Australian Catholic University -> NSW, CSIRO -> ACT).
ORG_STATE: Dict[str, str] = {
    "The Australian National University": "ACT",
    "University of Canberra": "ACT",
    "Commonwealth Scientific and Industrial Research Organisation": "ACT",
    "The University of Sydney": "NSW",
    "The University of New South Wales": "NSW",
    "Macquarie University": "NSW",
    "University of Technology Sydney": "NSW",
    "Western Sydney University": "NSW",
    "University of Wollongong": "NSW",
    "The University of Newcastle": "NSW",
    "The University of New England": "NSW",
    "Southern Cross University": "NSW",
    "Charles Sturt University": "NSW",
    "Australian Catholic University": "NSW",
    "Garvan Institute of Medical Research": "NSW",
    "Victor Chang Cardiac Research Institute": "NSW",
    "Australian Nuclear Science and Technology Organisation": "NSW",
    "The Australian Museum": "NSW",
    "The University of Melbourne": "VIC",
    "Monash University": "VIC",
    "Deakin University": "VIC",
    "La Trobe University": "VIC",
    "RMIT University": "VIC",
    "Swinburne University of Technology": "VIC",
    "Victoria University": "VIC",
    "Federation University Australia": "VIC",
    "University of Divinity": "VIC",
    "The Walter and Eliza Hall Institute of Medical Research": "VIC",
    "St Vincent's Institute of Medical Research": "VIC",
    "Hudson Institute of Medical Research": "VIC",
    "Macfarlane Burnet Institute for Medical Research and Public Health Ltd.": "VIC",
    "The Florey Institute of Neuroscience and Mental Health": "VIC",
    "MURDOCH CHILDREN'S RESEARCH INSTITUTE": "VIC",
    "Baker IDI Heart and Diabetes Institute": "VIC",
    "The University of Queensland": "QLD",
    "Queensland University of Technology": "QLD",
    "Griffith University": "QLD",
    "James Cook University": "QLD",
    "University of Southern Queensland": "QLD",
    "Central Queensland University": "QLD",
    "University of the Sunshine Coast": "QLD",
    "Bond University": "QLD",
    "Queensland Institute of Medical Research": "QLD",
    "Mater Research Institute": "QLD",
    "The Australian Institute of Marine Science": "QLD",
    "The University of Western Australia": "WA",
    "Curtin University": "WA",
    "Murdoch University": "WA",
    "Edith Cowan University": "WA",
    "The University of Notre Dame Australia": "WA",
    "The University of Adelaide": "SA",
    "Adelaide University": "SA",
    "University of South Australia": "SA",
    "Flinders University": "SA",
    "Torrens University Australia": "SA",
    "University of Tasmania": "TAS",
    "Charles Darwin University": "NT",
    "Batchelor Institute of Indigenous Tertiary Education": "NT",
}


def to_2020_division(code: str) -> Optional[str]:
    div = code[:2]
    if not div.isdigit():
        return None
    if int(div) >= 30:
        return div
    if int(div) >= 23:
        return ""  # legacy RFCD 1998 code (some 2010 DPs); those grants also carry FoR 2008 codes
    return FOR_2008_TO_2020.get(code[:4]) or FOR_2008_TO_2020.get(div)


def _split_codes(raw: str) -> List[str]:
    return [c.strip() for c in (raw or "").split(";") if c.strip()]


def build_payload() -> Dict[str, Any]:
    schemes = [{"id": "dp", "label": "Discovery Projects"}]
    scheme_index = {"Discovery Projects": 0}
    for scheme_name, sid, label in SCHEME_ORDER:
        scheme_index[scheme_name] = len(schemes)
        schemes.append({"id": sid, "label": label})

    orgs: List[str] = []
    org_index: Dict[str, int] = {}
    grants: List[List[Any]] = []
    unmapped: Dict[str, int] = {}

    sources = [(P.DISCOVERY_CSV_2026, None), (P.FELLOWSHIP_CSV, "scheme_name")]
    for csv_path, scheme_col in sources:
        with csv_path.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                scheme = row[scheme_col].strip() if scheme_col else "Discovery Projects"
                if scheme not in scheme_index:
                    print(f"Warning: skipping unknown scheme {scheme!r}", file=sys.stderr)
                    continue
                try:
                    year = int(row["funding_commencement_year"])
                except ValueError:
                    continue
                org = row["administering_organisation"].strip() or UNKNOWN_ORG
                if org not in org_index:
                    org_index[org] = len(orgs)
                    orgs.append(org)
                codes = _split_codes(row.get("for_all_codes", ""))
                divs = set()
                for c in codes:
                    d = to_2020_division(c)
                    if d:
                        divs.add(d)
                    elif d is None:
                        unmapped[c] = unmapped.get(c, 0) + 1
                grants.append(
                    [
                        scheme_index[scheme],
                        org_index[org],
                        year,
                        ";".join(codes),
                        ";".join(sorted(divs)),
                    ]
                )

    if unmapped:
        print(f"Warning: {len(unmapped)} FoR codes not mapped to a 2020 division: "
              f"{sorted(unmapped)[:20]}", file=sys.stderr)

    missing_state = [o for o in orgs if o != UNKNOWN_ORG and o not in ORG_STATE]
    if missing_state:
        print(f"Warning: no state for organisations: {missing_state}", file=sys.stderr)

    return {
        "fields": ["scheme", "org", "year", "for_all_codes", "for_2020_divisions"],
        "schemes": schemes,
        "orgs": orgs,
        "org_meta": [
            {"state": ORG_STATE.get(o, "Unknown"), "go8": o in GO8} for o in orgs
        ],
        "for_2008_to_2020": FOR_2008_TO_2020,
        "grants": grants,
    }


def main() -> int:
    for p in (P.DISCOVERY_CSV_2026, P.FELLOWSHIP_CSV):
        if not p.is_file():
            print(f"Missing input CSV: {p}", file=sys.stderr)
            return 1
    payload = build_payload()
    P.OUTPUTS_ANALYSIS.mkdir(parents=True, exist_ok=True)
    with P.UNIVERSITY_TRENDS_JSON.open("w", encoding="utf-8") as f:
        json.dump(payload, f, separators=(",", ":"))
        f.write("\n")
    print(f"Wrote {P.UNIVERSITY_TRENDS_JSON} ({len(payload['grants'])} grants, "
          f"{len(payload['orgs'])} organisations)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
