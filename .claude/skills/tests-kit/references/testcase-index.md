# Test Case Index

> Auto-generated index of all test cases in `specs/testcases/`.
> Grep pattern to find a TC by ID: `grep -rn "TC-XXX-NNN" specs/testcases/`

## 01-user.md (User)

| TC ID | Description |
|-------|-------------|
| TC-USER-001 | 创建 participant 用户 |
| TC-USER-002 | 创建 organizer 用户 |
| TC-USER-003 | 创建 admin 用户 |
| TC-USER-004 | 读取已创建的用户 |
| TC-USER-010 | 用户修改自己的个人信息 |
| TC-USER-011 | Admin 修改其他用户的角色 |
| TC-USER-020 | 删除用户及级联影响 |
| TC-USER-900 | 重复 username 被拒绝 |
| TC-USER-901 | 重复 email 被拒绝 |
| TC-USER-902 | 非本人/非 Admin 修改用户信息被拒绝 |
| TC-USER-903 | 缺少必填字段 email |

## 02-event.md (Event)

| TC ID | Description |
|-------|-------------|
| TC-CAT-001 | 创建 competition 类型活动 |
| TC-CAT-002 | 创建 operation 类型活动 |
| TC-CAT-003 | 读取已创建的活动 |
| TC-CAT-010 | 活动状态流转 draft → published → closed |
| TC-CAT-011 | 修改活动名称和描述 |
| TC-CAT-020 | 删除活动及级联影响 |
| TC-CAT-900 | 非法 type 枚举被拒绝 |
| TC-CAT-901 | 非法 status 枚举被拒绝 |
| TC-CAT-902 | participant 创建活动被拒绝 |

## 03-rule.md (Rule)

| TC ID | Description |
|-------|-------------|
| TC-RULE-001 | 创建含完整 scoring_criteria 的规则 |
| TC-RULE-002 | 创建 select-only 规则 |
| TC-RULE-003 | 读取已创建的规则 |
| TC-RULE-010 | 修改规则配置字段 |
| TC-RULE-011 | 修改 scoring_criteria 权重 |
| TC-RULE-020 | 删除规则及级联 |
| TC-RULE-100 | 提交截止后创建 event_post 被拒绝 |
| TC-RULE-101 | 提交未开始时创建 event_post 被拒绝 |
| TC-RULE-102 | 超出 max_submissions 后创建 event_post 被拒绝 |
| TC-RULE-103 | 提交格式不符时创建 event_post 被拒绝 |
| TC-RULE-104 | 团队人数不足时创建 event_post 被拒绝 |
| TC-RULE-105 | 团队已满时创建 group_user 被拒绝 |
| TC-RULE-106 | allow_public=false 时直接发布被拒绝 |
| TC-RULE-107 | allow_public=false 时 pending_review 状态被允许 |
| TC-RULE-108 | 无 rule 关联时 event_post 正常创建 |
| TC-RULE-109 | 多条 rule 全部满足才允许（AND 逻辑） |
| TC-RULE-900 | participant 创建规则被拒绝 |
| TC-RULE-901 | scoring_criteria 权重总和不等于 100 |

## 04-group.md (Group)

| TC ID | Description |
|-------|-------------|
| TC-GRP-001 | 创建需审批的公开团队 |
| TC-GRP-002 | 创建无需审批的私有团队 |
| TC-GRP-003 | Owner 自动加入 |
| TC-GRP-004 | 需审批团队 — 成员申请加入为 pending |
| TC-GRP-005 | Owner 批准成员申请 |
| TC-GRP-006 | Owner 拒绝成员申请 |
| TC-GRP-007 | 被拒绝后重新申请 |
| TC-GRP-008 | 无需审批团队 — 成员直接 accepted |
| TC-GRP-010 | Owner 更新团队信息 |
| TC-GRP-011 | 变更审批设置 |
| TC-GRP-012 | 变更可见性 |
| TC-GRP-020 | 删除团队及级联 |
| TC-GRP-900 | 非法 visibility 枚举被拒绝 |
| TC-GRP-901 | 非 Owner/Admin 修改团队信息被拒绝 |

## 05-post.md (Post)

| TC ID | Description |
|-------|-------------|
| TC-POST-001 | 最小字段创建帖子 |
| TC-POST-002 | 显式发布帖子 |
| TC-POST-003 | 带 tags 创建帖子 |
| TC-POST-004 | 按 type 筛选帖子 |
| TC-POST-010 | 创建 team 类型帖子 |
| TC-POST-011 | 创建 profile 类型帖子 |
| TC-POST-012 | 创建 proposal 类型帖子 |
| TC-POST-013 | 创建 certificate 类型帖子 |
| TC-POST-030 | 帖子进入 pending_review 状态 |
| TC-POST-031 | 帖子被审核通过 |
| TC-POST-032 | 帖子被驳回 |
| TC-POST-033 | 草稿发布 |
| TC-POST-040 | 通过新帖子实现版本管理 |
| TC-POST-041 | 发布新版本 |
| TC-POST-050 | 添加标签（+tag 语法） |
| TC-POST-051 | 移除标签（-tag 语法） |
| TC-POST-052 | "选择已有帖子"报名（标签打标） |
| TC-POST-060 | 更新帖子 title 和 Markdown body |
| TC-POST-070 | 创建 visibility=private 的帖子 |
| TC-POST-071 | private 帖子跳过 pending_review 直接发布 |
| TC-POST-072 | private 已发布帖子对非作者不可见 |
| TC-POST-073 | 将 public 帖子改为 private |
| TC-POST-074 | 将 private 帖子改为 public |
| TC-POST-075 | private 帖子的 interaction 对非作者不可见 |
| TC-POST-076 | 默认 visibility 为 public |
| TC-POST-900 | 缺少 title 被拒绝 |
| TC-POST-901 | 非法 type/status 枚举被拒绝 |
| TC-POST-902 | 未登录用户创建帖子被拒绝 |
| TC-POST-903 | 非法 visibility 枚举被拒绝 |

