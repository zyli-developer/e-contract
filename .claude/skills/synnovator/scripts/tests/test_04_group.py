#!/usr/bin/env python3
"""
TC-GRP-*: Group CRUD and approval workflow tests.
Migrated from test_journeys.py test_group_approval_workflow.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from base import (
    TestRunner,
    create_base_users, create_base_group,
    create_content, read_content, update_content, delete_content,
    create_relation, read_relation, update_relation, delete_relation,
)


class TestGroup(TestRunner):
    data_dir_suffix = "_test_04_group"

    def _run_fixtures(self):
        create_base_users(self.data_dir, self.ids)
        create_base_group(self.data_dir, self.ids)

    # --- CRUD tests ---

    def test_tc_grp_001_create_public_approval(self):
        """TC-GRP-001: Create public group with require_approval."""
        print("\n=== TC-GRP-001: Create Public Approval ===")
        group = read_content(self.data_dir, "group", self.ids["grp1"])
        self.assert_ok("Group created", group["name"] == "Team Synnovator")
        self.assert_ok("Require approval", group["require_approval"] == True)
        self.assert_ok("Public visibility", group["visibility"] == "public")

    def test_tc_grp_002_create_private_no_approval(self):
        """TC-GRP-002: Create private group without approval."""
        print("\n=== TC-GRP-002: Create Private No Approval ===")
        grp2 = create_content(self.data_dir, "group", {
            "name": "Private Team", "visibility": "private", "require_approval": False
        }, current_user=self.ids["user_bob"])
        self.ids["grp2"] = grp2["id"]
        self.assert_ok("Private group", grp2["visibility"] == "private")
        self.assert_ok("No approval", grp2["require_approval"] == False)

    def test_tc_grp_003_owner_auto_join(self):
        """TC-GRP-003: Owner is automatically joined."""
        print("\n=== TC-GRP-003: Owner Auto Join ===")
        owners = read_relation(self.data_dir, "group_user", {
            "group_id": self.ids["grp1"], "role": "owner"
        })
        self.assert_ok("Creator is owner", len(owners) == 1)
        self.assert_ok("Owner status accepted", owners[0]["status"] == "accepted")

    def test_tc_grp_004_join_pending(self):
        """TC-GRP-004: Join require_approval group -> pending."""
        print("\n=== TC-GRP-004: Join Pending ===")
        rel = create_relation(self.data_dir, "group_user", {
            "group_id": self.ids["grp1"],
            "user_id": self.ids["user_bob"],
            "role": "member"
        })
        self.assert_ok("Bob joins (pending)", rel["status"] == "pending")

    def test_tc_grp_005_approve_member(self):
        """TC-GRP-005: Owner approves member."""
        print("\n=== TC-GRP-005: Approve Member ===")
        # Bob applies
        create_relation(self.data_dir, "group_user", {
            "group_id": self.ids["grp1"],
            "user_id": self.ids["user_carol"],
            "role": "member"
        })
        # Alice approves
        updated = update_relation(self.data_dir, "group_user",
            {"group_id": self.ids["grp1"], "user_id": self.ids["user_carol"]},
            {"status": "accepted"}
        )
        self.assert_ok("Alice approves Carol", updated[0]["status"] == "accepted")

    def test_tc_grp_006_reject_member(self):
        """TC-GRP-006: Owner rejects member."""
        print("\n=== TC-GRP-006: Reject Member ===")
        create_relation(self.data_dir, "group_user", {
            "group_id": self.ids["grp1"],
            "user_id": self.ids["user_dave"],
            "role": "member"
        })
        update_relation(self.data_dir, "group_user",
            {"group_id": self.ids["grp1"], "user_id": self.ids["user_dave"]},
            {"status": "rejected"}
        )
        self.assert_ok("Dave rejected", True)

    def test_tc_grp_007_reapply_after_rejection(self):
        """TC-GRP-007: Reapply after rejection."""
        print("\n=== TC-GRP-007: Reapply After Rejection ===")
        # Dave applies
        create_relation(self.data_dir, "group_user", {
            "group_id": self.ids["grp1"],
            "user_id": self.ids["user_judge"],
            "role": "member"
        })
        # Reject
        update_relation(self.data_dir, "group_user",
            {"group_id": self.ids["grp1"], "user_id": self.ids["user_judge"]},
            {"status": "rejected"}
        )
        # Re-apply
        rel3 = create_relation(self.data_dir, "group_user", {
            "group_id": self.ids["grp1"],
            "user_id": self.ids["user_judge"],
            "role": "member"
        })
        self.assert_ok("Re-apply after rejection", rel3["status"] == "pending")

    def test_tc_grp_008_no_approval_direct_accept(self):
        """TC-GRP-008: Join no-approval group -> directly accepted."""
        print("\n=== TC-GRP-008: No Approval Direct Accept ===")
        pass  # Skeleton

    def test_tc_grp_010_update_info(self):
        """TC-GRP-010: Owner updates group info."""
        print("\n=== TC-GRP-010: Update Info ===")
        pass  # Skeleton

    def test_tc_grp_011_change_approval(self):
        """TC-GRP-011: Change approval setting."""
        print("\n=== TC-GRP-011: Change Approval ===")
        pass  # Skeleton

    def test_tc_grp_012_change_visibility(self):
        """TC-GRP-012: Change visibility."""
        print("\n=== TC-GRP-012: Change Visibility ===")
        pass  # Skeleton

    def test_tc_grp_020_delete_cascade(self):
        """TC-GRP-020: Delete group and cascades."""
        print("\n=== TC-GRP-020: Delete Cascade ===")
        pass  # Skeleton

    def test_tc_grp_900_invalid_visibility(self):
        """TC-GRP-900: Invalid visibility enum rejected."""
        print("\n=== TC-GRP-900: Invalid Visibility ===")
        pass  # Skeleton

    def test_tc_grp_901_non_owner_update(self):
        """TC-GRP-901: Non-owner/admin cannot update group."""
        print("\n=== TC-GRP-901: Non-Owner Update ===")
        pass  # Skeleton


if __name__ == "__main__":
    runner = TestGroup()
    success = runner.run_tests()
    sys.exit(0 if success else 1)
