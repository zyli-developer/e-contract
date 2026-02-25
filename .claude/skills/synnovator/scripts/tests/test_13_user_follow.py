#!/usr/bin/env python3
"""
TC-FRIEND-*: User follow/friend relationship tests.
Migrated from test_journeys.py test_journey_14_follow_friend.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from base import (
    TestRunner,
    create_base_users,
    create_content, read_content, update_content, delete_content,
    create_relation, read_relation, update_relation, delete_relation,
)


class TestUserFollow(TestRunner):
    data_dir_suffix = "_test_13_user_follow"

    def _run_fixtures(self):
        create_base_users(self.data_dir, self.ids)

    # --- Migrated tests ---

    def test_tc_friend_001_follow(self):
        """TC-FRIEND-001: Alice follows Bob."""
        print("\n=== TC-FRIEND-001: Follow ===")
        rel = create_relation(self.data_dir, "user_user", {
            "source_user_id": self.ids["user_alice"],
            "target_user_id": self.ids["user_bob"],
            "relation_type": "follow"
        })
        self.assert_ok("Alice follows Bob", rel["relation_type"] == "follow")

    def test_tc_friend_002_mutual_follow(self):
        """TC-FRIEND-002: Mutual follow makes friends."""
        print("\n=== TC-FRIEND-002: Mutual Follow ===")
        # Bob -> Carol
        create_relation(self.data_dir, "user_user", {
            "source_user_id": self.ids["user_bob"],
            "target_user_id": self.ids["user_carol"],
            "relation_type": "follow"
        })
        # Carol -> Bob
        rel2 = create_relation(self.data_dir, "user_user", {
            "source_user_id": self.ids["user_carol"],
            "target_user_id": self.ids["user_bob"],
            "relation_type": "follow"
        })
        self.assert_ok("Carol follows Bob", rel2["relation_type"] == "follow")

        b_to_c = read_relation(self.data_dir, "user_user", {
            "source_user_id": self.ids["user_bob"],
            "target_user_id": self.ids["user_carol"],
            "relation_type": "follow"
        })
        c_to_b = read_relation(self.data_dir, "user_user", {
            "source_user_id": self.ids["user_carol"],
            "target_user_id": self.ids["user_bob"],
            "relation_type": "follow"
        })
        self.assert_ok("Mutual follow = friends", len(b_to_c) == 1 and len(c_to_b) == 1)

    def test_tc_friend_003_single_direction(self):
        """TC-FRIEND-003: Single-direction follow is not friendship."""
        print("\n=== TC-FRIEND-003: Single Direction ===")
        create_relation(self.data_dir, "user_user", {
            "source_user_id": self.ids["user_judge"],
            "target_user_id": self.ids["user_dave"],
            "relation_type": "follow"
        })
        reverse = read_relation(self.data_dir, "user_user", {
            "source_user_id": self.ids["user_dave"],
            "target_user_id": self.ids["user_judge"],
            "relation_type": "follow"
        })
        self.assert_ok("Single follow not mutual", len(reverse) == 0)

    def test_tc_friend_004_unfollow(self):
        """TC-FRIEND-004: Unfollow."""
        print("\n=== TC-FRIEND-004: Unfollow ===")
        create_relation(self.data_dir, "user_user", {
            "source_user_id": self.ids["user_dave"],
            "target_user_id": self.ids["user_bob"],
            "relation_type": "follow"
        })
        delete_relation(self.data_dir, "user_user", {
            "source_user_id": self.ids["user_dave"],
            "target_user_id": self.ids["user_bob"],
            "relation_type": "follow"
        })
        after = read_relation(self.data_dir, "user_user", {
            "source_user_id": self.ids["user_dave"],
            "target_user_id": self.ids["user_bob"],
            "relation_type": "follow"
        })
        self.assert_ok("Unfollow removes relation", len(after) == 0)

    def test_tc_friend_005_block(self):
        """TC-FRIEND-005: Block user."""
        print("\n=== TC-FRIEND-005: Block ===")
        block_rel = create_relation(self.data_dir, "user_user", {
            "source_user_id": self.ids["user_carol"],
            "target_user_id": self.ids["user_dave"],
            "relation_type": "block"
        })
        self.assert_ok("Carol blocks Dave", block_rel["relation_type"] == "block")

    def test_tc_friend_006_blocked_cannot_follow(self):
        """TC-FRIEND-006: Blocked user cannot follow."""
        print("\n=== TC-FRIEND-006: Blocked Cannot Follow ===")
        # Block is created in test_tc_friend_005 (carol blocks dave).
        # Since tests run sequentially on same instance, block already exists.
        self.assert_raises(
            "Blocked user cannot follow",
            lambda: create_relation(self.data_dir, "user_user", {
                "source_user_id": self.ids["user_dave"],
                "target_user_id": self.ids["user_carol"],
                "relation_type": "follow"
            }),
            "blocked you"
        )

    def test_tc_friend_007_delete_user_cascades(self):
        """TC-FRIEND-007: Delete user cascades user:user relations."""
        print("\n=== TC-FRIEND-007: Delete User Cascades ===")
        pass  # Skeleton — requires delete + cascade verification

    def test_tc_friend_900_self_follow(self):
        """TC-FRIEND-900: Self-follow rejected."""
        print("\n=== TC-FRIEND-900: Self Follow ===")
        self.assert_raises(
            "Reject self-follow",
            lambda: create_relation(self.data_dir, "user_user", {
                "source_user_id": self.ids["user_alice"],
                "target_user_id": self.ids["user_alice"],
                "relation_type": "follow"
            }),
            "yourself"
        )

    def test_tc_friend_901_duplicate_follow(self):
        """TC-FRIEND-901: Duplicate follow rejected."""
        print("\n=== TC-FRIEND-901: Duplicate Follow ===")
        # alice->bob follow was created in test_tc_friend_001
        self.assert_raises(
            "Reject duplicate follow",
            lambda: create_relation(self.data_dir, "user_user", {
                "source_user_id": self.ids["user_alice"],
                "target_user_id": self.ids["user_bob"],
                "relation_type": "follow"
            }),
            "already exists"
        )

    def test_tc_friend_902_invalid_relation_type(self):
        """TC-FRIEND-902: Invalid relation_type rejected."""
        print("\n=== TC-FRIEND-902: Invalid Relation Type ===")
        pass  # Skeleton


if __name__ == "__main__":
    runner = TestUserFollow()
    success = runner.run_tests()
    sys.exit(0 if success else 1)
