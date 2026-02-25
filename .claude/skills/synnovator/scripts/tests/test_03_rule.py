#!/usr/bin/env python3
"""
TC-RULE-*: Rule CRUD and enforcement tests.
Migrated from test_journeys.py test_appendix_rule_definition + test_rule_enforcement.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from base import (
    TestRunner,
    create_full_baseline, create_submission_scenario,
    create_content, read_content, update_content, delete_content,
    create_relation, read_relation, update_relation, delete_relation,
)


class TestRule(TestRunner):
    data_dir_suffix = "_test_03_rule"

    def _run_fixtures(self):
        create_full_baseline(self.data_dir, self.ids)
        create_submission_scenario(self.data_dir, self.ids)
        # Create a daily post for select-only rule test
        post = create_content(self.data_dir, "post", {
            "title": "My Daily Update",
            "tags": ["diary"],
            "_body": "## Today\nWorked on the project."
        }, current_user=self.ids["user_bob"])
        self.ids["post_daily"] = post["id"]

    # --- CRUD tests ---

    def test_tc_rule_001_create_with_scoring(self):
        """TC-RULE-001: Create rule with complete scoring_criteria."""
        print("\n=== TC-RULE-001: Create with Scoring ===")
        rule = read_content(self.data_dir, "rule", self.ids["rule1"])
        self.assert_ok("Rule has scoring criteria", len(rule.get("scoring_criteria", [])) == 4)

    def test_tc_rule_002_create_select_only(self):
        """TC-RULE-002: Create select-only rule (allow_public=false, require_review=true)."""
        print("\n=== TC-RULE-002: Select-Only Rule ===")
        rule2 = create_content(self.data_dir, "rule", {
            "name": "Select Only Rule",
            "description": "Only allow selecting existing posts",
            "allow_public": False,
            "require_review": True,
        }, current_user=self.ids["user_alice"])
        self.ids["rule2"] = rule2["id"]
        self.assert_ok("Create select-only rule", rule2["allow_public"] == False)

        r = read_content(self.data_dir, "rule", rule2["id"])
        self.assert_ok("Read rule config", r["require_review"] == True)

        # Simulate: user selects existing post and adds tag
        existing_post = read_content(self.data_dir, "post", self.ids["post_daily"], current_user=self.ids["user_bob"])
        update_content(self.data_dir, "post", existing_post["id"], {
            "tags": "+for_ai_hackathon"
        }, current_user=self.ids["user_bob"])
        updated = read_content(self.data_dir, "post", existing_post["id"], current_user=self.ids["user_bob"])
        self.assert_ok("Add activity tag to existing post", "for_ai_hackathon" in updated["tags"])

    def test_tc_rule_003_read(self):
        """TC-RULE-003: Read created rule."""
        print("\n=== TC-RULE-003: Read Rule ===")
        rule = read_content(self.data_dir, "rule", self.ids["rule1"])
        self.assert_ok("Read rule", rule["name"] == "AI Hackathon Submission Rule")

    def test_tc_rule_010_update_config(self):
        """TC-RULE-010: Update rule configuration fields."""
        print("\n=== TC-RULE-010: Update Config ===")
        pass  # Skeleton

    def test_tc_rule_011_update_scoring_weights(self):
        """TC-RULE-011: Update scoring_criteria weights."""
        print("\n=== TC-RULE-011: Update Scoring Weights ===")
        pass  # Skeleton

    def test_tc_rule_020_delete_cascade(self):
        """TC-RULE-020: Delete rule and cascade event_rule."""
        print("\n=== TC-RULE-020: Delete Cascade ===")
        pass  # Skeleton

    def test_tc_rule_900_participant_rejected(self):
        """TC-RULE-900: Participant cannot create rule."""
        print("\n=== TC-RULE-900: Participant Rejected ===")
        pass  # Skeleton

    def test_tc_rule_901_scoring_weight_sum(self):
        """TC-RULE-901: scoring_criteria weights must sum to 100."""
        print("\n=== TC-RULE-901: Weight Sum ===")
        pass  # Skeleton

    # --- Enforcement tests (migrated from test_rule_enforcement) ---

    def test_tc_rule_100_deadline_passed(self):
        """TC-RULE-100: Reject submission after deadline."""
        print("\n=== TC-RULE-100: Deadline Passed ===")
        strict_cat = create_content(self.data_dir, "event", {
            "name": "Strict Contest", "description": "For rule tests",
            "type": "competition", "status": "published"
        }, current_user=self.ids["user_alice"])

        expired_rule = create_content(self.data_dir, "rule", {
            "name": "Expired Rule", "description": "Deadline passed",
            "submission_start": "2024-01-01T00:00:00Z",
            "submission_deadline": "2024-12-31T23:59:59Z",
        }, current_user=self.ids["user_alice"])
        create_relation(self.data_dir, "event_rule", {
            "event_id": strict_cat["id"], "rule_id": expired_rule["id"]
        })

        post1 = create_content(self.data_dir, "post", {
            "title": "Late Submission", "type": "proposal"
        }, current_user=self.ids["user_bob"])
        self.assert_raises(
            "Reject submission past deadline",
            lambda: create_relation(self.data_dir, "event_post", {
                "event_id": strict_cat["id"], "post_id": post1["id"],
                "relation_type": "submission"
            }),
            "deadline passed"
        )

    def test_tc_rule_101_not_yet_open(self):
        """TC-RULE-101: Reject submission before start."""
        print("\n=== TC-RULE-101: Not Yet Open ===")
        future_cat = create_content(self.data_dir, "event", {
            "name": "Future Contest", "description": "Not yet open",
            "type": "competition", "status": "published"
        }, current_user=self.ids["user_alice"])

        future_rule = create_content(self.data_dir, "rule", {
            "name": "Future Rule", "description": "Not yet open",
            "submission_start": "2030-06-01T00:00:00Z",
            "submission_deadline": "2030-12-31T23:59:59Z",
        }, current_user=self.ids["user_alice"])
        create_relation(self.data_dir, "event_rule", {
            "event_id": future_cat["id"], "rule_id": future_rule["id"]
        })

        post1 = create_content(self.data_dir, "post", {
            "title": "Early Submission", "type": "proposal"
        }, current_user=self.ids["user_bob"])
        self.assert_raises(
            "Reject submission before start",
            lambda: create_relation(self.data_dir, "event_post", {
                "event_id": future_cat["id"], "post_id": post1["id"],
                "relation_type": "submission"
            }),
            "not yet open"
        )

    def test_tc_rule_102_max_submissions(self):
        """TC-RULE-102: Reject exceeding max_submissions."""
        print("\n=== TC-RULE-102: Max Submissions ===")
        limit_cat = create_content(self.data_dir, "event", {
            "name": "One-Shot Contest", "description": "Max 1 submission",
            "type": "competition", "status": "published"
        }, current_user=self.ids["user_alice"])

        limit_rule = create_content(self.data_dir, "rule", {
            "name": "One Submission Rule", "description": "Max 1",
            "max_submissions": 1,
            "submission_start": "2025-01-01T00:00:00Z",
            "submission_deadline": "2030-12-31T23:59:59Z",
        }, current_user=self.ids["user_alice"])
        create_relation(self.data_dir, "event_rule", {
            "event_id": limit_cat["id"], "rule_id": limit_rule["id"]
        })

        post2 = create_content(self.data_dir, "post", {
            "title": "First Attempt", "type": "proposal"
        }, current_user=self.ids["user_bob"])
        create_relation(self.data_dir, "event_post", {
            "event_id": limit_cat["id"], "post_id": post2["id"],
            "relation_type": "submission"
        })
        self.assert_ok("First submission allowed", True)

        post3 = create_content(self.data_dir, "post", {
            "title": "Second Attempt", "type": "proposal"
        }, current_user=self.ids["user_bob"])
        self.assert_raises(
            "Reject exceeding max_submissions",
            lambda: create_relation(self.data_dir, "event_post", {
                "event_id": limit_cat["id"], "post_id": post3["id"],
                "relation_type": "submission"
            }),
            "max submissions reached"
        )

    def test_tc_rule_103_format_validation(self):
        """TC-RULE-103: Reject disallowed submission format."""
        print("\n=== TC-RULE-103: Format Validation ===")
        format_cat = create_content(self.data_dir, "event", {
            "name": "PDF Only Contest", "description": "Only PDF",
            "type": "competition", "status": "published"
        }, current_user=self.ids["user_alice"])

        format_rule = create_content(self.data_dir, "rule", {
            "name": "PDF Only Rule", "description": "Only PDF files",
            "submission_format": ["pdf"],
            "submission_start": "2025-01-01T00:00:00Z",
            "submission_deadline": "2030-12-31T23:59:59Z",
        }, current_user=self.ids["user_alice"])
        create_relation(self.data_dir, "event_rule", {
            "event_id": format_cat["id"], "rule_id": format_rule["id"]
        })

        post4 = create_content(self.data_dir, "post", {
            "title": "Wrong Format", "type": "proposal"
        }, current_user=self.ids["user_bob"])
        bad_res = create_content(self.data_dir, "resource", {
            "filename": "slides.pptx"
        }, current_user=self.ids["user_bob"])
        create_relation(self.data_dir, "post_resource", {
            "post_id": post4["id"], "resource_id": bad_res["id"],
            "display_type": "attachment"
        })

        self.assert_raises(
            "Reject disallowed format",
            lambda: create_relation(self.data_dir, "event_post", {
                "event_id": format_cat["id"], "post_id": post4["id"],
                "relation_type": "submission"
            }),
            "not allowed"
        )

    def test_tc_rule_104_min_team_size(self):
        """TC-RULE-104: Reject submission with too few team members."""
        print("\n=== TC-RULE-104: Min Team Size ===")
        team_cat = create_content(self.data_dir, "event", {
            "name": "Team Contest", "description": "Need 3+ members",
            "type": "competition", "status": "published"
        }, current_user=self.ids["user_alice"])

        team_rule = create_content(self.data_dir, "rule", {
            "name": "Team Size Rule", "description": "Min 3 members",
            "min_team_size": 3, "max_team_size": 5,
            "submission_start": "2025-01-01T00:00:00Z",
            "submission_deadline": "2030-12-31T23:59:59Z",
        }, current_user=self.ids["user_alice"])
        create_relation(self.data_dir, "event_rule", {
            "event_id": team_cat["id"], "rule_id": team_rule["id"]
        })

        small_grp = create_content(self.data_dir, "group", {
            "name": "Small Team", "visibility": "public", "require_approval": False
        }, current_user=self.ids["user_alice"])
        create_relation(self.data_dir, "group_user", {
            "group_id": small_grp["id"], "user_id": self.ids["user_alice"], "role": "owner"
        })
        create_relation(self.data_dir, "event_group", {
            "event_id": team_cat["id"], "group_id": small_grp["id"]
        })

        post5 = create_content(self.data_dir, "post", {
            "title": "Small Team Submission", "type": "proposal"
        }, current_user=self.ids["user_alice"])

        self.assert_raises(
            "Reject submission with too few members",
            lambda: create_relation(self.data_dir, "event_post", {
                "event_id": team_cat["id"], "post_id": post5["id"],
                "relation_type": "submission"
            }),
            "team too small"
        )

    def test_tc_rule_105_max_team_size(self):
        """TC-RULE-105: Reject joining full team."""
        print("\n=== TC-RULE-105: Max Team Size ===")
        tiny_cat = create_content(self.data_dir, "event", {
            "name": "Solo Contest", "description": "Max 1 member",
            "type": "competition", "status": "published"
        }, current_user=self.ids["user_alice"])

        tiny_rule = create_content(self.data_dir, "rule", {
            "name": "Solo Rule", "description": "Max 1",
            "max_team_size": 1,
        }, current_user=self.ids["user_alice"])
        create_relation(self.data_dir, "event_rule", {
            "event_id": tiny_cat["id"], "rule_id": tiny_rule["id"]
        })

        solo_grp = create_content(self.data_dir, "group", {
            "name": "Solo Group", "visibility": "public", "require_approval": False
        }, current_user=self.ids["user_alice"])
        create_relation(self.data_dir, "group_user", {
            "group_id": solo_grp["id"], "user_id": self.ids["user_alice"], "role": "owner"
        })
        create_relation(self.data_dir, "event_group", {
            "event_id": tiny_cat["id"], "group_id": solo_grp["id"]
        })

        self.assert_raises(
            "Reject joining full team",
            lambda: create_relation(self.data_dir, "group_user", {
                "group_id": solo_grp["id"], "user_id": self.ids["user_bob"],
                "role": "member"
            }),
            "team is full"
        )

    def test_tc_rule_106_no_direct_publish(self):
        """TC-RULE-106: allow_public=false blocks direct publish."""
        print("\n=== TC-RULE-106: No Direct Publish ===")
        strict_pub_cat = create_content(self.data_dir, "event", {
            "name": "Review Required Contest", "description": "No direct publish",
            "type": "competition", "status": "published"
        }, current_user=self.ids["user_alice"])

        strict_pub_rule = create_content(self.data_dir, "rule", {
            "name": "No Direct Publish", "description": "Must go through review",
            "allow_public": False, "require_review": True,
            "submission_start": "2025-01-01T00:00:00Z",
            "submission_deadline": "2030-12-31T23:59:59Z",
        }, current_user=self.ids["user_alice"])
        create_relation(self.data_dir, "event_rule", {
            "event_id": strict_pub_cat["id"], "rule_id": strict_pub_rule["id"]
        })

        post6 = create_content(self.data_dir, "post", {
            "title": "Needs Review", "type": "proposal"
        }, current_user=self.ids["user_bob"])
        create_relation(self.data_dir, "event_post", {
            "event_id": strict_pub_cat["id"], "post_id": post6["id"],
            "relation_type": "submission"
        })

        self.assert_raises(
            "Reject direct publish when review required",
            lambda: update_content(self.data_dir, "post", post6["id"], {"status": "published"}, current_user=self.ids["user_bob"]),
            "direct publish not allowed"
        )

    def test_tc_rule_107_pending_review_allowed(self):
        """TC-RULE-107: allow_public=false allows pending_review."""
        print("\n=== TC-RULE-107: Pending Review Allowed ===")
        strict_cat = create_content(self.data_dir, "event", {
            "name": "Review Only", "description": "No direct publish",
            "type": "competition", "status": "published"
        }, current_user=self.ids["user_alice"])

        strict_rule = create_content(self.data_dir, "rule", {
            "name": "No Pub", "description": "Must review",
            "allow_public": False, "require_review": True,
            "submission_start": "2025-01-01T00:00:00Z",
            "submission_deadline": "2030-12-31T23:59:59Z",
        }, current_user=self.ids["user_alice"])
        create_relation(self.data_dir, "event_rule", {
            "event_id": strict_cat["id"], "rule_id": strict_rule["id"]
        })

        post = create_content(self.data_dir, "post", {
            "title": "For Review", "type": "proposal"
        }, current_user=self.ids["user_bob"])
        create_relation(self.data_dir, "event_post", {
            "event_id": strict_cat["id"], "post_id": post["id"],
            "relation_type": "submission"
        })

        update_content(self.data_dir, "post", post["id"], {"status": "pending_review"}, current_user=self.ids["user_bob"])
        p = read_content(self.data_dir, "post", post["id"], current_user=self.ids["user_bob"])
        self.assert_ok("Pending review allowed", p["status"] == "pending_review")

    def test_tc_rule_108_no_rule_allows_freely(self):
        """TC-RULE-108: No rule linked means event_post creates freely."""
        print("\n=== TC-RULE-108: No Rule ===")
        pass  # Skeleton

    def test_tc_rule_109_multi_rule_and_logic(self):
        """TC-RULE-109: Multiple rules must all pass (AND logic)."""
        print("\n=== TC-RULE-109: Multi Rule AND ===")
        pass  # Skeleton


if __name__ == "__main__":
    runner = TestRule()
    success = runner.run_tests()
    sys.exit(0 if success else 1)
