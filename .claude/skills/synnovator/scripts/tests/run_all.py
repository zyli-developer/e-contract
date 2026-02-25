#!/usr/bin/env python3
"""
Test orchestrator — run all modular test files or a specific subset by number.

Usage:
    uv run python .claude/skills/synnovator/scripts/tests/run_all.py          # Run all
    uv run python .claude/skills/synnovator/scripts/tests/run_all.py 3 4 11   # Run specific files
"""

import importlib
import sys
from pathlib import Path

# Map file numbers to module names and test class names
TEST_FILES = {
    1:  ("test_01_user",                "TestUser"),
    2:  ("test_02_category",            "TestCategory"),
    3:  ("test_03_rule",                "TestRule"),
    4:  ("test_04_group",               "TestGroup"),
    5:  ("test_05_post",                "TestPost"),
    6:  ("test_06_resource",            "TestResource"),
    7:  ("test_07_interaction",         "TestInteraction"),
    8:  ("test_08_relations",           "TestRelations"),
    9:  ("test_09_cascade_delete",      "TestCascadeDelete"),
    10: ("test_10_permissions",         "TestPermissions"),
    11: ("test_11_user_journeys",       "TestUserJourneys"),
    12: ("test_12_resource_transfer",   "TestResourceTransfer"),
    13: ("test_13_user_follow",         "TestUserFollow"),
    14: ("test_14_category_association","TestCategoryAssociation"),
    15: ("test_15_entry_rules",         "TestEntryRules"),
    16: ("test_16_closure_rules",       "TestClosureRules"),
    17: ("test_17_rule_engine",         "TestRuleEngine"),
}


def run_tests(numbers=None):
    """Run test files by number. If numbers is None, run all."""
    tests_dir = Path(__file__).parent
    sys.path.insert(0, str(tests_dir))

    if numbers is None:
        numbers = sorted(TEST_FILES.keys())

    total_passed = 0
    total_failed = 0
    results = []

    for num in numbers:
        if num not in TEST_FILES:
            print(f"\nWARNING: No test file for number {num}, skipping.")
            continue

        module_name, class_name = TEST_FILES[num]
        print(f"\n{'='*60}")
        print(f"Running {module_name} ({class_name})")
        print(f"{'='*60}")

        try:
            mod = importlib.import_module(module_name)
            cls = getattr(mod, class_name)
            runner = cls()
            success = runner.run_tests()
            total_passed += runner.passed
            total_failed += runner.failed
            results.append((module_name, runner.passed, runner.failed, success))
        except Exception as e:
            print(f"  ERROR: {e}")
            total_failed += 1
            results.append((module_name, 0, 1, False))

    # Summary
    print(f"\n{'='*60}")
    print(f"OVERALL RESULTS")
    print(f"{'='*60}")
    for module_name, passed, failed, success in results:
        status = "PASS" if success else "FAIL"
        print(f"  [{status}] {module_name}: {passed} passed, {failed} failed")
    print(f"\nTotal: {total_passed} passed, {total_failed} failed")

    return total_failed == 0


if __name__ == "__main__":
    if len(sys.argv) > 1:
        numbers = [int(n) for n in sys.argv[1:]]
    else:
        numbers = None
    success = run_tests(numbers)
    sys.exit(0 if success else 1)
