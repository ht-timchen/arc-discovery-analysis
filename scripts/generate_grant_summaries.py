#!/usr/bin/env python3
"""Build code -> truncated grant summary JSON for lead_ci_citations_visualization.html."""

from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))

import paths as P  # noqa: E402

DEFAULT_MAX_LEN = 220
NCGP_GRANTS_URL = "https://dataportal.arc.gov.au/NCGP/API/grants"


def _truncate_summary(text: str, max_len: int) -> str:
    s = " ".join(str(text).split())
    if len(s) > max_len:
        return s[: max_len - 1] + "…"
    return s


def fill_missing_from_ncgp_api(out: dict[str, str], max_len: int) -> int:
    """Add entries for codes not yet in ``out`` using list responses (includes grant-summary)."""
    added = 0
    headers = {"User-Agent": "ARC-Crawl/grant-summaries (+https://github.com)"}
    page = 1
    page_size = 1000
    total_pages: int | None = None
    pages_done = 0

    while True:
        qs = urllib.parse.urlencode({"page[number]": page, "page[size]": page_size})
        req = urllib.request.Request(f"{NCGP_GRANTS_URL}?{qs}", headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, json.JSONDecodeError, OSError) as e:
            print(f"NCGP API stopped at page {page}: {e}", file=sys.stderr)
            break
        meta = payload.get("meta") or {}
        if total_pages is None:
            total_pages = max(1, int(meta.get("total-pages") or 1))
        for item in payload.get("data") or []:
            if not isinstance(item, dict):
                continue
            attrs = item.get("attributes") or {}
            code = attrs.get("code")
            summary = attrs.get("grant-summary")
            if not code or not summary:
                continue
            key = str(code).strip()
            if not key or key in out:
                continue
            out[key] = _truncate_summary(summary, max_len)
            added += 1
        pages_done += 1
        if total_pages is not None and page >= total_pages:
            break
        page += 1
        time.sleep(0.15)

    print(
        f"NCGP API: added {added} summaries not present in local JSON ({pages_done} page(s)).",
        file=sys.stderr,
    )
    return added


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-len", type=int, default=DEFAULT_MAX_LEN, help="Max summary characters")
    parser.add_argument(
        "--no-api",
        action="store_true",
        help="Do not call dataportal.arc.gov.au to fill codes missing from local JSON (offline).",
    )
    args = parser.parse_args()
    max_len = max(40, args.max_len)

    out: dict[str, str] = {}
    for src in (P.DISCOVERY_JSON_2026, P.FELLOWSHIP_JSON):
        if not src.is_file():
            print(f"Skip (missing): {src}", file=sys.stderr)
            continue
        try:
            data = json.loads(src.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            print(f"Skip {src}: {e}", file=sys.stderr)
            continue
        if not isinstance(data, list):
            continue
        for rec in data:
            if not isinstance(rec, dict):
                continue
            code = rec.get("code")
            summary = rec.get("summary")
            if not code or not summary:
                continue
            out[str(code).strip()] = _truncate_summary(summary, max_len)

    if not args.no_api:
        fill_missing_from_ncgp_api(out, max_len)

    P.DATA_DERIVED.mkdir(parents=True, exist_ok=True)
    P.GRANT_SUMMARIES_JSON.write_text(
        json.dumps(out, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    print(f"Wrote {len(out)} grant summaries -> {P.GRANT_SUMMARIES_JSON}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
