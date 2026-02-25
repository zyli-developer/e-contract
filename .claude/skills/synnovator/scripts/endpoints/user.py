"""User endpoint: user profiles with uniqueness constraints."""

from core import validate_uniqueness, list_records

DEFAULTS = {
    "role": "participant",
}

# Content types whose created_by field references user.id
_OWNED_CONTENT_TYPES = ["event", "post", "resource", "rule", "group"]


def on_create(data_dir, data, current_user):
    validate_uniqueness(data_dir, "user", data)


def on_pre_update(data_dir, record_id, rec, updates):
    validate_uniqueness(data_dir, "user", {**rec, **updates}, exclude_id=record_id)


def on_pre_delete(data_dir, record_id):
    """Referential integrity: refuse to delete a user who still owns content."""
    for ct in _OWNED_CONTENT_TYPES:
        records = list_records(data_dir, ct, filters={"created_by": record_id})
        if records:
            ids = [r.get("id", "?") for r in records[:5]]
            raise ValueError(
                f"Cannot delete user '{record_id}': still owns {len(records)} "
                f"{ct} record(s) (e.g. {', '.join(ids)}). "
                f"Delete or reassign them first."
            )


def on_delete_cascade(data_dir, record_id):
    from cascade import (
        _cascade_hard_delete_user_interactions,
        _cascade_delete_relations,
        _cascade_delete_user_user_relations,
    )
    _cascade_delete_relations(data_dir, "group_user", "user_id", record_id)
    _cascade_delete_user_user_relations(data_dir, record_id)
    _cascade_hard_delete_user_interactions(data_dir, record_id)
