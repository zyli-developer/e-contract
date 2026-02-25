#!/usr/bin/env python3
"""
Synnovator Data Engine - Relation CRUD + hooks + uniqueness checks.
"""

import os

from core import (
    RELATION_KEYS, ENUMS, CONTENT_TYPES,
    gen_id, now_iso, find_record, load_record, save_record,
    validate_reference_exists, get_user_role,
)
from rules import _validate_category_rules
from cache import _update_cache_stats


def _require_authenticated(data_dir, current_user, operation, relation_type):
    """Require an authenticated user for relation operations.

    When current_user is None (internal/cascade calls), skip the check.
    The calling content CRUD function has already verified permissions.
    """
    if current_user is None:
        return None
    role = get_user_role(data_dir, current_user)
    if role is None:
        raise ValueError(f"User '{current_user}' not found")
    return role


def create_relation(data_dir, relation_type, data, current_user=None):
    _require_authenticated(data_dir, current_user, "create", relation_type)

    keys = RELATION_KEYS.get(relation_type)
    if not keys:
        raise ValueError(f"Unknown relation type: {relation_type}")

    for k in keys:
        if k not in data:
            raise ValueError(f"Missing required key '{k}' for {relation_type}")

    _validate_relation_refs(data_dir, relation_type, data)
    _check_relation_uniqueness(data_dir, relation_type, data)

    # Rule enforcement hooks
    if relation_type == "event_post":
        post_fp = find_record(data_dir, "post", data["post_id"])
        post_rec = load_record(post_fp) if post_fp else {}
        _validate_category_rules(data_dir, data["event_id"], "submission", {
            "post_id": data["post_id"],
            "event_id": data["event_id"],
            "user_id": post_rec.get("created_by"),
            "group_id": data.get("group_id"),
        })
    elif relation_type == "group_user":
        cat_groups = read_relation(data_dir, "event_group", {"group_id": data["group_id"]})
        for cg in cat_groups:
            _validate_category_rules(data_dir, cg["event_id"], "team_join", {
                "group_id": data["group_id"],
            })

    if relation_type == "group_user":
        group_rec = validate_reference_exists(data_dir, "group", data["group_id"])
        if data.get("role") == "owner":
            data["status"] = "accepted"
            data["joined_at"] = now_iso()
        elif group_rec.get("require_approval", False):
            data.setdefault("status", "pending")
        else:
            data.setdefault("status", "accepted")
            data["joined_at"] = now_iso()
        data.setdefault("role", "member")

    if relation_type == "target_interaction":
        target_type = data.get("target_type")
        target_id = data.get("target_id")
        # Check duplicate like: same user can only like same target once
        iact_fp = find_record(data_dir, "interaction", data["interaction_id"])
        if iact_fp:
            iact = load_record(iact_fp)
            if iact.get("type") == "like":
                user_id = iact.get("created_by")
                if user_id:
                    existing_rels = read_relation(data_dir, "target_interaction", {
                        "target_type": target_type, "target_id": target_id
                    })
                    for er in existing_rels:
                        ex_fp = find_record(data_dir, "interaction", er["interaction_id"])
                        if ex_fp:
                            ex_iact = load_record(ex_fp)
                            if (ex_iact.get("type") == "like" and
                                    ex_iact.get("created_by") == user_id):
                                raise ValueError("User already liked this target")

    # Self-reference and relationship-specific validation
    if relation_type == "user_user":
        if data["source_user_id"] == data["target_user_id"]:
            raise ValueError("Cannot create a user_user relation with yourself")
        # Block check: if target blocks source, source cannot follow target
        if data.get("relation_type") == "follow":
            blocks = read_relation(data_dir, "user_user", {
                "source_user_id": data["target_user_id"],
                "target_user_id": data["source_user_id"],
                "relation_type": "block",
            })
            if blocks:
                raise ValueError("Cannot follow a user who has blocked you")

    if relation_type == "event_event":
        if data["source_category_id"] == data["target_category_id"]:
            raise ValueError("Cannot create a event_event relation with itself")
        # Circular dependency detection for stage/prerequisite
        if data.get("relation_type") in ("stage", "prerequisite"):
            _check_circular_dependency(
                data_dir, data["source_category_id"],
                data["target_category_id"], data["relation_type"]
            )

    # Prerequisite enforcement for event registration
    if relation_type == "event_group":
        prereqs = read_relation(data_dir, "event_event", {
            "target_category_id": data["event_id"],
            "relation_type": "prerequisite",
        })
        for prereq in prereqs:
            prereq_fp = find_record(data_dir, "event", prereq["source_category_id"])
            if prereq_fp:
                prereq_rec = load_record(prereq_fp)
                if prereq_rec.get("status") != "closed":
                    raise ValueError(
                        f"Prerequisite event '{prereq['source_category_id']}' must be closed before registering"
                    )

    # Enum validation for relation fields
    for field in ["relation_type", "display_type", "role", "status", "target_type"]:
        if field in data:
            enum_key = f"{relation_type}.{field}"
            if enum_key in ENUMS and data[field] not in ENUMS[enum_key]:
                raise ValueError(f"Invalid value '{data[field]}' for {enum_key}. Allowed: {ENUMS[enum_key]}")

    rel_id = gen_id("rel")
    data.setdefault("_id", rel_id)
    data["created_at"] = data.get("created_at") or now_iso()

    filepath = data_dir / "relations" / relation_type / f"{rel_id}.md"
    save_record(filepath, data)

    # Side effect: update cache stats when linking interaction to target
    if relation_type == "target_interaction":
        _update_cache_stats(data_dir, data.get("target_type"), data.get("target_id"))

    return data


