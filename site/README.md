# Static site bundle

HTML served by GitHub Pages (or `python scripts/server.py` from the repo root).

Large JSON/CSV files in this folder are **gitignored** (they duplicate `data/` and `outputs/`). After clone, run:

```bash
python scripts/sync_site_assets.py
```

- **Regenerate** the main analysis page: `python scripts/static_analysis_optimized.py`
- **Yearly awards/funding:** `python scripts/build_yearly_funding_stats.py`, then sync copies `yearly_funding_stats.json` into `site/`.
- **CI** runs the static generator, yearly funding build, and `sync_site_assets.py`. The hub stays as `index.html`; CI rankings are at `arc_analysis_optimized.html`.
- **Lead citations:** after `lead_ci_citations_openalex.py`, run `python scripts/generate_grant_summaries.py`, then sync copies lead CSVs and `grant_summaries.json` into `site/` when present.
- **GitHub Pages CDN:** `deploy.yml` substitutes `__GITHUB_RUN_NUMBER__` in `lead_ci_citations_visualization.html`, `arc_yearly_funding_trends.html`, and the hub link so each deploy fetches fresh JSON/CSV. Locally, the placeholder stays in the file (still works). If a cached old page persists in the browser, use a hard refresh or open the URL with any query string (e.g. `?v=1`).
