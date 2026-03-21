#!/usr/bin/env python3
"""Quick checks on lead-citations CSV (run after lead_ci_citations_openalex.py)."""

from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))
import paths as P  # noqa: E402


def main() -> int:
    path = P.DISCOVERY_CSV_LEAD_CITATIONS
    if not path.is_file():
        print(f"Missing {path}", file=sys.stderr)
        return 1

    base = P.DISCOVERY_CSV_2026
    with base.open(encoding="utf-8", newline="") as f:
        base_rows = sum(1 for _ in csv.DictReader(f))

    nonempty = 0
    zero_cit = 0
    by_year: dict[int, list[int]] = defaultdict(list)
    sample_high: list[tuple[str, int, int]] = []

    with path.open(encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        cols = r.fieldnames or []
        for req in (
            "code",
            "funding_commencement_year",
            "lead_ci_citations_openalex_through_award_year",
        ):
            if req not in cols:
                print(f"Missing column {req!r}", file=sys.stderr)
                return 1
        n = 0
        for row in r:
            n += 1
            raw = (row.get("lead_ci_citations_openalex_through_award_year") or "").strip()
            if raw == "":
                continue
            nonempty += 1
            try:
                c = int(raw)
            except ValueError:
                print(f"Non-integer citation row {row.get('code')}: {raw!r}", file=sys.stderr)
                return 1
            if c == 0:
                zero_cit += 1
            try:
                y = int(str(row.get("funding_commencement_year", "")).strip())
            except ValueError:
                continue
            by_year[y].append(c)
            if len(sample_high) < 5 or c > min(t[2] for t in sample_high):
                sample_high.append((row.get("code", ""), y, c))
                sample_high.sort(key=lambda t: t[2], reverse=True)
                sample_high = sample_high[:5]

    if n != base_rows:
        print(f"Row count mismatch: output {n} vs base {base_rows}", file=sys.stderr)
        return 1

    print(f"OK: {n} data rows (matches base Discovery CSV)")
    print(f"Rows with numeric citation field: {nonempty} ({100 * nonempty / n:.1f}%)")
    print(f"  of those, value == 0: {zero_cit}")
    years = sorted(by_year.keys())
    if years:
        print(f"Citation stats by award year (mean | n grants with value) — sample:")
        for y in years[:: max(1, len(years) // 8)]:
            vals = by_year[y]
            m = sum(vals) / len(vals)
            print(f"  {y}: mean={m:.0f}  (n={len(vals)})")
    print("Top 5 by citation (code, year, citations):")
    for code, y, c in sample_high:
        print(f"  {code}  {y}  {c}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