## 06-resource.md (Resource)

| TC ID | Description |
|-------|-------------|
| TC-RES-001 | 最小字段创建资源 |
| TC-RES-002 | 带完整元信息创建资源 |
| TC-RES-030 | 更新资源元信息 |
| TC-RES-031 | 删除资源后级联解除 post:resource |
| TC-RES-040 | 关联到 published + public 帖子的 resource 可被任何人读取 |
| TC-RES-041 | 关联到 draft 帖子的 resource 对非作者不可读 |
| TC-RES-042 | 关联到 private 帖子的 resource 对非作者不可读 |
| TC-RES-043 | 帖子从 public 改为 private 后 resource 不可见性同步变更 |
| TC-RES-044 | resource 同时关联到 public 和 private 帖子时的可见性 |
| TC-RES-045 | 帖子删除后 resource 的可访问性 |
| TC-RES-900 | 缺少 filename 被拒绝 |
| TC-RES-901 | 未登录用户创建资源被拒绝 |
| TC-RES-902 | 引用不存在的 post_id/resource_id 创建关系被拒绝 |
| TC-RES-903 | 非法 display_type 枚举被拒绝 |

## 07-interaction.md (Interaction)

| TC ID | Description |
|-------|-------------|
| TC-IACT-001 | 对帖子点赞 |
| TC-IACT-002 | 重复点赞被拒绝 |
| TC-IACT-003 | 取消点赞后 like_count 递减 |
| TC-IACT-010 | 创建顶层评论 |
| TC-IACT-011 | 创建嵌套回复（一级回复） |
| TC-IACT-012 | 创建二级回复 |
| TC-IACT-013 | comment_count 包含所有层级 |
| TC-IACT-014 | 删除父评论级联删除子回复 |
| TC-IACT-020 | 创建多维度评分 |
| TC-IACT-021 | 多个评分的均值计算 |
| TC-IACT-050 | 修改评论文本 |
| TC-IACT-051 | 修改评分重新打分 |
| TC-IACT-060 | 对 event 点赞 |
| TC-IACT-061 | 对 event 发表评论 |
| TC-IACT-062 | 对 resource 点赞 |
| TC-IACT-063 | 对 resource 发表评论 |
| TC-IACT-900 | 非法 interaction type 被拒绝 |
| TC-IACT-901 | 非法 target_type 被拒绝 |
| TC-IACT-902 | target_id 不存在被拒绝 |
| TC-IACT-903 | 对已删除的帖子点赞被拒绝 |
| TC-IACT-904 | 缺少 target_id 被拒绝 |
| TC-IACT-905 | 非本人修改 interaction 被拒绝 |

## 08-relations.md (Relations)

| TC ID | Description |
|-------|-------------|
| TC-REL-CR-001 | 将规则关联到活动 |
| TC-REL-CR-002 | 更新 event:rule priority |
| TC-REL-CR-003 | 删除 event:rule 关系 |
| TC-REL-CR-900 | 重复关联同一规则到同一活动被拒绝 |
| TC-REL-CP-001 | 将帖子关联为活动的 submission |
| TC-REL-CP-002 | 将帖子关联为活动的 reference |
| TC-REL-CP-003 | 按 relation_type 筛选活动帖子 |
| TC-REL-CP-004 | 不带筛选读取所有 event:post |
| TC-REL-CP-900 | 规则截止后提交 event_post 被拒绝 |
| TC-REL-CP-901 | 格式不符时提交 event_post 被拒绝 |
| TC-REL-CP-902 | 超出 max_submissions 时提交 event_post 被拒绝 |
| TC-REL-CG-001 | 团队报名活动 |
| TC-REL-CG-002 | 读取活动已报名团队列表 |
| TC-REL-CG-003 | 团队取消报名 |
| TC-REL-CG-900 | 重复报名同一活动被拒绝 |
| TC-REL-CG-901 | 同一用户在同一活动中属于多个团队被拒绝 |
| TC-REL-PP-001 | 创建 embed 关系 |
| TC-REL-PP-002 | 创建 reference 关系 |
| TC-REL-PP-003 | 创建 reply 关系 |
| TC-REL-PP-004 | 更新 post:post 关系类型和位置 |
| TC-REL-PP-005 | 删除 post:post 关系 |
| TC-REL-PR-001 | 资源作为 attachment 挂到帖子 |
| TC-REL-PR-002 | 资源作为 inline 挂到帖子 |
| TC-REL-PR-003 | 同一帖子挂多个资源 position 排序 |
| TC-REL-PR-004 | 更新 post:resource display_type |
| TC-REL-PR-005 | 删除 post:resource 关系 |
| TC-REL-GU-001 | 移出团队成员 |
| TC-REL-GU-900 | 已有成员重复加入被拒绝 |
| TC-REL-GU-901 | 创建 group_user 时使用非法 role 枚举 |
| TC-REL-GU-902 | 团队已满时加入被拒绝 |
| TC-REL-TI-001 | 创建 target_interaction 关系 |
| TC-REL-TI-002 | 删除 target:interaction 关系 |

