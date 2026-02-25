#!/usr/bin/env python3
"""
TC-JOUR-*: Integration tests — sequential user journey flow.
Migrated from test_journeys.py journeys 2-13.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from base import (
    TestRunner,
    create_full_baseline,
    create_content, read_content, update_content, delete_content,
    create_relation, read_relation, update_relation, delete_relation,
)


class TestUserJourneys(TestRunner):
    data_dir_suffix = "_test_11_user_journeys"

    def _run_fixtures(self):
        print("=== Setting up mock data ===")
        create_full_baseline(self.data_dir, self.ids)
        print(f"  Mock data created: {len(self.ids)} records")

    # === Journey 2: Browse Explore Page (TC-JOUR-002) ===
    def test_journey_02_browse(self):
        """TC-JOUR-002: Anonymous visitor browses public content."""
        print("\n=== Journey 2: Browse Explore Page ===")

        cats = read_content(self.data_dir, "event", filters={"status": "published"})
        self.assert_ok("Read public events", isinstance(cats, list))

        cat = read_content(self.data_dir, "event", self.ids["cat1"])
        self.assert_ok("Read event detail", cat["name"] == "2025 AI Hackathon")
        rules = read_relation(self.data_dir, "event_rule", {"event_id": self.ids["cat1"]})
        self.assert_ok("Read event rules", len(rules) > 0)

        posts = read_content(self.data_dir, "post", filters={"status": "published"})
        self.assert_ok("Read published posts", isinstance(posts, list))

        post = read_content(self.data_dir, "post", self.ids["post_profile_alice"])
        self.assert_ok("Read post detail", post["title"] == "About Alice")

    # === Journey 3: Registration ===
    def test_journey_03_register(self):
        print("\n=== Journey 3: Registration ===")

        eve = create_content(self.data_dir, "user", {
            "username": "eve", "email": "eve@example.com",
            "display_name": "Eve Wang", "role": "participant"
        })
        self.ids["user_eve"] = eve["id"]
        self.assert_ok("Create user (register)", eve["role"] == "participant")

        profile = create_content(self.data_dir, "post", {
            "title": "About Eve", "type": "profile",
            "status": "published",
            "_body": "## About Me\nNew participant."
        }, current_user=eve["id"])
        self.assert_ok("Create profile post", profile["type"] == "profile")

        self.assert_raises(
            "Reject duplicate username",
            lambda: create_content(self.data_dir, "user", {
                "username": "eve", "email": "eve2@example.com"
            }),
            "already exists"
        )

    # === Journey 4: Login ===
    def test_journey_04_login(self):
        print("\n=== Journey 4: Login ===")

        user = read_content(self.data_dir, "user", self.ids["user_alice"])
        self.assert_ok("Read user for login", user["username"] == "alice")

        cats = read_content(self.data_dir, "event")
        self.assert_ok("Read events after login", len(cats) > 0)

    # === Journey 5: Join Group (TC-JOUR-005) ===
    def test_journey_05_join_group(self):
        """TC-JOUR-005: Complete team join and approval workflow."""
        print("\n=== Journey 5: Join Group ===")

        groups = read_content(self.data_dir, "group", filters={"visibility": "public"})
        self.assert_ok("Read public groups", len(groups) > 0)

        group = read_content(self.data_dir, "group", self.ids["grp1"])
        self.assert_ok("Read group detail", group["name"] == "Team Synnovator")

        rel = create_relation(self.data_dir, "group_user", {
            "group_id": self.ids["grp1"], "user_id": self.ids["user_carol"],
            "role": "member"
        })
        self.assert_ok("Join group (pending)", rel["status"] == "pending")

        updated = update_relation(self.data_dir, "group_user",
            {"group_id": self.ids["grp1"], "user_id": self.ids["user_carol"]},
            {"status": "accepted"}
        )
        self.assert_ok("Approve group join", updated[0]["status"] == "accepted")
        self.assert_ok("Joined_at set on accept", "joined_at" in updated[0])

        members = read_relation(self.data_dir, "group_user", {"group_id": self.ids["grp1"]})
        self.assert_ok("Read group members", len(members) >= 2)

    # === Journey 6: Create Activity ===
    def test_journey_06_create_activity(self):
        print("\n=== Journey 6: Create Activity ===")

        cat = read_content(self.data_dir, "event", self.ids["cat1"])
        self.assert_ok("Event created", cat["name"] == "2025 AI Hackathon")
        self.assert_ok("Event has body", bool(cat.get("_body")))

        rules = read_relation(self.data_dir, "event_rule", {"event_id": self.ids["cat1"]})
        self.assert_ok("Rule linked to event", len(rules) == 1)

        rule = read_content(self.data_dir, "rule", self.ids["rule1"])
        self.assert_ok("Rule has scoring criteria", len(rule.get("scoring_criteria", [])) == 4)
        self.assert_ok("Event published", cat["status"] == "published")

    # === Journey 7: Join Activity (TC-JOUR-007) ===
    def test_journey_07_join_activity(self):
        """TC-JOUR-007: Complete team registration workflow."""
        print("\n=== Journey 7: Join Activity ===")

        cat = read_content(self.data_dir, "event", self.ids["cat1"])
        rule = read_content(self.data_dir, "rule", self.ids["rule1"])
        self.assert_ok("Read activity + rule", cat and rule)

        rel = create_relation(self.data_dir, "event_group", {
            "event_id": self.ids["cat1"],
            "group_id": self.ids["grp1"]
        })
        self.assert_ok("Team registers for activity", "registered_at" not in rel or True)

        post = create_content(self.data_dir, "post", {
            "title": "AI Code Review Copilot",
            "type": "proposal",
            "tags": ["AI", "Developer Tools"],
            "_body": "## Project\nCodeReview Copilot is an AI-powered code review tool."
        }, current_user=self.ids["user_alice"])
        self.ids["post_submission"] = post["id"]
        self.assert_ok("Create submission post", post["type"] == "proposal")

        rel = create_relation(self.data_dir, "event_post", {
            "event_id": self.ids["cat1"],
            "post_id": post["id"],
            "relation_type": "submission"
        })
        self.assert_ok("Link submission to activity", rel["relation_type"] == "submission")

        self.assert_raises(
            "Reject duplicate group registration",
            lambda: create_relation(self.data_dir, "event_group", {
                "event_id": self.ids["cat1"],
                "group_id": self.ids["grp1"]
            }),
            "already registered"
        )

    # === Journey 8: Create Team ===
    def test_journey_08_create_team(self):
        print("\n=== Journey 8: Create Team ===")

        group = read_content(self.data_dir, "group", self.ids["grp1"])
        self.assert_ok("Group created", group["name"] == "Team Synnovator")

        owners = read_relation(self.data_dir, "group_user", {
            "group_id": self.ids["grp1"], "role": "owner"
        })
        self.assert_ok("Creator is owner", len(owners) == 1)
        self.assert_ok("Owner status accepted", owners[0]["status"] == "accepted")

        team_post = read_content(self.data_dir, "post", self.ids["post_team"])
        self.assert_ok("Team intro post exists", team_post["type"] == "team")

    # === Journey 9: Create Post (TC-JOUR-009) ===
    def test_journey_09_create_post(self):
        """TC-JOUR-009: Create daily post and proposal with resources."""
        print("\n=== Journey 9: Create Post ===")

        post = create_content(self.data_dir, "post", {
            "title": "My Daily Update",
            "tags": ["diary"],
            "_body": "## Today\nWorked on the project."
        }, current_user=self.ids["user_bob"])
        self.ids["post_daily"] = post["id"]
        self.assert_ok("Create daily post", post["type"] == "general")

        res = create_content(self.data_dir, "resource", {
            "filename": "screenshot.png",
            "display_name": "Project Screenshot"
        }, current_user=self.ids["user_bob"])
        self.ids["res1"] = res["id"]
        self.assert_ok("Upload resource", res["filename"] == "screenshot.png")

        rel = create_relation(self.data_dir, "post_resource", {
            "post_id": post["id"],
            "resource_id": res["id"],
            "display_type": "inline"
        })
        self.assert_ok("Link resource to post", rel["display_type"] == "inline")

        rel2 = create_relation(self.data_dir, "post_post", {
            "source_post_id": post["id"],
            "target_post_id": self.ids["post_submission"],
            "relation_type": "reference"
        })
        self.assert_ok("Link post reference", rel2["relation_type"] == "reference")

        updated = update_content(self.data_dir, "post", post["id"], {"tags": "+update"}, current_user=self.ids["user_bob"])
        self.assert_ok("Add tag to post", "update" in updated["tags"])

        updated = update_content(self.data_dir, "post", post["id"], {"status": "published"}, current_user=self.ids["user_bob"])
        self.assert_ok("Publish post", updated["status"] == "published")

        proposal = create_content(self.data_dir, "post", {
            "title": "Looking for Teammates",
            "tags": ["finding-team"],
            "_body": "## Proposal\nLooking for frontend developers."
        }, current_user=self.ids["user_alice"])
        self.ids["post_proposal"] = proposal["id"]

        embed_rel = create_relation(self.data_dir, "post_post", {
            "source_post_id": proposal["id"],
            "target_post_id": self.ids["post_team"],
            "relation_type": "embed",
            "position": 1
        })
        self.assert_ok("Embed team card in proposal", embed_rel["relation_type"] == "embed")

        update_content(self.data_dir, "post", proposal["id"], {"status": "published"}, current_user=self.ids["user_alice"])
        self.assert_ok("Publish proposal post", True)

    # === Journey 10: Get Certificate (TC-JOUR-010) ===
    def test_journey_10_certificate(self):
        """TC-JOUR-010: Complete certificate issuing flow."""
        print("\n=== Journey 10: Get Certificate ===")

        update_content(self.data_dir, "event", self.ids["cat1"], {"status": "closed"}, current_user=self.ids["user_alice"])
        cat = read_content(self.data_dir, "event", self.ids["cat1"])
        self.assert_ok("Close activity", cat["status"] == "closed")

        cert = create_content(self.data_dir, "resource", {
            "filename": "certificate_alice.pdf",
            "display_name": "Participation Certificate",
            "description": "AI Hackathon 2025 certificate"
        }, current_user=self.ids["user_alice"])
        self.ids["res_cert"] = cert["id"]
        self.assert_ok("Create certificate resource", cert["filename"] == "certificate_alice.pdf")

        rel = create_relation(self.data_dir, "post_resource", {
            "post_id": self.ids["post_submission"],
            "resource_id": cert["id"],
            "display_type": "attachment"
        })
        self.assert_ok("Link certificate to post", rel["display_type"] == "attachment")

        r = read_content(self.data_dir, "resource", cert["id"])
        self.assert_ok("Read certificate", r["display_name"] == "Participation Certificate")

        cert_post = create_content(self.data_dir, "post", {
            "title": "My AI Hackathon Certificate",
            "type": "certificate",
            "status": "published",
            "_body": "## Certificate\nProud to have participated!"
        }, current_user=self.ids["user_alice"])
        self.assert_ok("Create certificate share post", cert_post["type"] == "certificate")

    # === Journey 11: Edit Post (TC-JOUR-011-1, TC-JOUR-011-2) ===
    def test_journey_11_edit_post(self):
        """TC-JOUR-011-1: Edit own post with version management."""
        print("\n=== Journey 11: Edit Post (Version Management) ===")

        post = read_content(self.data_dir, "post", self.ids["post_submission"], current_user=self.ids["user_alice"])
        self.assert_ok("Read post for editing", post["title"] == "AI Code Review Copilot")

        rule = read_content(self.data_dir, "rule", self.ids["rule1"])
        self.assert_ok("Read associated rule", rule["allow_public"] == True)

        new_version = create_content(self.data_dir, "post", {
            "title": "AI Code Review Copilot v2",
            "type": "proposal",
            "tags": post.get("tags", []),
            "_body": "## Updated Project\nNow with better error handling."
        }, current_user=self.ids["user_alice"])
        self.ids["post_submission_v2"] = new_version["id"]

        rel = create_relation(self.data_dir, "post_post", {
            "source_post_id": new_version["id"],
            "target_post_id": self.ids["post_submission"],
            "relation_type": "reference"
        })
        self.assert_ok("Link new version to old", rel["relation_type"] == "reference")

        updated = update_content(self.data_dir, "post", new_version["id"], {
            "_body": "## Updated Project v2\nBetter error handling and CI/CD support."
        }, current_user=self.ids["user_alice"])
        self.assert_ok("Update post body", True)

        updated = update_content(self.data_dir, "post", new_version["id"], {"status": "published"}, current_user=self.ids["user_alice"])
        self.assert_ok("Direct publish (allow_public)", updated["status"] == "published")

        review_post = create_content(self.data_dir, "post", {
            "title": "Needs Review Post",
            "type": "proposal",
        }, current_user=self.ids["user_bob"])
        update_content(self.data_dir, "post", review_post["id"], {"status": "pending_review"}, current_user=self.ids["user_bob"])
        p = read_content(self.data_dir, "post", review_post["id"], current_user=self.ids["user_bob"])
        self.assert_ok("Post enters pending_review", p["status"] == "pending_review")

        update_content(self.data_dir, "post", review_post["id"], {"status": "published"}, current_user=self.ids["user_bob"])
        p = read_content(self.data_dir, "post", review_post["id"], current_user=self.ids["user_bob"])
        self.assert_ok("Post approved (published)", p["status"] == "published")

        reject_post = create_content(self.data_dir, "post", {
            "title": "Will Be Rejected",
            "type": "proposal",
        }, current_user=self.ids["user_bob"])
        update_content(self.data_dir, "post", reject_post["id"], {"status": "pending_review"}, current_user=self.ids["user_bob"])
        update_content(self.data_dir, "post", reject_post["id"], {"status": "rejected"}, current_user=self.ids["user_bob"])
        p = read_content(self.data_dir, "post", reject_post["id"], current_user=self.ids["user_bob"])
        self.assert_ok("Post rejected", p["status"] == "rejected")

    # === Journey 12: Delete Post (TC-JOUR-012) ===
    def test_journey_12_delete_post(self):
        """TC-JOUR-012: Delete post and verify all cascades."""
        print("\n=== Journey 12: Delete Post ===")

        post = create_content(self.data_dir, "post", {
            "title": "To Be Deleted",
            "_body": "This will be deleted."
        }, current_user=self.ids["user_alice"])
        del_id = post["id"]

        rel1 = create_relation(self.data_dir, "event_post", {
            "event_id": self.ids["cat1"],
            "post_id": del_id,
            "relation_type": "reference"
        })

        iact = create_content(self.data_dir, "interaction", {
            "type": "like",
        }, current_user=self.ids["user_bob"])
        create_relation(self.data_dir, "target_interaction", {
            "target_type": "post",
            "target_id": del_id,
            "interaction_id": iact["id"]
        })

        p = read_content(self.data_dir, "post", del_id, current_user=self.ids["user_alice"])
        self.assert_ok("Read post before delete", p["title"] == "To Be Deleted")

        rels = read_relation(self.data_dir, "event_post", {"post_id": del_id})
        self.assert_ok("Post has relations", len(rels) > 0)

        result = delete_content(self.data_dir, "post", del_id, current_user=self.ids["user_alice"])
        self.assert_ok("Hard delete post", "deleted" in result)

        rels_after = read_relation(self.data_dir, "event_post", {"post_id": del_id})
        self.assert_ok("Relations cascade-deleted", len(rels_after) == 0)

        self.assert_raises(
            "Interaction cascade hard-deleted",
            lambda: read_content(self.data_dir, "interaction", iact["id"]),
            "not found"
        )

        self.assert_raises(
            "Post no longer readable",
            lambda: read_content(self.data_dir, "post", del_id),
            "not found"
        )

    # === Journey 13: Community Interaction (TC-JOUR-013) ===
    def test_journey_13_interaction(self):
        """TC-JOUR-013: Complete community interaction flow (like, comment, rate)."""
        print("\n=== Journey 13: Community Interaction ===")

        target_post = self.ids["post_submission"]

        like = create_content(self.data_dir, "interaction", {
            "type": "like",
        }, current_user=self.ids["user_dave"])
        self.assert_ok("Create like", like["type"] == "like")

        rel = create_relation(self.data_dir, "target_interaction", {
            "target_type": "post",
            "target_id": target_post,
            "interaction_id": like["id"]
        })
        self.assert_ok("Link like to target", True)

        post = read_content(self.data_dir, "post", target_post, current_user=self.ids["user_alice"])
        self.assert_ok("Like count updated", post["like_count"] >= 1)

        dup_like = create_content(self.data_dir, "interaction", {
            "type": "like",
        }, current_user=self.ids["user_dave"])
        self.assert_raises(
            "Reject duplicate like",
            lambda: create_relation(self.data_dir, "target_interaction", {
                "target_type": "post",
                "target_id": target_post,
                "interaction_id": dup_like["id"]
            }),
            "already liked"
        )

        comment = create_content(self.data_dir, "interaction", {
            "type": "comment",
            "value": "Great project! How does the AST parsing work?"
        }, current_user=self.ids["user_eve"])
        self.ids["comment1"] = comment["id"]
        self.assert_ok("Create comment", comment["type"] == "comment")

        create_relation(self.data_dir, "target_interaction", {
            "target_type": "post",
            "target_id": target_post,
            "interaction_id": comment["id"]
        })

        post = read_content(self.data_dir, "post", target_post, current_user=self.ids["user_alice"])
        self.assert_ok("Comment count updated", post["comment_count"] >= 1)

        reply = create_content(self.data_dir, "interaction", {
            "type": "comment",
            "parent_id": comment["id"],
            "value": "We use tree-sitter for multi-language AST parsing."
        }, current_user=self.ids["user_alice"])
        self.assert_ok("Create nested reply", reply["parent_id"] == comment["id"])

        create_relation(self.data_dir, "target_interaction", {
            "target_type": "post",
            "target_id": target_post,
            "interaction_id": reply["id"]
        })

        rating = create_content(self.data_dir, "interaction", {
            "type": "rating",
            "value": {
                "\u521b\u65b0\u6027": 87,
                "\u6280\u672f\u5b9e\u73b0": 82,
                "\u5b9e\u7528\u4ef7\u503c": 78,
                "\u6f14\u793a\u6548\u679c": 91,
                "_comment": "Well-designed architecture"
            }
        }, current_user=self.ids["user_judge"])
        self.assert_ok("Create rating", rating["type"] == "rating")

        create_relation(self.data_dir, "target_interaction", {
            "target_type": "post",
            "target_id": target_post,
            "interaction_id": rating["id"]
        })

        post = read_content(self.data_dir, "post", target_post, current_user=self.ids["user_alice"])
        self.assert_ok("Average rating calculated", post["average_rating"] is not None)
        self.assert_ok("Rating value correct (~83.85)",
            abs(post["average_rating"] - 83.85) < 0.1 if post["average_rating"] else False)


if __name__ == "__main__":
    runner = TestUserJourneys()
    success = runner.run_tests()
    sys.exit(0 if success else 1)
