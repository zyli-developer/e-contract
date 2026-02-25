#!/usr/bin/env python3
"""
Test suite for data importer.

Run with: python test_importer.py
"""

import json
import sys
import tempfile
from pathlib import Path
from datetime import datetime

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Mock SQLAlchemy before importing importer
sys.modules['sqlalchemy'] = type(sys)('sqlalchemy')
sys.modules['sqlalchemy.orm'] = type(sys)('sqlalchemy.orm')
sys.modules['sqlalchemy'].create_engine = lambda x: None
sys.modules['sqlalchemy.orm'].sessionmaker = lambda **kw: lambda: None
sys.modules['sqlalchemy'].inspect = lambda x: None

from importer import DataImporter


class TestImporter:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.test_dir = None

    def setup(self):
        """Create test directory with sample .md files."""
        self.test_dir = tempfile.mkdtemp()
        test_path = Path(self.test_dir)

        # Create .synnovator structure
        user_dir = test_path / "user"
        user_dir.mkdir(parents=True)

        # Create sample user file
        user_file = user_dir / "user_alice.md"
        user_file.write_text("""---
id: user_alice
username: alice
email: alice@example.com
display_name: Alice
role: participant
created_at: '2025-01-01T00:00:00Z'
---
""")

        # Create post directory
        post_dir = test_path / "post"
        post_dir.mkdir(parents=True)

        # Create sample post file
        post_file = post_dir / "post_hello.md"
        post_file.write_text("""---
id: post_hello
title: Hello World
type: general
status: published
tags: ["test", "demo"]
created_by: user_alice
created_at: '2025-01-01T00:00:00Z'
---

This is a test post.
""")

        print(f"✅ Created test directory: {self.test_dir}")

    def cleanup(self):
        """Remove test directory."""
        import shutil
        if self.test_dir and Path(self.test_dir).exists():
            shutil.rmtree(self.test_dir)
            print(f"🧹 Cleaned up test directory")

    def test_parse_md_file(self):
        """Test parsing .md files with YAML frontmatter."""
        print("\n" + "=" * 60)
        print("Test 1: Parse .md file with YAML frontmatter")
        print("=" * 60)

        # Create mock importer
        importer = DataImporter.__new__(DataImporter)
        importer.source_dir = Path(self.test_dir)

        # Test file
        test_file = Path(self.test_dir) / "user" / "user_alice.md"

        result = importer.parse_md_file(test_file)

        checks = [
            (result is not None, "File parsed successfully"),
            ("data" in result, "Has 'data' field"),
            ("body" in result, "Has 'body' field"),
            (result["data"]["id"] == "user_alice", "Correct ID parsed"),
            (result["data"]["username"] == "alice", "Correct username parsed"),
        ]

        all_passed = self._check_results(checks)
        if all_passed:
            print("✅ PASSED: parse_md_file works correctly")
            self.passed += 1
        else:
            print("❌ FAILED: parse_md_file test failed")
            self.failed += 1

    def test_convert_value(self):
        """Test value type conversion."""
        print("\n" + "=" * 60)
        print("Test 2: Convert values to database types")
        print("=" * 60)

        importer = DataImporter.__new__(DataImporter)

        tests = [
            ("2025-01-01T00:00:00Z", "datetime", "Datetime conversion"),
            (["tag1", "tag2"], "json", "JSON array conversion"),
            ("true", "boolean", "Boolean conversion"),
            ("123", "integer", "Integer conversion"),
        ]

        checks = []
        for value, col_type, description in tests:
            result = importer.convert_value(value, col_type)
            checks.append((result is not None, description))

        all_passed = self._check_results(checks)
        if all_passed:
            print("✅ PASSED: convert_value works correctly")
            self.passed += 1
        else:
            print("❌ FAILED: convert_value test failed")
            self.failed += 1

    def test_import_order(self):
        """Test import order is correct."""
        print("\n" + "=" * 60)
        print("Test 3: Import order follows dependencies")
        print("=" * 60)

        checks = [
            ("user" in DataImporter.IMPORT_ORDER, "user in import order"),
            (
                DataImporter.IMPORT_ORDER.index("user")
                < DataImporter.IMPORT_ORDER.index("post"),
                "user before post",
            ),
            (
                DataImporter.IMPORT_ORDER.index("post")
                < DataImporter.IMPORT_ORDER.index("post_resource"),
                "post before post_resource",
            ),
            (len(DataImporter.IMPORT_ORDER) == 14, "All 14 types defined"),
        ]

        all_passed = self._check_results(checks)
        if all_passed:
            print("✅ PASSED: Import order is correct")
            self.passed += 1
        else:
            print("❌ FAILED: Import order test failed")
            self.failed += 1

    def _check_results(self, checks):
        """Check test results and print status."""
        all_passed = True
        for condition, description in checks:
            if condition:
                print(f"  ✅ {description}")
            else:
                print(f"  ❌ {description}")
                all_passed = False
        return all_passed

    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 60)
        print("Test Summary")
        print("=" * 60)
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"Total: {self.passed + self.failed}")

        if self.failed == 0:
            print("\n🎉 All tests passed!")
            return True
        else:
            print(f"\n⚠️  {self.failed} test(s) failed")
            return False

    def run_all(self):
        """Run all tests."""
        print("🚀 Running data-importer tests\n")

        self.setup()

        try:
            self.test_parse_md_file()
            self.test_convert_value()
            self.test_import_order()

            return self.print_summary()
        finally:
            self.cleanup()


def main():
    tester = TestImporter()
    all_passed = tester.run_all()
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