def read_relation(data_dir, relation_type, filters=None):
    folder = data_dir / "relations" / relation_type
    if not folder.exists():
        return []
    results = []
    for f in sorted(folder.iterdir()):
        if f.suffix != ".md":
            continue
        rec = load_record(f)
        if filters:
            match = True
            for k, v in filters.items():
                if rec.get(k) != v:
                    match = False
                    break
            if not match:
                continue
        results.append(rec)
    return results


def update_relation(data_dir, relation_type, filters, updates, current_user=None):
    _require_authenticated(data_dir, current_user, "update", relation_type)

    folder = data_dir / "relations" / relation_type
    if not folder.exists():
        raise ValueError(f"No relations of type {relation_type}")

    updated = []
    for f in folder.iterdir():
        if f.suffix != ".md":
            continue
        rec = load_record(f)
        match = True
        for k, v in filters.items():
            if rec.get(k) != v:
                match = False
                break
        if match:
            for field in ["relation_type", "display_type", "role", "status"]:
                if field in updates:
                    enum_key = f"{relation_type}.{field}"
                    if enum_key in ENUMS and updates[field] not in ENUMS[enum_key]:
                        raise ValueError(f"Invalid value '{updates[field]}' for {enum_key}")

            for k, v in updates.items():
                rec[k] = v

            if relation_type == "group_user" and "status" in updates:
                if updates["status"] == "accepted" and not rec.get("joined_at"):
                    rec["joined_at"] = now_iso()
                rec["status_changed_at"] = now_iso()

            save_record(f, rec)
            updated.append(rec)

    return updated


def delete_relation(data_dir, relation_type, filters, current_user=None):
    _require_authenticated(data_dir, current_user, "delete", relation_type)

    folder = data_dir / "relations" / relation_type
    if not folder.exists():
        return []

    deleted = []
    for f in list(folder.iterdir()):
        if f.suffix != ".md":
            continue
        rec = load_record(f)
        match = True
        for k, v in filters.items():
            if rec.get(k) != v:
                match = False
                break
        if match:
            os.remove(f)
            deleted.append(rec)

    return deleted


# === Internal helpers ===

