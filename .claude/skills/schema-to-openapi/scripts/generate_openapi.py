#!/usr/bin/env python3
"""
Generate OpenAPI 3.0 specification from Synnovator schema.md.

Dynamically reads:
  - .claude/skills/synnovator/references/schema.md

Usage:
    uv run python generate_openapi.py [--output PATH] [--schema PATH]

Output:
    Writes openapi.yaml to the specified path (default: .synnovator/openapi.yaml)
"""

import argparse
import json
import re
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None


# === Schema Parser ===

def parse_schema_md(schema_path: Path) -> dict:
    """Parse schema.md and extract content types, relations, and enums."""
    content = schema_path.read_text(encoding="utf-8")

    result = {
        "content_types": {},
        "relations": {},
        "enums": {},
        "uniqueness": []
    }

    # Parse content type tables
    content_type_pattern = r"### (\w+)\n\|[^\n]+\n\|[-|\s]+\n((?:\|[^\n]+\n)+)"
    for match in re.finditer(content_type_pattern, content):
        type_name = match.group(1)
        table_rows = match.group(2)
        fields = parse_table_rows(table_rows)
        result["content_types"][type_name] = fields

        # Extract enums from fields
        for field in fields:
            if field.get("enum_values"):
                enum_key = f"{type_name}.{field['name']}"
                result["enums"][enum_key] = field["enum_values"]

    # Parse relation types
    relation_pattern = r"### (\w+)\n`([^`]+)`"
    relation_section = content.split("## Relation Types")[-1].split("## Uniqueness")[0] if "## Relation Types" in content else ""
    for match in re.finditer(relation_pattern, relation_section):
        rel_name = match.group(1)
        rel_def = match.group(2)
        result["relations"][rel_name] = parse_relation_def(rel_def)

    # Parse uniqueness constraints
    if "## Uniqueness Constraints" in content:
        uniqueness_section = content.split("## Uniqueness Constraints")[-1]
        for line in uniqueness_section.split("\n"):
            if line.startswith("- "):
                result["uniqueness"].append(line[2:].strip())

    return result


def parse_table_rows(table_text: str) -> list:
    """Parse markdown table rows into field definitions."""
    fields = []
    for line in table_text.strip().split("\n"):
        if not line.startswith("|"):
            continue
        # Replace escaped pipes with placeholder before splitting
        line_processed = line.replace("\\|", "\x00PIPE\x00")
        cells = [c.strip().replace("\x00PIPE\x00", "|") for c in line_processed.split("|")[1:-1]]
        if len(cells) < 4:
            continue

        field_name = cells[0].strip()
        field_type = cells[1].strip()
        required = cells[2].strip().lower()
        default = cells[3].strip() if len(cells) > 3 else ""
        notes = cells[4].strip() if len(cells) > 4 else ""

        # Skip combined fields like "id, created_by, created_at..."
        if "," in field_name:
            continue

        # Parse enum values from notes
        # Format in schema.md: `value1` \| `value2` \| `value3`
        enum_values = None
        if field_type == "enum" or "\\|" in notes or (notes.count("`") >= 4):
            # Find all backtick-enclosed values
            enum_match = re.findall(r"`([^`]+)`", notes)
            if len(enum_match) >= 2:
                enum_values = [v.strip() for v in enum_match if v.strip()]

        # Determine OpenAPI type
        openapi_type = map_field_type(field_type, notes)

        fields.append({
            "name": field_name,
            "type": openapi_type["type"],
            "format": openapi_type.get("format"),
            "required": required == "yes",
            "default": None if default in ("—", "-", "") else default,
            "auto": required == "auto" or "auto" in default.lower() if default else False,
            "cache": "cache" in required,
            "enum_values": enum_values,
            "notes": notes,
            "is_array": "list[" in field_type.lower() or "array" in field_type.lower(),
            "items_type": extract_array_item_type(field_type)
        })

    return fields


def map_field_type(field_type: str, notes: str = "") -> dict:
    """Map schema.md field type to OpenAPI type."""
    ft = field_type.lower()

    if ft in ("string", "str"):
        if "url" in notes.lower() or "uri" in notes.lower():
            return {"type": "string", "format": "uri"}
        if "email" in notes.lower():
            return {"type": "string", "format": "email"}
        return {"type": "string"}
    elif ft in ("integer", "int"):
        return {"type": "integer"}
    elif ft in ("number", "float", "double"):
        return {"type": "number", "format": "float"}
    elif ft in ("boolean", "bool"):
        return {"type": "boolean"}
    elif ft == "datetime":
        return {"type": "string", "format": "date-time"}
    elif ft == "enum":
        return {"type": "string"}
    elif ft.startswith("list[") or ft.startswith("array"):
        return {"type": "array"}
    elif "user_id" in ft or "id" in ft:
        return {"type": "string"}
    elif ft == "object":
        return {"type": "object"}
    else:
        return {"type": "string"}


def extract_array_item_type(field_type: str) -> str | None:
    """Extract item type from list[X] or array[X]."""
    match = re.search(r"list\[(\w+)\]", field_type.lower())
    if match:
        return match.group(1)
    return None


