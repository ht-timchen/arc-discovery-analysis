#!/usr/bin/env python3
"""Aggregate yearly award counts and median funding_at_announcement for DP + fellowship schemes."""

from __future__ import annotations

import csv
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))

import paths as P  # noqa: E402

FUNDING_FIELD = "funding_at_announcement"

# Stable display order for fellowship schemes (portal scheme_name -> id, short label)
SCHEME_ORDER: List[Tuple[str, str, str]] = [
    (
        "Discovery Early Career Researcher Award",
        "decra",
        "DECRA",
    ),
    (
        "ARC Future Fellowships",
        "future",
        "Future Fellowships",
    ),
    (
        "Australian Laureate Fellowships",
        "laureate",
        "Laureate Fellowships",
    ),
    (
        "Industry Laureate Fellowships",
        "industry_laureate",
        "Industry Laureate",
    ),
]


def _parse_year(raw: str) -> Optional[int]:
    raw = (raw or "").strip()
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError:
        return None


def _parse_funding(raw: str) -> Optional[float]:
    raw = (raw or "").strip()
    if not raw:
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def _amounts_by_year(csv_path: Path) -> Dict[int, List[float]]:
    by_year: Dict[int, List[float]] = defaultdict(list)
    with csv_path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            year = _parse_year(row.get("funding_commencement_year", ""))
            amount = _parse_funding(row.get(FUNDING_FIELD, ""))
            if year is None or amount is None:
                continue
            by_year[year].append(amount)
    return by_year


def _amounts_by_year_and_scheme(
    csv_path: Path,
) -> Dict[str, Dict[int, List[float]]]:
    by_scheme: Dict[str, Dict[int, List[float]]] = defaultdict(
        lambda: defaultdict(list)
    )
    with csv_path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            scheme = (row.get("scheme_name") or "").strip()
            year = _parse_year(row.get("funding_commencement_year", ""))
            amount = _parse_funding(row.get(FUNDING_FIELD, ""))
            if not scheme or year is None or amount is None:
                continue
            by_scheme[scheme][year].append(amount)
    return by_scheme


def _series_arrays(
    by_year: Dict[int, List[float]], years: List[int]
) -> Tuple[List[int], List[Optional[float]]]:
    counts: List[int] = []
    medians: List[Optional[float]] = []
    for y in years:
        amounts = by_year.get(y, [])
        counts.append(len(amounts))
        if amounts:
            medians.append(round(statistics.median(amounts), 2))
        else:
            medians.append(None)
    return counts, medians


def build_payload() -> Dict[str, Any]:
    dp_by_year = _amounts_by_year(P.DISCOVERY_CSV_2026)
    fel_by_scheme = _amounts_by_year_and_scheme(P.FELLOWSHIP_CSV)

    all_years = set(dp_by_year)
    for scheme_years in fel_by_scheme.values():
        all_years.update(scheme_years)
    years = sorted(all_years)

    series: List[Dict[str, Any]] = []
    counts, medians = _series_arrays(dp_by_year, years)
    series.append(
        {
            "id": "dp",
            "label": "Discovery Projects",
            "kind": "discovery",
            "counts": counts,
            "medians": medians,
        }
    )

    known_schemes = {name for name, _, _ in SCHEME_ORDER}
    for scheme_name, series_id, label in SCHEME_ORDER:
        counts, medians = _series_arrays(fel_by_scheme.get(scheme_name, {}), years)
        series.append(
            {
                "id": series_id,
                "label": label,
                "kind": "fellowship",
                "scheme_name": scheme_name,
                "counts": counts,
                "medians": medians,
            }
        )

    # Any unexpected scheme names appended at the end
    for scheme_name in sorted(fel_by_scheme):
        if scheme_name in known_schemes:
            continue
        slug = (
            scheme_name.lower()
            .replace(" ", "_")
            .replace("-", "_")
        )
        counts, medians = _series_arrays(fel_by_scheme[scheme_name], years)
        series.append(
            {
                "id": slug,
                "label": scheme_name,
                "kind": "fellowship",
                "scheme_name": scheme_name,
                "counts": counts,
                "medians": medians,
            }
        )

    return {
        "funding_field": FUNDING_FIELD,
        "years": years,
        "series": series,
    }


def main() -> int:
    if not P.DISCOVERY_CSV_2026.is_file():
        print(f"Missing discovery CSV: {P.DISCOVERY_CSV_2026}", file=sys.stderr)
        return 1
    if not P.FELLOWSHIP_CSV.is_file():
        print(f"Missing fellowship CSV: {P.FELLOWSHIP_CSV}", file=sys.stderr)
        return 1

    payload = build_payload()
    P.OUTPUTS_ANALYSIS.mkdir(parents=True, exist_ok=True)
    with P.YEARLY_FUNDING_STATS_JSON.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")
    print(f"Wrote {P.YEARLY_FUNDING_STATS_JSON} ({len(payload['years'])} years, {len(payload['series'])} series)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
