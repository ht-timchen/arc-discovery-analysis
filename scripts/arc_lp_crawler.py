#!/usr/bin/env python3
"""Crawl funded Linkage Projects from the ARC NCGP list API (no per-grant detail fetch)."""

from __future__ import annotations

import argparse
import csv
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))
import paths as P  # noqa: E402

API_BASE = "https://dataportal.arc.gov.au/NCGP/API/grants"

CSV_FIELDS = [
    "code",
    "scheme_name",
    "funding_commencement_year",
    "grant_status",
    "funding_at_announcement",
    "funding_current",
    "administering_organisation",
]


def fetch_page(
    page_number: int,
    page_size: int = 1000,
    filter_q: str = "LP",
) -> Dict[str, Any]:
    params = {
        "page[number]": str(page_number),
        "page[size]": str(page_size),
        "filter": filter_q,
    }
    url = f"{API_BASE}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": "arc-lp-crawler/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code} fetching {url}") from e


def is_linkage_project(attributes: Dict[str, Any]) -> bool:
    return (attributes.get("scheme-name") or "").strip().lower() == "linkage projects"


def is_funded(attributes: Dict[str, Any]) -> bool:
    for key in ("announced-funding-amount", "current-funding-amount"):
        try:
            val = attributes.get(key)
            if isinstance(val, (int, float)) and float(val) > 0:
                return True
        except Exception:
            continue
    return False


def row_from_list_attributes(attributes: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "code": attributes.get("code"),
        "scheme_name": attributes.get("scheme-name"),
        "funding_commencement_year": attributes.get("funding-commencement-year"),
        "grant_status": attributes.get("grant-status"),
        "funding_at_announcement": attributes.get("announced-funding-amount"),
        "funding_current": attributes.get("current-funding-amount"),
        "administering_organisation": attributes.get("current-admin-organisation")
        or attributes.get("administering-organisation"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Crawl ARC Linkage Projects (list endpoint only) for yearly trends"
    )
    parser.add_argument("--out-csv", default=str(P.LINKAGE_CSV), help="Output CSV path")
    parser.add_argument("--max-pages", type=int, default=None, help="Limit pages (testing)")
    parser.add_argument("--page-size", type=int, default=1000, help="List page size")
    parser.add_argument(
        "--year-from",
        type=int,
        default=2010,
        help="Only include funding-commencement-year >= this year (default: 2010)",
    )
    parser.add_argument(
        "--year-to",
        type=int,
        default=None,
        help="Only include funding-commencement-year <= this year",
    )
    args = parser.parse_args()

    out_path = Path(args.out_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    rows: List[Dict[str, Any]] = []
    page = 1
    total_pages: Optional[int] = None

    print("Crawling Linkage Projects (filter=LP, list only)...", file=sys.stderr)
    while True:
        if args.max_pages and page > args.max_pages:
            break
        data = fetch_page(page, args.page_size)
        meta = data.get("meta", {})
        if total_pages is None:
            total_pages = meta.get("total-pages")
            print(
                f"Portal reports total-size={meta.get('total-size')} pages={total_pages}",
                file=sys.stderr,
            )
        items = data.get("data", [])
        if not items:
            break
        for item in items:
            attributes = item.get("attributes", {}) or {}
            if not is_linkage_project(attributes):
                continue
            year = attributes.get("funding-commencement-year") or 0
            if args.year_from and year < args.year_from:
                continue
            if args.year_to and year > args.year_to:
                continue
            if not is_funded(attributes):
                continue
            rows.append(row_from_list_attributes(attributes))
        if page % 5 == 0:
            print(f"Scanned page {page}/{total_pages or '?'}; kept {len(rows)}", file=sys.stderr)
        page += 1
        if total_pages and page > total_pages:
            break

    rows.sort(
        key=lambda r: (
            r.get("funding_commencement_year") or 0,
            r.get("code") or "",
        )
    )

    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} Linkage Projects to {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