def parse_relation_def(rel_def: str) -> dict:
    """Parse relation definition string."""
    parts = [p.strip() for p in rel_def.split("+")]
    keys = []
    optional = []
    for part in parts:
        if part.startswith("optional "):
            optional.append(part.replace("optional ", "").strip())
        elif part.startswith("auto "):
            pass  # Skip auto fields
        else:
            keys.append(part)
    return {"keys": keys, "optional": optional}


# === OpenAPI Generator ===

def generate_openapi_spec(schema: dict, title: str = "Synnovator API", version: str = "1.0.0") -> dict:
    """Generate complete OpenAPI 3.0 specification from parsed schema."""

    spec = {
        "openapi": "3.0.3",
        "info": {
            "title": title,
            "version": version,
            "description": "API for Synnovator - Activity and Competition Management Platform",
            "contact": {"name": "API Support"},
            "license": {"name": "MIT", "url": "https://opensource.org/licenses/MIT"}
        },
        "servers": [
            {"url": "http://localhost:8000", "description": "Development server"},
            {"url": "https://api.synnovator.com", "description": "Production server"}
        ],
        "tags": generate_tags(),
        "paths": generate_paths(schema),
        "components": {
            "securitySchemes": generate_security_schemes(),
            "schemas": generate_schemas(schema),
            "parameters": generate_common_parameters(),
            "responses": generate_common_responses()
        },
        "security": [{"oauth2": ["read", "write"]}]
    }

    return spec


def generate_tags() -> list:
    """Generate API tags for grouping endpoints."""
    return [
        {"name": "events", "description": "Activity and competition events"},
        {"name": "posts", "description": "User posts and submissions"},
        {"name": "resources", "description": "File resources and attachments"},
        {"name": "rules", "description": "Event rules and scoring criteria"},
        {"name": "users", "description": "User management"},
        {"name": "groups", "description": "Teams and groups"},
        {"name": "interactions", "description": "Likes, comments, and ratings"},
        {"name": "admin", "description": "Admin batch operations"}
    ]


def generate_security_schemes() -> dict:
    """Generate OAuth2 security scheme."""
    return {
        "oauth2": {
            "type": "oauth2",
            "flows": {
                "authorizationCode": {
                    "authorizationUrl": "/oauth/authorize",
                    "tokenUrl": "/oauth/token",
                    "scopes": {
                        "read": "Read access to resources",
                        "write": "Write access to resources",
                        "admin": "Admin access for batch operations"
                    }
                }
            }
        },
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }


def generate_common_parameters() -> dict:
    """Generate common query parameters."""
    return {
        "SkipParam": {
            "name": "skip",
            "in": "query",
            "schema": {"type": "integer", "default": 0, "minimum": 0},
            "description": "Number of records to skip"
        },
        "LimitParam": {
            "name": "limit",
            "in": "query",
            "schema": {"type": "integer", "default": 20, "minimum": 1, "maximum": 100},
            "description": "Maximum number of records to return"
        },
        "IncludeDeletedParam": {
            "name": "include_deleted",
            "in": "query",
            "schema": {"type": "boolean", "default": False},
            "description": "Include soft-deleted records (admin only)"
        }
    }


def generate_common_responses() -> dict:
    """Generate common response definitions."""
    return {
        "NotFound": {
            "description": "Resource not found",
            "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}
        },
        "ValidationError": {
            "description": "Validation error",
            "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}
        },
        "Unauthorized": {
            "description": "Authentication required",
            "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}
        },
        "Forbidden": {
            "description": "Permission denied",
            "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}
        }
    }


