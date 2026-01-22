#!/usr/bin/env python3
"""
YAML Variable Inserter

This script allows you to add new variables to existing YAML files within a folder
by specifying the variable after which you would like to define the new variable.

Usage:
    python add_yaml_variable.py

The script will prompt you for:
- Folder path containing YAML files
- The existing variable name after which to insert
- The new variable name and value
- Whether to apply to all YAML files in the folder

Author: Generated for hypnose project
"""

import os
import re
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional


class YAMLVariableInserter:
    """Class to handle insertion of variables into YAML files."""
    
    def __init__(self):
        self.yaml_extensions = ['.yml', '.yaml']
    
    def find_yaml_files(self, folder_path: str) -> List[Path]:
        """Find all YAML files in the specified folder."""
        folder = Path(folder_path)
        yaml_files = []
        
        if not folder.exists():
            raise FileNotFoundError(f"Folder not found: {folder_path}")
        
        for file_path in folder.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in self.yaml_extensions:
                yaml_files.append(file_path)
        
        return sorted(yaml_files)
    
    def read_file_with_formatting(self, file_path: Path) -> List[str]:
        """Read file and return lines with original formatting preserved."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.readlines()
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return []
    
    def detect_indentation(self, lines: List[str], target_variable: str) -> str:
        """Detect the indentation level of the target variable."""
        for line in lines:
            stripped_line = line.strip()
            if stripped_line.startswith(f"{target_variable}:"):
                # Calculate indentation
                indentation = len(line) - len(line.lstrip())
                return ' ' * indentation
        return ''  # Default to no indentation
    
    def insert_variable_after_target(self, lines: List[str], target_variable: str, 
                                   new_variable: str, new_value: str) -> List[str]:
        """Insert new variable after every occurrence of the target variable in the lines."""
        modified_lines = []
        found_count = 0
        
        for i, line in enumerate(lines):
            # Check if this line contains our target variable
            stripped_line = line.strip()
            if stripped_line.startswith(f"{target_variable}:"):
                found_count += 1
                
                # Detect indentation for the new variable
                indentation = self.detect_indentation(lines, target_variable)
                
                # Check if the line needs a comma (if it doesn't already end with one)
                if not line.rstrip().endswith(','):
                    # Add comma to the current line
                    modified_line = line.rstrip() + ',\n'
                    modified_lines.append(modified_line)
                else:
                    modified_lines.append(line)
                
                # Format the new variable line
                if isinstance(new_value, bool):
                    formatted_value = str(new_value)
                elif isinstance(new_value, (int, float)):
                    formatted_value = str(new_value)
                elif isinstance(new_value, str):
                    # Check if value needs quotes
                    if new_value.isdigit() or new_value.lower() in ['true', 'false', 'null']:
                        formatted_value = f'"{new_value}"'
                    else:
                        formatted_value = new_value
                else:
                    formatted_value = str(new_value)
                
                new_line = f"{indentation}{new_variable}: {formatted_value}\n"
                modified_lines.append(new_line)
            else:
                modified_lines.append(line)
        
        if found_count == 0:
            raise ValueError(f"Target variable '{target_variable}' not found in the file")
        
        return modified_lines
    
    def process_file(self, file_path: Path, target_variable: str, 
                    new_variable: str, new_value: str, backup: bool = True) -> bool:
        """Process a single YAML file to add the new variable."""
        try:
            # Read original file
            lines = self.read_file_with_formatting(file_path)
            if not lines:
                print(f"Skipping empty file: {file_path}")
                return False
            
            # Create backup if requested
            if backup:
                backup_path = file_path.with_suffix(file_path.suffix + '.backup')
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                print(f"Backup created: {backup_path}")
            
            # Insert new variable
            modified_lines = self.insert_variable_after_target(
                lines, target_variable, new_variable, new_value
            )
            
            # Write modified content back to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(modified_lines)
            
            print(f"✓ Successfully modified: {file_path}")
            return True
            
        except Exception as e:
            print(f"✗ Error processing {file_path}: {e}")
            return False
    
    def validate_yaml_syntax(self, file_path: Path) -> bool:
        """Validate that the modified YAML file has correct syntax."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                yaml.safe_load(f)
            return True
        except yaml.YAMLError as e:
            print(f"YAML syntax error in {file_path}: {e}")
            return False
    
    def process_files(self, file_list: List[Path], target_variable: str, 
                     new_variable: str, new_value: str, 
                     validate_syntax: bool = True, backup: bool = True) -> Dict[str, bool]:
        """Process a list of YAML files."""
        results = {}
        
        try:
            if not file_list:
                print("No files to process.")
                return results
            
            print(f"Processing {len(file_list)} YAML file(s):")
            for file_path in file_list:
                print(f"  - {file_path.name}")
            
            print(f"\nProcessing files...")
            print(f"Target variable: {target_variable}")
            print(f"New variable: {new_variable} = {new_value}")
            print("-" * 50)
            
            success_count = 0
            
            for file_path in file_list:
                success = self.process_file(file_path, target_variable, new_variable, new_value, backup)
                results[str(file_path)] = success
                
                if success and validate_syntax:
                    if not self.validate_yaml_syntax(file_path):
                        print(f"⚠ Warning: YAML syntax validation failed for {file_path}")
                        results[str(file_path)] = False
                    else:
                        success_count += 1
                elif success:
                    success_count += 1
            
            print("-" * 50)
            print(f"Processing complete: {success_count}/{len(file_list)} files successfully modified")
            
            return results
            
        except Exception as e:
            print(f"Error processing files: {e}")
            return results
    def process_folder(self, folder_path: str, target_variable: str, 
                      new_variable: str, new_value: str, 
                      validate_syntax: bool = True, backup: bool = True) -> Dict[str, bool]:
        """Process all YAML files in a folder."""
        try:
            yaml_files = self.find_yaml_files(folder_path)
            
            if not yaml_files:
                print(f"No YAML files found in {folder_path}")
                return {}
            
            return self.process_files(yaml_files, target_variable, new_variable, new_value, validate_syntax, backup)
            
        except Exception as e:
            print(f"Error processing folder: {e}")
            return {}