## 09-cascade-delete.md (Cascade Delete)

| TC ID | Description |
|-------|-------------|
| TC-DEL-001 | 删除 event |
| TC-DEL-002 | 删除 rule |
| TC-DEL-003 | 删除 user |
| TC-DEL-004 | 删除 group |
| TC-DEL-005 | 删除 interaction |
| TC-DEL-010 | 删除 event → 关联 interaction 级联硬删除 |
| TC-DEL-011 | 删除 user → interaction + group:user 级联处理 |
| TC-DEL-012 | 删除 post → 完整级联链 |
| TC-DEL-013 | 删除 rule → 级联 event:rule |
| TC-DEL-014 | 删除 group → 级联 event:group |
| TC-DEL-015 | 删除父评论 → 级联删除所有子评论 |
| TC-DEL-020 | 读取已删除记录返回 not found |
| TC-DEL-021 | 已删除记录不可恢复 |
| TC-DEL-022 | 已删除记录无法被更新 |

## 10-permissions.md (Permissions)

| TC ID | Description |
|-------|-------------|
| TC-PERM-001 | participant 创建 event 被拒绝 |
| TC-PERM-002 | participant 创建 rule 被拒绝 |
| TC-PERM-003 | participant 更新 event 被拒绝 |
| TC-PERM-012 | 非本人修改用户信息被拒绝 |
| TC-PERM-013 | 非 Owner 修改团队信息被拒绝 |
| TC-PERM-014 | 非本人修改评论被拒绝 |
| TC-PERM-020 | 访客读取 draft 帖子不可见 |
| TC-PERM-021 | 访客读取 draft 活动不可见 |
| TC-PERM-022 | 非成员读取 private 团队不可见 |
| TC-PERM-023 | 已发布活动下的 draft 帖子在列表中不可见 |
| TC-PERM-024 | 已发布活动下的 private 帖子在列表中不可见 |
| TC-PERM-025 | private 帖子的关联 resource 在活动资源列表中不可见 |

## 11-user-journeys.md (User Journeys)

| TC ID | Description |
|-------|-------------|
| TC-JOUR-002 | 匿名访客浏览公开内容 |
| TC-JOUR-005 | 完整团队加入与审批流程 |
| TC-JOUR-007 | 完整团队报名流程 |
| TC-JOUR-009 | 创建日常帖子和参赛提案 |
| TC-JOUR-010 | 完整证书颁发流程 |
| TC-JOUR-011-1 | 编辑自己的帖子（版本管理） |
| TC-JOUR-011-2 | 编辑他人帖子（副本机制） |
| TC-JOUR-012 | 删除帖子后验证全部级联 |
| TC-JOUR-013 | 完整社区互动流程 |

## 12-resource-transfer.md (Resource Transfer)

| TC ID | Description |
|-------|-------------|
| TC-TRANSFER-001 | 证书资源从组织者帖子转移到参赛帖 |
| TC-TRANSFER-002 | 提案间文件转移 |
| TC-TRANSFER-003 | 资源同时关联多个 post（共享模式） |
| TC-TRANSFER-004 | 转移溯源 |

## 13-user-follow.md (User Follow)

| TC ID | Description |
|-------|-------------|
| TC-FRIEND-001 | 用户 A 关注用户 B |
| TC-FRIEND-002 | 用户 B 回关用户 A 成为好友 |
| TC-FRIEND-003 | 单向关注不构成好友 |
| TC-FRIEND-004 | 取消关注 |
| TC-FRIEND-005 | 拉黑用户 |
| TC-FRIEND-006 | 被拉黑用户无法关注 |
| TC-FRIEND-007 | 删除用户后级联解除 user:user |
| TC-FRIEND-900 | 自己关注自己被拒绝 |
| TC-FRIEND-901 | 重复关注被拒绝 |
| TC-FRIEND-902 | 非法 relation_type 被拒绝 |

## 14-event-association.md (Event Association)

| TC ID | Description |
|-------|-------------|
| TC-STAGE-001 | 创建连续赛段关联 |
| TC-STAGE-002 | 按 stage_order 排序读取赛段 |
| TC-STAGE-003 | 赛段未完成时无法进入下一赛段 |
| TC-STAGE-004 | 赛段完成后可进入下一赛段 |
| TC-TRACK-001 | 创建并行赛道关联 |
| TC-TRACK-002 | 团队可同时参加不同赛道 |
| TC-TRACK-003 | 团队在同一赛道内受 Rule 约束 |
| TC-PREREQ-001 | 悬赏活动作为前置条件关联到常规赛 |
| TC-PREREQ-002 | 前置活动完成后团队可报名目标活动 |
| TC-PREREQ-003 | 前置活动未完成时团队报名目标活动被拒绝 |
| TC-PREREQ-004 | 前置活动中组建的团队保持完整进入目标活动 |
| TC-CATREL-010 | 查看活动关联列表 |
| TC-CATREL-011 | 从关联活动跳转 |
| TC-CATREL-012 | 活动关联双向可见 |
| TC-CATREL-020 | 提案在多个关联活动中独立评审 |
| TC-CATREL-021 | 提案在多个活动中独立获奖 |
| TC-CATTRACK-010 | 常规赛道（X类型）标识展示 |
| TC-CATTRACK-011 | 命题赛道（Y类型）标识展示 |
| TC-CATREL-900 | 重复创建同一活动关联被拒绝 |
| TC-CATREL-901 | 自引用被拒绝 |
| TC-CATREL-902 | 赛段循环依赖被拒绝 |
| TC-CATREL-903 | 非法 relation_type 被拒绝 |
| TC-CATREL-904 | 已关闭活动无法添加关联 |
| TC-CATREL-905 | 非关联活动无法共享提案 |

