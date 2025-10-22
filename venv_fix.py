#!/usr/bin/env python3
"""
Windows venv executable repair tool
Fixes the shebang line in Python virtual environment executables
"""

import re
import argparse
import sys
import os
from pathlib import Path


def repair_file(filename, base_interpreter=None, print_only=False, debug=False, backup=False):
    """Repair a single venv executable file"""
    # Validate file exists
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' does not exist", file=sys.stderr)
        return False

    if not os.path.isfile(filename):
        print(f"Error: '{filename}' is not a file", file=sys.stderr)
        return False

    try:
        # Read file content
        with open(filename, 'rb') as f:
            content = f.read()

        if debug:
            print(f"Processing: {filename}")
            print(f"File size: {len(content)} bytes")
            print(f"First 100 bytes: {content[:100]}")

        # 修复正则表达式 - 使用原始字节字符串避免转义问题
        # 方法1: 查找 #! 到换行符之间的内容
        pattern1 = br'(?<=#!)[^\r\n]*(?=[\r\n]+PK)'
        # 方法2: 如果没有PK，查找 #! 到行尾的内容
        pattern2 = br'(?<=#!)[^\r\n]*'

        r = re.search(pattern1, content)

        if r is None:
            # Try alternative pattern in case file doesn't have PK header
            r = re.search(pattern2, content)
            if r is None:
                print(f"Error: {filename} does not appear to be a venv executable", file=sys.stderr)
                return False

        current_shebang = r.group().decode('utf-8', errors='replace')
        print(f"{filename}: Current shebang: {current_shebang}")

        if print_only:
            return True

        if backup:
            # Create backup
            backup_file = filename + '.backup'
            try:
                with open(backup_file, 'wb') as f:
                    f.write(content)
                if debug:
                    print(f"Backup created: {backup_file}")
            except Exception as e:
                print(f"Warning: Could not create backup for {filename}: {e}")

        # 使用更简单的方法替换内容 - 直接定位和替换
        old_shebang_part = r.group()
        new_shebang_part = base_interpreter.encode('utf-8')

        # 直接替换匹配到的部分
        start, end = r.span()
        new_content = content[:start] + new_shebang_part + content[end:]

        # Write modified content
        with open(filename, 'wb') as f:
            f.write(new_content)

        print(f"{filename}: Successfully updated shebang to: {base_interpreter}")
        return True

    except PermissionError:
        print(f"Error: Permission denied when accessing '{filename}'", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Error processing {filename}: {e}", file=sys.stderr)
        if debug:
            import traceback
            traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Repair Windows venv executable shebang lines",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Print current shebang only
  venv_repair.py -f venv/Scripts/python.exe -p

  # Repair with specific Python interpreter
  venv_repair.py -f venv/Scripts/python.exe -b "C:/Python39/python.exe"

  # Read multiple filenames from stdin (e.g., from ls or dir)
  ls venv/Scripts/*.exe | venv_repair.py -b "C:/Python39/python.exe"

  # Repair with backup
  venv_repair.py -f venv/Scripts/python.exe -b "C:/Python39/python.exe" --backup

  # Debug mode
  venv_repair.py -f venv/Scripts/pip.exe -b "C:/Python39/python.exe" -d
        """
    )

    parser.add_argument('-b', '--base_interpreter',
                        help='Path to base Python interpreter')
    parser.add_argument('-f', '--filename',
                        help='Path to venv executable to repair')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Enable debug output')
    parser.add_argument('-p', '--print_only', action='store_true',
                        help='Only print current shebang, do not modify')
    parser.add_argument('--backup', action='store_true',
                        help='Create backup files before modifying')

    args = parser.parse_args()

    # Validate arguments
    if not args.print_only and not args.base_interpreter:
        parser.error("--base_interpreter is required unless using --print_only")

    # Get file list - 如果没有指定文件，自动从stdin读取
    if args.filename:
        filenames = [args.filename]
    else:
        # 从stdin读取文件名
        filenames = []
        for line in sys.stdin:
            filename = line.strip()
            if filename:  # Skip empty lines
                filenames.append(filename)
        if not filenames:
            parser.error("No filenames provided via stdin or --filename")

    if args.debug:
        print(f"Files to process: {filenames}")

    # Process each file
    success_count = 0
    total_count = len(filenames)

    for filename in filenames:
        if repair_file(filename, args.base_interpreter, args.print_only, args.debug, args.backup):
            success_count += 1

    # Print summary
    if total_count > 1:
        print(f"\nSummary: {success_count}/{total_count} files processed successfully")

    # Exit with error code if any files failed
    if success_count < total_count:
        sys.exit(1)


if __name__ == '__main__':
    main()
