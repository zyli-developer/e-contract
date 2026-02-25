#!/usr/bin/env python3
"""
Synnovator Data Engine - Generic content CRUD dispatch.

Routes to per-endpoint modules for type-specific behavior.
All deletes are hard deletes (file removal).
"""

import os

from core import (
    validate_required, validate_enum, validate_uniqueness,
    validate_state_transition, check_permission, get_user_role,
    gen_id, now_iso, find_record, load_record, save_record, list_records,
    PREFIX_MAP,
)
from endpoints import get_endpoint


def create_content(data_dir, content_type, data, current_user=None):
    check_permission(data_dir, current_user, "create", content_type)
    validate_required(content_type, data)

    for field in ["type", "status", "role", "visibility", "target_type"]:
        if field in data:
            validate_enum(content_type, field, data[field])

    endpoint = get_endpoint(content_type)
    if endpoint and hasattr(endpoint, 'on_create'):
        endpoint.on_create(data_dir, data, current_user)
    else:
        validate_uniqueness(data_dir, content_type, data)

    record_id = gen_id(PREFIX_MAP.get(content_type, content_type))
    data["id"] = record_id
    data["created_at"] = data.get("created_at") or now_iso()
    data["updated_at"] = data["created_at"]

    if current_user and content_type != "user":
        data.setdefault("created_by", current_user)

    # Apply endpoint defaults
    if endpoint and hasattr(endpoint, 'DEFAULTS'):
        for k, v in endpoint.DEFAULTS.items():
            if isinstance(v, list):
                data.setdefault(k, list(v))  # copy mutable defaults
            else:
                data.setdefault(k, v)

    filepath = data_dir / content_type / f"{record_id}.md"
    body = data.pop("_body", "")
    save_record(filepath, data, body=body)
    data["_body"] = body

    # Post-create hook (e.g., auto-create target_interaction for interactions)
    if endpoint and hasattr(endpoint, 'on_post_create'):
        endpoint.on_post_create(data_dir, data, current_user)

    return data


def read_content(data_dir, content_type, record_id=None, filters=None, current_user=None):
    user_role = get_user_role(data_dir, current_user) if current_user else None

    if record_id:
        fp = find_record(data_dir, content_type, record_id)
        if not fp:
            raise ValueError(f"{content_type} '{record_id}' not found")
        rec = load_record(fp)
        if not _is_visible(content_type, rec, current_user, user_role):
            raise ValueError(f"{content_type} '{record_id}' is not visible")
        return rec

    records = list_records(data_dir, content_type, filters=filters)
    return [r for r in records if _is_visible(content_type, r, current_user, user_role)]


def update_content(data_dir, content_type, record_id, updates, current_user=None):
    fp = find_record(data_dir, content_type, record_id)
    if not fp:
        raise ValueError(f"{content_type} '{record_id}' not found")
    rec = load_record(fp)

    check_permission(data_dir, current_user, "update", content_type, record=rec)

    # Endpoint-specific pre-update hooks
    endpoint = get_endpoint(content_type)
    if endpoint and hasattr(endpoint, 'on_pre_update'):
        endpoint.on_pre_update(data_dir, record_id, rec, updates)

    for field in ["type", "status", "role", "visibility", "target_type"]:
        if field in updates:
            validate_enum(content_type, field, updates[field])

    # Enforce state machine: validate status transitions
    if "status" in updates and updates["status"] != rec.get("status"):
        validate_state_transition(
            content_type, "status", rec.get("status"), updates["status"]
        )

    for k, v in updates.items():
        if k == "tags" and isinstance(v, str) and v.startswith("+"):
            tag = v[1:]
            if "tags" not in rec:
                rec["tags"] = []
            if tag not in rec["tags"]:
                rec["tags"].append(tag)
        elif k == "tags" and isinstance(v, str) and v.startswith("-"):
            tag = v[1:]
            if "tags" in rec and tag in rec["tags"]:
                rec["tags"].remove(tag)
        else:
            rec[k] = v

    rec["updated_at"] = now_iso()
    body = rec.pop("_body", "")
    save_record(fp, rec, body=body)
    rec["_body"] = body
    return rec


def delete_content(data_dir, content_type, record_id, current_user=None):
    """Hard-delete a content record and cascade to related data."""
    fp = find_record(data_dir, content_type, record_id)
    if not fp:
        raise ValueError(f"{content_type} '{record_id}' not found")
    rec = load_record(fp)

    check_permission(data_dir, current_user, "delete", content_type, record=rec)

    # Pre-delete validation (e.g., referential integrity checks)
    endpoint = get_endpoint(content_type)
    if endpoint and hasattr(endpoint, 'on_pre_delete'):
        endpoint.on_pre_delete(data_dir, record_id)

    # Run cascade before deleting the record file
    if endpoint and hasattr(endpoint, 'on_delete_cascade'):
        endpoint.on_delete_cascade(data_dir, record_id)

    os.remove(fp)
    return {"deleted": record_id}


# === Visibility helpers ===

def _is_visible(content_type, rec, current_user, user_role):
    """Check if a record is visible to current_user. Skip resource indirect visibility."""
    if content_type not in ("post", "event", "group"):
        return True
    if user_role == "admin":
        return True
    if current_user and rec.get("created_by") == current_user:
        return True
    if content_type == "post":
        if rec.get("visibility") == "private":
            return False
        if rec.get("status") not in ("published",):
            return False
    elif content_type == "event":
        if rec.get("status") not in ("published", "closed"):
            return False
    elif content_type == "group":
        if rec.get("visibility") == "private":
            return False
    return True