## 15-entry-rules.md (Entry Rules)

| TC ID | Description |
|-------|-------------|
| TC-ENTRY-001 | 报名前必须已加入团队 |
| TC-ENTRY-002 | 提交前必须已有团队报名 |
| TC-ENTRY-003 | 报名前必须已有 profile 帖子 |
| TC-ENTRY-004 | 已满足前置条件时报名成功 |
| TC-ENTRY-010 | 提交时帖子必须包含至少一个 resource |
| TC-ENTRY-011 | 提交时帖子必须包含指定格式的 resource |
| TC-ENTRY-012 | 帖子包含符合要求的 resource 时提交成功 |
| TC-ENTRY-020 | 一个用户在同一活动中只能有一个参赛提案 |
| TC-ENTRY-021 | 同一用户在同一活动中只能属于一个团队 |
| TC-ENTRY-022 | 不同活动中同一用户可分别提交提案 |
| TC-ENTRY-030 | 固定字段和自定义 checks 同时生效 |
| TC-ENTRY-031 | 固定字段和自定义 checks 均满足时操作成功 |
| TC-ENTRY-900 | checks 中引用不存在的 condition type 被拒绝 |
| TC-ENTRY-901 | checks 缺少必填字段被拒绝 |
| TC-ENTRY-902 | pre 阶段 check 缺少 condition 被拒绝 |

## 16-closure-rules.md (Closure Rules)

| TC ID | Description |
|-------|-------------|
| TC-CLOSE-001 | 活动关闭前校验所有团队人数 |
| TC-CLOSE-002 | 活动关闭前严格校验（deny 模式） |
| TC-CLOSE-010 | 活动关闭后标记不合格团队 |
| TC-CLOSE-011 | 活动关闭后标记不合格提案 |
| TC-CLOSE-012 | 所有团队均合格时无标记 |
| TC-CLOSE-020 | 活动关闭后按 average_rating 计算排名 |
| TC-CLOSE-021 | average_rating 相同时排名并列 |
| TC-CLOSE-022 | 无评分的帖子不参与排名 |
| TC-CLOSE-030 | 活动关闭后自动颁发证书 |
| TC-CLOSE-031 | 无排名结果时不颁发证书 |
| TC-CLOSE-032 | 证书帖子可被获奖者读取 |
| TC-CLOSE-040 | 完整活动结束流程 |
| TC-CLOSE-900 | 非 closed 状态变更不触发关闭 checks |
| TC-CLOSE-901 | 活动无关联 Rule 时关闭不触发任何 check |
| TC-CLOSE-902 | post phase action 失败不回滚活动关闭 |

## 17-rule-engine.md (Rule Engine)

| TC ID | Description |
|-------|-------------|
| TC-ENGINE-001 | time_window 条件 — 开始时间未到 |
| TC-ENGINE-002 | time_window 条件 — 截止时间已过 |
| TC-ENGINE-003 | count 条件 — 计数满足 |
| TC-ENGINE-004 | count 条件 — 计数不满足 |
| TC-ENGINE-005 | exists 条件 — 实体存在时通过 |
| TC-ENGINE-006 | exists 条件 — 实体不存在时拒绝 |
| TC-ENGINE-007 | exists 条件 — require=false 时实体不存在通过 |
| TC-ENGINE-008 | field_match 条件 — 字段匹配 |
| TC-ENGINE-009 | resource_format 条件 — 格式匹配 |
| TC-ENGINE-010 | resource_required 条件 — 数量和格式均满足 |
| TC-ENGINE-011 | aggregate 条件 — 聚合计算满足 |
| TC-ENGINE-020 | 固定字段自动展开为 checks |
| TC-ENGINE-021 | 固定字段展开的 check 排在自定义 checks 之前 |
| TC-ENGINE-022 | 纯 checks 定义（无固定字段） |
| TC-ENGINE-030 | 多 Rule 的 checks 合并后 AND 逻辑执行 |
| TC-ENGINE-031 | 多 Rule 中一条有 checks 一条只有固定字段 |
| TC-ENGINE-040 | post phase check 在操作成功后执行 |
| TC-ENGINE-041 | post phase check 条件不满足时 action 不执行 |
| TC-ENGINE-042 | post phase check 失败不回滚主操作 |
| TC-ENGINE-050 | on_fail=deny 时操作被拒绝 |
| TC-ENGINE-051 | on_fail=warn 时操作允许但返回警告 |
| TC-ENGINE-052 | on_fail=flag 时操作允许并标记 |
| TC-ENGINE-060 | Rule 无固定字段且 checks 为空数组 |
| TC-ENGINE-061 | 活动未关联任何 Rule |

## 18-content-browsing.md (Content Browsing)

