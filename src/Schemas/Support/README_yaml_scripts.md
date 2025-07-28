# YAML Variable Insertion Scripts

This repository contains Python scripts to help you add new variables to existing YAML files in the hypnose project.

## Scripts

### 1. `simple_yaml_adder.py` (Recommended)
A streamlined script specifically designed for the hypnose project's YAML structure.

**Features:**
- Interactive prompts for easy use
- **Single file or folder processing** - choose to process one file or all files in a folder
- Preserves original formatting and indentation
- Works with the Schemas folder by default
- **Handles multiple occurrences** - adds the new variable after EVERY occurrence of the target variable
- **Proper YAML formatting** - automatically adds commas where needed to maintain valid YAML structure
- Simple and focused functionality

**Usage:**
```bash
python simple_yaml_adder.py
```

**Example interaction:**
```
Process (1) single file or (2) all files in folder? Enter 1 or 2: 1
Enter the path to the YAML file: src/Schemas/quintuples-stage6.yml
Selected file: quintuples-stage6.yml
Enter the existing variable name to insert after: maximumTime
Enter the new variable name: warningTime
Enter the new variable value: 8
Add 'warningTime: 8' after 'maximumTime' in 1 file? (y/n): y
```

### 2. `add_yaml_variable.py` (Advanced)
A more comprehensive script with additional features like backup creation and YAML validation.

**Features:**
- **Single file or folder processing** options
- Creates backup files before modification
- YAML syntax validation after changes
- More detailed error handling
- Type detection for values (boolean, int, float, string)

**Usage:**
```bash
python add_yaml_variable.py
```

### 3. `yaml_adder_cli.py` (Command Line)
A command-line version for automation and scripting.

**Features:**
- Non-interactive command-line interface
- Supports glob patterns for multiple files
- Perfect for automation scripts
- Can be integrated into build processes

**Usage:**
```bash
# Single file
python yaml_adder_cli.py src/Schemas/quintuples-stage6.yml maximumTime warningTime 8

# Multiple files with glob pattern
python yaml_adder_cli.py "src/Schemas/*.yml" maximumTime warningTime 8

# Specific pattern
python yaml_adder_cli.py "src/Schemas/quintuples-*.yml" maximumTime warningTime 8
```

## Installation

1. Install required dependency:
```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install PyYAML
```

## Use Cases

### Single File Processing
Perfect when you want to:
- Test changes on one file first
- Modify a specific configuration file
- Work with a file that has a unique structure

### Folder Processing  
Ideal when you need to:
- Apply changes to all schema files at once
- Maintain consistency across multiple configurations
- Batch update configuration parameters

### Command Line Processing
Great for:
- Automation scripts and CI/CD pipelines
- Scripted configuration updates
- Integration with other tools and workflows

## Example

Given a YAML file with this structure:
```yaml
sequences: [
  [
    {
      name: DoublesA_Stage1,
      maximumTime: 10,
      responseTime: 99999,
      interTrialInterval: 0
    },
    {
      name: DoublesB_Stage1,
      maximumTime: 10,
      responseTime: 99999,
      interTrialInterval: 0
    }
  ]
]
```

Running the script with:
- Target variable: `maximumTime`
- New variable: `warningTime`
- New value: `8`

Results in:
```yaml
sequences: [
  [
    {
      name: DoublesA_Stage1,
      maximumTime: 10,
      warningTime: 8,         # <- newly added
      responseTime: 99999,
      interTrialInterval: 0
    },
    {
      name: DoublesB_Stage1,
      maximumTime: 10,
      warningTime: 8,         # <- newly added here too
      responseTime: 99999,
      interTrialInterval: 0
    }
  ]
]
```

**Note:** The script adds the new variable after **every** occurrence of the target variable, and automatically adds commas to maintain proper YAML formatting.

## Notes

- The scripts preserve the original indentation and formatting
- **Variables are inserted after EVERY occurrence** of the specified target variable throughout the file
- **Automatic comma handling** - commas are added where needed to maintain valid YAML syntax
- All `.yml` files in the specified folder are processed
- The scripts handle nested YAML structures correctly
- Use git to track changes and revert if needed

## Safety

- Always run in a git repository or create backups
- The advanced script (`add_yaml_variable.py`) creates automatic backups
- Test on a single file first if unsure
- Use `git diff` to review changes before committing
