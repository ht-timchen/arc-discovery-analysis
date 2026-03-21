"""Repository root and standard data / site paths for CLI scripts."""

from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = _SCRIPT_DIR.parent

DATA = REPO_ROOT / "data"
DATA_DISCOVERY = DATA / "discovery"
DATA_FELLOWSHIP = DATA / "fellowship"
DATA_REFERENCE = DATA / "reference"
DATA_DERIVED = DATA / "derived"

OUTPUTS = REPO_ROOT / "outputs"
OUTPUTS_ANALYSIS = OUTPUTS / "analysis"
OUTPUTS_FELLOWSHIP = OUTPUTS / "fellowship"
OUTPUTS_CACHE = OUTPUTS / "cache"
OPENALEX_AUTHORS_CACHE = OUTPUTS_CACHE / "openalex_authors.json"

SITE_DIR = REPO_ROOT / "site"

# Discovery datasets
DISCOVERY_CSV_2025 = DATA_DISCOVERY / "arc_discovery_projects_2010_2025_with_for.csv"
DISCOVERY_CSV_2026 = DATA_DISCOVERY / "arc_discovery_projects_2010_2026_with_for.csv"
DISCOVERY_CSV_LEAD_CITATIONS = DATA_DISCOVERY / (
    "arc_discovery_projects_2010_2026_with_for_lead_citations.csv"
)
DISCOVERY_JSON_2026 = DATA_DISCOVERY / "arc_discovery_projects_2010_2026_with_for.json"
DISCOVERY_UNIVERSITIES_CSV = DATA_DERIVED / "arc_discovery_projects_universities.csv"
DISCOVERY_UNIVERSITIES_JSON = DATA_DERIVED / "arc_discovery_projects_universities.json"
GRANT_SUMMARIES_JSON = DATA_DERIVED / "grant_summaries.json"

# Fellowship
FELLOWSHIP_CSV = DATA_FELLOWSHIP / "arc_fellowships.csv"
FELLOWSHIP_JSON = DATA_FELLOWSHIP / "arc_fellowships.json"
FELLOWSHIP_CSV_LEAD_CITATIONS = DATA_FELLOWSHIP / "arc_fellowships_lead_citations.csv"

# FoR reference
FOR_CODES_JSON = DATA_REFERENCE / "for_codes.json"
FOR_CODES_FLAT = DATA_REFERENCE / "for_codes_flat.json"
FOR_CODES_HIERARCHICAL = DATA_REFERENCE / "for_codes_hierarchical.json"
FOR_CODE_TXT = DATA_REFERENCE / "for_code.txt"
FOR_CODE_FORMAT_TXT = DATA_REFERENCE / "for_code_format.txt"

# Build / analysis outputs
VISUALIZATION_DATA_JSON = OUTPUTS_ANALYSIS / "visualization_data.json"
FELLOWSHIP_VIZ_DATA_JSON = OUTPUTS_FELLOWSHIP / "fellowship_visualization_data.json"
CHIEF_INVESTIGATORS_JSON = OUTPUTS_ANALYSIS / "chief_investigators_data.json"
UNIVERSITY_EXTRACTION_SUMMARY = OUTPUTS_ANALYSIS / "university_extraction_summary.txt"

# Site bundle (flat names for fetch())
SITE_DISCOVERY_CSV = SITE_DIR / "arc_discovery_projects_2010_2026_with_for.csv"
SITE_FOR_CODES_FLAT = SITE_DIR / "for_codes_flat.json"
SITE_VISUALIZATION_DATA = SITE_DIR / "visualization_data.json"
SITE_FELLOWSHIP_VIZ_DATA = SITE_DIR / "fellowship_visualization_data.json"
SITE_OPTIMIZED_HTML = SITE_DIR / "arc_analysis_optimized.html"
SITE_LEAD_CITATIONS_CSV = SITE_DIR / "arc_discovery_projects_2010_2026_with_for_lead_citations.csv"
SITE_FELLOWSHIP_LEAD_CITATIONS_CSV = SITE_DIR / "arc_fellowships_lead_citations.csv"
SITE_GRANT_SUMMARIES_JSON = SITE_DIR / "grant_summaries.json"
