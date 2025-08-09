#!/usr/bin/env python3
"""
Simple build script for static ARC Discovery Projects Analysis.
"""

import json
import os
import pandas as pd
import shutil

def load_and_process_data():
    """Load and process the ARC data"""
    print("Loading data...")
    df = pd.read_csv('arc_discovery_projects_2010_2025_with_for.csv')
    
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
    
    return {
        'specific_codes': [{'value': c, 'label': f"{c} — {c}"} for c in specific_codes],
        'two_digit_codes': [{'value': c, 'label': f"{c} — {c}"} for c in two_digit_codes],
        'top_cis': [{'ci_name': ci, 'num_projects': count} for ci, count in top_cis],
        'ci_counts': ci_counts
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
