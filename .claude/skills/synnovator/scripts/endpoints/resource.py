"""Resource endpoint: uploaded file attachments."""

DEFAULTS = {}


def on_create(data_dir, data, current_user):
    pass


def on_pre_update(data_dir, record_id, rec, updates):
    pass


def on_delete_cascade(data_dir, record_id):
    from cascade import (
        _cascade_hard_delete_interactions,
        _cascade_delete_relations,
    )
    _cascade_hard_delete_interactions(data_dir, "resource", record_id)
    _cascade_delete_relations(data_dir, "post_resource", "resource_id", record_id)