def _validate_relation_refs(data_dir, relation_type, data):
    ref_map = {
        "event_rule": [("event", "event_id"), ("rule", "rule_id")],
        "event_post": [("event", "event_id"), ("post", "post_id")],
        "event_group": [("event", "event_id"), ("group", "group_id")],
        "post_post": [("post", "source_post_id"), ("post", "target_post_id")],
        "post_resource": [("post", "post_id"), ("resource", "resource_id")],
        "group_user": [("group", "group_id"), ("user", "user_id")],
        "target_interaction": [("interaction", "interaction_id")],
        "user_user": [("user", "source_user_id"), ("user", "target_user_id")],
        "event_event": [("event", "source_category_id"), ("event", "target_category_id")],
    }
    for content_type, field in ref_map.get(relation_type, []):
        if field in data:
            validate_reference_exists(data_dir, content_type, data[field])
    # Dynamic target validation for target_interaction
    if relation_type == "target_interaction":
        target_type = data.get("target_type")
        target_id = data.get("target_id")
        if target_type and target_id and target_type in CONTENT_TYPES:
            validate_reference_exists(data_dir, target_type, target_id)


def _check_relation_uniqueness(data_dir, relation_type, data):
    if relation_type == "event_rule":
        existing = read_relation(data_dir, relation_type, {
            "event_id": data["event_id"], "rule_id": data["rule_id"]
        })
        if existing:
            raise ValueError("This rule is already linked to this event")
    elif relation_type == "event_group":
        existing = read_relation(data_dir, relation_type, {
            "event_id": data["event_id"], "group_id": data["group_id"]
        })
        if existing:
            raise ValueError("This group is already registered for this event")
        # Business rule: a user can only be in one group per event
        new_members = read_relation(data_dir, "group_user", {"group_id": data["group_id"]})
        accepted_user_ids = {m["user_id"] for m in new_members if m.get("status") == "accepted"}
        other_groups = read_relation(data_dir, relation_type, {"event_id": data["event_id"]})
        for og in other_groups:
            if og["group_id"] == data["group_id"]:
                continue
            og_members = read_relation(data_dir, "group_user", {"group_id": og["group_id"]})
            for m in og_members:
                if m.get("status") == "accepted" and m["user_id"] in accepted_user_ids:
                    raise ValueError(
                        f"User '{m['user_id']}' already belongs to group '{og['group_id']}' "
                        f"in event '{data['event_id']}'"
                    )
    elif relation_type == "group_user":
        existing = read_relation(data_dir, relation_type, {
            "group_id": data["group_id"], "user_id": data["user_id"]
        })
        if existing:
            for e in existing:
                if e.get("status") == "rejected":
                    delete_relation(data_dir, relation_type, {
                        "group_id": data["group_id"], "user_id": data["user_id"]
                    })
                    return
            raise ValueError("This user is already in this group")
    elif relation_type == "user_user":
        flt = {
            "source_user_id": data["source_user_id"],
            "target_user_id": data["target_user_id"],
        }
        if data.get("relation_type"):
            flt["relation_type"] = data["relation_type"]
        existing = read_relation(data_dir, relation_type, flt)
        if existing:
            raise ValueError("This user_user relation already exists")
    elif relation_type == "event_event":
        existing = read_relation(data_dir, relation_type, {
            "source_category_id": data["source_category_id"],
            "target_category_id": data["target_category_id"],
        })
        if existing:
            raise ValueError("This event_event relation already exists")


def _check_circular_dependency(data_dir, source_id, target_id, rel_type):
    """Check that creating source_id -> target_id doesn't create a cycle."""
    visited = set()
    stack = [target_id]
    while stack:
        current = stack.pop()
        if current == source_id:
            raise ValueError(
                f"Circular dependency detected in event_event ({rel_type})"
            )
        if current in visited:
            continue
        visited.add(current)
        # Follow outgoing edges from current
        downstream = read_relation(data_dir, "event_event", {
            "source_category_id": current,
        })
        for rel in downstream:
            if rel.get("relation_type") == rel_type:
                stack.append(rel["target_category_id"])
