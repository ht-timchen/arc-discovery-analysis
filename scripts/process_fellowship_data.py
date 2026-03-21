#!/usr/bin/env python3
import json
import csv
import sys
from collections import defaultdict, Counter
from pathlib import Path
import re

_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))

import paths as P

def load_fellowship_data(csv_file):
    """Load fellowship data from CSV and convert to visualization format"""
    universities = defaultdict(lambda: defaultdict(int))
    for_codes = set()
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            uni = row['administering_organisation']
            if not uni or uni.strip() == '':
                continue
                
            # Clean university name
            uni = uni.strip()
            
            # Get all FoR codes
            all_codes = row['for_all_codes']
            if all_codes:
                codes = [code.strip() for code in all_codes.split(';') if code.strip()]
                for code in codes:
                    # Extract 2-digit and 4-digit codes
                    if len(code) == 2:
                        universities[uni][f"FOR_{code}"] += 1
                        for_codes.add(f"FOR_{code}")
                    elif len(code) == 4:
                        universities[uni][f"FOR_4DIGIT_{code}"] += 1
                        for_codes.add(f"FOR_4DIGIT_{code}")
    
    return universities, for_codes

def create_visualization_data(universities, for_codes):
    """Create the visualization data structure"""
    # Create nodes
    nodes = []
    
    # Add university nodes
    for uni_name in universities.keys():
        nodes.append({
            "id": uni_name,
            "name": uni_name,
            "type": "university"
        })
    
    # Add FoR code nodes
    for for_code in for_codes:
        if for_code.startswith("FOR_4DIGIT_"):
            code = for_code.replace("FOR_4DIGIT_", "")
            nodes.append({
                "id": for_code,
                "name": code,
                "type": "for_code_4digit"
            })
        else:
            code = for_code.replace("FOR_", "")
            nodes.append({
                "id": for_code,
                "name": code,
                "type": "for_code_2digit"
            })
    
    # Create links
    links = []
    for uni_name, for_counts in universities.items():
        for for_code, count in for_counts.items():
            if count > 0:
                links.append({
                    "source": uni_name,
                    "target": for_code,
                    "value": count
                })
    
    return {
        "nodes": nodes,
        "links": links
    }

def main():
    # Load fellowship data
    print("Loading fellowship data...")
    universities, for_codes = load_fellowship_data(str(P.FELLOWSHIP_CSV))
    
    print(f"Found {len(universities)} universities")
    print(f"Found {len(for_codes)} FoR codes")
    
    # Create visualization data
    print("Creating visualization data...")
    viz_data = create_visualization_data(universities, for_codes)
    
    # Save visualization data
    P.OUTPUTS_FELLOWSHIP.mkdir(parents=True, exist_ok=True)
    out = P.FELLOWSHIP_VIZ_DATA_JSON
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(viz_data, f, ensure_ascii=False, indent=2)
    
    print(f"Saved {out}")
    
    # Print some statistics
    print("\nTop 10 universities by total fellowships:")
    uni_totals = {uni: sum(counts.values()) for uni, counts in universities.items()}
    for uni, total in sorted(uni_totals.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {uni}: {total}")
    
    print(f"\nTotal fellowships: {sum(uni_totals.values())}")

if __name__ == "__main__":
    main()
