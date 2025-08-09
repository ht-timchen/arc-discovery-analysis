from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
from pathlib import Path
import json

app = Flask(__name__)

# Configuration
INPUT_CSV = "./arc_discovery_projects_2010_2025_with_for.csv"
TOP_K = 30

def load_data():
    """Load and prepare the data"""
    path = Path(INPUT_CSV)
    if not path.exists():
        raise FileNotFoundError(f"Input CSV not found: {path}")
    
    df = pd.read_csv(path)
    
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

# Load data once at startup
try:
    df, exploded, for_code_to_name, for_2digit_to_name = load_data()
    choices = sorted(for_code_to_name.keys())
    two_digit_choices = sorted(for_2digit_to_name.keys())
except Exception as e:
    print(f"Error loading data: {e}")
    df, exploded, for_code_to_name, for_2digit_to_name = None, None, {}, {}
    choices, two_digit_choices = [], []

def label_for(c):
    n = for_code_to_name.get(c)
    return f"{c} — {n}" if n else c

def label_2digit_for(c):
    n = for_2digit_to_name.get(c)
    return f"{c} — {n}" if n else c

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/for_codes')
def get_for_codes():
    """Get available FoR codes"""
    specific_codes = [{"value": c, "label": label_for(c)} for c in choices]
    two_digit_codes = [{"value": c, "label": label_2digit_for(c)} for c in two_digit_choices]
    
    return jsonify({
        "specific_codes": specific_codes,
        "two_digit_codes": two_digit_codes
    })

@app.route('/api/ranked_cis', methods=['GET'])
def get_ranked_cis():
    """Get ranked CIs based on selected FoR codes"""
    selected_codes = request.args.getlist('selected_codes')
    selected_2digit_codes = request.args.getlist('selected_2digit_codes')
    
    if exploded is None:
        return jsonify({"error": "Data not loaded"}), 500
    
    # Filter by FoR
    filt = exploded.copy()
    
    # Apply specific code filter
    if selected_codes:
        filt = filt[filt["for_code"].isin(selected_codes)]
    
    # Apply 2-digit code filter
    if selected_2digit_codes:
        # Create mask for codes that start with any of the selected 2-digit codes
        mask = filt["for_code"].str.startswith(tuple(selected_2digit_codes))
        filt = filt[mask]
    
    # If no filters are selected, use the original dataframe for overall ranking
    if not selected_codes and not selected_2digit_codes:
        # Use the original df for overall ranking (no FoR filtering)
        overall_ranking = (
            df.assign(ci_name=df["chief_investigators"].fillna("").astype(str).apply(
                lambda s: [x.strip() for x in s.split(";") if x.strip()]
            ))
            .explode("ci_name")
            .dropna(subset=["ci_name"])
            .groupby("ci_name")["code"].nunique().reset_index(name="num_projects")
            .sort_values("num_projects", ascending=False)
            .head(TOP_K)
        )
        return jsonify({
            "ranked_cis": overall_ranking.to_dict('records'),
            "is_overall": True
        })
    
    # Rank CIs - FIXED: deduplicate by project code first
    ranked = (
        filt.drop_duplicates(subset=["ci_name", "code"])
            .groupby("ci_name")["code"].nunique().reset_index(name="num_projects")
            .sort_values("num_projects", ascending=False)
            .head(TOP_K)
    )
    
    return jsonify({
        "ranked_cis": ranked.to_dict('records'),
        "is_overall": False
    })

@app.route('/api/ci_detail/<ci_name>', methods=['GET'])
def get_ci_detail(ci_name):
    """Get detailed project information for a specific CI"""
    selected_codes = request.args.getlist('selected_codes')
    selected_2digit_codes = request.args.getlist('selected_2digit_codes')
    
    if exploded is None or df is None:
        return jsonify({"error": "Data not loaded"}), 500
    
    # If no filters are selected, show all projects for the CI
    if not selected_codes and not selected_2digit_codes:
        # Get all projects for this CI from the original dataframe
        ci_projects = df[df["chief_investigators"].fillna("").astype(str).str.contains(ci_name, na=False)]
        codes = ci_projects["code"].dropna().astype(str).unique().tolist()
    else:
        # Filter by FoR
        filt = exploded.copy()
        
        # Apply specific code filter
        if selected_codes:
            filt = filt[filt["for_code"].isin(selected_codes)]
        
        # Apply 2-digit code filter
        if selected_2digit_codes:
            # Create mask for codes that start with any of the selected 2-digit codes
            mask = filt["for_code"].str.startswith(tuple(selected_2digit_codes))
            filt = filt[mask]
        
        # Filter DPs for selected CI within the current FoR filter
        subset = filt[filt["ci_name"] == ci_name]
        codes = subset["code"].dropna().astype(str).unique().tolist()
    
    if not codes:
        return jsonify({"projects": []})
    
    # Pull rows from original df for extra columns
    rows = df[df["code"].astype(str).isin(codes)].copy()
    rows = rows[[
        "code",
        "funding_commencement_year",
        "administering_organisation",
        "for_primary_names",
        "for_all_names",
        "grant_status",
        "funding_current",
    ]]
    
    # Sort by year and code
    rows = rows.sort_values(["funding_commencement_year", "code"], ascending=[False, True])
    
    projects = []
    for _, r in rows.iterrows():
        projects.append({
            "code": r["code"],
            "year": r.get("funding_commencement_year", ""),
            "org": r.get("administering_organisation", ""),
            "for_primary": r.get("for_primary_names", ""),
            "url": f"https://dataportal.arc.gov.au/NCGP/Web/Grant/Grant/{r['code']}"
        })
    
    return jsonify({
        "ci_name": ci_name,
        "projects": projects
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
