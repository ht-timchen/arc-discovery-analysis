#!/usr/bin/env python3
"""
Optimized Static ARC Analysis Generator
Creates a smaller HTML file with essential data only
"""

import pandas as pd
import json
from pathlib import Path

def load_and_process_data():
    """Load and process the ARC data"""
    input_csv = "./arc_discovery_projects_2010_2025_with_for.csv"
    
    if not Path(input_csv).exists():
        raise FileNotFoundError(f"Input CSV not found: {path}")
    
    df = pd.read_csv(input_csv)
    
    # Utility to split semicolon-separated values
    def split_list(col):
        return col.fillna("").astype(str).apply(lambda s: [x.strip() for x in s.split(";") if x.strip()])
    
    # Prepare exploded DataFrame for CI and FoR codes
    ci_names = split_list(df["chief_investigators"]).rename("ci_name")
    for_codes = split_list(df["for_all_codes"]).rename("for_code")
    
    exploded = (
        df.assign(ci_name=ci_names, for_code=for_codes)
          .explode("ci_name")
          .explode("for_code")
    )
    # Drop blanks
    exploded = exploded[(exploded["ci_name"].notna()) & (exploded["ci_name"].str.len() > 0)]
    exploded = exploded[(exploded["for_code"].notna()) & (exploded["for_code"].str.len() > 0)]
    
    # Build FoR options with simple labeling from names if available
    for_code_to_name = {}
    for code, names in zip(df["for_all_codes"], df["for_all_names"]):
        if pd.isna(code) or pd.isna(names):
            continue
        codes = [c.strip() for c in str(code).split(";") if c.strip()]
        name_list = [n.strip() for n in str(names).split(";") if n.strip()]
        for c, n in zip(codes, name_list):
            for_code_to_name.setdefault(c, n)
    
    # Extract 2-digit codes and their names
    for_2digit_to_name = {}
    for code, name in for_code_to_name.items():
        if len(code) >= 2:
            two_digit = code[:2]
            if two_digit not in for_2digit_to_name:
                for_2digit_to_name[two_digit] = name.split(" — ")[0] if " — " in name else name
    
    return df, exploded, for_code_to_name, for_2digit_to_name

def generate_essential_rankings(exploded, df, top_k=30):
    """Generate comprehensive rankings with all FoR codes"""
    rankings = {}
    
    # Overall ranking (no filters) - top 30
    overall_ranking = (
        df.assign(ci_name=df["chief_investigators"].fillna("").astype(str).apply(
            lambda s: [x.strip() for x in s.split(";") if x.strip()]
        ))
        .explode("ci_name")
        .dropna(subset=["ci_name"])
        .groupby("ci_name")["code"].nunique().reset_index(name="num_projects")
        .sort_values("num_projects", ascending=False)
        .head(top_k)
    )
    rankings["overall"] = overall_ranking.to_dict('records')
    
    # Generate rankings for each 2-digit code - top 20
    for code_2digit in sorted(set([code[:2] for code in exploded["for_code"].unique() if len(code) >= 2])):
        filt = exploded[exploded["for_code"].str.startswith(code_2digit)]
        if len(filt) > 0:
            ranked = (
                filt.drop_duplicates(subset=["ci_name", "code"])
                    .groupby("ci_name")["code"].nunique().reset_index(name="num_projects")
                    .sort_values("num_projects", ascending=False)
                    .head(20)
            )
            if len(ranked) > 0:  # Only include if there are results
                rankings[f"2digit_{code_2digit}"] = ranked.to_dict('records')
    
    # Generate rankings for ALL specific codes
    for code in sorted(exploded["for_code"].unique()):
        filt = exploded[exploded["for_code"] == code]
        if len(filt) > 0:
            ranked = (
                filt.drop_duplicates(subset=["ci_name", "code"])
                    .groupby("ci_name")["code"].nunique().reset_index(name="num_projects")
                    .sort_values("num_projects", ascending=False)
                    .head(15)
            )
            if len(ranked) > 0:
                rankings[f"specific_{code}"] = ranked.to_dict('records')
    
    return rankings

