# Static site bundle

HTML served by GitHub Pages (or `python scripts/server.py` from the repo root).

Large JSON/CSV files in this folder are **gitignored** (they duplicate `data/` and `outputs/`). After clone, run:

```bash
python scripts/sync_site_assets.py
```

- **Regenerate** the main analysis page: `python scripts/static_analysis_optimized.py`
- **CI** runs the static generator, `sync_site_assets.py`, then sets `index.html` from `arc_analysis_optimized.html` before deploy.