def generate_schemas(schema: dict) -> dict:
    """Generate OpenAPI schemas from parsed schema.md."""
    schemas = {}

    # Error schema (static)
    schemas["Error"] = {
        "type": "object",
        "required": ["error"],
        "properties": {
            "error": {
                "type": "object",
                "required": ["code", "message"],
                "properties": {
                    "code": {"type": "string", "example": "NOT_FOUND"},
                    "message": {"type": "string", "example": "Resource not found"},
                    "details": {"type": "object", "additionalProperties": True}
                }
            }
        }
    }

    # Generate enum schemas from parsed enums
    enum_schema_map = {
        "event.type": "CategoryType",
        "event.status": "CategoryStatus",
        "post.type": "PostType",
        "post.status": "PostStatus",
        "user.role": "UserRole",
        "group.visibility": "GroupVisibility",
        "interaction.type": "InteractionType",
    }

    for enum_key, enum_name in enum_schema_map.items():
        if enum_key in schema["enums"]:
            schemas[enum_name] = {
                "type": "string",
                "enum": schema["enums"][enum_key],
                "description": f"{enum_name.replace('Type', ' type').replace('Status', ' status').replace('Role', ' role').replace('Visibility', ' visibility')}"
            }

    # Additional enums for relations
    schemas["MemberRole"] = {"type": "string", "enum": ["owner", "admin", "member"], "description": "Group member role"}
    schemas["MemberStatus"] = {"type": "string", "enum": ["pending", "accepted", "rejected"], "description": "Group membership status"}

    # Generate content type schemas
    content_types = schema.get("content_types", {})

    # Event schemas
    if "event" in content_types:
        schemas.update(generate_content_schemas("Event", content_types["event"],
            create_required=["name", "description", "type"],
            response_required=["id", "name", "description", "type", "status", "created_at", "updated_at"],
            has_content=True))

    # Post schemas
    if "post" in content_types:
        schemas.update(generate_content_schemas("Post", content_types["post"],
            create_required=["title"],
            response_required=["id", "title", "type", "status", "created_at", "updated_at"],
            has_content=True))

    # Resource schemas
    if "resource" in content_types:
        schemas.update(generate_content_schemas("Resource", content_types["resource"],
            create_required=["filename"],
            response_required=["id", "filename", "created_at"]))

    # Rule schemas
    if "rule" in content_types:
        schemas.update(generate_content_schemas("Rule", content_types["rule"],
            create_required=["name", "description"],
            response_required=["id", "name", "description", "created_at"],
            has_content=True))
        # Add ScoringCriterion schema
        schemas["ScoringCriterion"] = {
            "type": "object",
            "required": ["name", "weight"],
            "properties": {
                "name": {"type": "string", "example": "Innovation"},
                "weight": {"type": "integer", "minimum": 0, "maximum": 100, "example": 30},
                "description": {"type": "string"}
            }
        }

    # User schemas
    if "user" in content_types:
        schemas.update(generate_content_schemas("User", content_types["user"],
            create_required=["username", "email"],
            response_required=["id", "username", "email", "role", "created_at"]))

    # Group schemas
    if "group" in content_types:
        schemas.update(generate_content_schemas("Group", content_types["group"],
            create_required=["name"],
            response_required=["id", "name", "visibility", "created_at"]))

    # Interaction-related schemas (static, as they have special structure)
    schemas.update(generate_interaction_schemas())

    # Relation schemas
    schemas.update(generate_relation_schemas())

    # Paginated response schemas
    for resource in ["Event", "Post", "Resource", "Rule", "User", "Group", "Comment", "Rating", "Member"]:
        schemas[f"Paginated{resource}List"] = {
            "type": "object",
            "required": ["items", "total", "skip", "limit"],
            "properties": {
                "items": {"type": "array", "items": {"$ref": f"#/components/schemas/{resource}"}},
                "total": {"type": "integer", "description": "Total number of records"},
                "skip": {"type": "integer"},
                "limit": {"type": "integer"}
            }
        }

    # Batch operation schemas
    schemas.update(generate_batch_schemas())

    return schemas


def generate_content_schemas(name: str, fields: list, create_required: list, response_required: list, has_content: bool = False) -> dict:
    """Generate Create, Update, and Response schemas for a content type."""
    schemas = {}

    # Build properties from fields
    create_props = {}
    update_props = {}
    response_props = {}

    # Standard auto fields for response
    auto_fields = ["id", "created_by", "created_at", "updated_at"]

    for field in fields:
        fname = field["name"]

        # Skip auto fields for create/update
        if field.get("auto") or fname in auto_fields:
            # Add to response only
            prop = build_property(field, name)
            if fname == "id":
                prop["example"] = f"{name.lower()[:3]}_{name.lower()[:3]}123"
            response_props[fname] = prop
            continue

        # Skip cache fields for create/update
        if field.get("cache"):
            prop = build_property(field, name)
            prop["readOnly"] = True
            response_props[fname] = prop
            continue

        prop = build_property(field, name)

        # Add to create (all editable fields)
        create_props[fname] = prop.copy()

        # Add to update (all optional)
        update_props[fname] = prop.copy()

        # Add to response
        response_props[fname] = prop.copy()

    # Add content field for types with markdown body
    if has_content:
        content_prop = {"type": "string", "description": "Markdown content body"}
        create_props["content"] = content_prop.copy()
        update_props["content"] = content_prop.copy()
        response_props["content"] = content_prop.copy()

    # Create schema
    schemas[f"{name}Create"] = {
        "type": "object",
        "required": create_required,
        "properties": create_props
    }

    # Update schema (all optional)
    schemas[f"{name}Update"] = {
        "type": "object",
        "properties": update_props
    }

    # Response schema
    schemas[name] = {
        "type": "object",
        "required": response_required,
        "properties": response_props
    }

    return schemas


def build_property(field: dict, parent_name: str = "") -> dict:
    """Build OpenAPI property from field definition."""
    prop: dict[str, Any] = {"type": field["type"]}

    if field.get("format"):
        prop["format"] = field["format"]

    if field.get("enum_values"):
        # Use $ref for known enums
        enum_ref = get_enum_ref(parent_name, field["name"])
        if enum_ref:
            return {"$ref": f"#/components/schemas/{enum_ref}"}
        prop["enum"] = field["enum_values"]

    if field.get("is_array"):
        prop["type"] = "array"
        items_type = field.get("items_type", "string")
        if items_type == "object":
            prop["items"] = {"type": "object"}
        elif items_type == "string":
            prop["items"] = {"type": "string"}
        else:
            prop["items"] = {"type": "string"}

    if field.get("default") and field["default"] not in ("—", "-", ""):
        if field["default"].lower() == "true":
            prop["default"] = True
        elif field["default"].lower() == "false":
            prop["default"] = False
        elif field["default"].isdigit():
            prop["default"] = int(field["default"])
        else:
            prop["default"] = field["default"]

    return prop


