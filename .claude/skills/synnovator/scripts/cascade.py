#!/usr/bin/env python3
"""
Synnovator Data Engine - Cascade delete helpers.

All deletes are hard deletes (file removal). Uses lazy imports to avoid circular dependencies.
"""

import os

from core import find_record, list_records


def _cascade_hard_delete_interactions(data_dir, target_type, target_id):
    """Hard-delete all interactions linked to a target via target_interaction relations."""
    from relations import read_relation, delete_relation

    rels = read_relation(data_dir, "target_interaction", {
        "target_type": target_type, "target_id": target_id
    })
    for rel in rels:
        iact_id = rel.get("interaction_id")
        fp = find_record(data_dir, "interaction", iact_id)
        if fp:
            os.remove(fp)
    # Clean up the target_interaction relations
    delete_relation(data_dir, "target_interaction", {
        "target_type": target_type, "target_id": target_id
    })


def _cascade_hard_delete_user_interactions(data_dir, user_id):
    """Hard-delete all interactions by a user and update affected targets' cache stats."""
    from relations import read_relation, delete_relation
    from cache import _update_cache_stats

    affected_targets = set()
    for rec in list_records(data_dir, "interaction"):
        if rec.get("created_by") == user_id:
            iact_id = rec["id"]
            # Find targets before deleting
            rels = read_relation(data_dir, "target_interaction", {"interaction_id": iact_id})
            for rel in rels:
                affected_targets.add((rel.get("target_type"), rel.get("target_id")))
            # Delete target_interaction relation
            delete_relation(data_dir, "target_interaction", {"interaction_id": iact_id})
            # Hard-delete the interaction file
            fp = find_record(data_dir, "interaction", iact_id)
            if fp:
                os.remove(fp)
    for target_type, target_id in affected_targets:
        _update_cache_stats(data_dir, target_type, target_id)


def _cascade_delete_child_comments(data_dir, parent_id):
    """Hard-delete all child comments recursively."""
    from relations import delete_relation

    for rec in list_records(data_dir, "interaction"):
        if rec.get("parent_id") == parent_id:
            child_id = rec["id"]
            _cascade_delete_child_comments(data_dir, child_id)
            delete_relation(data_dir, "target_interaction", {"interaction_id": child_id})
            fp = find_record(data_dir, "interaction", child_id)
            if fp:
                os.remove(fp)


def _cascade_delete_relations(data_dir, relation_type, key_field, key_value):
    from relations import delete_relation
    delete_relation(data_dir, relation_type, {key_field: key_value})


def _cascade_delete_user_user_relations(data_dir, user_id):
    """Delete all user_user relations where user is source or target."""
    from relations import read_relation, delete_relation
    for rel in read_relation(data_dir, "user_user"):
        if rel.get("source_user_id") == user_id or rel.get("target_user_id") == user_id:
            delete_relation(data_dir, "user_user", {
                "source_user_id": rel["source_user_id"],
                "target_user_id": rel["target_user_id"],
            })


def _cascade_delete_category_category_relations(data_dir, event_id):
    """Delete all event_event relations where event is source or target."""
    from relations import read_relation, delete_relation
    for rel in read_relation(data_dir, "event_event"):
        if rel.get("source_category_id") == event_id or rel.get("target_category_id") == event_id:
            delete_relation(data_dir, "event_event", {
                "source_category_id": rel["source_category_id"],
                "target_category_id": rel["target_category_id"],
            })
