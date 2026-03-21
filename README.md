# ARC Research Hub

A comprehensive analysis hub for Australian Research Council (ARC) research data, featuring interactive visualizations and rankings for Discovery Projects and Fellowship schemes from 2010-2025.

## 🌐 Live Demo

**[View the live application](https://ht-timchen.github.io/arc-discovery-analysis/)**

## ✨ Analysis Cards

### 🏛️ Discovery Projects Analysis
- **Interactive stacked bar chart** showing university distribution across Fields of Research (FoR) codes
- **Research patterns** and institutional strengths across academic disciplines
- **Data coverage**: 2010-2025 Discovery Projects with comprehensive FoR code mapping

### 🏆 Fellowship Analysis  
- **Interactive visualization** of ARC Fellowship schemes (DECRA, Future Fellowships, Laureate Fellowships)
- **University distribution** across research areas and fellowship types
- **Data coverage**: 2010-2025 Fellowship data with 5,148 fellowships across 53 universities

### 👥 Chief Investigators Ranking
- **Comprehensive rankings** and performance metrics of Chief Investigators
- **Project details** and research patterns with hierarchical FoR code filtering
- **Data coverage**: Top 5,000 Chief Investigators with detailed project information

### ⚧ Gender Analysis (Experimental)
- **Experimental analysis** of gender distribution among Chief Investigators
- **Three-tier methodology** with web search, AI analysis, and manual review
- **Data coverage**: Chief Investigators with 3+ Discovery Projects

## 📈 Data Coverage

### Discovery Projects (2010-2025)
- **2,735 FoR codes** across all research disciplines
- **Top 5,000 Chief Investigators** with detailed project information
- **Tiered rankings**: Top 50 (broad), Top 30 (4-digit), Top 10 (6-digit)
- **Year-based filtering** for focused analysis

### Fellowship Schemes (2010-2025)
- **5,148 fellowships** across all ARC fellowship types
- **53 universities** with comprehensive coverage
- **290 FoR codes** mapped to fellowship activities
- **DECRA, Future Fellowships, and Laureate Fellowships** included

## 🎯 How to Use

1. **Select a 2-digit FoR code** (e.g., "01 — Pure Mathematics")
2. **Browse related 4-digit codes** that automatically appear
3. **Choose a 4-digit code** to see specific 6-digit options
4. **Apply year filters** to focus on recent projects
5. **Click "View Projects"** to see detailed Chief Investigator profiles

## 🏗️ Architecture

- **Hub Structure**: Central `site/index.html` with navigation to specialized analysis tools (the GitHub Actions deploy replaces this file with the optimized Discovery analysis build, matching previous behaviour)
- **Static Sites**: Each analysis tool is a self-contained HTML file under `site/`; some load JSON/CSV via `fetch()` from the same folder
- **Client-side Processing**: All filtering, ranking, and visualization done in browser
- **No Backend**: Fully self-contained for easy deployment
- **GitHub Pages**: Workflow publishes the `site/` directory only

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

Preview locally (serves `site/` on port 8000):

```bash
python scripts/server.py
```

## 📊 Data Sources

- **ARC Discovery Projects**: Official Australian Research Council data (2010-2025)
- **ARC Fellowship Schemes**: DECRA, Future Fellowships, and Laureate Fellowships data (2010-2025)
- **Field of Research Codes**: Australian and New Zealand Standard Research Classification (ANZSRC)
- **University Data**: Administering organization information from ARC grants database
- **Gender Analysis**: Experimental data with web search, AI analysis, and manual review methodology

## 👨‍💻 Author

**Tim Chen @ Adelaide**  
[Personal Website](https://ht-timchen.github.io/)

---

*Built with modern web technologies for seamless research discovery and analysis.*
