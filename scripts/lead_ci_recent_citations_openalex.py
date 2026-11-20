#!/usr/bin/env python3
"""
Add lead-holder "recent citations before application" to the lead-citation CSVs.

For a grant with funding_commencement_year Y (applied for early in Y-1), the new column
`lead_ci_citations_received_3y_pre_application` is the number of citations the lead
ORCID's works RECEIVED in calendar years Y-4, Y-3 and Y-2 (the three full years before
the application), from the live OpenAlex author `counts_by_year`.

Live OpenAlex `counts_by_year.cited_by_count` = citations received in that year, available
from 2012 only, so the column is filled for Y >= 2016 and left blank otherwise.

Fetches go to a separate cache (openalex_authors_live.json); the older cache and the
`lead_ci_citations_openalex_through_award_year` column are left untouched.
"""

from __future__ import annotations

import argparse
import csv
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict, List, Optional

_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))

import paths as P  # noqa: E402
from lead_ci_citations_openalex import load_cache, openalex_author_url, save_cache  # noqa: E402
from openalex_retry import fetch_openalex_json  # noqa: E402

NEW_COLUMN = "lead_ci_citations_received_3y_pre_application"
FIRST_CITATION_YEAR = 2012  # earliest year in live OpenAlex counts_by_year
WINDOW = (4, 2)  # years Y-4 .. Y-2 inclusive


def window_citations(counts_by_year: List[Dict[str, Any]], y: int) -> Optional[int]:
    lo, hi = y - WINDOW[0], y - WINDOW[1]
    if lo < FIRST_CITATION_YEAR:
        return None
    return sum(
        int(e.get("cited_by_count") or 0)
        for e in counts_by_year
        if isinstance(e, dict) and e.get("year") is not None and lo <= int(e["year"]) <= hi
    )


def fetch(orcid: str, timeout: float, max_retries: int, backoff: float, sleep: float) -> Dict[str, Any]:
    data, err = fetch_openalex_json(
        openalex_author_url(orcid),
        user_agent="ARC-Crawl-lead-ci-citations/1.0",
        timeout=timeout,
        max_retries=max_retries,
        backoff_base=backoff,
    )
    if sleep > 0:
        time.sleep(sleep)
    if err:
        return {"error": err, "openalex_id": "", "counts_by_year": []}
    return {
        "openalex_id": (data or {}).get("id") or "",
        "counts_by_year": (data or {}).get("counts_by_year") or [],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--csv",
        type=Path,
        nargs="+",
        default=[P.DISCOVERY_CSV_LEAD_CITATIONS, P.FELLOWSHIP_CSV_LEAD_CITATIONS],
        help="Lead-citation CSVs to update in place (need lead_ci_orcid column)",
    )
    ap.add_argument("--cache", type=Path, default=P.OUTPUTS_CACHE / "openalex_authors_live.json")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--sleep", type=float, default=0.3, help="Seconds each worker waits between calls")
    ap.add_argument("--timeout", type=float, default=60.0)
    ap.add_argument("--max-retries", type=int, default=8)
    ap.add_argument("--retry-backoff-base", type=float, default=15.0)
    ap.add_argument("--cache-only", action="store_true", help="Do not call OpenAlex")
    args = ap.parse_args()

    tables = []
    for path in args.csv:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fields = list(reader.fieldnames or [])
            rows = list(reader)
        if "lead_ci_orcid" not in fields:
            print(f"{path}: no lead_ci_orcid column", file=sys.stderr)
            return 1
        if NEW_COLUMN not in fields:
            fields.append(NEW_COLUMN)
        tables.append((path, fields, rows))

    cache = load_cache(args.cache)
    orcids = sorted({r["lead_ci_orcid"].strip() for _, _, rows in tables for r in rows if r["lead_ci_orcid"].strip()})
    todo = [o for o in orcids if o not in cache or cache[o].get("error")]
    print(f"{len(orcids)} lead ORCIDs, {len(todo)} to fetch", file=sys.stderr)

    if todo and not args.cache_only:
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            results = pool.map(
                lambda o: (o, fetch(o, args.timeout, args.max_retries, args.retry_backoff_base, args.sleep)),
                todo,
            )
            for i, (oid, rec) in enumerate(results, start=1):
                cache[oid] = rec
                if rec.get("error"):
                    print(f"ORCID {oid}: {rec['error']}", file=sys.stderr)
                if i % 200 == 0:
                    save_cache(args.cache, cache)
                    print(f"  ... {i}/{len(todo)} fetched", file=sys.stderr)
        save_cache(args.cache, cache)

    for path, fields, rows in tables:
        filled = 0
        for r in rows:
            oid = r["lead_ci_orcid"].strip()
            rec = cache.get(oid)
            val = None
            if oid and rec and not rec.get("error"):
                try:
                    val = window_citations(rec["counts_by_year"], int(r["funding_commencement_year"]))
                except (TypeError, ValueError):
                    val = None
            r[NEW_COLUMN] = "" if val is None else str(val)
            filled += val is not None
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)
        print(f"{path.name}: {filled}/{len(rows)} rows filled", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
