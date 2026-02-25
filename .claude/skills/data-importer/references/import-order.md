# Import Order

导入顺序必须遵循外键依赖关系，确保被引用的记录先于引用它的记录导入。

## Phase 1: Independent Content Types

这些类型没有外键依赖，可以首先导入：

1. **user** - 其他内容类型的 `created_by` 引用 user
2. **event** - 活动/竞赛
3. **rule** - 规则定义

## Phase 2: Dependent Content Types

这些类型依赖 Phase 1 的记录：

4. **group** - `created_by` 引用 user
5. **post** - `created_by` 引用 user
6. **resource** - `created_by` 引用 user

## Phase 3: Interactions

7. **interaction** - `created_by` 引用 user，`target_id` 可能引用 post/event/resource

## Phase 4: Relations

这些关系表必须在所有内容类型导入后才能导入：

8. **event_rule** - 引用 event 和 rule
9. **event_post** - 引用 event 和 post
10. **event_group** - 引用 event 和 group
11. **post_post** - 引用 post
12. **post_resource** - 引用 post 和 resource
13. **group_user** - 引用 group 和 user
14. **target_interaction** - 引用 interaction 和目标内容

## Import Strategy

### Batch Import
按类型批量导入所有记录，减少数据库往返次数。

### Error Handling
- 如果单个记录失败，记录错误但继续导入其他记录
- 跳过已存在的记录（基于 ID）
- 外键约束失败时报告详细错误

### Validation
导入前验证：
- 必需字段存在
- 数据类型正确
- 枚举值有效
- 外键引用存在
