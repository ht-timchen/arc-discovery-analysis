import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))

import paths as P

def extract_cis_and_affiliations():
    """
    Extract Chief Investigators and their affiliations from the CSV file
    and store them in a JSON file.
    """
    ci_data = []
    ci_affiliations = defaultdict(set)
    
    P.OUTPUTS_ANALYSIS.mkdir(parents=True, exist_ok=True)
    with open(P.DISCOVERY_CSV_2026, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            project_code = row['code']
            administering_org = row['administering_organisation']
            chief_investigators = row['chief_investigators']
            orcids = row['chief_investigators_orcids']
            
            # Skip if no chief investigators
            if not chief_investigators or chief_investigators.strip() == '':
                continue
            
            # Split chief investigators (they are separated by semicolons)
            ci_list = [ci.strip() for ci in chief_investigators.split(';') if ci.strip()]
            orcid_list = [orcid.strip() for orcid in orcids.split(';') if orcid.strip()]
            
            # Create entries for each CI
            for i, ci_name in enumerate(ci_list):
                ci_entry = {
                    'name': ci_name,
                    'affiliation': administering_org,
                    'project_code': project_code,
                    'orcids': orcid_list[i] if i < len(orcid_list) else None
                }
                ci_data.append(ci_entry)
                
                # Track affiliations for each CI
                ci_affiliations[ci_name].add(administering_org)
    
    # Create a summary with unique CIs and all their affiliations
    unique_cis = []
    for ci_name, affiliations in ci_affiliations.items():
        unique_ci = {
            'name': ci_name,
            'affiliations': list(affiliations),
            'total_projects': len([entry for entry in ci_data if entry['name'] == ci_name])
        }
        unique_cis.append(unique_ci)
    
    # Sort by name for easier reading
    unique_cis.sort(key=lambda x: x['name'])
    
    # Create the final output structure
    output = {
        'total_unique_cis': len(unique_cis),
        'total_ci_entries': len(ci_data),
        'unique_chief_investigators': unique_cis,
        'detailed_entries': ci_data
    }
    
    # Save to JSON file
    out_path = P.CHIEF_INVESTIGATORS_JSON
    with open(out_path, 'w', encoding='utf-8') as json_file:
        json.dump(output, json_file, indent=2, ensure_ascii=False)
    
    print(f"Extracted {len(unique_cis)} unique Chief Investigators")
    print(f"Total CI entries: {len(ci_data)}")
    print(f"Data saved to {out_path}")
    
    return output

if __name__ == "__main__":
    extract_cis_and_affiliations()
