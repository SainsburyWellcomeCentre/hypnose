#!/usr/bin/env python3
"""
Script to rename strings in all YAML files within a specified folder.

This script recursively searches through a folder for all .yml and .yaml files,
opens each file, and replaces all occurrences of a specified string with a new string.

Usage:
    python rename_strings_in_yml.py <folder_path> <old_string> <new_string> [--dry-run]

Arguments:
    folder_path: Path to the folder containing YAML files
    old_string: The string to be replaced
    new_string: The replacement string
    --dry-run: Optional flag to preview changes without modifying files

Example:
    python rename_strings_in_yml.py ./src "old_value" "new_value"
    python rename_strings_in_yml.py ./src "old_value" "new_value" --dry-run
"""

import os
import sys
import argparse
import glob
from pathlib import Path


def find_yml_files(folder_path):
    """
    Find all YAML files in the specified folder and its subdirectories.
    
    Args:
        folder_path (str): Path to the folder to search
        
    Returns:
        list: List of paths to YAML files
    """
    yml_files = []
    folder_path = Path(folder_path)
    
    # Search for .yml and .yaml files recursively
    for pattern in ['**/*.yml', '**/*.yaml']:
        yml_files.extend(folder_path.glob(pattern))
    
    return [str(file) for file in yml_files]


def replace_string_in_file(file_path, old_string, new_string, dry_run=False):
    """
    Replace all occurrences of old_string with new_string in a file.
    
    Args:
        file_path (str): Path to the file
        old_string (str): String to be replaced
        new_string (str): Replacement string
        dry_run (bool): If True, only preview changes without modifying the file
        
    Returns:
        tuple: (number_of_replacements, modified_content_preview)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Count occurrences
        count = content.count(old_string)
        
        if count == 0:
            return 0, None
        
        # Replace the string
        new_content = content.replace(old_string, new_string)
        
        if not dry_run:
            # Write the modified content back to the file
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(new_content)
        
        return count, new_content if dry_run else None
    
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return 0, None


def main():
    """Main function to handle command line arguments and execute the replacement."""
    parser = argparse.ArgumentParser(
        description='Rename strings in all YAML files within a folder',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python rename_strings_in_yml.py ./src "old_value" "new_value"
  python rename_strings_in_yml.py ./src "old_value" "new_value" --dry-run
        """
    )
    
    parser.add_argument('folder_path', help='Path to the folder containing YAML files')
    parser.add_argument('old_string', help='The string to be replaced')
    parser.add_argument('new_string', help='The replacement string')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Preview changes without modifying files')
    
    args = parser.parse_args()
    
    # Validate folder path
    if not os.path.exists(args.folder_path):
        print(f"Error: Folder '{args.folder_path}' does not exist.")
        sys.exit(1)
    
    if not os.path.isdir(args.folder_path):
        print(f"Error: '{args.folder_path}' is not a directory.")
        sys.exit(1)
    
    # Find all YAML files
    print(f"Searching for YAML files in '{args.folder_path}'...")
    yml_files = find_yml_files(args.folder_path)
    
    if not yml_files:
        print("No YAML files found in the specified folder.")
        sys.exit(0)
    
    print(f"Found {len(yml_files)} YAML file(s).")
    
    if args.dry_run:
        print(f"\n--- DRY RUN MODE ---")
        print(f"This will replace '{args.old_string}' with '{args.new_string}'")
        print("No files will be modified.\n")
    else:
        print(f"\nReplacing '{args.old_string}' with '{args.new_string}'...")
        print("Files will be modified.\n")
    
    total_replacements = 0
    files_modified = 0
    
    # Process each YAML file
    for yml_file in yml_files:
        replacements, preview = replace_string_in_file(
            yml_file, args.old_string, args.new_string, args.dry_run
        )
        
        if replacements > 0:
            files_modified += 1
            total_replacements += replacements
            status = "WOULD MODIFY" if args.dry_run else "MODIFIED"
            print(f"{status}: {yml_file} ({replacements} replacement(s))")
            
            # Show preview for dry run
            if args.dry_run and preview:
                print("  Preview of first few lines with changes:")
                lines = preview.split('\n')[:10]  # Show first 10 lines
                for i, line in enumerate(lines, 1):
                    if args.new_string in line:
                        print(f"    {i:2d}: {line}")
                print()
        else:
            print(f"NO CHANGES: {yml_file}")
    
    # Summary
    print(f"\n--- SUMMARY ---")
    if args.dry_run:
        print(f"Would modify {files_modified} file(s)")
        print(f"Would make {total_replacements} replacement(s)")
        print("Run without --dry-run to apply changes.")
    else:
        print(f"Modified {files_modified} file(s)")
        print(f"Made {total_replacements} replacement(s)")
        print("Changes have been applied.")


if __name__ == "__main__":
    main()