def generate_essential_ci_details(exploded, df):
    """Generate CI details for top 2000 CIs with 15 projects each"""
    ci_details = {}
    
    # Get top 2000 CIs from overall ranking
    top_cis = (
        df.assign(ci_name=df["chief_investigators"].fillna("").astype(str).apply(
            lambda s: [x.strip() for x in s.split(";") if x.strip()]
        ))
        .explode("ci_name")
        .dropna(subset=["ci_name"])
        .groupby("ci_name")["code"].nunique().reset_index(name="num_projects")
        .sort_values("num_projects", ascending=False)
        .head(2000)  # Top 2000 CIs
    )
    
    for _, row in top_cis.iterrows():
        ci_name = row["ci_name"]
        # Get all projects for this CI
        ci_projects = df[df["chief_investigators"].fillna("").astype(str).str.contains(ci_name, na=False)]
        codes = ci_projects["code"].dropna().astype(str).unique().tolist()
        
        if codes:
            # Pull rows from original df for extra columns
            rows = df[df["code"].astype(str).isin(codes)].copy()
            rows = rows[[
                "code",
                "funding_commencement_year",
                "administering_organisation",
                "for_primary_names",
            ]]
            
            # Sort by year and code
            rows = rows.sort_values(["funding_commencement_year", "code"], ascending=[False, True])
            
            # Limit to top 15 projects per CI
            rows = rows.head(15)
            
            projects = []
            for _, r in rows.iterrows():
                projects.append({
                    "code": r["code"],
                    "year": r.get("funding_commencement_year", ""),
                    "org": r.get("administering_organisation", ""),
                    "for_primary": r.get("for_primary_names", ""),
                    "url": f"https://dataportal.arc.gov.au/NCGP/Web/Grant/Grant/{r['code']}"
                })
            
            ci_details[ci_name] = {
                "ci_name": ci_name,
                "projects": projects
            }
    
    return ci_details

