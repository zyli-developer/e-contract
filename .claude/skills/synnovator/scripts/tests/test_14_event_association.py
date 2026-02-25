#!/usr/bin/env python3
"""
TC-STAGE-*, TC-TRACK-*, TC-PREREQ-*, TC-CATREL-*: Event association tests.
Migrated from test_journeys.py test_journey_15_activity_association.
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


class TestCategoryAssociation(TestRunner):
    data_dir_suffix = "_test_14_category_association"

    def _run_fixtures(self):
        create_base_users(self.data_dir, self.ids)

    # --- Stage tests ---

    def test_tc_stage_001_create_stage_chain(self):
        """TC-STAGE-001: Create sequential stage associations."""
        print("\n=== TC-STAGE-001: Stage Chain ===")
        alice = self.ids["user_alice"]

        stage1 = create_content(self.data_dir, "event", {
            "name": "Stage 1: Proposal", "description": "Submit proposals",
            "type": "competition", "status": "published"
        }, current_user=alice)

        stage2 = create_content(self.data_dir, "event", {
            "name": "Stage 2: Prototype", "description": "Build prototypes",
            "type": "competition", "status": "published"
        }, current_user=alice)

        stage3 = create_content(self.data_dir, "event", {
            "name": "Stage 3: Final", "description": "Final presentation",
            "type": "competition", "status": "published"
        }, current_user=alice)

        self.ids["stage1"] = stage1["id"]
        self.ids["stage2"] = stage2["id"]
        self.ids["stage3"] = stage3["id"]

        rel1 = create_relation(self.data_dir, "event_event", {
            "source_category_id": stage1["id"],
            "target_category_id": stage2["id"],
            "relation_type": "stage",
            "stage_order": 1
        })
        self.assert_ok("Stage 1->2 created", rel1["relation_type"] == "stage")

        rel2 = create_relation(self.data_dir, "event_event", {
            "source_category_id": stage2["id"],
            "target_category_id": stage3["id"],
            "relation_type": "stage",
            "stage_order": 2
        })
        self.assert_ok("Stage 2->3 created", rel2["relation_type"] == "stage")

    def test_tc_stage_002_read_by_order(self):
        """TC-STAGE-002: Read stages ordered by stage_order."""
        print("\n=== TC-STAGE-002: Read by Order ===")
        pass  # Skeleton

    def test_tc_stage_003_incomplete_blocks_next(self):
        """TC-STAGE-003: Incomplete stage blocks entry to next."""
        print("\n=== TC-STAGE-003: Incomplete Blocks Next ===")
        pass  # Skeleton

    def test_tc_stage_004_complete_allows_next(self):
        """TC-STAGE-004: Completed stage allows entry to next."""
        print("\n=== TC-STAGE-004: Complete Allows Next ===")
        pass  # Skeleton

    # --- Track tests ---

    def test_tc_track_001_parallel_tracks(self):
        """TC-TRACK-001: Create parallel track associations."""
        print("\n=== TC-TRACK-001: Parallel Tracks ===")
        alice = self.ids["user_alice"]

        main_cat = create_content(self.data_dir, "event", {
            "name": "Main Event", "description": "Parent event",
            "type": "competition", "status": "published"
        }, current_user=alice)

        track_a = create_content(self.data_dir, "event", {
            "name": "Track A: AI", "description": "AI track",
            "type": "competition", "status": "published"
        }, current_user=alice)

        track_b = create_content(self.data_dir, "event", {
            "name": "Track B: Web3", "description": "Web3 track",
            "type": "competition", "status": "published"
        }, current_user=alice)

        self.ids["main_cat"] = main_cat["id"]
        self.ids["track_a"] = track_a["id"]
        self.ids["track_b"] = track_b["id"]

        rel_a = create_relation(self.data_dir, "event_event", {
            "source_category_id": main_cat["id"],
            "target_category_id": track_a["id"],
            "relation_type": "track"
        })
        self.assert_ok("Track A linked", rel_a["relation_type"] == "track")

        rel_b = create_relation(self.data_dir, "event_event", {
            "source_category_id": main_cat["id"],
            "target_category_id": track_b["id"],
            "relation_type": "track"
        })
        self.assert_ok("Track B linked", rel_b["relation_type"] == "track")

        tracks = read_relation(self.data_dir, "event_event", {
            "source_category_id": main_cat["id"],
            "relation_type": "track"
        })
        self.assert_ok("Read parallel tracks", len(tracks) == 2)

    def test_tc_track_002_team_multiple_tracks(self):
        """TC-TRACK-002: Team can join different tracks simultaneously."""
        print("\n=== TC-TRACK-002: Team Multiple Tracks ===")
        pass  # Skeleton

    def test_tc_track_003_rule_per_track(self):
        """TC-TRACK-003: Rule enforcement within a single track."""
        print("\n=== TC-TRACK-003: Rule Per Track ===")
        pass  # Skeleton

    # --- Prerequisite tests ---

    def test_tc_prereq_001_create_prerequisite(self):
        """TC-PREREQ-001: Link bounty as prerequisite to main competition."""
        print("\n=== TC-PREREQ-001: Prerequisite Link ===")
        alice = self.ids["user_alice"]

        bounty = create_content(self.data_dir, "event", {
            "name": "Bounty Challenge", "description": "Complete bounty first",
            "type": "competition", "status": "published"
        }, current_user=alice)

        main_comp = create_content(self.data_dir, "event", {
            "name": "Main Competition", "description": "Requires bounty completion",
            "type": "competition", "status": "published"
        }, current_user=alice)

        self.ids["bounty"] = bounty["id"]
        self.ids["main_comp"] = main_comp["id"]

        create_relation(self.data_dir, "event_event", {
            "source_category_id": bounty["id"],
            "target_category_id": main_comp["id"],
            "relation_type": "prerequisite"
        })
        self.assert_ok("Prerequisite link created", True)

    def test_tc_prereq_002_register_after_closed(self):
        """TC-PREREQ-002: Registration allowed after prerequisite closed."""
        print("\n=== TC-PREREQ-002: Register After Closed ===")
        alice = self.ids["user_alice"]

        bounty = create_content(self.data_dir, "event", {
            "name": "Bounty2", "description": "Prereq test",
            "type": "competition", "status": "published"
        }, current_user=alice)
        main_comp = create_content(self.data_dir, "event", {
            "name": "Main2", "description": "Requires bounty",
            "type": "competition", "status": "published"
        }, current_user=alice)
        create_relation(self.data_dir, "event_event", {
            "source_category_id": bounty["id"],
            "target_category_id": main_comp["id"],
            "relation_type": "prerequisite"
        })

        prereq_grp = create_content(self.data_dir, "group", {
            "name": "Prereq Team", "visibility": "public", "require_approval": False
        }, current_user=alice)
        create_relation(self.data_dir, "group_user", {
            "group_id": prereq_grp["id"], "user_id": alice, "role": "owner"
        })

        # Close bounty
        update_content(self.data_dir, "event", bounty["id"], {"status": "closed"}, current_user=alice)

        # Now registration should succeed
        create_relation(self.data_dir, "event_group", {
            "event_id": main_comp["id"],
            "group_id": prereq_grp["id"]
        })
        self.assert_ok("Registration after prerequisite closed", True)

    def test_tc_prereq_003_reject_open_prerequisite(self):
        """TC-PREREQ-003: Reject registration when prerequisite not closed."""
        print("\n=== TC-PREREQ-003: Reject Open Prerequisite ===")
        alice = self.ids["user_alice"]

        bounty = create_content(self.data_dir, "event", {
            "name": "Bounty3", "description": "Still open",
            "type": "competition", "status": "published"
        }, current_user=alice)
        main_comp = create_content(self.data_dir, "event", {
            "name": "Main3", "description": "Requires bounty",
            "type": "competition", "status": "published"
        }, current_user=alice)
        create_relation(self.data_dir, "event_event", {
            "source_category_id": bounty["id"],
            "target_category_id": main_comp["id"],
            "relation_type": "prerequisite"
        })

        prereq_grp = create_content(self.data_dir, "group", {
            "name": "Prereq Team 3", "visibility": "public", "require_approval": False
        }, current_user=alice)
        create_relation(self.data_dir, "group_user", {
            "group_id": prereq_grp["id"], "user_id": alice, "role": "owner"
        })

        self.assert_raises(
            "Reject registration (prerequisite not closed)",
            lambda: create_relation(self.data_dir, "event_group", {
                "event_id": main_comp["id"],
                "group_id": prereq_grp["id"]
            }),
            "must be closed"
        )

    def test_tc_prereq_004_team_preserved(self):
        """TC-PREREQ-004: Team from prerequisite preserved into target activity."""
        print("\n=== TC-PREREQ-004: Team Preserved ===")
        pass  # Skeleton

    # --- Event relation validation tests ---

    def test_tc_catrel_900_duplicate_rejected(self):
        """TC-CATREL-900: Duplicate event_event rejected."""
        print("\n=== TC-CATREL-900: Duplicate Rejected ===")
        alice = self.ids["user_alice"]

        cat_a = create_content(self.data_dir, "event", {
            "name": "Cat A", "description": "A", "type": "competition", "status": "published"
        }, current_user=alice)
        cat_b = create_content(self.data_dir, "event", {
            "name": "Cat B", "description": "B", "type": "competition", "status": "published"
        }, current_user=alice)

        create_relation(self.data_dir, "event_event", {
            "source_category_id": cat_a["id"],
            "target_category_id": cat_b["id"],
            "relation_type": "stage",
            "stage_order": 1
        })

        self.assert_raises(
            "Reject duplicate event_event",
            lambda: create_relation(self.data_dir, "event_event", {
                "source_category_id": cat_a["id"],
                "target_category_id": cat_b["id"],
                "relation_type": "stage",
                "stage_order": 1
            }),
            "already exists"
        )

    def test_tc_catrel_901_self_reference(self):
        """TC-CATREL-901: Self-reference rejected."""
        print("\n=== TC-CATREL-901: Self Reference ===")
        alice = self.ids["user_alice"]

        cat = create_content(self.data_dir, "event", {
            "name": "Self Cat", "description": "Self", "type": "competition", "status": "published"
        }, current_user=alice)

        self.assert_raises(
            "Reject self-reference",
            lambda: create_relation(self.data_dir, "event_event", {
                "source_category_id": cat["id"],
                "target_category_id": cat["id"],
                "relation_type": "stage"
            }),
            "itself"
        )

    def test_tc_catrel_902_circular_dependency(self):
        """TC-CATREL-902: Circular stage dependency rejected."""
        print("\n=== TC-CATREL-902: Circular Dependency ===")
        alice = self.ids["user_alice"]

        s1 = create_content(self.data_dir, "event", {
            "name": "Circ1", "description": "C1", "type": "competition", "status": "published"
        }, current_user=alice)
        s2 = create_content(self.data_dir, "event", {
            "name": "Circ2", "description": "C2", "type": "competition", "status": "published"
        }, current_user=alice)
        s3 = create_content(self.data_dir, "event", {
            "name": "Circ3", "description": "C3", "type": "competition", "status": "published"
        }, current_user=alice)

        create_relation(self.data_dir, "event_event", {
            "source_category_id": s1["id"], "target_category_id": s2["id"],
            "relation_type": "stage", "stage_order": 1
        })
        create_relation(self.data_dir, "event_event", {
            "source_category_id": s2["id"], "target_category_id": s3["id"],
            "relation_type": "stage", "stage_order": 2
        })

        self.assert_raises(
            "Reject circular stage dependency",
            lambda: create_relation(self.data_dir, "event_event", {
                "source_category_id": s3["id"],
                "target_category_id": s1["id"],
                "relation_type": "stage",
                "stage_order": 3
            }),
            "Circular dependency"
        )

    def test_tc_catrel_903_invalid_relation_type(self):
        """TC-CATREL-903: Invalid relation_type rejected."""
        print("\n=== TC-CATREL-903: Invalid Relation Type ===")
        pass  # Skeleton


if __name__ == "__main__":
    runner = TestCategoryAssociation()
    success = runner.run_tests()
    sys.exit(0 if success else 1)
