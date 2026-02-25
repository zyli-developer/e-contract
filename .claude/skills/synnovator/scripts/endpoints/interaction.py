"""Interaction endpoint: likes, comments, ratings."""

DEFAULTS = {}


def on_create(data_dir, data, current_user):
    pass


def on_post_create(data_dir, data, current_user):
    """Auto-create target_interaction relation after interaction creation."""
    target_type = data.get("target_type")
    target_id = data.get("target_id")
    interaction_id = data.get("id")
    if target_type and target_id and interaction_id:
        from relations import create_relation
        create_relation(data_dir, "target_interaction", {
            "target_type": target_type,
            "target_id": target_id,
            "interaction_id": interaction_id,
        })


def on_pre_update(data_dir, record_id, rec, updates):
    pass


def on_delete_cascade(data_dir, record_id):
    from cascade import _cascade_delete_child_comments, _cascade_delete_relations
    from relations import read_relation
    from cache import _update_cache_stats

    _cascade_delete_child_comments(data_dir, record_id)
    # Find target before deleting relation (needed for cache update)
    target_rels = read_relation(data_dir, "target_interaction", {"interaction_id": record_id})
    _cascade_delete_relations(data_dir, "target_interaction", "interaction_id", record_id)
    for rel in target_rels:
        _update_cache_stats(data_dir, rel.get("target_type"), rel.get("target_id"))
