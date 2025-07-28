#!/usr/bin/env python3
"""
Command-line YAML Variable Adder

A command-line version of the YAML variable insertion script that can accept
file paths as arguments for easier automation and scripting.

Usage:
    python yaml_adder_cli.py <yaml_file> <target_var> <new_var> <new_value>
    python yaml_adder_cli.py src/Schemas/doubles-stage1.yml maximumTime warningTime 8

For multiple files:
    python yaml_adder_cli.py "src/Schemas/*.yml" maximumTime warningTime 8

Author: Generated for hypnose project
"""

import sys
import glob
from pathlib import Path
from typing import List


def add_variable_to_file(file_path: Path, target_var: str, new_var: str, new_value: str) -> bool:
    """Add a new variable after every occurrence of the target variable in a YAML file."""
    try:
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Find all target variables and insert after each one
        modified_lines = []
        found_count = 0
        
        for i, line in enumerate(lines):
            # Check if this line contains the target variable
            stripped = line.strip()
            if stripped.startswith(f"{target_var}:"):
                found_count += 1
                
                # Get the indentation of the current line
                indent = len(line) - len(line.lstrip())
                indent_str = ' ' * indent
                
                # Check if the line needs a comma (if it doesn't already end with one)
                if not line.rstrip().endswith(','):
                    # Add comma to the current line
                    modified_line = line.rstrip() + ',\n'
                    modified_lines.append(modified_line)
                else:
                    modified_lines.append(line)
                
                # Create the new variable line with same indentation
                new_line = f"{indent_str}{new_var}: {new_value}\n"
                modified_lines.append(new_line)
            else:
                modified_lines.append(line)
        
        if found_count == 0:
            print(f"Warning: Target variable '{target_var}' not found in {file_path.name}")
            return False
        
        # Write the modified content back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(modified_lines)
        
        print(f"✓ {file_path.name}: Added {found_count} occurrences")
        return True
        
    except Exception as e:
        print(f"✗ Error processing {file_path.name}: {e}")
        return False


def expand_file_patterns(file_patterns: List[str]) -> List[Path]:
    """Expand file patterns (including globs) into actual file paths."""
    files = []
    
    for pattern in file_patterns:
        if '*' in pattern or '?' in pattern:
            # Handle glob patterns
            expanded = glob.glob(pattern)
            for file_str in expanded:
                file_path = Path(file_str)
                if file_path.is_file() and file_path.suffix.lower() in ['.yml', '.yaml']:
                    files.append(file_path)
        else:
            # Handle direct file paths
            file_path = Path(pattern)
            if file_path.is_file() and file_path.suffix.lower() in ['.yml', '.yaml']:
                files.append(file_path)
            elif file_path.is_file():
                print(f"Warning: {file_path} is not a YAML file")
            else:
                print(f"Warning: {file_path} not found")
    
    return list(set(files))  # Remove duplicates


def main():
    """Main command-line interface."""
    if len(sys.argv) < 5:
        print("YAML Variable Adder - Command Line Interface")
        print("=" * 50)
        print("\nUsage:")
        print("  python yaml_adder_cli.py <yaml_file> <target_var> <new_var> <new_value>")
        print("\nExamples:")
        print("  python yaml_adder_cli.py doubles-stage1.yml maximumTime warningTime 8")
        print("  python yaml_adder_cli.py src/Schemas/doubles-stage1.yml maximumTime warningTime 8")
        print('  python yaml_adder_cli.py "src/Schemas/*.yml" maximumTime warningTime 8')
        print("\nArguments:")
        print("  <yaml_file>   : Path to YAML file or glob pattern (e.g., '*.yml')")
        print("  <target_var>  : Existing variable name to insert after")
        print("  <new_var>     : New variable name to add")
        print("  <new_value>   : Value for the new variable")
        sys.exit(1)
    
    file_pattern = sys.argv[1]
    target_var = sys.argv[2]
    new_var = sys.argv[3]
    new_value = sys.argv[4]
    
    # Expand file patterns
    files = expand_file_patterns([file_pattern])
    
    if not files:
        print(f"No YAML files found matching pattern: {file_pattern}")
        sys.exit(1)
    
    print(f"Processing {len(files)} file(s)...")
    print(f"Target variable: {target_var}")
    print(f"New variable: {new_var} = {new_value}")
    print("-" * 30)
    
    success_count = 0
    
    for file_path in sorted(files):
        if add_variable_to_file(file_path, target_var, new_var, new_value):
            success_count += 1
    
    print("-" * 30)
    print(f"Completed: {success_count}/{len(files)} files successfully modified")
    
    if success_count > 0:
        print(f"\nVariable '{new_var}: {new_value}' added after every occurrence of '{target_var}'")


if __name__ == "__main__":
    main()
