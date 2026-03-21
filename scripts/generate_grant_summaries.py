#!/usr/bin/env python3
"""Build code -> truncated grant summary JSON for lead_ci_citations_visualization.html."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))

import paths as P  # noqa: E402

DEFAULT_MAX_LEN = 220


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-len", type=int, default=DEFAULT_MAX_LEN, help="Max summary characters")
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
            s = " ".join(str(summary).split())
            if len(s) > max_len:
                s = s[: max_len - 1] + "…"
            out[str(code)] = s

    P.DATA_DERIVED.mkdir(parents=True, exist_ok=True)
    P.GRANT_SUMMARIES_JSON.write_text(
        json.dumps(out, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    print(f"Wrote {len(out)} grant summaries -> {P.GRANT_SUMMARIES_JSON}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
