#!/usr/bin/env python3
"""
Base test infrastructure for Synnovator modular tests.
Provides TestRunner class and composable fixture builders.
"""

import shutil
import sys
from pathlib import Path

# Add scripts dir to path so engine imports work
_scripts_dir = Path(__file__).parent.parent
sys.path.insert(0, str(_scripts_dir))

from engine import (
    init_dirs, get_data_dir,
    create_content, read_content, update_content, delete_content,
    create_relation, read_relation, update_relation, delete_relation,
)


class TestRunner:
    """Base test runner with assertion helpers and lifecycle management."""

    # Subclasses should override this for data isolation
    data_dir_suffix = "_test_base"

    def __init__(self):
        self.data_dir = (
            Path(__file__).parent.parent.parent.parent.parent
            / f".synnovator{self.data_dir_suffix}"
        )
        self.passed = 0
        self.failed = 0
        self.errors = []
        self.ids = {}

    def setup(self):
        if self.data_dir.exists():
            shutil.rmtree(self.data_dir)
        init_dirs(self.data_dir)

    def teardown(self):
        if self.data_dir.exists():
            shutil.rmtree(self.data_dir)

    def assert_ok(self, name, condition, msg=""):
        if condition:
            self.passed += 1
            print(f"  PASS: {name}")
        else:
            self.failed += 1
            self.errors.append(f"{name}: {msg}")
            print(f"  FAIL: {name} - {msg}")

    def assert_raises(self, name, fn, error_substr=""):
        try:
            fn()
            self.failed += 1
            self.errors.append(f"{name}: Expected error but succeeded")
            print(f"  FAIL: {name} - Expected error")
        except (ValueError, Exception) as e:
            if error_substr and error_substr not in str(e):
                self.failed += 1
                self.errors.append(f"{name}: Expected '{error_substr}' in error, got: {e}")
                print(f"  FAIL: {name} - Wrong error: {e}")
            else:
                self.passed += 1
                print(f"  PASS: {name}")

    def run_tests(self):
        """Run all test_* methods on this class."""
        self.setup()
        try:
            self._run_fixtures()
            methods = [m for m in sorted(dir(self)) if m.startswith("test_")]
            for method_name in methods:
                getattr(self, method_name)()
        finally:
            self.report()
            self.teardown()
        return self.failed == 0

    def _run_fixtures(self):
        """Override in subclasses to set up fixture data before tests."""
        pass

    def report(self):
        print(f"\n{'='*50}")
        print(f"Results: {self.passed} passed, {self.failed} failed")
        if self.errors:
            print(f"\nFailures:")
            for e in self.errors:
                print(f"  - {e}")


# ---------------------------------------------------------------------------
# Composable fixture builders
# ---------------------------------------------------------------------------

def create_base_users(data_dir, ids):
    """Create the standard set of 5 users: alice (organizer), bob, carol, dave (participants), judge (organizer)."""
    alice = create_content(data_dir, "user", {
        "id": "user_alice", "username": "alice", "email": "alice@example.com",
        "display_name": "Alice Chen", "role": "organizer"
    })
    ids["user_alice"] = alice["id"]

    bob = create_content(data_dir, "user", {
        "id": "user_bob", "username": "bob", "email": "bob@example.com",
        "display_name": "Bob Li", "role": "participant"
    })
    ids["user_bob"] = bob["id"]

    carol = create_content(data_dir, "user", {
        "id": "user_carol", "username": "carol", "email": "carol@example.com",
        "display_name": "Carol Zhang", "role": "participant"
    })
    ids["user_carol"] = carol["id"]

    dave = create_content(data_dir, "user", {
        "id": "user_dave", "username": "dave", "email": "dave@example.com",
        "display_name": "Dave Wu", "role": "participant"
    })
    ids["user_dave"] = dave["id"]

    judge = create_content(data_dir, "user", {
        "id": "user_judge", "username": "judge01", "email": "judge@example.com",
        "display_name": "Judge One", "role": "organizer"
    })
    ids["user_judge"] = judge["id"]


