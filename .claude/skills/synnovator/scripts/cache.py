#!/usr/bin/env python3
"""
Synnovator Data Engine - Cache stats and scoring criteria.

Uses lazy imports for relations to avoid circular dependencies.
"""

from core import find_record, load_record, save_record, now_iso


def _update_cache_stats(data_dir, target_type, target_id):
    """Recalculate cache stats for a target by querying via target_interaction relations."""
    if target_type != "post":
        return

    fp = find_record(data_dir, "post", target_id)
    if not fp:
        return

    from relations import read_relation

    post = load_record(fp)

    # Find all interactions for this target via target_interaction relations
    rels = read_relation(data_dir, "target_interaction", {
        "target_type": target_type, "target_id": target_id
    })
    all_interactions = []
    for rel in rels:
        iact_fp = find_record(data_dir, "interaction", rel["interaction_id"])
        if iact_fp:
            iact = load_record(iact_fp)
            all_interactions.append(iact)

    post["like_count"] = sum(1 for i in all_interactions if i.get("type") == "like")
    post["comment_count"] = sum(1 for i in all_interactions if i.get("type") == "comment")

    ratings = [i for i in all_interactions if i.get("type") == "rating"]
    if ratings:
        scoring_criteria = _find_scoring_criteria(data_dir, target_id)
        if scoring_criteria:
            weight_map = {sc["name"]: sc["weight"] for sc in scoring_criteria}
            total_weighted_scores = []
            for r in ratings:
                val = r.get("value", {})
                if isinstance(val, dict):
                    weighted_score = 0
                    for dim_name, dim_score in val.items():
                        if dim_name.startswith("_"):
                            continue
                        if dim_name in weight_map and isinstance(dim_score, (int, float)):
                            weighted_score += dim_score * weight_map[dim_name] / 100
                    if weighted_score > 0:
                        total_weighted_scores.append(weighted_score)
            if total_weighted_scores:
                post["average_rating"] = round(
                    sum(total_weighted_scores) / len(total_weighted_scores), 2
                )
            else:
                post["average_rating"] = None
        else:
            post["average_rating"] = None
    else:
        post["average_rating"] = None

    post["updated_at"] = now_iso()
    body = post.pop("_body", "")
    save_record(fp, post, body=body)


def _find_scoring_criteria(data_dir, post_id):
    from relations import read_relation

    cat_post_rels = read_relation(data_dir, "event_post", {"post_id": post_id})
    for rel in cat_post_rels:
        cat_id = rel.get("event_id")
        cat_rule_rels = read_relation(data_dir, "event_rule", {"event_id": cat_id})
        for cr in cat_rule_rels:
            rule_id = cr.get("rule_id")
            fp = find_record(data_dir, "rule", rule_id)
            if fp:
                rule = load_record(fp)
                if rule.get("scoring_criteria"):
                    return rule["scoring_criteria"]
    return None
