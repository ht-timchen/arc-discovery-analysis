#!/usr/bin/env python3
"""
Simple build script for static ARC Discovery Projects Analysis.
"""

import json
import os
import pandas as pd
import shutil

def get_for_labels():
    """Get proper FoR code labels"""
    # This is a simplified version - in a real app you'd have a complete lookup table
    labels = {
        "0101": "Pure Mathematics",
        "0102": "Applied Mathematics", 
        "0103": "Numerical and Computational Mathematics",
        "0104": "Statistics",
        "0105": "Mathematical Physics",
        "0201": "Astronomical and Space Sciences",
        "0202": "Atomic, Molecular, Nuclear, Particle and Plasma Physics",
        "0203": "Classical Physics",
        "0204": "Condensed Matter Physics",
        "0205": "Optical Physics",
        "0206": "Quantum Physics",
        "0301": "Analytical Chemistry",
        "0302": "Inorganic Chemistry",
        "0303": "Macromolecular and Materials Chemistry",
        "0304": "Medicinal and Biomolecular Chemistry",
        "0305": "Organic Chemistry",
        "0306": "Physical Chemistry (Incl. Structural)",
        "0307": "Theoretical and Computational Chemistry",
        "0401": "Atmospheric Sciences",
        "0402": "Geochemistry",
        "0403": "Geology",
        "0404": "Geophysics",
        "0405": "Oceanography",
        "0406": "Physical Geography and Environmental Geoscience",
        "0501": "Ecological Applications",
        "0502": "Environmental Science and Management",
        "0503": "Soil Sciences",
        "0601": "Biochemistry and Cell Biology",
        "0602": "Ecology",
        "0603": "Evolutionary Biology",
        "0604": "Genetics",
        "0605": "Microbiology",
        "0606": "Physiology",
        "0607": "Plant Biology",
        "0608": "Zoology",
        "0801": "Artificial Intelligence and Image Processing",
        "0802": "Computation Theory and Mathematics",
        "0803": "Computer Software",
        "0804": "Data Format",
        "0805": "Distributed Computing",
        "0806": "Information Systems",
        "0807": "Library and Information Studies",
        "0901": "Aerospace Engineering",
        "0902": "Automotive Engineering",
        "0903": "Biomedical Engineering",
        "0904": "Chemical Engineering",
        "0905": "Civil Engineering",
        "0906": "Electrical and Electronic Engineering",
        "0907": "Environmental Engineering",
        "0908": "Food Sciences",
        "0909": "Geomatic Engineering",
        "0910": "Manufacturing Engineering",
        "0911": "Maritime Engineering",
        "0912": "Materials Engineering",
        "0913": "Mechanical Engineering",
        "0914": "Resources Engineering and Extractive Metallurgy",
        "0915": "Interdisciplinary Engineering",
        "1001": "Agricultural Biotechnology",
        "1002": "Environmental Biotechnology",
        "1003": "Industrial Biotechnology",
        "1004": "Medical Biotechnology",
        "1005": "Communications Technologies",
        "1006": "Computer Hardware",
        "1007": "Nanotechnology",
        "1101": "Medical Biochemistry and Metabolomics",
        "1102": "Cardiorespiratory Medicine and Haematology",
        "1103": "Clinical Sciences",
        "1104": "Complementary and Alternative Medicine",
        "1106": "Human Movement and Sports Science",
        "1107": "Immunology",
        "1108": "Medical Microbiology",
        "1109": "Neurosciences",
        "1110": "Nursing",
        "1111": "Nutrition and Dietetics",
        "1112": "Oncology and Carcinogenesis",
        "1113": "Ophthalmology and Optometry",
        "1114": "Paediatrics and Reproductive Medicine",
        "1115": "Pharmacology and Pharmaceutical Sciences",
        "1116": "Medical Physiology",
        "1117": "Public Health and Health Services",
        "1201": "Architecture",
        "1202": "Building",
        "1203": "Design Practice and Management",
        "1204": "Engineering Design",
        "1205": "Urban and Regional Planning",
        "1301": "Education Systems",
        "1302": "Curriculum and Pedagogy",
        "1303": "Specialist Studies In Education",
        "1401": "Economic Theory",
        "1402": "Applied Economics",
        "1403": "Econometrics",
        "1501": "Accounting, Auditing and Accountability",
        "1502": "Banking, Finance and Investment",
        "1503": "Business and Management",
        "1504": "Commercial Services",
        "1505": "Marketing",
        "1506": "Tourism",
        "1507": "Transportation and Freight Services",
        "1601": "Anthropology",
        "1602": "Criminology",
        "1603": "Demography",
        "1604": "Human Geography",
        "1605": "Policy and Administration",
        "1606": "Political Science",
        "1607": "Social Work",
        "1608": "Sociology",
        "1701": "Psychology",
        "1702": "Cognitive Sciences",
        "1801": "Law",
        "1901": "Art Theory and Criticism",
        "1902": "Film, Television and Digital Media",
        "1903": "Journalism and Professional Writing",
        "1904": "Performing Arts and Creative Writing",
        "1905": "Visual Arts and Crafts",
        "2001": "Communication and Media Studies",
        "2002": "Cultural Studies",
        "2003": "Language Studies",
        "2004": "Linguistics",
        "2005": "Literary Studies",
        "2101": "Archaeology",
        "2102": "Curatorial and Related Studies",
        "2103": "Historical Studies",
        "2201": "Applied Ethics",
        "2202": "History and Philosophy of Specific Fields",
        "2203": "Philosophy",
        "2204": "Religion and Religious Studies"
    }
    return labels