def create_base_category_and_rule(data_dir, ids):
    """Create the standard AI Hackathon event and submission rule, linked via event_rule."""
    cat = create_content(data_dir, "event", {
        "id": "cat_hackathon_2025", "name": "2025 AI Hackathon",
        "description": "Global AI innovation competition",
        "type": "competition", "status": "published",
        "start_date": "2025-03-01T00:00:00Z", "end_date": "2025-03-15T23:59:59Z",
        "_body": "## About\n\nAI Hackathon for developers worldwide."
    }, current_user=ids["user_alice"])
    ids["cat1"] = cat["id"]

    rule = create_content(data_dir, "rule", {
        "id": "rule_submission_01", "name": "AI Hackathon Submission Rule",
        "description": "2025 AI Hackathon submission requirements",
        "allow_public": True, "require_review": True,
        "reviewers": [ids["user_judge"]],
        "submission_start": "2025-01-01T00:00:00Z",
        "submission_deadline": "2030-12-31T23:59:59Z",
        "submission_format": ["markdown", "pdf", "zip"],
        "max_submissions": 3, "min_team_size": 1, "max_team_size": 5,
        "scoring_criteria": [
            {"name": "\u521b\u65b0\u6027", "weight": 30, "description": "Originality"},
            {"name": "\u6280\u672f\u5b9e\u73b0", "weight": 30, "description": "Code quality"},
            {"name": "\u5b9e\u7528\u4ef7\u503c", "weight": 25, "description": "Practical value"},
            {"name": "\u6f14\u793a\u6548\u679c", "weight": 15, "description": "Demo quality"}
        ],
        "_body": "## Rules\n\n1. Submit project docs, source code, demo video."
    }, current_user=ids["user_alice"])
    ids["rule1"] = rule["id"]

    create_relation(data_dir, "event_rule", {
        "event_id": cat["id"], "rule_id": rule["id"], "priority": 1
    })


def create_base_group(data_dir, ids):
    """Create Team Synnovator group with alice as owner."""
    grp = create_content(data_dir, "group", {
        "id": "grp_team_synnovator", "name": "Team Synnovator",
        "description": "AI Hackathon team", "visibility": "public",
        "max_members": 5, "require_approval": True
    }, current_user=ids["user_alice"])
    ids["grp1"] = grp["id"]

    create_relation(data_dir, "group_user", {
        "group_id": grp["id"], "user_id": ids["user_alice"], "role": "owner"
    })


def create_base_posts(data_dir, ids):
    """Create profile and team posts."""
    profile_alice = create_content(data_dir, "post", {
        "id": "post_profile_alice", "title": "About Alice",
        "type": "profile", "status": "published",
        "tags": ["backend", "AI"],
        "_body": "## About Me\n\nFull-stack developer with AI focus."
    }, current_user=ids["user_alice"])
    ids["post_profile_alice"] = profile_alice["id"]

    team_post = create_content(data_dir, "post", {
        "id": "post_team_synnovator", "title": "Team Synnovator",
        "type": "team", "status": "published",
        "tags": ["fullstack", "AI"],
        "_body": "## Team\n\nWe build AI applications."
    }, current_user=ids["user_alice"])
    ids["post_team"] = team_post["id"]


def create_full_baseline(data_dir, ids):
    """Create the complete baseline: users + event + rule + group + posts."""
    create_base_users(data_dir, ids)
    create_base_category_and_rule(data_dir, ids)
    create_base_group(data_dir, ids)
    create_base_posts(data_dir, ids)


def create_submission_scenario(data_dir, ids):
    """Extend baseline with a submission post linked to the event.
    Requires create_full_baseline() to have been called first.
    Also registers the group for the event and adds carol to the group.
    """
    # Carol joins group
    rel = create_relation(data_dir, "group_user", {
        "group_id": ids["grp1"], "user_id": ids["user_carol"], "role": "member"
    })
    update_relation(data_dir, "group_user",
        {"group_id": ids["grp1"], "user_id": ids["user_carol"]},
        {"status": "accepted"}
    )

    # Register group for event
    create_relation(data_dir, "event_group", {
        "event_id": ids["cat1"], "group_id": ids["grp1"]
    })

    # Create submission post
    post = create_content(data_dir, "post", {
        "title": "AI Code Review Copilot",
        "type": "proposal",
        "tags": ["AI", "Developer Tools"],
        "_body": "## Project\nCodeReview Copilot is an AI-powered code review tool."
    }, current_user=ids["user_alice"])
    ids["post_submission"] = post["id"]

    # Link to event
    create_relation(data_dir, "event_post", {
        "event_id": ids["cat1"], "post_id": post["id"],
        "relation_type": "submission"
    })
