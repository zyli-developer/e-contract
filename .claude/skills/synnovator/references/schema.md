# Synnovator Data Schema Reference

## Content Types

### event
| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| name | string | yes | — | Activity name |
| description | string | yes | — | Short description |
| type | enum | yes | — | `competition` \| `operation` |
| status | enum | no | `draft` | `draft` \| `published` \| `closed` |
| cover_image | string | no | — | Cover image URL |
| start_date | datetime | no | — | Start time |
| end_date | datetime | no | — | End time |
| id | string | auto | — | Unique ID |
| created_by | user_id | auto | — | Creator |
| created_at | datetime | auto | — | Creation time |
| updated_at | datetime | auto | — | Last update |
| deleted_at | datetime | auto | null | Soft delete timestamp |

### post
| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| title | string | yes | — | Post title |
| type | enum | no | `general` | `profile` \| `team` \| `event` \| `proposal` \| `certificate` \| `general` |
| tags | list[string] | no | [] | Tag list |
| status | enum | no | `draft` | `draft` \| `pending_review` \| `published` \| `rejected` |
| like_count | integer | cache | 0 | Read-only, auto-maintained via `target_interaction` |
| comment_count | integer | cache | 0 | Read-only, auto-maintained via `target_interaction` |
| average_rating | number | cache | null | Read-only, auto-maintained via `target_interaction` |
| id, created_by, created_at, updated_at, deleted_at | — | auto | — | Standard fields |

### resource
| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| filename | string | yes | — | Original filename |
| display_name | string | no | — | Display name |
| description | string | no | — | File description |
| mime_type | string | auto | — | MIME type |
| size | integer | auto | — | File size (bytes) |
| url | string | auto | — | Storage URL |
| id, created_by, created_at, updated_at, deleted_at | — | auto | — | Standard fields |

### rule

Supports two constraint styles: **fixed fields** (syntactic sugar) and **declarative checks** (extensible). See `docs/rule-engine.md`.

| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| name | string | yes | — | Rule name |
| description | string | yes | — | Rule description |
| allow_public | boolean | no | false | Allow public publishing (sugar → `checks`) |
| require_review | boolean | no | false | Require review (sugar → `checks`) |
| reviewers | list[user_id] | no | — | Reviewer list |
| submission_start | datetime | no | — | Submission start (sugar → `time_window` check) |
| submission_deadline | datetime | no | — | Submission deadline (sugar → `time_window` check) |
| submission_format | list[string] | no | — | Allowed formats (sugar → `resource_format` check) |
| max_submissions | integer | no | — | Max submissions per user/team (sugar → `count` check) |
| min_team_size | integer | no | — | Min team size (sugar → `count` check) |
| max_team_size | integer | no | — | Max team size (sugar → `count` check) |
| scoring_criteria | list[object] | no | — | `[{name, weight, description}]` |
| checks | list[object] | no | — | Declarative condition-action rules (see below) |
| id, created_by, created_at, updated_at, deleted_at | — | auto | — | Standard fields |

**checks element schema:**

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| trigger | string | yes | Hook point: `create_relation(event_post)`, `create_relation(group_user)`, `create_relation(event_group)`, `update_content(post.status)`, `update_content(event.status)` |
| phase | enum | yes | `pre` \| `post` |
| condition | object | pre: yes | `{ type: string, params: object }` — see condition types |
| on_fail | enum | no | `deny` (default) \| `warn` \| `flag` |
| action | string | no | Post-phase action: `flag_disqualified` \| `compute_ranking` \| `award_certificate` \| `notify` |
| action_params | object | no | Action-specific parameters |
| message | string | yes | Human-readable message |

**Condition types:** `time_window`, `count`, `exists`, `field_match`, `resource_format`, `resource_required`, `unique_per_scope`, `aggregate`

