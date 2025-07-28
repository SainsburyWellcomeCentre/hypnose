#!/usr/bin/env python3
"""
Simple YAML Variable Adder for Hypnose Project

A streamlined script to add variables to YAML files in the Schemas folder.
Specifically designed for the hypnose project's YAML structure.

Usage:
    python simple_yaml_adder.py

Example:
    Target variable: maximumTime
    New variable: newTimeout
    New value: 15
    
    Result:
    maximumTime: 10
    newTimeout: 15  # <- newly added
    responseTime: 99999
"""

import os
import sys
from pathlib import Path
from typing import List


def find_yaml_files(folder_path: str) -> List[Path]:
    """Find all .yml files in the specified folder."""
    folder = Path(folder_path)
    if not folder.exists():
        print(f"Error: Folder '{folder_path}' does not exist.")
        return []
    
    yaml_files = [f for f in folder.iterdir() if f.suffix.lower() == '.yml']
    return sorted(yaml_files)


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
        
        print(f"  Added {found_count} occurrences", end="")
        return True
        
    except Exception as e:
        print(f"Error processing {file_path.name}: {e}")
        return False


def main():
    """Main function with interactive prompts."""
    print("Simple YAML Variable Adder")
    print("=" * 40)
    
    # Ask if user wants to process a single file or all files in a folder
    mode = input("Process (1) single file or (2) all files in folder? Enter 1 or 2: ").strip()
    
    yaml_files = []
    
    if mode == "1":
        # Single file mode
        file_input = input("Enter the path to the YAML file: ").strip()
        file_path = Path(file_input)
        
        if not file_path.exists():
            print(f"File not found: {file_path}")
            return
        
        if file_path.suffix.lower() not in ['.yml', '.yaml']:
            print(f"File is not a YAML file: {file_path}")
            return
        
        yaml_files = [file_path]
        print(f"\nSelected file: {file_path.name}")
        
    elif mode == "2":
        # Folder mode (original functionality)
        # Default to Schemas folder if it exists
        default_folder = "src/Schemas"
        if os.path.exists(default_folder):
            folder_input = input(f"YAML folder path (default: {default_folder}): ").strip()
            folder_path = folder_input if folder_input else default_folder
        else:
            folder_path = input("YAML folder path: ").strip()
        
        # Find YAML files
        yaml_files = find_yaml_files(folder_path)
        if not yaml_files:
            print("No .yml files found in the specified folder.")
            return
            
        print(f"\nFound {len(yaml_files)} YAML files:")
        for i, file_path in enumerate(yaml_files, 1):
            print(f"  {i:2d}. {file_path.name}")
    
    else:
        print("Invalid option. Please enter 1 or 2.")
        return
    
    # Get target variable
    target_var = input("\nEnter the existing variable name to insert after: ").strip()
    if not target_var:
        print("Target variable name cannot be empty.")
        return
    
    # Get new variable details
    new_var = input("Enter the new variable name: ").strip()
    if not new_var:
        print("New variable name cannot be empty.")
        return
    
    new_value = input("Enter the new variable value: ").strip()
    if not new_value:
        print("New variable value cannot be empty.")
        return
    
    # Show preview
    print(f"\nPreview of change:")
    print(f"  {target_var}: <existing_value>")
    print(f"  {new_var}: {new_value}  # <- This will be added")
    print(f"  <next_variable>: <next_value>")
    
    # Confirm
    file_count = len(yaml_files)
    file_word = "file" if file_count == 1 else "files"
    confirm = input(f"\nAdd '{new_var}: {new_value}' after '{target_var}' in {file_count} {file_word}? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Operation cancelled.")
        return
    
    # Process files
    print(f"\nProcessing files...")
    success_count = 0
    total_additions = 0
    
    for file_path in yaml_files:
        print(f"Processing {file_path.name}...", end=" ")
        if add_variable_to_file(file_path, target_var, new_var, new_value):
            print(" ✓")
            success_count += 1
        else:
            print(" ✗")
    
    print(f"\nCompleted: {success_count}/{len(yaml_files)} files successfully modified.")
    
    if success_count > 0:
        print(f"\nVariable '{new_var}: {new_value}' has been added after every occurrence of '{target_var}' in the modified files.")
        print("Tip: You can check the changes using git diff if the files are in a git repository.")


if __name__ == "__main__":
    main()
