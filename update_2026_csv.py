#!/usr/bin/env python3
"""
Update CSV file to populate administering_organisation for 2026 projects
using administering_organisation_announcement from JSON file.
"""

import json
import csv
import sys
from pathlib import Path

def main():
    json_file = Path('arc_discovery_projects_2010_2026_with_for.json')
    csv_file = Path('arc_discovery_projects_2010_2026_with_for.csv')
    
    # Load JSON data
    print(f"Loading JSON file: {json_file}", file=sys.stderr)
    with open(json_file, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    
    # Build mapping for 2026 projects
    # Map: code -> administering_organisation_announcement
    org_mapping = {}
    for project in json_data:
        if project.get('funding_commencement_year') == 2026:
            code = project.get('code')
            org_announcement = project.get('administering_organisation_announcement')
            org_current = project.get('administering_organisation')
            
            # Use announcement value if current is null/empty
            if (not org_current or org_current.strip() == '') and org_announcement:
                org_mapping[code] = org_announcement.strip()
    
    print(f"Found {len(org_mapping)} 2026 projects with administering_organisation_announcement", file=sys.stderr)
    
    # Read CSV file
    print(f"Reading CSV file: {csv_file}", file=sys.stderr)
    rows = []
    updated_count = 0
    
    with open(csv_file, 'r', encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        
        for row in reader:
            year = row.get('funding_commencement_year', '').strip()
            code = row.get('code', '').strip()
            org = row.get('administering_organisation', '').strip()
            
            # Update if year is 2026 and org is empty and we have a mapping
            if year == '2026' and (not org or org == '') and code in org_mapping:
                row['administering_organisation'] = org_mapping[code]
                updated_count += 1
                print(f"Updated {code}: {org_mapping[code]}", file=sys.stderr)
            
            rows.append(row)
    
    print(f"Updated {updated_count} rows in CSV", file=sys.stderr)
    
    # Write updated CSV back
    print(f"Writing updated CSV file: {csv_file}", file=sys.stderr)
    with open(csv_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"Successfully updated {csv_file} with {updated_count} 2026 project administering_organisation fields", file=sys.stderr)

if __name__ == '__main__':
    main()

