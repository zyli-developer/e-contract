"""Rule endpoint: event rules created by organizers."""

DEFAULTS = {}


def _validate_scoring_criteria(criteria):
    """Validate scoring_criteria: each weight 0-100, total sum == 100."""
    if not isinstance(criteria, list) or len(criteria) == 0:
        raise ValueError("scoring_criteria must be a non-empty list")
    total = 0
    for i, item in enumerate(criteria):
        if not isinstance(item, dict):
            raise ValueError(f"scoring_criteria[{i}] must be a dict")
        weight = item.get("weight")
        if weight is None:
            raise ValueError(f"scoring_criteria[{i}] missing 'weight'")
        if not isinstance(weight, (int, float)):
            raise ValueError(f"scoring_criteria[{i}].weight must be a number, got {type(weight).__name__}")
        if weight < 0 or weight > 100:
            raise ValueError(f"scoring_criteria[{i}].weight={weight} out of range [0, 100]")
        total += weight
    if total != 100:
        raise ValueError(
            f"scoring_criteria weights must sum to 100, got {total}"
        )


def on_create(data_dir, data, current_user):
    if "scoring_criteria" in data:
        _validate_scoring_criteria(data["scoring_criteria"])


def on_pre_update(data_dir, record_id, rec, updates):
    if "scoring_criteria" in updates:
        _validate_scoring_criteria(updates["scoring_criteria"])


def on_delete_cascade(data_dir, record_id):
    from cascade import _cascade_delete_relations
    _cascade_delete_relations(data_dir, "event_rule", "rule_id", record_id)