### user
| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| username | string | yes | — | Unique username |
| email | string | yes | — | Unique email |
| display_name | string | no | — | Display name |
| avatar_url | string | no | — | Avatar URL |
| bio | string | no | — | Bio |
| role | enum | no | `participant` | `participant` \| `organizer` \| `admin` |
| id, created_at, updated_at, deleted_at | — | auto | — | Standard fields |

### group
| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| name | string | yes | — | Group name |
| description | string | no | — | Description |
| visibility | enum | no | `public` | `public` \| `private` |
| max_members | integer | no | — | Max member count |
| require_approval | boolean | no | false | Require join approval |
| id, created_by, created_at, updated_at, deleted_at | — | auto | — | Standard fields |

### interaction
| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| type | enum | yes | — | `like` \| `comment` \| `rating` |
| value | string/object | no | — | Comment text or rating object |
| parent_id | interaction_id | no | — | Parent comment ID (nested replies) |
| id, created_by, created_at, updated_at, deleted_at | — | auto | — | Standard fields |

> **Note:** `interaction` does not store target info. The link between an interaction and its target is maintained exclusively via the `target_interaction` relation (`target_type` + `target_id` + `interaction_id`).

### notification
| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| type | enum | yes | — | `system` \| `activity` \| `team` \| `social` |
| content | string | yes | — | Notification content |
| title | string | no | — | Notification title |
| related_url | string | no | — | Related link |
| is_read | boolean | no | false | Read status |
| user_id | user_id | yes | — | Recipient user |
| id, created_at | — | auto | — | Standard fields (no soft delete) |

> **Note:** Notifications do not support soft delete. Read notifications can be archived via periodic cleanup.

## Relation Types

### event_rule
`event_id` + `rule_id` + optional `priority` (integer, default 0)

### event_post
`event_id` + `post_id` + `relation_type` (`submission` \| `reference`) + auto `created_at`

### event_group
`event_id` + `group_id` + auto `registered_at`

### event_resource
`event_id` + `resource_id` + `display_type` (`banner` \| `attachment` \| `inline`) + optional `position`

### post_post
`source_post_id` + `target_post_id` + `relation_type` (`reference` \| `reply` \| `embed`) + optional `position`

### post_resource
`post_id` + `resource_id` + `display_type` (`attachment` \| `inline`) + optional `position`

### group_user
`group_id` + `user_id` + `role` (`owner` \| `admin` \| `member`) + `status` (`pending` \| `accepted` \| `rejected`) + auto `joined_at`, `status_changed_at`

### group_post
`group_id` + `post_id` + `relation_type` (`team_submission` \| `announcement` \| `reference`) + auto `created_at`

### group_resource
`group_id` + `resource_id` + `access_level` (`read_only` \| `read_write`) + auto `created_at`

### user_user
`source_user_id` + `target_user_id` + `relation_type` (`follow` \| `block`) + auto `created_at`

### event_event
`source_category_id` + `target_category_id` + `relation_type` (`stage` \| `track` \| `prerequisite`) + optional `stage_order` (integer, for stage ordering) + auto `created_at`

### target_interaction
`target_type` + `target_id` + `interaction_id`

## Uniqueness Constraints
- user: `(username)`, `(email)`
- target_interaction (like): `(created_by, target_type, target_id)` — enforced when creating `target_interaction` relation for a `like` interaction
- event_rule: `(event_id, rule_id)`
- event_group: `(event_id, group_id)`
- group_user: `(group_id, user_id)`
- user_user: `(source_user_id, target_user_id, relation_type)`
- event_event: `(source_category_id, target_category_id)`
- **Business rule**: A user can only belong to one group per event — enforced at `event_group` creation by checking all accepted members against other groups in the same event
- **Self-reference**: `user_user` and `event_event` cannot have the same entity as both source and target
- **Block enforcement**: If B blocks A, A cannot follow B
- **Circular dependency**: `event_event` stage/prerequisite chains cannot form cycles
- **Prerequisite enforcement**: `event_group` creation checks all prerequisite events are closed
