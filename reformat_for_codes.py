#!/usr/bin/env python3
"""
Reformat for_code.txt into individual lines with one code-name pair per line.
Each line in the input file contains multiple code-name pairs separated by tabs.
This script splits them into individual lines in for_code_format.txt.
"""

import re

def reformat_for_codes(input_file: str, output_file: str):
    """
    Reformat the for_code.txt file by splitting each line into individual code-name pairs.
    
    Args:
        input_file: Path to the input file (for_code.txt)
        output_file: Path to the output file (for_code_format.txt)
    """
    
    print(f"Reformatting {input_file} into {output_file}...")
    
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8') as outfile:
        
        line_count = 0
        output_count = 0
        
        for line in infile:
            line_count += 1
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Split the line by tabs to get individual parts
            parts = line.split('\t')
            
            # Process parts in pairs (code, name, code, name, ...)
            i = 0
            while i < len(parts):
                part = parts[i].strip()
                if not part:
                    i += 1
                    continue
                
                # Check if this part is a code (starts with digits)
                if re.match(r'^\d+$', part):
                    code = part
                    # Look for the corresponding name in the next part
                    if i + 1 < len(parts):
                        name = parts[i + 1].strip()
                        if name:  # Make sure we have a name
                            # Write the code-name pair to the output file
                            outfile.write(f"{code}\t{name}\n")
                            output_count += 1
                            i += 2  # Skip both code and name
                            continue
                
                # If not a code, try the old pattern matching
                match = re.match(r'^(\d+)\s+(.+)$', part)
                if not match:
                    # Try matching without the start anchor in case there are leading spaces
                    match = re.match(r'(\d+)\s+(.+)$', part)
                if match:
                    code = match.group(1)
                    name = match.group(2).strip()
                    
                    # Write the code-name pair to the output file
                    outfile.write(f"{code}\t{name}\n")
                    output_count += 1
                
                i += 1
        
        print(f"✅ Processing complete!")
        print(f"   - Input lines processed: {line_count}")
        print(f"   - Output code-name pairs: {output_count}")
        print(f"   - Output file: {output_file}")

def main():
    """
    Main function to run the reformatting process.
    """
    input_file = "for_code.txt"
    output_file = "for_code_format.txt"
    
    try:
        reformat_for_codes(input_file, output_file)
        
        # Show a sample of the output
        print(f"\n📋 Sample of reformatted output:")
        with open(output_file, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i < 10:  # Show first 10 lines
                    print(f"   {line.strip()}")
                else:
                    break
        print(f"   ... (and {output_count - 10} more lines)")
        
    except FileNotFoundError:
        print(f"❌ Error: {input_file} not found in current directory")
    except Exception as e:
        print(f"❌ Error processing file: {e}")

if __name__ == "__main__":
    main()