| TC ID | Description |
|-------|-------------|
| TC-BROWSE-001 | 浏览首页热门内容 |
| TC-BROWSE-002 | 浏览探索页发现内容 |
| TC-BROWSE-003 | 点击热点榜跳转帖子 |
| TC-BROWSE-010 | 按标签筛选帖子 |
| TC-BROWSE-011 | 按内容类型筛选帖子 |
| TC-BROWSE-012 | 关键词搜索内容 |
| TC-BROWSE-013 | 组合筛选条件 |
| TC-BROWSE-020 | 查看活动详情 |
| TC-BROWSE-021 | 查看帖子详情 |
| TC-BROWSE-022 | 查看参赛提案详情 |
| TC-BROWSE-030 | 点击作者进入个人主页 |
| TC-BROWSE-031 | 点击团队进入团队主页 |
| TC-BROWSE-032 | 在团队页面查看队友信息 |
| TC-BROWSE-040 | 通过左侧导航栏跳转页面 |
| TC-BROWSE-041 | 点击帮助支持入口 |
| TC-BROWSE-050 | 登录完成后返回原页面 |
| TC-BROWSE-051 | 登录后内容展示增强 |
| TC-BROWSE-900 | 访问不存在的内容返回 404 |
| TC-BROWSE-901 | 访问已删除内容返回 404 |

## 19-auth-profile.md (Auth & Profile)

| TC ID | Description |
|-------|-------------|
| TC-AUTH-001 | 手机号密码注册 |
| TC-AUTH-002 | 邮箱密码注册 |
| TC-AUTH-003 | 手机验证码注册 |
| TC-AUTH-010 | 账号密码登录 |
| TC-AUTH-011 | 手机验证码登录 |
| TC-AUTH-012 | 忘记密码 — 手机号找回 |
| TC-AUTH-013 | 忘记密码 — 邮箱找回 |
| TC-PROFILE-001 | 创建个人简介 |
| TC-PROFILE-002 | 更新个人简介 |
| TC-PROFILE-003 | 更改头像 |
| TC-PROFILE-004 | 更改显示名称 |
| TC-PROFILE-010 | 填写职业信息 |
| TC-PROFILE-011 | 填写学校信息 |
| TC-PROFILE-012 | 填写兴趣爱好 |
| TC-PROFILE-013 | 填写性格标签 |
| TC-PROFILE-014 | 活动中收集的信息自动展示 |
| TC-PROFILE-020 | 添加社交媒体链接 |
| TC-PROFILE-021 | 更新社交媒体链接 |
| TC-PROFILE-022 | 删除社交媒体链接 |
| TC-AUTH-900 | 重复手机号注册被拒绝 |
| TC-AUTH-902 | 密码格式不符被拒绝 |
| TC-AUTH-903 | 验证码过期被拒绝 |
| TC-AUTH-904 | 错误密码登录被拒绝 |
| TC-AUTH-905 | 不存在的账号登录被拒绝 |

## 20-notification.md (Notification)

| TC ID | Description |
|-------|-------------|
| TC-NOTIF-001 | 点击通知图标查看通知列表 |
| TC-NOTIF-002 | 未读通知标记展示 |
| TC-NOTIF-003 | 标记单条通知为已读 |
| TC-NOTIF-004 | 标记全部通知为已读 |
| TC-NOTIF-010 | 点击通知跳转到对应页面 |
| TC-NOTIF-011 | 团队申请通知跳转 |
| TC-NOTIF-012 | 评论回复通知跳转 |
| TC-NOTIF-013 | 活动状态变更通知跳转 |
| TC-NOTIF-020 | 在通知中心批准团队申请 |
| TC-NOTIF-021 | 在通知中心拒绝团队申请 |
| TC-NOTIF-022 | 在通知中心接受团队邀请 |
| TC-NOTIF-023 | 在通知中心拒绝团队邀请 |
| TC-NOTIF-030 | 接收点赞通知 |
| TC-NOTIF-031 | 接收评论通知 |
| TC-NOTIF-032 | 接收关注通知 |
| TC-NOTIF-033 | 接收系统公告通知 |
| TC-NOTIF-900 | 访问不存在的通知返回错误 |
| TC-NOTIF-901 | 非本人通知不可操作 |

## 21-event-management.md (Event Management)

| TC ID | Description |
|-------|-------------|
| TC-CATMGMT-001 | 发起常规赛道活动（X 类型） |
| TC-CATMGMT-002 | 发起企业命题活动（Y 类型） |
| TC-CATMGMT-003 | 发起悬赏组队活动（Y 类型） |
| TC-CATMGMT-004 | 创建运营活动 |
| TC-CATMGMT-010 | 编写活动说明 |
| TC-CATMGMT-011 | 设定活动规则 — 时间限制 |
| TC-CATMGMT-012 | 设定活动规则 — 团队要求 |
| TC-CATMGMT-013 | 设定活动规则 — 提交要求 |
| TC-CATMGMT-014 | 设定活动规则 — 内容审核 |
| TC-CATMGMT-015 | 设定评分标准 |
| TC-CATMGMT-020 | 发布活动 — draft 到 published |
| TC-CATMGMT-021 | 关闭活动 — published 到 closed |
| TC-CATMGMT-022 | 修改已发布活动需创建新版本 |
| TC-CATMGMT-030 | 设置活动审核人员 |
| TC-CATMGMT-031 | 审核人员审核提交内容 |
| TC-CATMGMT-032 | 评委对参赛内容打分 |
| TC-CATMGMT-050 | 组织者配置报名表单字段 |
| TC-CATMGMT-051 | 配置必填与选填字段 |
| TC-CATMGMT-052 | 配置字段类型 |
| TC-CATMGMT-053 | 报名时用户填写自定义字段 |
| TC-CATMGMT-054 | 预览报名表单 |
| TC-CATMGMT-042 | 一个提案参加多个关联活动 |
| TC-CATMGMT-901 | closed 状态活动不可修改 |
| TC-CATMGMT-903 | 活动结束时间早于开始时间被拒绝 |
| TC-CATMGMT-904 | 报名时必填字段缺失被拒绝 |

