#!/usr/bin/env python3
"""
Parse for_code_2008.txt into a hierarchical JSON file.
This script handles the complex multi-column layout of the 2008 FoR codes file.
"""

import re
import json
from typing import Dict, List, Tuple

def parse_for_code_2008(content: str) -> Dict:
    """
    Parse the 2008 format FoR codes into a hierarchical structure.
    
    The file has a complex multi-column layout where:
    - 2-digit codes start at the beginning of lines
    - 4-digit codes are indented and may be in multiple columns
    - 6-digit codes are further indented and may be in multiple columns
    """
    result = {}
    
    # Split content into lines and process each line
    lines = content.split('\n')
    
    current_2digit = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Look for 2-digit codes (e.g., "01 MATHEMATICAL SCIENCES")
        two_digit_match = re.match(r'^(\d{2})\s+([A-Z\s]+)', line)
        if two_digit_match:
            code_2digit = two_digit_match.group(1)
            name_2digit = two_digit_match.group(2).strip()
            
            result[code_2digit] = {
                'name': name_2digit,
                '4digit': {}
            }
            current_2digit = code_2digit
            continue
            
        # Look for 4-digit codes in the entire line (they may be in multiple columns)
        if current_2digit:
            # First, try to find 4-digit codes that span the entire line
            four_digit_matches = re.finditer(r'(\d{4})\s+([A-Za-z\s,\-]+)', line)
            for match in four_digit_matches:
                code_4digit = match.group(1)
                name_4digit = match.group(2).strip()
                
                # Verify this 4-digit code belongs to the current 2-digit code
                if code_4digit.startswith(current_2digit):
                    # Check if we already have this code with a shorter name
                    if (code_4digit not in result[current_2digit]['4digit'] or 
                        len(name_4digit) > len(result[current_2digit]['4digit'][code_4digit]['name'])):
                        result[current_2digit]['4digit'][code_4digit] = {
                            'name': name_4digit,
                            '6digit': {}
                        }
            
            # Also split the line by tabs to handle the column structure
            columns = line.split('\t')
            
            for column in columns:
                column = column.strip()
                if not column:
                    continue
                    
                # Look for 4-digit codes in this column
                four_digit_match = re.match(r'(\d{4})\s+([A-Za-z\s,\-]+)', column)
                if four_digit_match:
                    code_4digit = four_digit_match.group(1)
                    name_4digit = four_digit_match.group(2).strip()
                    
                    # Verify this 4-digit code belongs to the current 2-digit code
                    if code_4digit.startswith(current_2digit):
                        # Check if we already have this code with a shorter name
                        if (code_4digit not in result[current_2digit]['4digit'] or 
                            len(name_4digit) > len(result[current_2digit]['4digit'][code_4digit]['name'])):
                            result[current_2digit]['4digit'][code_4digit] = {
                                'name': name_4digit,
                                '6digit': {}
                            }
        
        # Look for 6-digit codes in the entire line (they may be in multiple columns)
        if current_2digit:
            # Find all 6-digit codes in this line
            six_digit_matches = re.finditer(r'(\d{6})\s+([A-Za-z\s\(\)]+)', line)
            for match in six_digit_matches:
                code_6digit = match.group(1)
                name_6digit = match.group(2).strip()
                
                # Find which 4-digit code this 6-digit code belongs to
                code_4digit = code_6digit[:4]
                code_2digit = code_6digit[:2]
                
                # Verify this 6-digit code belongs to the current 2-digit code
                if code_2digit == current_2digit:
                    # Make sure the 4-digit code exists
                    if code_4digit not in result[current_2digit]['4digit']:
                        result[current_2digit]['4digit'][code_4digit] = {
                            'name': f"Unknown {code_4digit}",
                            '6digit': {}
                        }
                    
                    result[current_2digit]['4digit'][code_4digit]['6digit'][code_6digit] = name_6digit
        
        # Look for 6-digit codes in the entire line (they may be in multiple columns)
        if current_2digit:
            # Find all 6-digit codes in this line
            six_digit_matches = re.finditer(r'(\d{6})\s+([A-Za-z\s\(\)]+)', line)
            for match in six_digit_matches:
                code_6digit = match.group(1)
                name_6digit = match.group(2).strip()
                
                # Find which 4-digit code this 6-digit code belongs to
                code_4digit = code_6digit[:4]
                code_2digit = code_6digit[:2]
                
                # Verify this 6-digit code belongs to the current 2-digit code
                if code_2digit == current_2digit:
                    # Make sure the 4-digit code exists
                    if code_4digit not in result[current_2digit]['4digit']:
                        result[current_2digit]['4digit'][code_4digit] = {
                            'name': f"Unknown {code_4digit}",
                            '6digit': {}
                        }
                    
                    result[current_2digit]['4digit'][code_4digit]['6digit'][code_6digit] = name_6digit
    
    return result

