# ARC Research Hub

A comprehensive analysis hub for Australian Research Council (ARC) research data, featuring interactive visualizations and rankings for Discovery Projects and Fellowship schemes (fellowships through **2026** commencement where published on the ARC Data Portal).

## 🌐 Live Demo

**[View the live application](https://ht-timchen.github.io/arc-discovery-analysis/)**

## ✨ Analysis Cards

### 🏛️ Discovery Projects Analysis
- **Interactive stacked bar chart** showing university distribution across Fields of Research (FoR) codes
- **Research patterns** and institutional strengths across academic disciplines
- **Data coverage**: 2010-2026 Discovery Projects with comprehensive FoR code mapping

### 🏆 Fellowship Analysis  
- **Interactive visualization** of ARC Fellowship schemes (DECRA, Future Fellowships, Laureate Fellowships)
- **University distribution** across research areas and fellowship types
- **Data coverage**: 2010-2026 Fellowship data with **5,382** funded fellowships (ARC Data Portal), **54** administering organisations in the viz export

### 👥 Chief Investigators Ranking
- **Comprehensive rankings** and performance metrics of Chief Investigators
- **Project details** and research patterns with hierarchical FoR code filtering
- **Data coverage**: Top 5,000 Chief Investigators with detailed project information

### ⚧ Gender Analysis (Experimental)
- **Experimental analysis** of gender distribution among Chief Investigators
- **Three-tier methodology** with web search, AI analysis, and manual review
- **Data coverage**: Chief Investigators with 3+ Discovery Projects

## 📈 Data Coverage

### Discovery Projects (2010-2026)
- **2,735 FoR codes** across all research disciplines
- **Top 5,000 Chief Investigators** with detailed project information
- **Tiered rankings**: Top 50 (broad), Top 30 (4-digit), Top 10 (6-digit)
- **Year-based filtering** for focused analysis

### Fellowship Schemes (2010-2026)
- **5,382 funded fellowships** in the crawl (DECRA, Future, Laureate, Industry Laureate; **2026** cohort is DECRA-only in the portal as of last refresh)
- **54 universities** (administering organisations) in the fellowship visualization export
- **297 FoR codes** mapped to fellowship activities
- **DECRA, Future Fellowships, and Laureate Fellowships** included

## 🎯 How to Use

1. **Select a 2-digit FoR code** (e.g., "01 — Pure Mathematics")
2. **Browse related 4-digit codes** that automatically appear
3. **Choose a 4-digit code** to see specific 6-digit options
4. **Apply year filters** to focus on recent projects
5. **Click "View Projects"** to see detailed Chief Investigator profiles

## 🏗️ Architecture

- **Hub Structure**: Central `site/index.html` links to specialized tools; CI rankings live at `site/arc_analysis_optimized.html` (also linked from the hub)
- **Static Sites**: Each analysis tool is a self-contained HTML file under `site/`; some load JSON/CSV via `fetch()` from the same folder
- **Client-side Processing**: All filtering, ranking, and visualization done in browser
- **No Backend**: Fully self-contained for easy deployment
- **GitHub Pages**: Workflow publishes the `site/` directory only

### GitHub Pages deploy

The workflow [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml) runs on push to `main` / `master`: it builds `arc_analysis_optimized.html`, runs `scripts/sync_site_assets.py`, and publishes the **`site/`** folder with the official **GitHub Actions** Pages flow (`upload-pages-artifact` + `deploy-pages`).

**One-time setup:** In the GitHub repo go to **Settings → Pages → Build and deployment → Source** and choose **GitHub Actions** (not “Deploy from a branch”). If Source is still **main** `/` (root), GitHub serves `README.md` instead of the hub HTML — switch to **GitHub Actions** so the workflow output is what visitors see.

The **lead citations** page loads CSVs from the same origin. Those files are copied into `site/` during the workflow **only if** the enriched inputs exist in the repository:

- `data/discovery/arc_discovery_projects_2010_2026_with_for_lead_citations.csv`
- `data/fellowship/arc_fellowships_lead_citations.csv`

Generate them with `scripts/lead_ci_citations_openalex.py`, run `sync_site_assets.py`, then **commit the `data/...` files** so CI can ship them. (Mirrored `site/*.csv` copies are gitignored on the default branch to avoid duplicates; the deploy job recreates them from `data/`.)

## Repository layout

| Path | Purpose |
|------|---------|
| `scripts/` | Python crawlers, FoR tooling, analysis, and `paths.py` (shared locations) |
| `data/discovery/` | Discovery Projects CSV/JSON (canonical inputs) |
| `data/fellowship/` | Fellowship CSV/JSON |
| `data/reference/` | FoR taxonomy files (`for_codes_flat.json`, etc.) |
| `data/derived/` | Enriched exports (e.g. university-attached Discovery data) |
| `outputs/analysis/` | Plots, `visualization_data.json`, `chief_investigators_data.json`, etc. |
| `outputs/fellowship/` | `fellowship_visualization_data.json` |
| `site/` | HTML dashboards and **copies** of assets needed for static hosting |

Regenerate the main optimized page and refresh synced assets:

```bash
pip install -r requirements.txt
python scripts/static_analysis_optimized.py
python scripts/sync_site_assets.py
```

Refresh **fellowship** extracts from the ARC Data Portal (writes `data/fellowship/arc_fellowships.{csv,json}`), then rebuild viz and sync:

```bash
pip install requests
python scripts/arc_fellowship_crawler.py   # default --year-from 2010
python scripts/process_fellowship_data.py
python scripts/sync_site_assets.py
```

**Lead CI citations (OpenAlex):** citations are computed for grants with **`funding_commencement_year >= 2010`** by default (matches the chart). Use a higher `--min-funding-year` to limit API calls. Build the enriched CSV (uses `outputs/cache/`; pass `--mailto your@email` for OpenAlex), then sync:

```bash
python scripts/lead_ci_citations_openalex.py --mailto your@email
python scripts/lead_ci_citations_openalex.py --mailto your@email --input data/fellowship/arc_fellowships.csv --output data/fellowship/arc_fellowships_lead_citations.csv
python scripts/sync_site_assets.py
```

Use `--cache-only` to apply the existing cache without new API calls. Timeouts and rate limits are handled with retries (`--max-retries`, `--retry-backoff-base`; 429 responses honor `Retry-After` when sent). Open `site/lead_ci_citations_visualization.html` from the hub or directly (grant scheme picker: **DP**, **DECRA**, **other fellowships**, or all three; `scheme_name` in the fellowship CSV; chart uses **year ≥ 2010** by default, same as enrichment).

Preview locally (serves `site/` on port 8000):

```bash
python scripts/server.py
```

## 📊 Data Sources

- **ARC Discovery Projects**: Official Australian Research Council data (2010-2026)
- **ARC Fellowship Schemes**: DECRA, Future Fellowships, Laureate and Industry Laureate data (2010-2026; refreshed from `dataportal.arc.gov.au`)
- **Field of Research Codes**: Australian and New Zealand Standard Research Classification (ANZSRC)
- **University Data**: Administering organization information from ARC grants database
- **Gender Analysis**: Experimental data with web search, AI analysis, and manual review methodology

## 👨‍💻 Author

**Tim Chen @ Adelaide**  
[Personal Website](https://ht-timchen.github.io/)

---

*Built with modern web technologies for seamless research discovery and analysis.*