## 22-team-management.md (Team Management)

| TC ID | Description |
|-------|-------------|
| TC-TEAM-001 | 创建团队并成为 Owner |
| TC-TEAM-002 | 创建团队并添加团队简介 |
| TC-TEAM-010 | 关联个人提案为团队提案 |
| TC-TEAM-011 | 向团队提案添加个人资产 |
| TC-TEAM-012 | 非作者无法编辑他人资产 |
| TC-TEAM-013 | 申请复制他人资产 |
| TC-TEAM-020 | 搜索并邀请成员 |
| TC-TEAM-021 | 被邀请成员接受邀请 |
| TC-TEAM-022 | 被邀请成员拒绝邀请 |
| TC-TEAM-030 | 成员主动退出团队 |
| TC-TEAM-031 | 队长移除成员 |
| TC-TEAM-032 | 离开团队后资产解除关联 |
| TC-TEAM-033 | 离开团队后无法使用团队资产 |
| TC-TEAM-902 | 非 Owner 移除成员被拒绝 |
| TC-TEAM-903 | Owner 无法退出团队 |

## 23-activity-participation.md (Activity Participation)

| TC ID | Description |
|-------|-------------|
| TC-PART-001 | 选择团队和提案报名活动 |
| TC-PART-002 | 报名时执行规则约束校验 |
| TC-PART-003 | 规则校验不满足时拒绝报名 |
| TC-PART-010 | 新建参赛作品帖 |
| TC-PART-011 | 选择已有作品关联活动 |
| TC-PART-012 | 报名成功自动打标 |
| TC-PART-020 | 上传演示视频 |
| TC-PART-021 | 上传文档资源 |
| TC-PART-022 | 上传代码包 |
| TC-PART-023 | 资源关联指定显示方式 |
| TC-PART-900 | 未加入团队时个人报名被拒绝 |
| TC-PART-903 | 未登录用户报名被拒绝 |

## 24-content-creation.md (Content Creation)

| TC ID | Description |
|-------|-------------|
| TC-CREATE-001 | 通过 MD 编辑器创建文档资产 |
| TC-CREATE-002 | 同步 ELF 内容创建资产 |
| TC-CREATE-003 | 本地上传文件创建资产 |
| TC-CREATE-010 | 使用资产发布帖子 |
| TC-CREATE-011 | 发布日常帖子 |
| TC-CREATE-020 | 发布提案并创建新资产 |
| TC-CREATE-021 | 发布提案并放入已有资产 |
| TC-CREATE-022 | 提案关联活动 |
| TC-CREATE-040 | 编辑自己的帖子 |
| TC-CREATE-041 | 编辑提案标题和简介 |
| TC-CREATE-042 | 编辑提案中的资产 |
| TC-CREATE-043 | 在提案内创建并关联新资产 |
| TC-CREATE-051 | 编辑提案产生新版本 |
| TC-CREATE-052 | 查看历史版本 |
| TC-CREATE-060 | 请求协作编辑他人帖子 |
| TC-CREATE-061 | 接受协作编辑请求 |
| TC-CREATE-062 | 协作者创建编辑副本 |
| TC-CREATE-070 | 删除帖子（软删除） |
| TC-CREATE-071 | 删除评论 |
| TC-CREATE-072 | 删除资源 |
| TC-CREATE-900 | 非本人编辑帖子被拒绝 |
| TC-CREATE-901 | 已删除内容无法编辑 |
| TC-CREATE-903 | 缺少必填字段被拒绝 |

## 25-social-interaction.md (Social Interaction)

| TC ID | Description |
|-------|-------------|
| TC-SOCIAL-012 | 删除评论 |
| TC-SOCIAL-021 | 查看评分详情 |
| TC-SOCIAL-040 | 关注提案 |
| TC-SOCIAL-041 | 关注团队 |
| TC-SOCIAL-042 | 取消内容关注 |
| TC-SOCIAL-050 | 分享活动 |
| TC-SOCIAL-051 | 分享帖子 |
| TC-SOCIAL-052 | 分享通知 |
| TC-SOCIAL-903 | 非本人删除评论被拒绝 |
| TC-SOCIAL-905 | 评分权重不符规则被拒绝 |

## 26-settlement-reward.md (Settlement & Reward)

| TC ID | Description |
|-------|-------------|
| TC-SETTLE-001 | 查看评审结果 |
| TC-SETTLE-002 | 查看排名详情 |
| TC-SETTLE-010 | 领取电子证书 |
| TC-SETTLE-011 | 下载电子证书 |
| TC-SETTLE-012 | 证书自动关联到参赛作品 |
| TC-SETTLE-013 | 分享证书成就 |
| TC-SETTLE-020 | 下载官方资料 |
| TC-SETTLE-021 | 下载他人公开分享资源 |
| TC-SETTLE-030 | 完成运营活动获得资产奖励 |
| TC-SETTLE-031 | 运营活动与比赛活动绑定 |
| TC-SETTLE-040 | 获得勋章资产 |
| TC-SETTLE-041 | 使用勋章投票 |
| TC-SETTLE-042 | 投票活动开启 |
| TC-SETTLE-043 | 勋章限制投票生效 |
| TC-SETTLE-900 | 活动未关闭时无法查看最终排名 |
| TC-SETTLE-901 | 非获奖者无法领取证书 |
| TC-SETTLE-902 | 无效勋章投票被拒绝 |
| TC-SETTLE-903 | 重复投票被拒绝 |

