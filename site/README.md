# Static site bundle

HTML served by GitHub Pages (or `python scripts/server.py` from the repo root).

Large JSON/CSV files in this folder are **gitignored** (they duplicate `data/` and `outputs/`). After clone, run:

```bash
python scripts/sync_site_assets.py
```

- **Regenerate** the main analysis page: `python scripts/static_analysis_optimized.py`
- **CI** runs the static generator and `sync_site_assets.py`. The hub stays as `index.html`; CI rankings are at `arc_analysis_optimized.html`.
- **Lead citations:** after `lead_ci_citations_openalex.py`, run `python scripts/generate_grant_summaries.py`, then sync copies lead CSVs and `grant_summaries.json` into `site/` when present.
