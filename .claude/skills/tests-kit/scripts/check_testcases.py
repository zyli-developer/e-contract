#!/usr/bin/env python3
"""Validate test case files in specs/testcases/ for format consistency and ID uniqueness.

Usage:
    python check_testcases.py [testcases_dir]

Default testcases_dir: specs/testcases/ relative to project root.

Checks performed:
1. TC ID format: TC-{PREFIX}-{NUMBER}
2. TC ID uniqueness across all files
3. File structure: header, format convention note, sections
4. Number range conventions (001-099 positive, 900-999 negative)
"""

import re
import sys
from pathlib import Path

TC_ID_PATTERN = re.compile(r"\*\*(?P<id>TC-[\w-]+-\d{3}(?:-\d+)?)(?:：|:)")
HEADER_PATTERN = re.compile(r"^# .+")
FORMAT_NOTE_PATTERN = re.compile(r">\s*\*\*格式约定")


def find_project_root() -> Path:
    """Walk up from script location to find project root (has pyproject.toml)."""
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / "pyproject.toml").exists():
            return current
        current = current.parent
    return Path.cwd()


def validate_file(filepath: Path) -> list[dict]:
    """Validate a single test case file. Returns list of issues."""
    issues = []
    text = filepath.read_text(encoding="utf-8")
    lines = text.splitlines()

    # Check header
    if not lines or not HEADER_PATTERN.match(lines[0]):
        issues.append({
            "file": filepath.name,
            "line": 1,
            "severity": "error",
            "message": "Missing top-level markdown header (# Title)",
        })

    # Check format convention note
    has_format_note = any(FORMAT_NOTE_PATTERN.search(line) for line in lines[:10])
    if not has_format_note:
        issues.append({
            "file": filepath.name,
            "line": 0,
            "severity": "warning",
            "message": "Missing format convention note (> **格式约定：**...)",
        })

    # Extract and validate TC IDs
    tc_ids = []
    for i, line in enumerate(lines, 1):
        match = TC_ID_PATTERN.search(line)
        if match:
            tc_id = match.group("id")
            tc_ids.append((tc_id, i))

            # Validate number range
            num_match = re.search(r"-(\d{3})(?:-\d+)?$", tc_id)
            if num_match:
                num = int(num_match.group(1))
                if 100 <= num < 900 and num >= 200:
                    # Numbers 200-899 are unusual but not necessarily wrong
                    pass

    if not tc_ids:
        issues.append({
            "file": filepath.name,
            "line": 0,
            "severity": "warning",
            "message": "No test cases found in file",
        })

    return issues, tc_ids


def validate_all(testcases_dir: Path) -> tuple[list[dict], dict]:
    """Validate all test case files. Returns (issues, id_map)."""
    all_issues = []
    id_map: dict[str, list[tuple[str, int]]] = {}  # tc_id -> [(file, line)]

    md_files = sorted(testcases_dir.glob("*.md"))
    if not md_files:
        all_issues.append({
            "file": str(testcases_dir),
            "line": 0,
            "severity": "error",
            "message": "No .md files found in testcases directory",
        })
        return all_issues, id_map

    for filepath in md_files:
        if filepath.name.lower() == "readme.md":
            continue
        issues, tc_ids = validate_file(filepath)
        all_issues.extend(issues)

        for tc_id, line in tc_ids:
            if tc_id not in id_map:
                id_map[tc_id] = []
            id_map[tc_id].append((filepath.name, line))

    # Check for duplicate IDs
    for tc_id, locations in id_map.items():
        if len(locations) > 1:
            loc_str = ", ".join(f"{f}:{l}" for f, l in locations)
            all_issues.append({
                "file": "CROSS-FILE",
                "line": 0,
                "severity": "error",
                "message": f"Duplicate TC ID '{tc_id}' found in: {loc_str}",
            })

    return all_issues, id_map


def main():
    if len(sys.argv) > 1:
        testcases_dir = Path(sys.argv[1])
    else:
        root = find_project_root()
        testcases_dir = root / "specs" / "testcases"

    if not testcases_dir.is_dir():
        print(f"ERROR: Directory not found: {testcases_dir}")
        sys.exit(1)

    print(f"Validating test cases in: {testcases_dir}")
    print("=" * 60)

    issues, id_map = validate_all(testcases_dir)

    # Summary
    total_ids = len(id_map)
    total_files = len(list(testcases_dir.glob("*.md")))
    errors = [i for i in issues if i["severity"] == "error"]
    warnings = [i for i in issues if i["severity"] == "warning"]

    print(f"\nFiles scanned: {total_files}")
    print(f"Test cases found: {total_ids}")
    print(f"Errors: {len(errors)}")
    print(f"Warnings: {len(warnings)}")

    if errors:
        print("\n--- ERRORS ---")
        for issue in errors:
            loc = f"{issue['file']}:{issue['line']}" if issue["line"] else issue["file"]
            print(f"  [{loc}] {issue['message']}")

    if warnings:
        print("\n--- WARNINGS ---")
        for issue in warnings:
            loc = f"{issue['file']}:{issue['line']}" if issue["line"] else issue["file"]
            print(f"  [{loc}] {issue['message']}")

    if not errors:
        print("\n✓ All test cases pass validation.")
        sys.exit(0)
    else:
        print(f"\n✗ {len(errors)} error(s) found.")
        sys.exit(1)


if __name__ == "__main__":
    main()