## 27-bounty-enterprise.md (Bounty & Enterprise)

| TC ID | Description |
|-------|-------------|
| TC-BOUNTY-001 | 发布悬赏活动 |
| TC-BOUNTY-002 | 承接悬赏 |
| TC-BOUNTY-003 | 悬赏活动提案互不可见 |
| TC-BOUNTY-010 | 创建第一阶段悬赏活动 |
| TC-BOUNTY-011 | 第一阶段结束选择优秀提案 |
| TC-BOUNTY-012 | 创建第二阶段关联活动 |
| TC-BOUNTY-013 | 晋级用户自动加入新团队 |
| TC-BOUNTY-014 | 悬赏方共享详细需求 |
| TC-BOUNTY-015 | 最终确认成果发放奖励 |
| TC-BOUNTY-016 | 发放阶段性奖励资源 |
| TC-BOUNTY-017 | 团队成员基于详细需求工作 |
| TC-ENTERPRISE-001 | 发布企业出题活动 |
| TC-ENTERPRISE-002 | 企业出题提案互不可见 |
| TC-ENTERPRISE-010 | 创建第一阶段企业出题活动 |
| TC-ENTERPRISE-011 | 第一阶段评审选出优秀提案 |
| TC-ENTERPRISE-012 | 创建第二阶段关联活动 |
| TC-ENTERPRISE-013 | 企业方发送进阶信息到用户资产 |
| TC-ENTERPRISE-014 | 后续阶段确认需求与成果 |
| TC-VISIBLE-001 | 悬赏活动中参赛者提案对其他参赛者不可见 |
| TC-VISIBLE-002 | 企业出题活动中参赛者提案对其他参赛者不可见 |
| TC-VISIBLE-003 | 悬赏方可查看所有提案 |
| TC-VISIBLE-004 | 企业方可查看所有提案 |
| TC-VISIBLE-005 | 评委可查看分配给自己的提案 |
| TC-VISIBLE-006 | 活动结束后提案可见性变更 |
| TC-BOUNTY-901 | 非悬赏方无法选择晋级提案 |
| TC-BOUNTY-902 | 第一阶段未关闭无法选择晋级 |
| TC-ENTERPRISE-900 | 非企业方无法发送资产到用户 |
| TC-ENTERPRISE-901 | 参赛者尝试查看其他参赛者提案被拒绝 |

## 28-personalization.md (Personalization)

| TC ID | Description |
|-------|-------------|
| TC-PERSONAL-001 | 基本个人信息在主页展示 |
| TC-PERSONAL-002 | 显示名称展示 |
| TC-PERSONAL-010 | 更改头像 — 上传图片 |
| TC-PERSONAL-011 | 更改头像 — 选择预设 |
| TC-PERSONAL-030 | 填写职业信息 |
| TC-PERSONAL-031 | 填写学校信息 |
| TC-PERSONAL-032 | 填写性格标签 |
| TC-PERSONAL-033 | 填写兴趣爱好 |
| TC-PERSONAL-034 | 活动收集信息自动展示 |
| TC-PERSONAL-040 | 添加社交媒体链接 |
| TC-PERSONAL-041 | 更新社交媒体链接 |
| TC-PERSONAL-042 | 删除社交媒体链接 |
| TC-PERSONAL-043 | 点击社交媒体链接跳转 |
| TC-PERSONAL-050 | 活动收集信息聚合到个人主页 |
| TC-PERSONAL-051 | 设置单项信息为公开可见 |
| TC-PERSONAL-052 | 设置单项信息为仅自己可见 |
| TC-PERSONAL-053 | 批量设置信息可见性 |
| TC-PERSONAL-054 | 新收集信息的默认可见性 |
| TC-PERSONAL-055 | 团队主页聚合成员公开信息 |
| TC-PERSONAL-056 | 访客只能查看公开信息 |
| TC-PERSONAL-900 | 头像格式不支持被拒绝 |
| TC-PERSONAL-901 | 头像尺寸过大被拒绝 |
| TC-PERSONAL-902 | 社交媒体链接格式无效被拒绝 |
| TC-PERSONAL-903 | 未授权信息不展示在主页 |

## 29-planet-camp.md (Planet & Camp)

| TC ID | Description |
|-------|-------------|
| TC-PLANET-001 | 访问星球页面 |
| TC-PLANET-002 | 按进行中状态筛选活动 |
| TC-PLANET-003 | 按已结束状态筛选活动 |
| TC-PLANET-004 | 按关联活动筛选 |
| TC-PLANET-005 | 按活动类型筛选 |
| TC-PLANET-006 | 按时间范围筛选活动 |
| TC-PLANET-007 | 组合多条件筛选活动 |
| TC-CAMP-001 | 访问营地页面 |
| TC-CAMP-010 | 查看个人提案列表 |
| TC-CAMP-011 | 查看团队提案列表 |
| TC-CAMP-012 | 查看参加的团队列表 |
| TC-CAMP-020 | 筛选个人提案 |
| TC-CAMP-021 | 筛选团队提案 |
| TC-CAMP-022 | 筛选团队 |
| TC-NAV-001 | 从星球页面进入活动详情 |
| TC-NAV-002 | 从营地页面进入提案详情 |
| TC-NAV-003 | 从营地页面进入团队详情 |
| TC-NAV-004 | 星球和营地页面切换 |
| TC-PLANET-900 | 未登录用户访问营地页面 |
| TC-PLANET-901 | 无任何提案时营地页面展示空状态 |
| TC-PLANET-902 | 无任何团队时营地页面展示空状态 |

