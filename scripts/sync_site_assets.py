#!/usr/bin/env python3
"""Copy canonical data and viz outputs into site/ for static hosting (fetch() paths stay flat)."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))

from paths import (  # noqa: E402
    DISCOVERY_CSV_2026,
    DISCOVERY_CSV_LEAD_CITATIONS,
    FELLOWSHIP_CSV_LEAD_CITATIONS,
    FELLOWSHIP_VIZ_DATA_JSON,
    FOR_CODES_FLAT,
    GRANT_SUMMARIES_JSON,
    SITE_DIR,
    SITE_DISCOVERY_CSV,
    SITE_FELLOWSHIP_LEAD_CITATIONS_CSV,
    SITE_FELLOWSHIP_VIZ_DATA,
    SITE_FOR_CODES_FLAT,
    SITE_GRANT_SUMMARIES_JSON,
    SITE_LEAD_CITATIONS_CSV,
    SITE_VISUALIZATION_DATA,
    VISUALIZATION_DATA_JSON,
)


def main() -> None:
    SITE_DIR.mkdir(parents=True, exist_ok=True)
    pairs = [
        (DISCOVERY_CSV_2026, SITE_DISCOVERY_CSV),
        (DISCOVERY_CSV_LEAD_CITATIONS, SITE_LEAD_CITATIONS_CSV),
        (FELLOWSHIP_CSV_LEAD_CITATIONS, SITE_FELLOWSHIP_LEAD_CITATIONS_CSV),
        (FOR_CODES_FLAT, SITE_FOR_CODES_FLAT),
        (GRANT_SUMMARIES_JSON, SITE_GRANT_SUMMARIES_JSON),
        (VISUALIZATION_DATA_JSON, SITE_VISUALIZATION_DATA),
        (FELLOWSHIP_VIZ_DATA_JSON, SITE_FELLOWSHIP_VIZ_DATA),
    ]
    for src, dest in pairs:
        if src.is_file():
            shutil.copy2(src, dest)
            print(f"Copied {src} -> {dest}")
        else:
            print(f"Skip (missing): {src}")


if __name__ == "__main__":
    main()