def create_optimized_html_template():
    """Create the HTML template with embedded JavaScript"""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ARC Discovery Projects - Chief Investigators Analysis</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body {
            background: #fafafa;
            min-height: 100vh;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            color: #333;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        
        .card {
            background: white;
            border: 1px solid #e1e5e9;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
            margin-bottom: 24px;
            transition: all 0.2s ease;
            overflow: hidden;
        }
        
        .card:hover {
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
        }
        
        .card-header {
            background: white;
            color: #1a1a1a;
            border-bottom: 1px solid #e1e5e9;
            padding: 32px 32px 24px;
            font-weight: 500;
        }
        
        .form-select {
            border-radius: 8px;
            border: 1px solid #d1d5db;
            transition: all 0.15s ease;
            cursor: pointer;
            padding: 12px 16px;
            font-size: 14px;
            background: white;
            color: #374151;
        }
        
        .form-select:focus {
            border-color: #3b82f6;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
            outline: none;
        }
        
        .form-select:hover {
            border-color: #9ca3af;
            background-color: #f9fafb;
        }
        
        /* Modern dropdown styling */
        .modern-dropdown {
            background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%236b7280'%3e%3cpath stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M19 9l-7 7-7-7'%3e%3c/path%3e%3c/svg%3e");
            background-repeat: no-repeat;
            background-position: right 12px center;
            background-size: 20px 20px;
            padding-right: 40px;
            appearance: none;
            -webkit-appearance: none;
            -moz-appearance: none;
        }
        
        .btn-primary {
            background: #3b82f6;
            border: none;
            border-radius: 8px;
            padding: 12px 24px;
            font-weight: 500;
            font-size: 14px;
            transition: all 0.15s ease;
            color: white;
        }
        
        .btn-primary:hover {
            background: #2563eb;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
        }
        
        .table {
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
            border: 1px solid #e1e5e9;
        }
        
        .table thead th {
            background: #f8fafc;
            color: #374151;
            border: none;
            padding: 16px 20px;
            font-weight: 600;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .table tbody tr {
            transition: all 0.15s ease;
            border-bottom: 1px solid #f1f5f9;
        }
        
        .table tbody tr:hover {
            background-color: #f8fafc;
        }
        
        .table tbody tr:last-child {
            border-bottom: none;
        }
        
        .table tbody td {
            padding: 16px 20px;
            border: none;
            vertical-align: middle;
            font-size: 14px;
            color: #374151;
        }
        
        .project-item {
            background: #f8fafc;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 12px;
            border: 1px solid #e1e5e9;
            transition: all 0.15s ease;
        }
        
        .project-item:hover {
            background: #f1f5f9;
            border-color: #cbd5e1;
        }
        
        .project-code {
            color: #3b82f6;
            text-decoration: none;
            font-weight: 600;
            font-size: 14px;
        }
        
        .project-code:hover {
            color: #2563eb;
        }
        
        .project-meta {
            color: #6b7280;
            font-size: 13px;
            margin-top: 8px;
        }
        
        .project-for {
            color: #374151;
            font-size: 13px;
            margin-top: 6px;
            font-weight: 500;
        }
        
        .fade-in {
            animation: fadeIn 0.5s ease-in;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .form-label {
            font-weight: 600;
            color: #374151;
            margin-bottom: 8px;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .form-label i {
            color: #6b7280;
        }
        
        .help-text {
            color: #6b7280;
            font-size: 12px;
            margin-top: 6px;
            font-weight: 400;
        }
        
        .info-badge {
            background: #f0f9ff;
            color: #0369a1;
            padding: 8px 16px;
            border-radius: 6px;
            font-size: 13px;
            margin-bottom: 24px;
            border: 1px solid #bae6fd;
            font-weight: 500;
        }
        
        /* Enhanced filter section styling */
        .card-body {
            padding: 32px;
        }
        
        .row > .col-md-4 {
            margin-bottom: 20px;
        }
        
        /* Responsive design improvements */
        @media (max-width: 768px) {
            .container {
                padding: 15px;
            }
            
            .card-header h1 {
                font-size: 1.5rem;
            }
            
            .col-md-4 {
                margin-bottom: 25px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h1 class="mb-0">
                            <i class="fas fa-chart-line me-2"></i>
                            ARC Discovery Projects - Chief Investigators Analysis
                        </h1>
                    </div>
                    <div class="card-body">
                        <div class="info-badge">
                            <i class="fas fa-info-circle me-1"></i>
                            Comprehensive version: All FoR codes, top 2000 CIs, 15 projects per CI
                        </div>
                        
                        <div class="row">
                            <div class="col-md-4">
                                <label for="for2DigitSelector" class="form-label">
                                    <i class="fas fa-layer-group me-1"></i>
                                    Broad FoR Categories
                                </label>
                                <select id="for2DigitSelector" class="form-select" multiple size="8">
                                    <!-- Populated by JavaScript -->
                                </select>
                                <div class="help-text">
                                    <i class="fas fa-info-circle me-1"></i>
                                    Single-click to select (clears others). Ctrl/Cmd+click to select multiple.
                                </div>
                            </div>
                            <div class="col-md-4">
                                <label for="forSelector" class="form-label">
                                    <i class="fas fa-tags me-1"></i>
                                    Specific FoR Codes
                                </label>
                                <select id="forSelector" class="form-select" multiple size="8">
                                    <!-- Populated by JavaScript -->
                                </select>
                                <div class="help-text">
                                    <i class="fas fa-info-circle me-1"></i>
                                    Single-click to select (clears others). Ctrl/Cmd+click to select multiple.
                                </div>
                            </div>
                            <div class="col-md-4">
                                <label for="yearSelector" class="form-label">
                                    <i class="fas fa-calendar me-1"></i>
                                    Starting Year
                                </label>
                                <select id="yearSelector" class="form-select modern-dropdown">
                                    <option value="">All Years</option>
                                    <!-- Populated by JavaScript -->
                                </select>
                                <div class="help-text">
                                    <i class="fas fa-info-circle me-1"></i>
                                    Filter projects from this year onwards.
                                </div>
                            </div>
                        </div>
                        
                        <div class="row mt-3">
                            <div class="col-12">
                                <button id="clearFilters" class="btn btn-primary">
                                    <i class="fas fa-eraser me-1"></i>
                                    Clear All Filters
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row">
            <div class="col-md-8">
                <div class="card">
                    <div class="card-header">
                        <h3 class="mb-0">
                            <i class="fas fa-trophy me-2"></i>
                            <span id="resultsTitle">Top Chief Investigators</span>
                        </h3>
                    </div>
                    <div class="card-body">
                        <div id="noResults" class="text-center text-muted d-none">
                            <i class="fas fa-search fa-2x mb-3"></i>
                            <p>No results found for the selected filters.</p>
                        </div>
                        
                        <div id="resultsSection">
                            <div class="table-responsive">
                                <table class="table table-hover">
                                    <thead>
                                        <tr>
                                            <th>Rank</th>
                                            <th>Chief Investigator</th>
                                            <th>Number of Projects</th>
                                            <th>Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody id="resultsTable">
                                        <!-- Populated by JavaScript -->
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="col-md-4">
                <div id="ciDetailSection" class="card d-none">
                    <div class="card-header">
                        <h4 class="mb-0">
                            <i class="fas fa-user-tie me-2"></i>
                            <span id="ciDetailTitle">CI Details</span>
                        </h4>
                    </div>
                    <div class="card-body">
                        <div id="ciDetailContent">
                            <!-- Populated by JavaScript -->
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Embedded data will be inserted here
        const EMBEDDED_DATA = {
            forCodes: FOR_CODES_DATA,
            rankings: RANKINGS_DATA,
            ciDetails: CI_DETAILS_DATA
        };

        class OptimizedARCAnalysisApp {
            constructor() {
                this.initializeElements();
                this.bindEvents();
                this.loadData();
            }

            initializeElements() {
                this.forSelector = document.getElementById('forSelector');
                this.for2DigitSelector = document.getElementById('for2DigitSelector');
                this.yearSelector = document.getElementById('yearSelector');
                this.clearFiltersBtn = document.getElementById('clearFilters');
                this.resultsTable = document.getElementById('resultsTable');
                this.resultsTitle = document.getElementById('resultsTitle');
                this.noResults = document.getElementById('noResults');
                this.resultsSection = document.getElementById('resultsSection');
                this.ciDetailSection = document.getElementById('ciDetailSection');
                this.ciDetailTitle = document.getElementById('ciDetailTitle');
                this.ciDetailContent = document.getElementById('ciDetailContent');
                
                this.selectedCodes = [];
                this.selected2DigitCodes = [];
                this.selectedYear = "";
                this.currentCIs = [];
                this.selectedCI = null;
            }

            bindEvents() {
                this.forSelector.addEventListener('change', () => this.updateView());
                this.for2DigitSelector.addEventListener('change', () => {
                    this.filterSpecificCodes();
                    this.updateView();
                });
                this.yearSelector.addEventListener('change', () => this.updateView());
                this.clearFiltersBtn.addEventListener('click', () => this.clearFilters());
            }

            loadData() {
                // Populate FoR codes
                this.allSpecificCodes = EMBEDDED_DATA.forCodes.specific_codes;
                this.allTwoDigitCodes = EMBEDDED_DATA.forCodes.two_digit_codes;
                
                this.populateSpecificCodes(this.allSpecificCodes);
                this.populate2DigitCodes(this.allTwoDigitCodes);
                this.populateYears(EMBEDDED_DATA.forCodes.years);
                
                // Show overall ranking initially
                this.updateView();
            }

            populateSpecificCodes(codesToShow) {
                this.forSelector.innerHTML = '';
                codesToShow.forEach(code => {
                    const option = document.createElement('option');
                    option.value = code.value;
                    option.textContent = code.label;
                    this.forSelector.appendChild(option);
                });
            }

            populate2DigitCodes(codes) {
                this.for2DigitSelector.innerHTML = '';
                codes.forEach(code => {
                    const option = document.createElement('option');
                    option.value = code.value;
                    option.textContent = code.label;
                    this.for2DigitSelector.appendChild(option);
                });
            }

            populateYears(years) {
                this.yearSelector.innerHTML = '<option value="">All Years</option>';
                years.forEach(year => {
                    const option = document.createElement('option');
                    option.value = year.value;
                    option.textContent = year.label;
                    this.yearSelector.appendChild(option);
                });
            }

            filterSpecificCodes() {
                const selectedBroadCodes = Array.from(this.for2DigitSelector.selectedOptions).map(opt => opt.value);
                
                if (selectedBroadCodes.length === 0) {
                    this.populateSpecificCodes(this.allSpecificCodes);
                } else {
                    const filteredCodes = this.allSpecificCodes.filter(code => {
                        return selectedBroadCodes.some(broadCode => code.value.startsWith(broadCode));
                    });
                    this.populateSpecificCodes(filteredCodes);
                }
            }

            updateView() {
                this.selectedCodes = Array.from(this.forSelector.selectedOptions).map(opt => opt.value);
                this.selected2DigitCodes = Array.from(this.for2DigitSelector.selectedOptions).map(opt => opt.value);
                this.selectedYear = this.yearSelector.value;
                
                // Find the appropriate ranking
                let rankingKey = 'overall';
                let rankedCIs = EMBEDDED_DATA.rankings.overall;
                let isOverall = true;
                
                if (this.selectedCodes.length > 0) {
                    // Use the first selected specific code
                    rankingKey = `specific_${this.selectedCodes[0]}`;
                    if (EMBEDDED_DATA.rankings[rankingKey]) {
                        rankedCIs = EMBEDDED_DATA.rankings[rankingKey];
                        isOverall = false;
                    }
                } else if (this.selected2DigitCodes.length > 0) {
                    // Use the first selected 2-digit code
                    rankingKey = `2digit_${this.selected2DigitCodes[0]}`;
                    if (EMBEDDED_DATA.rankings[rankingKey]) {
                        rankedCIs = EMBEDDED_DATA.rankings[rankingKey];
                        isOverall = false;
                    }
                }
                
                // Apply year filter dynamically if selected
                if (this.selectedYear && rankedCIs) {
                    rankedCIs = this.applyYearFilter(rankedCIs, this.selectedYear);
                }
                
                this.displayResults(rankedCIs, isOverall);
            }
            
            applyYearFilter(rankedCIs, year) {
                // Filter the CI details to only include projects from the selected year onwards
                const filteredCIs = [];
                
                for (const ci of rankedCIs) {
                    const ciDetails = EMBEDDED_DATA.ciDetails[ci.ci_name];
                    if (ciDetails) {
                        // Count projects from the selected year onwards
                        const filteredProjects = ciDetails.projects.filter(project => 
                            project.year >= parseInt(year)
                        );
                        
                        if (filteredProjects.length > 0) {
                            filteredCIs.push({
                                ...ci,
                                num_projects: filteredProjects.length
                            });
                        }
                    }
                }
                
                // Re-sort by number of projects
                return filteredCIs.sort((a, b) => b.num_projects - a.num_projects);
            }

            displayResults(rankedCIs, isOverall = false) {
                this.currentCIs = rankedCIs;
                
                if (rankedCIs.length === 0) {
                    this.showNoResults();
                    return;
                }
                
                this.resultsTitle.textContent = isOverall ? 
                    'Overall Top Chief Investigators' : 
                    'Top Chief Investigators (Filtered)';
                
                let html = '';
                rankedCIs.forEach((ci, index) => {
                    html += `
                        <tr class="fade-in">
                            <td><span class="badge bg-primary">${index + 1}</span></td>
                            <td><strong>${ci.ci_name}</strong></td>
                            <td><span class="badge bg-success">${ci.num_projects}</span></td>
                            <td>
                                <button class="btn btn-sm btn-outline-primary" onclick="app.onCISelection('${ci.ci_name}')">
                                    <i class="fas fa-eye me-1"></i>View Projects
                                </button>
                            </td>
                        </tr>
                    `;
                });
                
                this.resultsTable.innerHTML = html;
                this.resultsSection.classList.remove('d-none');
            }

            onCISelection(ciName) {
                this.selectedCI = ciName;
                
                const ciDetail = EMBEDDED_DATA.ciDetails[ciName];
                if (ciDetail) {
                    this.displayCIDetail(ciDetail);
                } else {
                    this.showError('CI details not found');
                }
            }

            displayCIDetail(data) {
                this.ciDetailTitle.textContent = `Project Details: ${data.ci_name}`;
                
                if (data.projects.length === 0) {
                    this.ciDetailContent.innerHTML = '<p class="text-muted">No projects found for this CI.</p>';
                } else {
                    let html = `<p class="text-muted mb-3">Found ${data.projects.length} project(s):</p>`;
                    
                    data.projects.forEach((project, index) => {
                        html += `
                            <div class="project-item fade-in">
                                <div class="d-flex justify-content-between align-items-start">
                                    <div>
                                        <a href="${project.url}" target="_blank" class="project-code">
                                            ${project.code}
                                        </a>
                                        <div class="project-meta">
                                            ${project.year} • ${project.org}
                                        </div>
                                        <div class="project-for">
                                            ${project.for_primary}
                                        </div>
                                    </div>
                                    <span class="badge bg-secondary">${index + 1}</span>
                                </div>
                            </div>
                        `;
                    });
                    
                    this.ciDetailContent.innerHTML = html;
                }
                
                this.ciDetailSection.classList.remove('d-none');
            }

            clearFilters() {
                this.forSelector.selectedIndex = -1;
                this.for2DigitSelector.selectedIndex = -1;
                this.yearSelector.value = "";
                
                this.selectedCodes = [];
                this.selected2DigitCodes = [];
                this.selectedYear = "";
                this.currentCIs = [];
                this.selectedCI = null;
                
                this.populateSpecificCodes(this.allSpecificCodes);
                this.updateView();
            }

            showNoResults() {
                this.resultsSection.classList.add('d-none');
                this.ciDetailSection.classList.add('d-none');
                this.noResults.classList.remove('d-none');
            }

            showError(message) {
                alert('Error: ' + message);
            }
        }

        // Initialize the app when the page loads
        let app;
        document.addEventListener('DOMContentLoaded', () => {
            app = new OptimizedARCAnalysisApp();
        });
    </script>
    
    <!-- Footer -->
    <footer style="
        text-align: center;
        padding: 40px 20px 20px;
        color: #6b7280;
        font-size: 14px;
        border-top: 1px solid #e1e5e9;
        margin-top: 40px;
        background: white;
    ">
        <div style="max-width: 1400px; margin: 0 auto;">
            <p style="margin: 0; font-weight: 500;">
                <i class="fas fa-code" style="color: #3b82f6; margin-right: 8px;"></i>
                Vibe Code by 
                <a href="https://ht-timchen.github.io/" 
                   target="_blank" 
                   rel="noopener noreferrer"
                   style="
                       color: #3b82f6;
                       text-decoration: none;
                       font-weight: 600;
                       transition: color 0.15s ease;
                   "
                   onmouseover="this.style.color='#2563eb'"
                   onmouseout="this.style.color='#3b82f6'">
                    Tim Chen @ Adelaide
                </a>
            </p>
        </div>
    </footer>
</body>
</html>"""

def main():
    """Main function to generate the optimized static HTML file"""
    print("Loading and processing ARC data...")
    df, exploded, for_code_to_name, for_2digit_to_name = load_and_process_data()
    
    print("Generating essential rankings...")
    rankings = generate_essential_rankings(exploded, df)
    
    print("Generating essential CI details...")
    ci_details = generate_essential_ci_details(exploded, df)
    
    print("Preparing FoR codes and years...")
    specific_codes = [{"value": c, "label": f"{c} — {for_code_to_name.get(c, c)}"} for c in sorted(for_code_to_name.keys())]
    two_digit_codes = [{"value": c, "label": f"{c} — {for_2digit_to_name.get(c, c)}"} for c in sorted(for_2digit_to_name.keys())]
    
    # Get available years
    years = sorted(df["funding_commencement_year"].dropna().unique())
    year_options = [{"value": str(int(year)), "label": f"From {int(year)} onwards"} for year in years]
    
    for_codes_data = {
        "specific_codes": specific_codes,
        "two_digit_codes": two_digit_codes,
        "years": year_options
    }
    
    print("Creating optimized HTML template...")
    html_template = create_optimized_html_template()
    
    # Replace placeholders with actual data
    html_content = html_template.replace(
        'FOR_CODES_DATA', 
        json.dumps(for_codes_data, indent=2)
    ).replace(
        'RANKINGS_DATA', 
        json.dumps(rankings, indent=2)
    ).replace(
        'CI_DETAILS_DATA', 
        json.dumps(ci_details, indent=2)
    )
    
    # Write the final HTML file
    output_file = "arc_analysis_optimized.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Optimized static HTML file generated: {output_file}")
    print(f"📊 Rankings generated: {len(rankings)}")
    print(f"👥 CI details generated: {len(ci_details)}")
    print(f"🏷️  FoR codes: {len(specific_codes)} specific, {len(two_digit_codes)} broad")
    print(f"📁 File size: {len(html_content) / 1024 / 1024:.1f} MB")
    
    return output_file

if __name__ == "__main__":
    main()