def get_enum_ref(parent_name: str, field_name: str) -> str | None:
    """Get enum schema reference name."""
    refs = {
        ("Event", "type"): "CategoryType",
        ("Event", "status"): "CategoryStatus",
        ("Post", "type"): "PostType",
        ("Post", "status"): "PostStatus",
        ("User", "role"): "UserRole",
        ("Group", "visibility"): "GroupVisibility",
        ("Interaction", "type"): "InteractionType",
    }
    return refs.get((parent_name, field_name))


def generate_interaction_schemas() -> dict:
    """Generate interaction-related schemas (Comment, Rating)."""
    return {
        "CommentCreate": {
            "type": "object",
            "required": ["content"],
            "properties": {
                "content": {"type": "string", "minLength": 1, "maxLength": 2000},
                "parent_id": {"type": "string", "description": "Parent comment ID for replies"}
            }
        },
        "Comment": {
            "type": "object",
            "required": ["id", "content", "created_by", "created_at"],
            "properties": {
                "id": {"type": "string", "example": "iact_abc123"},
                "content": {"type": "string"},
                "parent_id": {"type": "string"},
                "created_by": {"type": "string"},
                "author": {"$ref": "#/components/schemas/User"},
                "created_at": {"type": "string", "format": "date-time"},
                "updated_at": {"type": "string", "format": "date-time"}
            }
        },
        "RatingCreate": {
            "type": "object",
            "required": ["scores"],
            "properties": {
                "scores": {
                    "type": "object",
                    "additionalProperties": {"type": "number", "minimum": 0, "maximum": 100},
                    "example": {"Innovation": 87, "Technical": 82, "Practical": 78}
                },
                "comment": {"type": "string", "description": "Optional rating comment"}
            }
        },
        "Rating": {
            "type": "object",
            "required": ["id", "scores", "created_by", "created_at"],
            "properties": {
                "id": {"type": "string"},
                "scores": {"type": "object", "additionalProperties": {"type": "number"}},
                "comment": {"type": "string"},
                "created_by": {"type": "string"},
                "author": {"$ref": "#/components/schemas/User"},
                "created_at": {"type": "string", "format": "date-time"}
            }
        },
        "MemberAdd": {
            "type": "object",
            "required": ["user_id"],
            "properties": {
                "user_id": {"type": "string"},
                "role": {"$ref": "#/components/schemas/MemberRole"}
            }
        },
        "MemberUpdate": {
            "type": "object",
            "properties": {
                "role": {"$ref": "#/components/schemas/MemberRole"},
                "status": {"$ref": "#/components/schemas/MemberStatus"}
            }
        },
        "Member": {
            "type": "object",
            "required": ["user_id", "role", "status"],
            "properties": {
                "user_id": {"type": "string"},
                "user": {"$ref": "#/components/schemas/User"},
                "role": {"$ref": "#/components/schemas/MemberRole"},
                "status": {"$ref": "#/components/schemas/MemberStatus"},
                "joined_at": {"type": "string", "format": "date-time"},
                "status_changed_at": {"type": "string", "format": "date-time"}
            }
        }
    }


def generate_relation_schemas() -> dict:
    """Generate relation-related schemas."""
    return {
        "CategoryRuleAdd": {
            "type": "object",
            "required": ["rule_id"],
            "properties": {
                "rule_id": {"type": "string"},
                "priority": {"type": "integer", "default": 0}
            }
        },
        "CategoryPostAdd": {
            "type": "object",
            "required": ["post_id"],
            "properties": {
                "post_id": {"type": "string"},
                "relation_type": {"type": "string", "enum": ["submission", "reference"], "default": "submission"}
            }
        },
        "CategoryGroupAdd": {
            "type": "object",
            "required": ["group_id"],
            "properties": {"group_id": {"type": "string"}}
        },
        "PostResourceAdd": {
            "type": "object",
            "required": ["resource_id"],
            "properties": {
                "resource_id": {"type": "string"},
                "display_type": {"type": "string", "enum": ["attachment", "inline"], "default": "attachment"},
                "position": {"type": "integer"}
            }
        },
        "PostRelationAdd": {
            "type": "object",
            "required": ["target_post_id"],
            "properties": {
                "target_post_id": {"type": "string"},
                "relation_type": {"type": "string", "enum": ["reference", "reply", "embed"], "default": "reference"},
                "position": {"type": "integer"}
            }
        }
    }