def load_and_process_data():
    """Load and process the ARC data"""
    print("Loading data...")
    df = pd.read_csv('arc_discovery_projects_2010_2025_with_for.csv')
    
    # Get proper FoR labels
    for_labels = get_for_labels()
    
    # Get unique FoR codes
    all_codes = set()
    for codes_str in df['for_all_codes'].dropna():
        codes = [c.strip() for c in str(codes_str).split(';') if c.strip()]
        all_codes.update(codes)
    
    # Get 2-digit codes
    two_digit_codes = sorted(set(c[:2] for c in all_codes if len(c) >= 2))
    specific_codes = sorted(all_codes)
    
    # Process Chief Investigators
    all_cis = set()
    for ci_str in df['chief_investigators'].dropna():
        cis = [ci.strip() for ci in str(ci_str).split(';') if ci.strip()]
        all_cis.update(cis)
    
    # Count projects per CI
    ci_counts = {}
    for ci_str in df['chief_investigators'].dropna():
        cis = [ci.strip() for ci in str(ci_str).split(';') if ci.strip()]
        for ci in cis:
            ci_counts[ci] = ci_counts.get(ci, 0) + 1
    
    # Get top 30 CIs
    top_cis = sorted(ci_counts.items(), key=lambda x: x[1], reverse=True)[:30]
    
    # Create proper labels for codes
    def get_label(code):
        if code in for_labels:
            return f"{code} — {for_labels[code]}"
        else:
            return f"{code} — {code}"
    
    return {
        'specific_codes': [{'value': c, 'label': get_label(c)} for c in specific_codes],
        'two_digit_codes': [{'value': c, 'label': get_label(c)} for c in two_digit_codes],
        'top_cis': [{'ci_name': ci, 'num_projects': count} for ci, count in top_cis],
        'ci_counts': ci_counts,
        'df': df  # Keep the dataframe for CI details
    }

def generate_static_files(data):
    """Generate static JSON files"""
    print("Generating static files...")
    
    # Create build directory
    os.makedirs('build/api', exist_ok=True)
    
    # Generate for_codes.json
    with open('build/api/for_codes.json', 'w') as f:
        json.dump({
            'specific_codes': data['specific_codes'],
            'two_digit_codes': data['two_digit_codes']
        }, f, indent=2)
    
    # Generate ranked_cis.json (overall ranking)
    with open('build/api/ranked_cis.json', 'w') as f:
        json.dump({
            'ranked_cis': data['top_cis'],
            'is_overall': True
        }, f, indent=2)
    
    # Generate CI detail files for top CIs
    print("Generating CI detail files...")
    df = data['df']
    
    for ci_data in data['top_cis']:
        ci_name = ci_data['ci_name']
        print(f"  Generating details for: {ci_name}")
        
        # Get all projects for this CI
        ci_projects = df[df['chief_investigators'].fillna('').astype(str).str.contains(ci_name, na=False)]
        
        projects = []
        for _, project in ci_projects.iterrows():
            projects.append({
                'code': project['code'],
                'title': project.get('title', ''),
                'year': project.get('year', ''),
                'org': project.get('org', ''),
                'for_primary': project.get('for_primary', ''),
                'url': f"https://dataportal.arc.gov.au/NCGP/Web/Grant/Grant/{project['code']}"
            })
        
        # Create filename-safe version of CI name
        safe_name = ci_name.replace(' ', '_').replace(',', '').replace('.', '').replace('(', '').replace(')', '')
        safe_name = ''.join(c for c in safe_name if c.isalnum() or c == '_')
        
        print(f"    Creating file: ci_detail_{safe_name}.json with {len(projects)} projects")
        
        with open(f'build/api/ci_detail_{safe_name}.json', 'w') as f:
            json.dump({
                'ci_name': ci_name,
                'projects': projects
            }, f, indent=2)
    
    print("Generated API files")