def get_user_input():
    """Get user input for the script parameters."""
    print("YAML Variable Inserter")
    print("=" * 50)
    
    # Ask if user wants to process a single file or all files in a folder
    mode = input("Process (1) single file or (2) all files in folder? Enter 1 or 2: ").strip()
    
    if mode == "1":
        # Single file mode
        while True:
            file_input = input("Enter the path to the YAML file: ").strip()
            file_path = Path(file_input)
            
            if not file_path.exists():
                print("File not found. Please try again.")
                continue
            
            if file_path.suffix.lower() not in ['.yml', '.yaml']:
                print("File is not a YAML file. Please select a .yml or .yaml file.")
                continue
            
            folder_path = str(file_path.parent)
            selected_files = [file_path]
            break
            
        print(f"\nSelected file: {file_path.name}")
        
    elif mode == "2":
        # Folder mode (original functionality)
        while True:
            folder_path = input("Enter the folder path containing YAML files: ").strip()
            if folder_path and os.path.exists(folder_path):
                break
            print("Invalid folder path. Please try again.")
        
        selected_files = None  # Will find all files in folder
        
    else:
        print("Invalid option. Please enter 1 or 2.")
        return None, None, None, None, False
    
    # Get target variable
    target_variable = input("Enter the existing variable name after which to insert: ").strip()
    
    # Get new variable name
    new_variable = input("Enter the new variable name: ").strip()
    
    # Get new variable value
    new_value_input = input("Enter the new variable value: ").strip()
    
    # Try to convert value to appropriate type
    new_value = new_value_input
    if new_value_input.lower() in ['true', 'false']:
        new_value = new_value_input.lower() == 'true'
    elif new_value_input.isdigit():
        new_value = int(new_value_input)
    elif '.' in new_value_input:
        try:
            new_value = float(new_value_input)
        except ValueError:
            pass  # Keep as string
    
    # Show configuration
    if mode == "1":
        print(f"\nConfiguration:")
        print(f"File: {selected_files[0].name}")
        print(f"Target variable: {target_variable}")
        print(f"New variable: {new_variable} = {new_value} ({type(new_value).__name__})")
    else:
        print(f"\nConfiguration:")
        print(f"Folder: {folder_path}")
        print(f"Target variable: {target_variable}")
        print(f"New variable: {new_variable} = {new_value} ({type(new_value).__name__})")
    
    confirm = input("\nProceed with these settings? (y/n): ").strip().lower()
    
    return folder_path, target_variable, new_variable, new_value, confirm == 'y', selected_files if mode == "1" else None


def main():
    """Main function to run the script."""
    try:
        user_input = get_user_input()
        if user_input[0] is None:  # User cancelled or invalid input
            return
            
        folder_path, target_variable, new_variable, new_value, confirmed, selected_files = user_input
        
        if not confirmed:
            print("Operation cancelled.")
            return
        
        inserter = YAMLVariableInserter()
        
        if selected_files:
            # Single file mode
            results = inserter.process_files(selected_files, target_variable, new_variable, new_value)
        else:
            # Folder mode
            results = inserter.process_folder(folder_path, target_variable, new_variable, new_value)
        
        # Summary
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        
        if successful == total and total > 0:
            print(f"\n✓ All {total} files processed successfully!")
        elif successful > 0:
            print(f"\n⚠ {successful}/{total} files processed successfully.")
            print("Failed files:")
            for file_path, success in results.items():
                if not success:
                    print(f"  - {Path(file_path).name}")
        else:
            print(f"\n✗ No files were processed successfully.")
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")


if __name__ == "__main__":
    main()
