#!/usr/bin/env python3
"""
Enrich Discovery or Fellowship CSV with approximate lead-holder citations through award year.

Lead ORCID: first entry in `chief_investigators_orcids` (Discovery) or
`fellowship_holders_orcids` (Fellowships), auto-detected from headers.

Uses OpenAlex Author counts_by_year: for funding year Y, citations = sum of cited_by_count
for entries with entry.year <= Y. Award year proxy: funding_commencement_year.

By default rows with funding_commencement_year >= 2010 are enriched; raise the floor with
--min-funding-year to skip older years and reduce API calls.

See https://docs.openalex.org/how-to-use-the-api/rate-limits-and-authentication

Transient failures (timeouts, 429, 5xx) are retried with exponential backoff; HTTP 429
honors Retry-After when present. Tune with --max-retries and --retry-backoff-base.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
import urllib.parse
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))

import paths as P  # noqa: E402
from openalex_retry import fetch_openalex_json  # noqa: E402

NEW_COLUMNS = [
    "lead_ci_orcid",
    "lead_ci_citations_openalex_through_award_year",
    "lead_ci_openalex_author_id",
    "lead_ci_citation_source",
]


def detect_orcid_column(fieldnames: List[str], override: str) -> str:
    if override:
        if override not in fieldnames:
            raise ValueError(f"--orcid-column {override!r} not in CSV headers")
        return override
    if "chief_investigators_orcids" in fieldnames:
        return "chief_investigators_orcids"
    if "fellowship_holders_orcids" in fieldnames:
        return "fellowship_holders_orcids"
    raise ValueError(
        "Could not detect ORCID column: need chief_investigators_orcids or "
        "fellowship_holders_orcids (or pass --orcid-column)"
    )


def lead_orcid(raw: str) -> str:
    if not raw or not str(raw).strip():
        return ""
    first = str(raw).split(";")[0].strip()
    return first


def parse_award_year(raw: str) -> Optional[int]:
    if not raw or not str(raw).strip():
        return None
    try:
        return int(str(raw).strip())
    except ValueError:
        return None


def citations_through_year(counts_by_year: Any, y: int) -> int:
    if not isinstance(counts_by_year, list):
        return 0
    total = 0
    for entry in counts_by_year:
        if not isinstance(entry, dict):
            continue
        ey = entry.get("year")
        if ey is None:
            continue
        try:
            yi = int(ey)
        except (TypeError, ValueError):
            continue
        if yi <= y:
            try:
                total += int(entry.get("cited_by_count") or 0)
            except (TypeError, ValueError):
                pass
    return total


def openalex_author_url(orcid: str) -> str:
    path = f"https://orcid.org/{orcid.strip()}"
    encoded = urllib.parse.quote(path, safe="")
    return f"https://api.openalex.org/authors/{encoded}?select=id,orcid,counts_by_year"


def fetch_author(
    orcid: str,
    mailto: str,
    timeout: float,
    *,
    max_retries: int,
    backoff_base: float,
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    url = openalex_author_url(orcid)
    ua = f"ARC-Crawl-lead-ci-citations/1.0 mailto:{mailto}"
    return fetch_openalex_json(
        url,
        user_agent=ua,
        timeout=timeout,
        max_retries=max_retries,
        backoff_base=backoff_base,
    )


def load_cache(path: Path) -> Dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def save_cache(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    tmp.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=P.DISCOVERY_CSV_2026,
        help="Input Discovery CSV",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=P.DISCOVERY_CSV_LEAD_CITATIONS,
        help="Output CSV path",
    )
    parser.add_argument(
        "--cache",
        type=Path,
        default=P.OPENALEX_AUTHORS_CACHE,
        help="JSON cache of OpenAlex author payloads by ORCID",
    )
    parser.add_argument(
        "--mailto",
        default="",
        help="Contact email for OpenAlex User-Agent (or set OPENALEX_MAILTO)",
    )
    parser.add_argument("--sleep", type=float, default=0.12, help="Seconds between API calls")
    parser.add_argument("--timeout", type=float, default=60.0, help="HTTP timeout seconds")
    parser.add_argument(
        "--max-retries",
        type=int,
        default=8,
        help="Max retries per ORCID after timeouts / 429 / 5xx (default: 8)",
    )
    parser.add_argument(
        "--retry-backoff-base",
        type=float,
        default=15.0,
        help="Base seconds for exponential backoff when no Retry-After (default: 15)",
    )
    parser.add_argument(
        "--limit-rows",
        type=int,
        default=0,
        help="If >0, only process first N data rows (for testing)",
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Re-fetch all ORCIDs even if present in cache",
    )
    parser.add_argument(
        "--cache-only",
        action="store_true",
        help="Do not call OpenAlex; fill from JSON cache only (uncached ORCIDs get empty citation fields)",
    )
    parser.add_argument(
        "--orcid-column",
        default="",
        help="CSV column for lead ORCID list (default: auto from Discovery vs Fellowship headers)",
    )
    parser.add_argument(
        "--min-funding-year",
        type=int,
        default=2010,
        help="Only compute citations for grants with funding_commencement_year >= this (default: 2010)",
    )
    args = parser.parse_args()
    min_year = args.min_funding_year

    if args.cache_only and args.refresh:
        print("Error: --cache-only and --refresh cannot be used together", file=sys.stderr)
        return 2

    mailto = args.mailto or __import__("os").environ.get("OPENALEX_MAILTO", "").strip()
    if not args.cache_only and not mailto:
        print(
            "Warning: pass --mailto or set OPENALEX_MAILTO for polite OpenAlex access.",
            file=sys.stderr,
        )
        mailto = "anonymous@example.com"
    if args.cache_only and not mailto:
        mailto = "unused@cache-only.local"

    if not args.input.is_file():
        print(f"Input not found: {args.input}", file=sys.stderr)
        return 1

    cache = {} if args.refresh else load_cache(args.cache)

    with open(args.input, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            print("Empty CSV", file=sys.stderr)
            return 1
        fieldnames = list(reader.fieldnames)
        try:
            orcid_col = detect_orcid_column(fieldnames, args.orcid_column.strip())
        except ValueError as e:
            print(e, file=sys.stderr)
            return 1
        print(f"Using ORCID column: {orcid_col}", file=sys.stderr)
        for col in NEW_COLUMNS:
            if col not in fieldnames:
                fieldnames.append(col)
        rows: List[Dict[str, str]] = []
        orcid_years: Dict[str, set] = {}
        for i, row in enumerate(reader):
            if args.limit_rows and i >= args.limit_rows:
                break
            oid = lead_orcid(row.get(orcid_col, ""))
            y = parse_award_year(row.get("funding_commencement_year", ""))
            if oid and y is not None and y >= min_year:
                orcid_years.setdefault(oid, set()).add(y)
            rows.append(dict(row))

    unique_orcids = sorted(orcid_years.keys())
    print(
        f"Rows: {len(rows)}, unique lead ORCIDs (for funding year >= {min_year}): {len(unique_orcids)}",
        file=sys.stderr,
    )

    fetched = 0
    errors = 0
    if args.cache_only:
        missing = [o for o in unique_orcids if o not in cache]
        print(
            f"Cache-only mode: {len(unique_orcids) - len(missing)} ORCIDs in cache, "
            f"{len(missing)} not in cache (citation fields left empty for those grants)",
            file=sys.stderr,
        )
    else:
        for idx, oid in enumerate(unique_orcids, start=1):
            need_fetch = args.refresh or oid not in cache
            if need_fetch:
                data, err = fetch_author(
                    oid,
                    mailto,
                    args.timeout,
                    max_retries=args.max_retries,
                    backoff_base=args.retry_backoff_base,
                )
                fetched += 1
                if err:
                    errors += 1
                    print(f"ORCID {oid}: {err}", file=sys.stderr)
                    cache[oid] = {
                        "error": err,
                        "openalex_id": "",
                        "counts_by_year": [],
                    }
                else:
                    cache[oid] = {
                        "openalex_id": (data or {}).get("id") or "",
                        "counts_by_year": (data or {}).get("counts_by_year") or [],
                    }
                if args.sleep > 0:
                    time.sleep(args.sleep)
                if idx % 50 == 0:
                    save_cache(args.cache, cache)
                    print(f"  ... {idx}/{len(unique_orcids)} ORCIDs processed", file=sys.stderr)
            else:
                if idx % 200 == 0:
                    print(f"  ... {idx}/{len(unique_orcids)} (cached)", file=sys.stderr)

        save_cache(args.cache, cache)

    no_orcid = 0
    skipped_low_year = 0
    for row in rows:
        oid = lead_orcid(row.get(orcid_col, ""))
        y = parse_award_year(row.get("funding_commencement_year", ""))
        if not oid or y is None:
            no_orcid += 1
            row["lead_ci_orcid"] = oid
            row["lead_ci_citations_openalex_through_award_year"] = ""
            row["lead_ci_openalex_author_id"] = ""
            row["lead_ci_citation_source"] = ""
            continue
        if y < min_year:
            skipped_low_year += 1
            row["lead_ci_orcid"] = oid
            row["lead_ci_citations_openalex_through_award_year"] = ""
            row["lead_ci_openalex_author_id"] = ""
            row["lead_ci_citation_source"] = ""
            continue
        rec = cache.get(oid)
        if rec is None:
            row["lead_ci_orcid"] = oid
            row["lead_ci_citations_openalex_through_award_year"] = ""
            row["lead_ci_openalex_author_id"] = ""
            row["lead_ci_citation_source"] = ""
            continue
        cby = rec.get("counts_by_year")
        total = citations_through_year(cby, y)
        row["lead_ci_orcid"] = oid
        row["lead_ci_citations_openalex_through_award_year"] = str(total)
        row["lead_ci_openalex_author_id"] = str(rec.get("openalex_id") or "")
        row["lead_ci_citation_source"] = "openalex_counts_by_year"

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    filled = sum(
        1
        for row in rows
        if (row.get("lead_ci_citations_openalex_through_award_year") or "").strip() != ""
    )
    print(
        f"Wrote {args.output} (API fetches: {fetched}, ORCID errors: {errors}, "
        f"rows without ORCID/year: {no_orcid}, skipped year<{min_year}: {skipped_low_year}, "
        f"rows with citation value: {filled}/{len(rows)})",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
