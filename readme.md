# Venv Exe Repair Tool

A tool to fix Python interpreter paths in Windows virtual environment executables.

## Features

- Fix shebang lines in venv executables
- Support single file or batch processing
- View current shebang without modifying files
- Optional backup creation
- Debug mode for detailed output

## Usage

```bash
# View current shebang
python venv_repair.py -f venv/Scripts/pip.exe -p

# Repair single file
python venv_repair.py -f venv/Scripts/pip.exe -b "C:/Python310/python.exe"

# Batch repair
ls venv/Scripts/*.exe | python venv_repair.py -b "C:/Python310/python.exe"

# With backup
python venv_repair.py -f venv/Scripts/pip.exe -b "C:/Python310/python.exe" --backup
```

## Options

- `-f, --filename`: Target executable file
- `-b, --base_interpreter`: New Python interpreter path
- `-p, --print_only`: Show current shebang only
- `--backup`: Create backup before modifying
- `-d, --debug`: Enable debug output

## Examples

```bash
# Move venv and repair
python venv_repair.py -f venv/Scripts/pip.exe -b "C:/NewPath/python.exe"

# Batch fix all executables
dir /b venv\Scripts\*.exe | python venv_repair.py -b "C:/Python310/python.exe"
```