# Field Mapping: .synnovator to SQLAlchemy

## Content Types

### event
| .md Field | Database Column | Type | Notes |
|-----------|----------------|------|-------|
| name | name | string | |
| description | description | string | |
| type | type | enum | competition \| operation |
| status | status | enum | draft \| published \| closed |
| cover_image | cover_image | string | URL |
| start_date | start_date | datetime | ISO 8601 |
| end_date | end_date | datetime | ISO 8601 |
| id | id | string | Auto-generated in .md |
| created_by | created_by | string | User ID |
| created_at | created_at | datetime | Auto-generated |
| updated_at | updated_at | datetime | Auto-generated |
| deleted_at | deleted_at | datetime | Null if not deleted |
| _body_ | body | text | Markdown content |

### post
| .md Field | Database Column | Type | Notes |
|-----------|----------------|------|-------|
| title | title | string | |
| type | type | enum | profile \| team \| event \| proposal \| certificate \| general |
| tags | tags | JSON | Array of strings |
| status | status | enum | draft \| pending_review \| published \| rejected |
| like_count | like_count | integer | Cache field |
| comment_count | comment_count | integer | Cache field |
| average_rating | average_rating | float | Cache field |
| id | id | string | |
| created_by | created_by | string | |
| created_at | created_at | datetime | |
| updated_at | updated_at | datetime | |
| deleted_at | deleted_at | datetime | |
| _body_ | body | text | Markdown content |

### resource
| .md Field | Database Column | Type | Notes |
|-----------|----------------|------|-------|
| filename | filename | string | |
| display_name | display_name | string | Optional |
| description | description | string | Optional |
| mime_type | mime_type | string | |
| size | size | integer | Bytes |
| url | url | string | Storage URL |
| id | id | string | |
| created_by | created_by | string | |
| created_at | created_at | datetime | |
| updated_at | updated_at | datetime | |
| deleted_at | deleted_at | datetime | |

### rule
| .md Field | Database Column | Type | Notes |
|-----------|----------------|------|-------|
| name | name | string | |
| description | description | string | |
| allow_public | allow_public | boolean | |
| require_review | require_review | boolean | |
| reviewers | reviewers | JSON | Array of user IDs |
| submission_start | submission_start | datetime | |
| submission_deadline | submission_deadline | datetime | |
| submission_format | submission_format | JSON | Array of strings |
| max_submissions | max_submissions | integer | |
| min_team_size | min_team_size | integer | |
| max_team_size | max_team_size | integer | |
| scoring_criteria | scoring_criteria | JSON | Array of objects |
| id | id | string | |
| created_by | created_by | string | |
| created_at | created_at | datetime | |
| updated_at | updated_at | datetime | |
| deleted_at | deleted_at | datetime | |
| _body_ | body | text | Markdown content |

### user
| .md Field | Database Column | Type | Notes |
|-----------|----------------|------|-------|
| username | username | string | Unique |
| email | email | string | Unique |
| display_name | display_name | string | |
| avatar_url | avatar_url | string | |
| bio | bio | string | |
| role | role | enum | participant \| organizer \| admin |
| id | id | string | |
| created_at | created_at | datetime | |
| updated_at | updated_at | datetime | |
| deleted_at | deleted_at | datetime | |

### group
| .md Field | Database Column | Type | Notes |
|-----------|----------------|------|-------|
| name | name | string | |
| description | description | string | |
| visibility | visibility | enum | public \| private |
| max_members | max_members | integer | |
| require_approval | require_approval | boolean | |
| id | id | string | |
| created_by | created_by | string | |
| created_at | created_at | datetime | |
| updated_at | updated_at | datetime | |
| deleted_at | deleted_at | datetime | |

### interaction
| .md Field | Database Column | Type | Notes |
|-----------|----------------|------|-------|
| type | type | enum | like \| comment \| rating |
| target_type | target_type | enum | post \| event \| resource |
| target_id | target_id | string | |
| value | value | JSON | Comment text or rating object |
| parent_id | parent_id | string | For nested comments |
| id | id | string | |
| created_by | created_by | string | |
| created_at | created_at | datetime | |
| updated_at | updated_at | datetime | |
| deleted_at | deleted_at | datetime | |

## Relation Types

### event_rule
| .md Field | Database Column | Type |
|-----------|----------------|------|
| event_id | event_id | string |
| rule_id | rule_id | string |
| priority | priority | integer |
| created_at | created_at | datetime |

### event_post
| .md Field | Database Column | Type |
|-----------|----------------|------|
| event_id | event_id | string |
| post_id | post_id | string |
| relation_type | relation_type | enum |
| created_at | created_at | datetime |

### event_group
| .md Field | Database Column | Type |
|-----------|----------------|------|
| event_id | event_id | string |
| group_id | group_id | string |
| created_at | created_at | datetime |

### post_post
| .md Field | Database Column | Type |
|-----------|----------------|------|
| from_post_id | from_post_id | string |
| to_post_id | to_post_id | string |
| relation_type | relation_type | enum |
| created_at | created_at | datetime |

### post_resource
| .md Field | Database Column | Type |
|-----------|----------------|------|
| post_id | post_id | string |
| resource_id | resource_id | string |
| created_at | created_at | datetime |

### group_user
| .md Field | Database Column | Type |
|-----------|----------------|------|
| group_id | group_id | string |
| user_id | user_id | string |
| role | role | enum |
| status | status | enum |
| joined_at | joined_at | datetime |

### target_interaction
| .md Field | Database Column | Type |
|-----------|----------------|------|
| target_type | target_type | enum |
| target_id | target_id | string |
| interaction_id | interaction_id | string |
| created_at | created_at | datetime |

## Data Type Conversions

- **datetime**: Parse ISO 8601 strings to datetime objects
- **JSON**: Parse JSON strings or arrays to JSON column type
- **enum**: Validate against allowed values
- **integer/float**: Convert strings to numbers
- **boolean**: Convert "true"/"false" strings to boolean
