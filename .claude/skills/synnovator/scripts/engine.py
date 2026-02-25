#!/usr/bin/env python3
"""
Synnovator Data Engine - CLI entry point and backward-compatible re-exports.

Data is stored as Markdown files with YAML frontmatter under PROJECT_DIR/.synnovator/
Each content record is a .md file: YAML frontmatter (structured fields) + Markdown body.
Relations are stored as lightweight .md files in relations/ subdirectories.

Directory structure:
  .synnovator/
    event/        # .md files with YAML frontmatter + Markdown body
    post/            # .md files with YAML frontmatter + Markdown body
    resource/        # .md files with YAML frontmatter
    rule/            # .md files with YAML frontmatter + Markdown body
    user/            # .md files with YAML frontmatter
    group/           # .md files with YAML frontmatter
    interaction/     # .md files with YAML frontmatter
    relations/
      event_rule/
      event_post/
      event_group/
      event_event/
      post_post/
      post_resource/
      group_user/
      user_user/
      target_interaction/
"""

import argparse
import json
import sys

# === Re-exports for backward compatibility ===
# test_journeys.py and other callers import from engine directly.

from core import (  # noqa: F401
    CONTENT_TYPES, RELATION_TYPES, BODY_TYPES, ENUMS,
    REQUIRED_FIELDS, RELATION_KEYS, CREATE_PERMISSIONS,
    parse_frontmatter_md, serialize_frontmatter_md,
    get_data_dir, init_dirs, now_iso, gen_id,
    load_record, save_record, find_record, list_records,
    validate_enum, validate_required, validate_uniqueness,
    validate_reference_exists, validate_state_transition,
    get_user_role, check_permission,
)
from content import (  # noqa: F401
    create_content, read_content, update_content, delete_content,
)
from relations import (  # noqa: F401
    create_relation, read_relation, update_relation, delete_relation,
)


# === CLI Interface ===

def main():
    parser = argparse.ArgumentParser(description="Synnovator Data Engine")
    parser.add_argument("--data-dir", default=None, help="Path to project root containing .synnovator/")
    parser.add_argument("--init", action="store_true", help="Initialize data directories")
    parser.add_argument("--user", default=None, help="Current user ID for permission context")

    sub = parser.add_subparsers(dest="command")

    for cmd in ["create", "read", "update", "delete"]:
        p = sub.add_parser(cmd)
        p.add_argument("type", help="Content type or relation type")
        p.add_argument("--id", default=None, help="Record ID")
        p.add_argument("--data", default=None, help="JSON data")
        p.add_argument("--body", default=None, help="Markdown body content")
        p.add_argument("--filters", default=None, help="JSON filters")

    args = parser.parse_args()

    data_dir = get_data_dir(args.data_dir) if args.data_dir else get_data_dir()

    if args.init:
        init_dirs(data_dir)
        print(json.dumps({"status": "ok", "data_dir": str(data_dir)}))
        return

    if not args.command:
        parser.print_help()
        return

    is_relation = args.type in RELATION_TYPES or args.type.replace(":", "_") in RELATION_TYPES
    normalized_type = args.type.replace(":", "_") if is_relation else args.type

    try:
        data = json.loads(args.data) if args.data else {}
        filters = json.loads(args.filters) if args.filters else {}
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON: {e}"}), file=sys.stderr)
        sys.exit(1)

    # Add Markdown body if provided
    if hasattr(args, 'body') and args.body:
        data["_body"] = args.body

    try:
        if args.command == "create":
            if is_relation:
                result = create_relation(data_dir, normalized_type, data, current_user=args.user)
            else:
                result = create_content(data_dir, normalized_type, data, current_user=args.user)
        elif args.command == "read":
            if is_relation:
                result = read_relation(data_dir, normalized_type, filters=filters or None)
            else:
                result = read_content(
                    data_dir, normalized_type,
                    record_id=args.id,
                    filters=filters or None,
                    current_user=args.user,
                )
        elif args.command == "update":
            if is_relation:
                result = update_relation(data_dir, normalized_type, filters, data, current_user=args.user)
            else:
                if not args.id:
                    raise ValueError("--id required for update")
                result = update_content(data_dir, normalized_type, args.id, data, current_user=args.user)
        elif args.command == "delete":
            if is_relation:
                result = delete_relation(data_dir, normalized_type, filters or data, current_user=args.user)
            else:
                if not args.id:
                    raise ValueError("--id required for delete")
                result = delete_content(data_dir, normalized_type, args.id, current_user=args.user)

        # Remove _body from JSON output for cleanliness, indicate presence
        def clean_output(obj):
            if isinstance(obj, dict):
                out = {k: v for k, v in obj.items() if k != "_body"}
                if obj.get("_body"):
                    out["has_body"] = True
                return out
            if isinstance(obj, list):
                return [clean_output(i) for i in obj]
            return obj

        print(json.dumps(clean_output(result), indent=2, ensure_ascii=False, default=str))

    except ValueError as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": str(e), "type": type(e).__name__}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