def generate_batch_schemas() -> dict:
    """Generate batch operation schemas."""
    return {
        "BatchIds": {
            "type": "object",
            "required": ["ids"],
            "properties": {
                "ids": {"type": "array", "items": {"type": "string"}, "minItems": 1, "maxItems": 100}
            }
        },
        "BatchStatusUpdate": {
            "type": "object",
            "required": ["ids", "status"],
            "properties": {
                "ids": {"type": "array", "items": {"type": "string"}, "minItems": 1, "maxItems": 100},
                "status": {"$ref": "#/components/schemas/PostStatus"}
            }
        },
        "BatchRoleUpdate": {
            "type": "object",
            "required": ["ids", "role"],
            "properties": {
                "ids": {"type": "array", "items": {"type": "string"}, "minItems": 1, "maxItems": 100},
                "role": {"$ref": "#/components/schemas/UserRole"}
            }
        },
        "BatchResult": {
            "type": "object",
            "required": ["success_count", "failed_count"],
            "properties": {
                "success_count": {"type": "integer"},
                "failed_count": {"type": "integer"},
                "failed_ids": {"type": "array", "items": {"type": "string"}},
                "errors": {"type": "object", "additionalProperties": {"type": "string"}}
            }
        }
    }


def generate_paths(_schema: dict) -> dict:
    """Generate all API paths."""
    paths = {}

    # Events
    paths["/events"] = crud_list_create("events", "Event")
    paths["/events/{event_id}"] = crud_get_update_delete("events", "Event", "event_id")
    paths["/events/{event_id}/rules"] = nested_list_add("events", "event_id", "rules", "Rule", "CategoryRuleAdd")
    paths["/events/{event_id}/rules/{rule_id}"] = nested_remove("events", "event_id", "rules", "rule_id")
    paths["/events/{event_id}/posts"] = nested_list_add("events", "event_id", "posts", "Post", "CategoryPostAdd", paginated=True, extra_params=[
        {"name": "relation_type", "in": "query", "schema": {"type": "string", "enum": ["submission", "reference"]}}
    ])
    paths["/events/{event_id}/groups"] = nested_list_add("events", "event_id", "groups", "Group", "CategoryGroupAdd")
    paths["/events/{event_id}/resources"] = nested_list_add("events", "event_id", "resources", "Resource", "CategoryResourceAdd", extra_params=[
        {"name": "display_type", "in": "query", "schema": {"type": "string", "enum": ["banner", "attachment", "inline"]}}
    ])

    # Posts
    paths["/posts"] = crud_list_create("posts", "Post", list_params=[
        {"name": "type", "in": "query", "schema": {"$ref": "#/components/schemas/PostType"}},
        {"name": "status", "in": "query", "schema": {"$ref": "#/components/schemas/PostStatus"}},
        {"name": "tags", "in": "query", "schema": {"type": "array", "items": {"type": "string"}}, "style": "form", "explode": False}
    ])
    paths["/posts/{post_id}"] = crud_get_update_delete("posts", "Post", "post_id")
    paths["/posts/{post_id}/like"] = interaction_like("post_id")
    paths["/posts/{post_id}/comments"] = interaction_comments("post_id")
    paths["/posts/{post_id}/comments/{comment_id}"] = interaction_comment_single("post_id", "comment_id")
    paths["/posts/{post_id}/ratings"] = interaction_ratings("post_id")
    paths["/posts/{post_id}/resources"] = nested_list_add("posts", "post_id", "resources", "Resource", "PostResourceAdd")
    paths["/posts/{post_id}/related"] = nested_list_add("posts", "post_id", "related", "Post", "PostRelationAdd", extra_params=[
        {"name": "relation_type", "in": "query", "schema": {"type": "string", "enum": ["reference", "reply", "embed"]}}
    ])

    # Resources
    paths["/resources"] = crud_list_create("resources", "Resource")
    paths["/resources/{resource_id}"] = {
        "get": endpoint_get("resources", "Resource", "resource_id"),
        "delete": endpoint_delete("resources", "resource_id")
    }

    # Rules
    paths["/rules"] = crud_list_create("rules", "Rule")
    paths["/rules/{rule_id}"] = crud_get_update_delete("rules", "Rule", "rule_id")

    # Users
    paths["/users"] = crud_list_create("users", "User", list_params=[
        {"name": "role", "in": "query", "schema": {"$ref": "#/components/schemas/UserRole"}}
    ])
    paths["/users/me"] = {
        "get": {"summary": "Get current user", "operationId": "get_current_user", "tags": ["users"],
                "responses": {"200": {"description": "Current user", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/User"}}}}}},
        "patch": {"summary": "Update current user", "operationId": "update_current_user", "tags": ["users"],
                  "requestBody": {"required": True, "content": {"application/json": {"schema": {"$ref": "#/components/schemas/UserUpdate"}}}},
                  "responses": {"200": {"description": "User updated", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/User"}}}}}}
    }
    paths["/users/{user_id}"] = crud_get_update_delete("users", "User", "user_id")

    # Groups
    paths["/groups"] = crud_list_create("groups", "Group", list_params=[
        {"name": "visibility", "in": "query", "schema": {"$ref": "#/components/schemas/GroupVisibility"}}
    ])
    paths["/groups/{group_id}"] = crud_get_update_delete("groups", "Group", "group_id")
    paths["/groups/{group_id}/members"] = {
        "get": {"summary": "List group members", "operationId": "list_group_members", "tags": ["groups"],
                "parameters": [path_param("group_id"), {"name": "status", "in": "query", "schema": {"$ref": "#/components/schemas/MemberStatus"}}],
                "responses": {"200": {"description": "List of members", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/PaginatedMemberList"}}}}}},
        "post": {"summary": "Add member to group", "operationId": "add_group_member", "tags": ["groups"],
                 "parameters": [path_param("group_id")],
                 "requestBody": {"required": True, "content": {"application/json": {"schema": {"$ref": "#/components/schemas/MemberAdd"}}}},
                 "responses": {"201": {"description": "Member added", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Member"}}}}}}
    }
    paths["/groups/{group_id}/members/{user_id}"] = {
        "patch": {"summary": "Update member", "operationId": "update_group_member", "tags": ["groups"],
                  "parameters": [path_param("group_id"), path_param("user_id")],
                  "requestBody": {"required": True, "content": {"application/json": {"schema": {"$ref": "#/components/schemas/MemberUpdate"}}}},
                  "responses": {"200": {"description": "Member updated", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Member"}}}}}},
        "delete": {"summary": "Remove member from group", "operationId": "remove_group_member", "tags": ["groups"],
                   "parameters": [path_param("group_id"), path_param("user_id")],
                   "responses": {"204": {"description": "Member removed"}}}
    }
    paths["/groups/{group_id}/posts"] = nested_list_add("groups", "group_id", "posts", "Post", "GroupPostAdd", extra_params=[
        {"name": "relation_type", "in": "query", "schema": {"type": "string", "enum": ["team_submission", "announcement", "reference"]}}
    ])
    paths["/groups/{group_id}/resources"] = nested_list_add("groups", "group_id", "resources", "Resource", "GroupResourceAdd", extra_params=[
        {"name": "access_level", "in": "query", "schema": {"type": "string", "enum": ["read_only", "read_write"]}}
    ])

    # Notifications
    paths["/notifications"] = {
        "get": {"summary": "List notifications", "operationId": "list_notifications", "tags": ["notifications"],
                "parameters": [{"$ref": "#/components/parameters/SkipParam"}, {"$ref": "#/components/parameters/LimitParam"},
                              {"name": "type", "in": "query", "schema": {"type": "string", "enum": ["system", "activity", "team", "social"]}},
                              {"name": "is_read", "in": "query", "schema": {"type": "boolean"}}],
                "responses": {"200": {"description": "List of notifications", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/PaginatedNotificationList"}}}}}}
    }
    paths["/notifications/{notification_id}"] = {
        "get": {"summary": "Get notification", "operationId": "get_notification", "tags": ["notifications"],
                "parameters": [path_param("notification_id")],
                "responses": {"200": {"description": "Notification details", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Notification"}}}}}},
        "patch": {"summary": "Mark notification as read", "operationId": "update_notification", "tags": ["notifications"],
                  "parameters": [path_param("notification_id")],
                  "requestBody": {"required": True, "content": {"application/json": {"schema": {"$ref": "#/components/schemas/NotificationUpdate"}}}},
                  "responses": {"200": {"description": "Notification updated", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Notification"}}}}}}
    }
    paths["/notifications/read-all"] = {
        "post": {"summary": "Mark all notifications as read", "operationId": "mark_all_notifications_read", "tags": ["notifications"],
                 "responses": {"200": {"description": "Marked count", "content": {"application/json": {"schema": {"type": "object", "properties": {"marked_count": {"type": "integer"}}}}}}}}
    }

    # Admin batch operations
    paths["/admin/posts"] = {
        "delete": {"summary": "Batch delete posts", "operationId": "batch_delete_posts", "tags": ["admin"],
                   "security": [{"oauth2": ["admin"]}],
                   "requestBody": {"required": True, "content": {"application/json": {"schema": {"$ref": "#/components/schemas/BatchIds"}}}},
                   "responses": {"200": {"description": "Batch result", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/BatchResult"}}}}}}
    }
    paths["/admin/posts/status"] = {
        "patch": {"summary": "Batch update post status", "operationId": "batch_update_post_status", "tags": ["admin"],
                  "security": [{"oauth2": ["admin"]}],
                  "requestBody": {"required": True, "content": {"application/json": {"schema": {"$ref": "#/components/schemas/BatchStatusUpdate"}}}},
                  "responses": {"200": {"description": "Batch result", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/BatchResult"}}}}}}
    }
    paths["/admin/users/role"] = {
        "patch": {"summary": "Batch update user roles", "operationId": "batch_update_user_roles", "tags": ["admin"],
                  "security": [{"oauth2": ["admin"]}],
                  "requestBody": {"required": True, "content": {"application/json": {"schema": {"$ref": "#/components/schemas/BatchRoleUpdate"}}}},
                  "responses": {"200": {"description": "Batch result", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/BatchResult"}}}}}}
    }

    return paths


# === Path Helper Functions ===

def singularize(word: str) -> str:
    """Convert plural to singular form."""
    irregulars = {
        "events": "event",
        "resources": "resource",
    }
    if word in irregulars:
        return irregulars[word]
    if word.endswith("ies"):
        return word[:-3] + "y"
    if word.endswith("s"):
        return word[:-1]
    return word


def path_param(name: str) -> dict:
    return {"name": name, "in": "path", "required": True, "schema": {"type": "string"}}


def crud_list_create(tag: str, schema_name: str, list_params: list = None) -> dict:
    params = [{"$ref": "#/components/parameters/SkipParam"}, {"$ref": "#/components/parameters/LimitParam"}]
    if list_params:
        params.extend(list_params)
    return {
        "get": {
            "summary": f"List {tag}",
            "operationId": f"list_{tag}",
            "tags": [tag],
            "parameters": params,
            "responses": {"200": {"description": f"List of {tag}", "content": {"application/json": {"schema": {"$ref": f"#/components/schemas/Paginated{schema_name}List"}}}}}
        },
        "post": {
            "summary": f"Create {schema_name.lower()}",
            "operationId": f"create_{schema_name.lower()}",
            "tags": [tag],
            "requestBody": {"required": True, "content": {"application/json": {"schema": {"$ref": f"#/components/schemas/{schema_name}Create"}}}},
            "responses": {"201": {"description": f"{schema_name} created", "content": {"application/json": {"schema": {"$ref": f"#/components/schemas/{schema_name}"}}}},
                         "422": {"$ref": "#/components/responses/ValidationError"}}
        }
    }


def crud_get_update_delete(tag: str, schema_name: str, id_param: str) -> dict:
    return {
        "get": endpoint_get(tag, schema_name, id_param),
        "patch": endpoint_update(tag, schema_name, id_param),
        "delete": endpoint_delete(tag, id_param)
    }


def endpoint_get(tag: str, schema_name: str, id_param: str) -> dict:
    return {
        "summary": f"Get {schema_name.lower()}",
        "operationId": f"get_{schema_name.lower()}",
        "tags": [tag],
        "parameters": [path_param(id_param)],
        "responses": {"200": {"description": f"{schema_name} details", "content": {"application/json": {"schema": {"$ref": f"#/components/schemas/{schema_name}"}}}},
                     "404": {"$ref": "#/components/responses/NotFound"}}
    }


def endpoint_update(tag: str, schema_name: str, id_param: str) -> dict:
    return {
        "summary": f"Update {schema_name.lower()}",
        "operationId": f"update_{schema_name.lower()}",
        "tags": [tag],
        "parameters": [path_param(id_param)],
        "requestBody": {"required": True, "content": {"application/json": {"schema": {"$ref": f"#/components/schemas/{schema_name}Update"}}}},
        "responses": {"200": {"description": f"{schema_name} updated", "content": {"application/json": {"schema": {"$ref": f"#/components/schemas/{schema_name}"}}}},
                     "404": {"$ref": "#/components/responses/NotFound"}}
    }


def endpoint_delete(tag: str, id_param: str) -> dict:
    return {
        "summary": f"Delete {singularize(tag)}",
        "operationId": f"delete_{singularize(tag)}",
        "tags": [tag],
        "parameters": [path_param(id_param)],
        "responses": {"204": {"description": "Deleted"}, "404": {"$ref": "#/components/responses/NotFound"}}
    }


def nested_list_add(parent_tag: str, parent_id: str, child_name: str, child_schema: str, add_schema: str, paginated: bool = False, extra_params: list = None) -> dict:
    params = [path_param(parent_id)]
    if paginated:
        params.extend([{"$ref": "#/components/parameters/SkipParam"}, {"$ref": "#/components/parameters/LimitParam"}])
    if extra_params:
        params.extend(extra_params)

    response_schema = {"$ref": f"#/components/schemas/Paginated{child_schema}List"} if paginated else {"type": "array", "items": {"$ref": f"#/components/schemas/{child_schema}"}}

    return {
        "get": {
            "summary": f"List {singularize(parent_tag)} {child_name}",
            "operationId": f"list_{singularize(parent_tag)}_{child_name}",
            "tags": [parent_tag],
            "parameters": params,
            "responses": {"200": {"description": f"List of {child_name}", "content": {"application/json": {"schema": response_schema}}}}
        },
        "post": {
            "summary": f"Add {singularize(child_name)} to {singularize(parent_tag)}",
            "operationId": f"add_{singularize(parent_tag)}_{singularize(child_name)}",
            "tags": [parent_tag],
            "parameters": [path_param(parent_id)],
            "requestBody": {"required": True, "content": {"application/json": {"schema": {"$ref": f"#/components/schemas/{add_schema}"}}}},
            "responses": {"201": {"description": "Added"}, "404": {"$ref": "#/components/responses/NotFound"}}
        }
    }


def nested_remove(parent_tag: str, parent_id: str, child_name: str, child_id: str) -> dict:
    return {
        "delete": {
            "summary": f"Remove {singularize(child_name)} from {singularize(parent_tag)}",
            "operationId": f"remove_{singularize(parent_tag)}_{singularize(child_name)}",
            "tags": [parent_tag],
            "parameters": [path_param(parent_id), path_param(child_id)],
            "responses": {"204": {"description": "Removed"}, "404": {"$ref": "#/components/responses/NotFound"}}
        }
    }


def interaction_like(post_param: str) -> dict:
    return {
        "post": {"summary": "Like post", "operationId": "like_post", "tags": ["interactions"],
                 "parameters": [path_param(post_param)],
                 "responses": {"201": {"description": "Post liked"}, "409": {"description": "Already liked"}}},
        "delete": {"summary": "Unlike post", "operationId": "unlike_post", "tags": ["interactions"],
                   "parameters": [path_param(post_param)],
                   "responses": {"204": {"description": "Like removed"}}}
    }


def interaction_comments(post_param: str) -> dict:
    return {
        "get": {"summary": "List post comments", "operationId": "list_post_comments", "tags": ["interactions"],
                "parameters": [path_param(post_param), {"$ref": "#/components/parameters/SkipParam"}, {"$ref": "#/components/parameters/LimitParam"}],
                "responses": {"200": {"description": "List of comments", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/PaginatedCommentList"}}}}}},
        "post": {"summary": "Add comment", "operationId": "add_post_comment", "tags": ["interactions"],
                 "parameters": [path_param(post_param)],
                 "requestBody": {"required": True, "content": {"application/json": {"schema": {"$ref": "#/components/schemas/CommentCreate"}}}},
                 "responses": {"201": {"description": "Comment added", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Comment"}}}}}}
    }


def interaction_comment_single(post_param: str, comment_param: str) -> dict:
    return {
        "patch": {"summary": "Update comment", "operationId": "update_post_comment", "tags": ["interactions"],
                  "parameters": [path_param(post_param), path_param(comment_param)],
                  "requestBody": {"required": True, "content": {"application/json": {"schema": {"$ref": "#/components/schemas/CommentCreate"}}}},
                  "responses": {"200": {"description": "Comment updated", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Comment"}}}}}},
        "delete": {"summary": "Delete comment", "operationId": "delete_post_comment", "tags": ["interactions"],
                   "parameters": [path_param(post_param), path_param(comment_param)],
                   "responses": {"204": {"description": "Comment deleted"}}}
    }


def interaction_ratings(post_param: str) -> dict:
    return {
        "get": {"summary": "List post ratings", "operationId": "list_post_ratings", "tags": ["interactions"],
                "parameters": [path_param(post_param), {"$ref": "#/components/parameters/SkipParam"}, {"$ref": "#/components/parameters/LimitParam"}],
                "responses": {"200": {"description": "List of ratings", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/PaginatedRatingList"}}}}}},
        "post": {"summary": "Submit rating", "operationId": "submit_post_rating", "tags": ["interactions"],
                 "parameters": [path_param(post_param)],
                 "requestBody": {"required": True, "content": {"application/json": {"schema": {"$ref": "#/components/schemas/RatingCreate"}}}},
                 "responses": {"201": {"description": "Rating submitted", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Rating"}}}}}}
    }


# === Output ===

def to_yaml(spec: dict) -> str:
    """Convert spec to YAML string."""
    if yaml:
        return yaml.dump(spec, default_flow_style=False, allow_unicode=True, sort_keys=False)
    else:
        return json.dumps(spec, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description="Generate OpenAPI spec from Synnovator schema.md")
    parser.add_argument("--output", "-o", default=".synnovator/openapi.yaml",
                        help="Output file path (default: .synnovator/openapi.yaml)")
    parser.add_argument("--schema", "-s", default=".claude/skills/synnovator/references/schema.md",
                        help="Path to schema.md (default: .claude/skills/synnovator/references/schema.md)")
    parser.add_argument("--title", default="Synnovator API", help="API title")
    parser.add_argument("--version", default="1.0.0", help="API version")
    parser.add_argument("--format", choices=["yaml", "json"], default="yaml", help="Output format")

    args = parser.parse_args()

    # Parse schema.md
    schema_path = Path(args.schema)
    if not schema_path.exists():
        print(f"Error: Schema file not found: {schema_path}")
        print("Trying to find it relative to script location...")
        script_dir = Path(__file__).parent.parent.parent
        schema_path = script_dir / "synnovator" / "references" / "schema.md"
        if not schema_path.exists():
            print(f"Error: Schema file not found: {schema_path}")
            return

    print(f"Reading schema from: {schema_path}")
    schema = parse_schema_md(schema_path)
    print(f"  - Found {len(schema['content_types'])} content types")
    print(f"  - Found {len(schema['relations'])} relation types")
    print(f"  - Found {len(schema['enums'])} enums")

    # Generate spec
    spec = generate_openapi_spec(schema, title=args.title, version=args.version)

    # Write output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        if args.format == "yaml" and yaml:
            f.write(to_yaml(spec))
        else:
            json.dump(spec, f, indent=2, ensure_ascii=False)

    print(f"\nGenerated OpenAPI spec: {output_path}")
    print(f"  - {len(spec['paths'])} endpoints")
    print(f"  - {len(spec['components']['schemas'])} schemas")


if __name__ == "__main__":
    main()