## 30-proposal-iteration.md (Proposal Iteration)

| TC ID | Description |
|-------|-------------|
| TC-PROPOSAL-001 | 编辑提案内资产并保存 |
| TC-PROPOSAL-002 | 多次更新后统一发布 |
| TC-PROPOSAL-003 | 保存资产同步更新关联资产 |
| TC-PROPOSAL-010 | 提案发布产生新版本号 |
| TC-PROPOSAL-011 | 系统自动生成迭代日志 |
| TC-PROPOSAL-012 | 迭代日志不可被用户更改 |
| TC-PROPOSAL-013 | 迭代日志展示在提案页面 |
| TC-PROPOSAL-020 | 查看任意两个版本的差异 |
| TC-PROPOSAL-021 | 查看单个版本的完整快照 |
| TC-PROPOSAL-900 | 未保存直接关闭编辑器 |
| TC-PROPOSAL-901 | 空更新发布被提示 |
| TC-PROPOSAL-902 | 已删除提案无法查看版本历史 |

## 31-page-interaction.md (Page Interaction)

| TC ID | Description |
|-------|-------------|
| TC-PAGEUI-001 | 点击搜索栏展开搜索界面 |
| TC-PAGEUI-002 | 输入关键词实时搜索 |
| TC-PAGEUI-003 | 搜索历史记录 |
| TC-PAGEUI-004 | 清除搜索历史 |
| TC-PAGEUI-010 | 导航栏当前位置高亮 |
| TC-PAGEUI-011 | 资产页导航入口 |
| TC-PAGEUI-020 | 右侧栏常态显示日历 |
| TC-PAGEUI-021 | 右侧栏常态显示热度榜 |
| TC-PAGEUI-022 | 点击消息展示通知页面 |
| TC-PAGEUI-023 | 点击发布展示发布页面 |
| TC-PAGEUI-024 | 多功能栏状态可切换 |
| TC-PAGEUI-025 | 消息图标显示未读数量 |
| TC-PAGEUI-900 | 未登录用户无法访问资产页面 |
| TC-PAGEUI-901 | 搜索无结果展示空状态 |

## 32-asset-copy-request.md (Asset Copy Request)

| TC ID | Description |
|-------|-------------|
| TC-ASSETCOPY-001 | 在团队提案中查看他人资产 |
| TC-ASSETCOPY-002 | 发起资产复制申请 |
| TC-ASSETCOPY-003 | 资产作者收到复制申请通知 |
| TC-ASSETCOPY-004 | 资产作者批准复制申请 |
| TC-ASSETCOPY-005 | 资产作者拒绝复制申请 |
| TC-ASSETCOPY-006 | 申请人获得资产副本 |
| TC-ASSETCOPY-010 | 副本与原资产独立 |
| TC-ASSETCOPY-011 | 副本可关联到其他提案 |
| TC-ASSETCOPY-012 | 副本保留来源溯源 |
| TC-ASSETCOPY-900 | 重复申请被拒绝 |
| TC-ASSETCOPY-901 | 自己资产无法申请复制 |
| TC-ASSETCOPY-902 | 已删除资产无法申请复制 |
| TC-ASSETCOPY-903 | 非团队成员无法申请团队提案内资产 |

## 33-frontend-integration.md (Frontend Integration) ⭐ 新增

> 验证前端表单与后端 API 的集成链路

| TC ID | Description |
|-------|-------------|
| TC-FEINT-001 | 前端创建日常帖子调用后端 API |
| TC-FEINT-002 | 前端保存帖子草稿调用后端 API |
| TC-FEINT-003 | 前端创建提案调用后端 API |
| TC-FEINT-004 | 前端创建帖子失败显示错误 |
| TC-FEINT-005 | 前端创建帖子时 API 返回错误 |
| TC-FEINT-010 | 前端创建团队调用后端 API |
| TC-FEINT-011 | 前端创建团队失败显示错误 |
| TC-FEINT-012 | 前端创建私有团队调用后端 API |
| TC-FEINT-020 | 前端创建活动调用后端 API |
| TC-FEINT-021 | 非组织者无法访问活动创建页 |
| TC-FEINT-030 | 前端登录调用后端 API |
| TC-FEINT-031 | 前端注册调用后端 API |
| TC-FEINT-032 | 前端登录失败显示错误 |
| TC-FEINT-040 | 前端编辑帖子调用后端 API |
| TC-FEINT-041 | 前端编辑团队信息调用后端 API |
| TC-FEINT-050 | 前端删除帖子调用后端 API |
| TC-FEINT-051 | 前端删除团队调用后端 API |
| TC-FEINT-090 | api-client.ts 包含所有 CRUD 方法 |
| TC-FEINT-091 | 前端创建页面无 TODO 遗留 |
| TC-FEINT-900 | 未登录用户创建帖子被拦截 |
| TC-FEINT-901 | API 客户端网络错误处理 |
| TC-FEINT-902 | 重复提交防护 |