def infer_4digit_names(hierarchical: Dict) -> Dict:
    """
    Infer 4-digit code names from 6-digit codes when they're not explicitly provided.
    """
    # Common 4-digit code names that we can infer
    common_names = {
        "0801": "ARTIFICIAL INTELLIGENCE AND IMAGE PROCESSING",
        "0802": "COMPUTATION THEORY AND MATHEMATICS",
        "0803": "COMPUTER SOFTWARE",
        "0804": "DATA FORMAT",
        "0805": "DISTRIBUTED COMPUTING",
        "0806": "INFORMATION SYSTEMS",
        "0807": "LIBRARY AND INFORMATION STUDIES",
        "4601": "APPLIED COMPUTING",
        "4602": "ARTIFICIAL INTELLIGENCE",
        "4603": "COMPUTER VISION AND MULTIMEDIA COMPUTATION",
        "4604": "CYBERSECURITY AND PRIVACY",
        "4605": "DATA MANAGEMENT AND DATA SCIENCE",
        "4606": "DISTRIBUTED COMPUTING AND SYSTEMS SOFTWARE",
        "4607": "GRAPHICS, AUGMENTED REALITY AND GAMES",
        "4608": "HUMAN-CENTRED COMPUTING",
        "4609": "INFORMATION SYSTEMS",
        "4610": "LIBRARY AND INFORMATION STUDIES",
        "4611": "MACHINE LEARNING",
        "4612": "SOFTWARE ENGINEERING",
        "4613": "THEORY OF COMPUTATION"
    }
    
    for code_2digit, data_2digit in hierarchical.items():
        for code_4digit, data_4digit in data_2digit['4digit'].items():
            # If the name is "Unknown" or very short, try to infer it
            if (data_4digit['name'].startswith("Unknown") or 
                len(data_4digit['name']) <= 3):
                
                # Check if we have a common name for this code
                if code_4digit in common_names:
                    data_4digit['name'] = common_names[code_4digit]
                else:
                    # Try to infer from the first 6-digit code name
                    if data_4digit['6digit']:
                        first_6digit = list(data_4digit['6digit'].keys())[0]
                        first_name = data_4digit['6digit'][first_6digit]
                        # Extract a meaningful prefix from the 6-digit name
                        words = first_name.split()
                        if len(words) >= 2:
                            data_4digit['name'] = " ".join(words[:2]).upper()
                        else:
                            data_4digit['name'] = first_name.upper()
    
    return hierarchical

def create_flat_structure(hierarchical: Dict) -> Dict[str, str]:
    """
    Create a flat structure mapping all codes to names.
    """
    flat = {}
    
    for code_2digit, data_2digit in hierarchical.items():
        flat[code_2digit] = data_2digit['name']
        
        for code_4digit, data_4digit in data_2digit['4digit'].items():
            flat[code_4digit] = data_4digit['name']
            
            for code_6digit, name_6digit in data_4digit['6digit'].items():
                flat[code_6digit] = name_6digit
    
    return flat

def create_hierarchical_json(hierarchical: Dict) -> Dict:
    """
    Create a structured hierarchical JSON with metadata.
    """
    # Count totals
    total_2digit = len(hierarchical)
    total_4digit = sum(len(data['4digit']) for data in hierarchical.values())
    total_6digit = sum(
        len(data_4digit['6digit']) 
        for data_2digit in hierarchical.values() 
        for data_4digit in data_2digit['4digit'].values()
    )
    
    return {
        'metadata': {
            'description': 'Australian Fields of Research (FoR) Classification - 2008',
            'source': 'for_code_2008.txt',
            'total_2digit': total_2digit,
            'total_4digit': total_4digit,
            'total_6digit': total_6digit
        },
        'divisions': hierarchical
    }

def main():
    """
    Main function to parse the 2008 FoR codes file.
    """
    print("Parsing FoR Code 2008 file...")
    
    try:
        # Read the 2008 file
        with open('for_code_2008.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"Read {len(content)} characters from for_code_2008.txt")
        
        # Parse the content
        hierarchical = parse_for_code_2008(content)
        
        # Infer missing 4-digit names
        hierarchical = infer_4digit_names(hierarchical)
        
        # Create flat structure
        flat = create_flat_structure(hierarchical)
        
        # Create structured hierarchical JSON
        structured = create_hierarchical_json(hierarchical)
        
        # Save flat structure
        with open('for_codes_2008.json', 'w', encoding='utf-8') as f:
            json.dump(flat, f, indent=2, ensure_ascii=False)
        
        # Save hierarchical structure
        with open('for_codes_2008_hierarchical.json', 'w', encoding='utf-8') as f:
            json.dump(structured, f, indent=2, ensure_ascii=False)
        
        # Print summary
        print(f"\n✅ Successfully parsed and created:")
        print(f"   - Flat structure: {len(flat)} total codes")
        print(f"   - Hierarchical structure: {structured['metadata']['total_2digit']} divisions, {structured['metadata']['total_4digit']} groups, {structured['metadata']['total_6digit']} fields")
        
        print(f"\nFiles created:")
        print(f"   - for_codes_2008.json (flat structure)")
        print(f"   - for_codes_2008_hierarchical.json (hierarchical structure)")
        
        # Show sample of what was parsed
        print(f"\nSample 2-digit codes:")
        for i, (code, name) in enumerate(list(hierarchical.items())[:5]):
            print(f"   {code}: {name['name']}")
            
        print(f"\nSample 4-digit codes from first division:")
        first_2digit = list(hierarchical.keys())[0]
        if hierarchical[first_2digit]['4digit']:
            first_4digit = list(hierarchical[first_2digit]['4digit'].keys())[0]
            print(f"   {first_4digit}: {hierarchical[first_2digit]['4digit'][first_4digit]['name']}")
            
            print(f"\nSample 6-digit codes from first group:")
            if hierarchical[first_2digit]['4digit'][first_4digit]['6digit']:
                first_6digit = list(hierarchical[first_2digit]['4digit'][first_4digit]['6digit'].keys())[0]
                print(f"   {first_6digit}: {hierarchical[first_2digit]['4digit'][first_4digit]['6digit'][first_6digit]}")
            else:
                print(f"   No 6-digit codes found in {first_4digit}")
        else:
            print(f"   No 4-digit codes found in {first_2digit}")
        
    except FileNotFoundError:
        print("❌ Error: for_code_2008.txt not found in current directory")
    except Exception as e:
        print(f"❌ Error parsing file: {e}")

if __name__ == "__main__":
    main()
