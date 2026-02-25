#!/usr/bin/env python3
"""
Synnovator Data Engine - Rule enforcement logic.

Uses lazy imports for relations to avoid circular dependencies.
"""

from datetime import datetime, timezone

from core import find_record, load_record


def _get_category_rules(data_dir, event_id):
    """Get all active rules linked to a event via event_rule relations."""
    from relations import read_relation

    cat_rule_rels = read_relation(data_dir, "event_rule", {"event_id": event_id})
    rules = []
    for rel in cat_rule_rels:
        rule_id = rel.get("rule_id")
        fp = find_record(data_dir, "rule", rule_id)
        if fp:
            rule = load_record(fp)
            rules.append(rule)
    return rules


def _validate_category_rules(data_dir, event_id, check_type, context):
    """Validate all rules for a event. Raises ValueError on first failure.

    check_type:
      - "submission": time window, submission count, format, min_team_size
      - "team_join": max_team_size
      - "publish": allow_public / require_review
    """
    rules = _get_category_rules(data_dir, event_id)
    if not rules:
        return
    for rule in rules:
        rule_name = rule.get("name", rule.get("id", "unknown"))
        if check_type == "submission":
            _validate_submission_rules(data_dir, rule, rule_name, context)
        elif check_type == "team_join":
            _validate_team_join_rules(data_dir, rule, rule_name, context)
        elif check_type == "publish":
            _validate_publish_rules(data_dir, rule, rule_name, context)


def _validate_submission_rules(data_dir, rule, rule_name, context):
    """Validate submission constraints: time window, count, format, team size."""
    from relations import read_relation

    now = datetime.now(timezone.utc)

    # Time window: submission_start
    start = rule.get("submission_start")
    if start:
        if isinstance(start, str):
            start = datetime.fromisoformat(start)
        if hasattr(start, 'tzinfo') and start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)
        if now < start:
            raise ValueError(
                f"Rule '{rule_name}': submission not yet open (starts: {start.isoformat()})"
            )

    # Time window: submission_deadline
    deadline = rule.get("submission_deadline")
    if deadline:
        if isinstance(deadline, str):
            deadline = datetime.fromisoformat(deadline)
        if hasattr(deadline, 'tzinfo') and deadline.tzinfo is None:
            deadline = deadline.replace(tzinfo=timezone.utc)
        if now > deadline:
            raise ValueError(
                f"Rule '{rule_name}': submission deadline passed (deadline: {deadline.isoformat()})"
            )

    # Max submissions per user
    max_sub = rule.get("max_submissions")
    if max_sub is not None:
        user_id = context.get("user_id")
        event_id = context.get("event_id")
        if user_id and event_id:
            existing = read_relation(data_dir, "event_post", {"event_id": event_id})
            user_submissions = 0
            for rel in existing:
                post_fp = find_record(data_dir, "post", rel.get("post_id"))
                if post_fp:
                    post = load_record(post_fp)
                    if post.get("created_by") == user_id:
                        user_submissions += 1
            if user_submissions >= max_sub:
                raise ValueError(
                    f"Rule '{rule_name}': max submissions reached ({user_submissions}/{max_sub})"
                )

    # Submission format
    allowed_formats = rule.get("submission_format")
    if allowed_formats:
        post_id = context.get("post_id")
        if post_id:
            post_resources = read_relation(data_dir, "post_resource", {"post_id": post_id})
            for pr in post_resources:
                res_fp = find_record(data_dir, "resource", pr.get("resource_id"))
                if res_fp:
                    res = load_record(res_fp)
                    filename = res.get("filename", "")
                    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
                    if ext and ext not in [f.lower() for f in allowed_formats]:
                        raise ValueError(
                            f"Rule '{rule_name}': format '{ext}' not allowed "
                            f"(allowed: {allowed_formats})"
                        )

    # Min team size
    min_size = rule.get("min_team_size")
    if min_size is not None:
        user_id = context.get("user_id")
        if user_id:
            group_id = context.get("group_id")
            if not group_id:
                event_id = context.get("event_id")
                cat_groups = read_relation(
                    data_dir, "event_group", {"event_id": event_id}
                )
                for cg in cat_groups:
                    members = read_relation(
                        data_dir, "group_user", {"group_id": cg["group_id"]}
                    )
                    accepted = [m for m in members if m.get("status") == "accepted"]
                    if any(m.get("user_id") == user_id for m in accepted):
                        group_id = cg["group_id"]
                        break
            if group_id:
                members = read_relation(data_dir, "group_user", {"group_id": group_id})
                accepted_count = sum(1 for m in members if m.get("status") == "accepted")
                if accepted_count < min_size:
                    raise ValueError(
                        f"Rule '{rule_name}': team too small "
                        f"({accepted_count}/{min_size} members)"
                    )


def _validate_team_join_rules(data_dir, rule, rule_name, context):
    """Validate team size constraints for joining a group."""
    from relations import read_relation

    max_size = rule.get("max_team_size")
    if max_size is not None:
        group_id = context.get("group_id")
        if group_id:
            members = read_relation(data_dir, "group_user", {"group_id": group_id})
            accepted_count = sum(1 for m in members if m.get("status") == "accepted")
            if accepted_count >= max_size:
                raise ValueError(
                    f"Rule '{rule_name}': team is full ({accepted_count}/{max_size} members)"
                )


def _validate_publish_rules(data_dir, rule, rule_name, context):
    """Validate publication path based on allow_public / require_review."""
    new_status = context.get("new_status")
    if new_status == "published":
        if not rule.get("allow_public", False):
            if rule.get("require_review", False):
                raise ValueError(
                    f"Rule '{rule_name}': direct publish not allowed, "
                    f"post must go through review (set status to 'pending_review')"
                )
            else:
                raise ValueError(
                    f"Rule '{rule_name}': public publishing not allowed"
                )
