"""Group endpoint: teams / permission groups."""

DEFAULTS = {
    "visibility": "public",
    "require_approval": False,
}


def on_create(data_dir, data, current_user):
    pass


def on_pre_update(data_dir, record_id, rec, updates):
    pass


def on_delete_cascade(data_dir, record_id):
    from cascade import _cascade_delete_relations
    _cascade_delete_relations(data_dir, "group_user", "group_id", record_id)
    _cascade_delete_relations(data_dir, "event_group", "group_id", record_id)
