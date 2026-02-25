# Synnovator API Endpoints Reference

All operations are executed via the engine script:
```
uv run python .claude/skills/synnovator/scripts/engine.py [OPTIONS] COMMAND TYPE [ARGS]
```

## Global Options
| Option | Description |
|--------|-------------|
| `--data-dir PATH` | Path to project root (default: cwd) |
| `--init` | Initialize `.synnovator/` directories |
| `--user USER_ID` | Set current user context for permissions |

## Content CRUD

### CREATE
```bash
engine.py create <type> --data '<json>' [--body 'markdown content'] [--user <user_id>]
```
Types: `event`, `post`, `resource`, `rule`, `user`, `group`, `interaction`

Markdown body can be passed via `--body` flag or `"_body"` key in JSON data.
Records are stored as `.md` files with YAML frontmatter + Markdown body.

### READ
```bash
# Read single record
engine.py read <type> --id <record_id>
# List with filters
engine.py read <type> --filters '<json>'
# Include soft-deleted
engine.py read <type> --include-deleted
```

### UPDATE
```bash
engine.py update <type> --id <record_id> --data '<json>'
```
Special: for post tags, use `"+tagname"` to append, `"-tagname"` to remove.
Note: `like_count`, `comment_count`, `average_rating` on posts are read-only cache fields — they are silently ignored in update data.

### DELETE
```bash
# Soft delete (default)
engine.py delete <type> --id <record_id>
# Hard delete
engine.py delete <type> --id <record_id> --hard
```

## Relation CRUD

Use `_` separator or `:` separator for relation type names.

### CREATE
```bash
engine.py create <relation_type> --data '<json>'
```
Relation types: `event_rule`, `event_post`, `event_group`, `event_event`, `post_post`, `post_resource`, `group_user`, `user_user`, `target_interaction`

### READ
```bash
engine.py read <relation_type> --filters '<json>'
```

### UPDATE
```bash
engine.py update <relation_type> --filters '<json>' --data '<json>'
```

### DELETE (hard delete)
```bash
engine.py delete <relation_type> --filters '<json>'
```

## Examples

### Create a user
```bash
engine.py create user --data '{"username":"alice","email":"alice@example.com","display_name":"Alice","role":"organizer"}'
```

### Create a event
```bash
engine.py --user user_alice create event --data '{"name":"AI Hackathon","description":"AI competition","type":"competition"}'
```

### Create a rule and link to event
```bash
engine.py --user user_alice create rule --data '{"name":"Submission Rule","description":"Rules for submissions","allow_public":true,"require_review":true,"scoring_criteria":[{"name":"Innovation","weight":30,"description":"Originality"},{"name":"Technical","weight":30,"description":"Code quality"},{"name":"Practical","weight":25,"description":"Usefulness"},{"name":"Demo","weight":15,"description":"Presentation"}]}'

engine.py create event_rule --data '{"event_id":"cat_xxx","rule_id":"rule_xxx","priority":1}'
```

### Create a group and add members
```bash
engine.py --user user_alice create group --data '{"name":"Team Alpha","require_approval":true}'
engine.py create group_user --data '{"group_id":"grp_xxx","user_id":"user_alice","role":"owner"}'
engine.py create group_user --data '{"group_id":"grp_xxx","user_id":"user_bob","role":"member"}'
```

### Approve group member
```bash
engine.py update group_user --filters '{"group_id":"grp_xxx","user_id":"user_bob"}' --data '{"status":"accepted"}'
```

### Create post and link to event
```bash
engine.py --user user_alice create post --data '{"title":"My Submission","type":"proposal","tags":["AI"]}'
engine.py create event_post --data '{"event_id":"cat_xxx","post_id":"post_xxx","relation_type":"submission"}'
```

### Like a post
```bash
# Step 1: Create the interaction record
engine.py --user user_bob create interaction --data '{"type":"like"}'
# Step 2: Link it to the target (triggers cache stats update + duplicate check)
engine.py create target_interaction --data '{"target_type":"post","target_id":"post_xxx","interaction_id":"iact_xxx"}'
```

### Comment on a post
```bash
# Step 1: Create the comment interaction
engine.py --user user_bob create interaction --data '{"type":"comment","value":"Great work!"}'
# Step 2: Link to target
engine.py create target_interaction --data '{"target_type":"post","target_id":"post_xxx","interaction_id":"iact_xxx"}'
```

### Submit a rating
```bash
# Step 1: Create the rating interaction
engine.py --user user_judge create interaction --data '{"type":"rating","value":{"Innovation":87,"Technical":82,"Practical":78,"Demo":91,"_comment":"Well done"}}'
# Step 2: Link to target (triggers average_rating recalculation)
engine.py create target_interaction --data '{"target_type":"post","target_id":"post_xxx","interaction_id":"iact_xxx"}'
```

### Follow a user
```bash
engine.py create user_user --data '{"source_user_id":"user_alice","target_user_id":"user_bob","relation_type":"follow"}'
```

### Block a user
```bash
engine.py create user_user --data '{"source_user_id":"user_alice","target_user_id":"user_bob","relation_type":"block"}'
```

### Unfollow a user
```bash
engine.py delete user_user --filters '{"source_user_id":"user_alice","target_user_id":"user_bob","relation_type":"follow"}'
```

### Check mutual follow (friends)
```bash
# Read A->B follow
engine.py read user_user --filters '{"source_user_id":"user_alice","target_user_id":"user_bob","relation_type":"follow"}'
# Read B->A follow
engine.py read user_user --filters '{"source_user_id":"user_bob","target_user_id":"user_alice","relation_type":"follow"}'
# Both exist = friends
```

### Create activity stage chain
```bash
# Stage 1 -> Stage 2 (sequential)
engine.py create event_event --data '{"source_category_id":"cat_stage1","target_category_id":"cat_stage2","relation_type":"stage","stage_order":1}'
engine.py create event_event --data '{"source_category_id":"cat_stage2","target_category_id":"cat_stage3","relation_type":"stage","stage_order":2}'
```

### Create parallel tracks
```bash
engine.py create event_event --data '{"source_category_id":"cat_main","target_category_id":"cat_track_a","relation_type":"track"}'
engine.py create event_event --data '{"source_category_id":"cat_main","target_category_id":"cat_track_b","relation_type":"track"}'
```

### Set prerequisite activity
```bash
# Bounty must close before main competition registration
engine.py create event_event --data '{"source_category_id":"cat_bounty","target_category_id":"cat_main_competition","relation_type":"prerequisite"}'
```
