#!/usr/bin/env python3
"""
Convert for_code_format.txt into JSON format.
The input file contains tab-separated code-name pairs.
This script creates both a flat JSON structure and a hierarchical JSON structure.
"""

import json
import re

def convert_to_json(input_file: str, output_flat: str, output_hierarchical: str):
    """
    Convert the for_code_format.txt file into JSON format.
    
    Args:
        input_file: Path to the input file (for_code_format.txt)
        output_flat: Path to the flat JSON output file
        output_hierarchical: Path to the hierarchical JSON output file
    """
    
    print(f"Converting {input_file} to JSON format...")
    
    # Read the input file and parse code-name pairs
    flat_codes = {}
    hierarchical = {}
    
    with open(input_file, 'r', encoding='utf-8') as infile:
        for line_num, line in enumerate(infile, 1):
            line = line.strip()
            if not line:
                continue
            
            # Split by tab to get code and name
            parts = line.split('\t')
            if len(parts) != 2:
                print(f"Warning: Line {line_num} has unexpected format: {line}")
                continue
            
            code = parts[0].strip()
            name = parts[1].strip()
            
            # Add to flat structure
            flat_codes[code] = name
            
            # Add to hierarchical structure
            code_length = len(code)
            if code_length == 2:  # 2-digit division
                hierarchical[code] = {
                    "name": name,
                    "type": "division",
                    "groups": {}
                }
            elif code_length == 4:  # 4-digit group
                division = code[:2]
                if division in hierarchical:
                    hierarchical[division]["groups"][code] = {
                        "name": name,
                        "type": "group",
                        "fields": {}
                    }
                else:
                    print(f"Warning: 4-digit code {code} has no parent division {division}")
            elif code_length == 6:  # 6-digit field
                division = code[:2]
                group = code[:4]
                if division in hierarchical and group in hierarchical[division]["groups"]:
                    hierarchical[division]["groups"][group]["fields"][code] = {
                        "name": name,
                        "type": "field"
                    }
                else:
                    print(f"Warning: 6-digit code {code} has no parent group {group}")
    
    # Create flat JSON structure
    flat_structure = {
        "metadata": {
            "description": "Australian Fields of Research (FoR) Classification - Flat Structure",
            "total_codes": len(flat_codes),
            "divisions": len([c for c in flat_codes.keys() if len(c) == 2]),
            "groups": len([c for c in flat_codes.keys() if len(c) == 4]),
            "fields": len([c for c in flat_codes.keys() if len(c) == 6])
        },
        "codes": flat_codes
    }
    
    # Create hierarchical JSON structure
    hierarchical_structure = {
        "metadata": {
            "description": "Australian Fields of Research (FoR) Classification - Hierarchical Structure",
            "total_divisions": len([k for k in hierarchical.keys()]),
            "total_groups": sum(len(div["groups"]) for div in hierarchical.values()),
            "total_fields": sum(len(group["fields"]) for div in hierarchical.values() for group in div["groups"].values())
        },
        "divisions": hierarchical
    }
    
    # Write flat JSON
    with open(output_flat, 'w', encoding='utf-8') as f:
        json.dump(flat_structure, f, indent=2, ensure_ascii=False)
    
    # Write hierarchical JSON
    with open(output_hierarchical, 'w', encoding='utf-8') as f:
        json.dump(hierarchical_structure, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Conversion complete!")
    print(f"   - Flat JSON: {output_flat}")
    print(f"   - Hierarchical JSON: {output_hierarchical}")
    print(f"   - Total codes processed: {len(flat_codes)}")
    
    # Print statistics
    divisions = [c for c in flat_codes.keys() if len(c) == 2]
    groups = [c for c in flat_codes.keys() if len(c) == 4]
    fields = [c for c in flat_codes.keys() if len(c) == 6]
    
    print(f"\n📊 Statistics:")
    print(f"   - 2-digit divisions: {len(divisions)}")
    print(f"   - 4-digit groups: {len(groups)}")
    print(f"   - 6-digit fields: {len(fields)}")
    
    # Show sample of each type
    print(f"\n📋 Sample codes:")
    if divisions:
        print(f"   - Sample division: {divisions[0]} - {flat_codes[divisions[0]]}")
    if groups:
        print(f"   - Sample group: {groups[0]} - {flat_codes[groups[0]]}")
    if fields:
        print(f"   - Sample field: {fields[0]} - {flat_codes[fields[0]]}")

def main():
    """
    Main function to run the conversion process.
    """
    input_file = "for_code_format.txt"
    output_flat = "for_codes_flat.json"
    output_hierarchical = "for_codes_hierarchical.json"
    
    try:
        convert_to_json(input_file, output_flat, output_hierarchical)
        
        # Show a sample of the flat JSON
        print(f"\n📋 Sample of flat JSON structure:")
        with open(output_flat, 'r', encoding='utf-8') as f:
            data = json.load(f)
            sample_codes = list(data["codes"].items())[:5]
            for code, name in sample_codes:
                print(f"   \"{code}\": \"{name}\"")
        
        # Show a sample of the hierarchical JSON
        print(f"\n📋 Sample of hierarchical JSON structure:")
        with open(output_hierarchical, 'r', encoding='utf-8') as f:
            data = json.load(f)
            first_division = list(data["divisions"].keys())[0]
            division_data = data["divisions"][first_division]
            print(f"   Division {first_division}: {division_data['name']}")
            if division_data["groups"]:
                first_group = list(division_data["groups"].keys())[0]
                group_data = division_data["groups"][first_group]
                print(f"     Group {first_group}: {group_data['name']}")
                if group_data["fields"]:
                    first_field = list(group_data["fields"].keys())[0]
                    field_data = group_data["fields"][first_field]
                    print(f"       Field {first_field}: {field_data['name']}")
        
    except FileNotFoundError:
        print(f"❌ Error: {input_file} not found in current directory")
    except Exception as e:
        print(f"❌ Error processing file: {e}")

if __name__ == "__main__":
    main()
