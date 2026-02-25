"""Post endpoint: user-submitted content."""

DEFAULTS = {
    "type": "general",
    "status": "draft",
    "visibility": "public",
    "tags": [],
    "like_count": 0,
    "comment_count": 0,
    "average_rating": None,
}

# Cache fields that users cannot set directly (system-maintained)
CACHE_FIELDS = ("like_count", "comment_count", "average_rating")


def on_create(data_dir, data, current_user):
    pass


def on_pre_update(data_dir, record_id, rec, updates):
    """Strip cache fields; enforce publish rules; validate state transitions."""
    # Strip read-only cache fields
    for cache_field in CACHE_FIELDS:
        updates.pop(cache_field, None)

    # Rule enforcement: validate post status transitions
    # Private posts skip event rule checks (can go draft → published directly)
    if "status" in updates and rec.get("visibility") != "private":
        from relations import read_relation
        from rules import _validate_category_rules

        cat_posts = read_relation(data_dir, "event_post", {"post_id": record_id})
        for cp in cat_posts:
            _validate_category_rules(data_dir, cp["event_id"], "publish", {
                "post_id": record_id,
                "new_status": updates["status"],
            })


def on_delete_cascade(data_dir, record_id):
    from cascade import (
        _cascade_hard_delete_interactions,
        _cascade_delete_relations,
    )
    _cascade_hard_delete_interactions(data_dir, "post", record_id)
    _cascade_delete_relations(data_dir, "event_post", "post_id", record_id)
    _cascade_delete_relations(data_dir, "post_post", "source_post_id", record_id)
    _cascade_delete_relations(data_dir, "post_post", "target_post_id", record_id)
    _cascade_delete_relations(data_dir, "post_resource", "post_id", record_id)