def copy_static_files():
    """Copy static files"""
    print("Copying static files...")
    
    # Copy static directory
    if os.path.exists('static'):
        shutil.copytree('static', 'build/static', dirs_exist_ok=True)
    
    # Copy data file
    if os.path.exists('arc_discovery_projects_2010_2025_with_for.csv'):
        shutil.copy2('arc_discovery_projects_2010_2025_with_for.csv', 'build/')

def create_index_html():
    """Create the main index.html file"""
    print("Creating index.html...")
    
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ARC Discovery Projects - Chief Investigators Analysis</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="static/css/style.css" rel="stylesheet">
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <div class="col-12">
                <div class="header">
                    <h1><i class="fas fa-chart-line"></i> ARC Discovery Projects Analysis</h1>
                    <p class="subtitle">Top Chief Investigators by Field of Research (2010-2025)</p>
                </div>
            </div>
        </div>

        <div class="row">
            <div class="col-lg-4 col-md-5">
                <div class="control-panel">
                    <div class="form-group mb-4">
                        <label class="form-label fw-bold">
                            <i class="fas fa-layer-group"></i> Broad FoR Categories (2-digit):
                        </label>
                        <select id="for2DigitSelector" class="form-select" multiple size="6">
                        </select>
                        <small class="form-text text-muted">Click to select (clears others) • Hold Ctrl/Cmd to select multiple categories</small>
                    </div>

                    <div class="form-group mb-4">
                        <label class="form-label fw-bold">
                            <i class="fas fa-filter"></i> Specific FoR Codes:
                        </label>
                        <select id="forSelector" class="form-select" multiple size="8">
                        </select>
                        <small class="form-text text-muted">Click to select (clears others) • Hold Ctrl/Cmd to select multiple codes</small>
                    </div>

                    <div class="form-group mb-4">
                        <label class="form-label fw-bold">
                            <i class="fas fa-user-tie"></i> Select Chief Investigator:
                        </label>
                        <select id="ciSelector" class="form-select" size="10">
                            <option value="">Select FoR codes first...</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <button id="clearFilters" class="btn btn-outline-secondary w-100">
                            <i class="fas fa-eraser"></i> Clear All Filters
                        </button>
                    </div>
                </div>
            </div>

            <div class="col-lg-8 col-md-7">
                <div class="results-panel">
                    <div id="loadingIndicator" class="text-center d-none">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                        <p class="mt-2">Processing data...</p>
                    </div>

                    <div id="resultsSection" class="d-none">
                        <div class="card">
                            <div class="card-header">
                                <h5 class="mb-0">
                                    <i class="fas fa-trophy"></i> Top 30 Chief Investigators
                                </h5>
                            </div>
                            <div class="card-body">
                                <div class="table-responsive">
                                    <table id="resultsTable" class="table table-striped table-hover">
                                        <thead class="table-dark">
                                            <tr>
                                                <th>Rank</th>
                                                <th>Chief Investigator</th>
                                                <th>Number of Projects</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div id="ciDetailSection" class="d-none">
                        <div class="card">
                            <div class="card-header">
                                <h5 id="ciDetailTitle" class="mb-0">
                                    <i class="fas fa-user-tie"></i> Project Details
                                </h5>
                            </div>
                            <div class="card-body">
                                <div id="ciDetailContent">
                                </div>
                            </div>
                        </div>
                    </div>

                    <div id="noResults" class="text-center d-none">
                        <div class="alert alert-info">
                            <i class="fas fa-info-circle"></i> No results found for the selected criteria.
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="static/js/app.js"></script>
</body>
</html>"""
    
    with open('build/index.html', 'w') as f:
        f.write(html_content)

def main():
    """Main build process"""
    print("Starting simple static site generation...")
    
    # Clean existing build
    if os.path.exists('build'):
        shutil.rmtree('build')
    
    # Load and process data
    data = load_and_process_data()
    
    # Generate static files
    generate_static_files(data)
    
    # Copy static files
    copy_static_files()
    
    # Create index.html
    create_index_html()
    
    # Copy debug page
    if os.path.exists('debug.html'):
        shutil.copy2('debug.html', 'build/')
        print("Copied debug.html")
    
    # Create .nojekyll file for GitHub Pages
    with open('build/.nojekyll', 'w') as f:
        f.write('')
    print("Created .nojekyll file")
    
    print("\nBuild completed successfully!")
    print("Static files are in the 'build' directory")

if __name__ == '__main__':
    main()
