# Frontend-API 对接文档

## 概览

所有页面组件位于 `frontend/components/pages/`，当前均为硬编码 mock 数据，无 API 客户端层。本文档梳理各页面组件中需要替换为 API 调用的具体位置。

API 规范参考：`.synnovator/openapi.yaml`

---

## 1. 基础设施（需新建）

| 模块 | 说明 |
|------|------|
| `lib/api-client.ts` | 统一的 fetch 封装，base URL、错误处理、token 注入 |
| `lib/types.ts` | 从 OpenAPI schema 生成的 TypeScript 类型 |
| `hooks/use-*.ts` | 各资源的数据获取 hooks（SWR / React Query / Server Components） |

---

## 2. 全局公共部分（Header）

所有页面的 `<header>` 区域共享以下 API 需求：

| UI 元素 | 位置（各文件中均有） | API 端点 | 说明 |
|---------|---------------------|---------|------|
| 用户头像 Avatar | 各文件 `<Avatar>` 组件 | `GET /users/me` | 获取 `avatar_url`, `display_name` |
| 通知铃铛 Bell | 各文件 `<Bell>` 图标 | 无端点（API 缺口） | 需新增通知 API |
| 搜索框 | 各文件搜索栏 | 无端点（API 缺口） | 需新增搜索 API |

---

## 3. home.tsx — 首页

**文件**: `components/pages/home.tsx`

| Mock 数据 / UI 区域 | 行号 | 变量/元素 | API 端点 | 对应 Schema |
|---------------------|------|----------|---------|------------|
| 精选内容卡片 | L17-33 | `const cards = [...]` | `GET /posts?status=published&limit=6` | `Post` -> `title`, `created_by` + `GET /users/{id}` 获取 author |
| 卡片封面图 | L22,27,32 | `card.image` | 帖子关联资源 `GET /posts/{id}/resources` | `Resource` -> `url` |
| 卡片作者头像 | L137 | `<div className="w-[18px]...bg-[#555555]" />` | `GET /users/{id}` | `User` -> `avatar_url` |
| 热门提案列表 | L35-50 | `const proposals = [...]` | `GET /posts?type=proposal&limit=4` | `Post` -> `title`, `content` |
| 提案作者 | L39,47 | `prop.author`, `prop.avatarColor` | `GET /users/{id}` | `User` -> `display_name`, `avatar_url` |
| 分类导航 tabs | L15 | `const tabs = [...]` | `GET /events?limit=10` | `Event` -> `name` |

---

## 4. post-list.tsx — 帖子列表

**文件**: `components/pages/post-list.tsx`

| Mock 数据 / UI 区域 | 行号 | 变量/元素 | API 端点 | 对应 Schema |
|---------------------|------|----------|---------|------------|
| 找队友卡片 | L12-17 | `const teamCards = [...]` | `GET /posts?type=team&limit=8` | `Post` -> `title` |
| 找点子卡片 | L19-24 | `const ideaCards = [...]` | `GET /posts?type=general&limit=8` | `Post` -> `title` |
| 卡片封面图 | L13-16, L20-23 | `card.image` | `GET /posts/{id}/resources` | `Resource` -> `url` |
| 卡片作者名 | L98 | `card.name` | `GET /users/{id}` | `User` -> `display_name` |
| 作者头像 | L97 | `<div className="w-6 h-6 rounded-full bg-[#555555]" />` | `GET /users/{id}` | `User` -> `avatar_url` |
| 主导航 tabs | L10 | `const mainTabs = [...]` | 静态（硬编码即可） | -- |

---

## 5. post-detail.tsx — 帖子详情

**文件**: `components/pages/post-detail.tsx`

| Mock 数据 / UI 区域 | 行号 | 变量/元素 | API 端点 | 对应 Schema |
|---------------------|------|----------|---------|------------|
| 作者信息行 | L78-82 | `"LIGHTNING鲸"`, `"Alibaba team"` | `GET /users/{user_id}` | `User` -> `display_name`, `bio` |
| 作者头像 | L78 | `<div className="w-10 h-10 rounded-full bg-[var(--nf-dark-bg)]" />` | `GET /users/{user_id}` | `User` -> `avatar_url` |
| 点赞数 | L87 | `234` (hardcoded) | `GET /posts/{post_id}` | `Post` -> `like_count` |
| 帖子标题 | L95-97 | `"帖子名帖子名..."` | `GET /posts/{post_id}` | `Post` -> `title` |
| 标签 | L14 | `const tags = [...]` | `GET /posts/{post_id}` | `Post` -> `tags` |
| 关联卡片 | L109-128 | 硬编码的 2 张卡片 | `GET /posts/{post_id}/related` | `Post[]` |
| 内容详情 | L137-140 | 硬编码文本 | `GET /posts/{post_id}` | `Post` -> `content`（Markdown） |
| 热点榜 | L16-27 | `const hotItems = [...]` | `GET /posts?status=published&limit=10` 按热度排序 | `Post` -> `title`, `like_count` |
| 点赞操作 | L86 | `<Heart>` 图标按钮 | `POST /posts/{post_id}/like` | -- |
| 评论区（未实现） | -- | 未在当前组件中 | `GET /posts/{post_id}/comments` | `Comment[]` |
| 评分（未实现） | -- | 未在当前组件中 | `GET /posts/{post_id}/ratings` | `Rating[]` |

---

## 6. proposal-list.tsx — 提案列表

**文件**: `components/pages/proposal-list.tsx`

| Mock 数据 / UI 区域 | 行号 | 变量/元素 | API 端点 | 对应 Schema |
|---------------------|------|----------|---------|------------|
| 提案卡片 | L14-43 | `const proposals = [...]` | `GET /posts?type=proposal` 或 `GET /events/{id}/posts?relation_type=submission` | `Post` -> `title` |
| 卡片封面 | L21,28,34,41 | `prop.image` | `GET /posts/{id}/resources` | `Resource` -> `url` |
| 作者信息 | L18-20, L25-27 | `prop.author`, `prop.avatarColor` | `GET /users/{id}` | `User` -> `display_name`, `avatar_url` |
| 赛道筛选栏 | L100-108 | `"赛道探索"`, `"热门"`, `"最新"` | `GET /events` | `Event[]` -> `name` |
| 导航 tabs | L12 | `const tabs = [...]` | 静态 | -- |

---

## 7. proposal-detail.tsx — 提案详情

**文件**: `components/pages/proposal-detail.tsx`

| Mock 数据 / UI 区域 | 行号 | 变量/元素 | API 端点 | 对应 Schema |
|---------------------|------|----------|---------|------------|
| 提案标题 | L128 | `"善意百宝——..."` | `GET /posts/{post_id}` | `Post` -> `title` |
| 作者信息 | L132-138 | `"LIGHTNING鲸"`, `"Alibaba team"` | `GET /users/{user_id}` | `User` -> `display_name`, `bio` |
| 浏览/点赞/评论数 | L141-153 | `"1.2k"`, `"234"`, `"56"` | `GET /posts/{post_id}` | `Post` -> `like_count`, `comment_count` |
| 标签 | L158-168 | 硬编码 Badge | `GET /posts/{post_id}` | `Post` -> `tags` |
| 项目概述内容 | L192-193 | 硬编码文本段落 | `GET /posts/{post_id}` | `Post` -> `content`（Markdown 解析） |
| 核心功能 | L17-33 | `const features = [...]` | `GET /posts/{post_id}` | `Post` -> `content` 内解析 |
| 技术架构 | L35-41 | `const techStack = [...]` | `GET /posts/{post_id}` | `Post` -> `content` 内解析 |
| 市场分析数据 | L243-256 | `"$340B"`, `"23.4%"`, `"1.5亿"` | `GET /posts/{post_id}` | `Post` -> `content` 内解析 |
| 团队信息卡片 | L43-49 | `const teamMembers = [...]` | `GET /posts/{post_id}/related?relation_type=reference` + `GET /groups/{group_id}/members` | `Member[]`, `User[]` |
| 相关提案 | L51-62 | `const relatedProposals = [...]` | `GET /posts/{post_id}/related` | `Post[]` |
| 里程碑 | L64-70 | `const milestones = [...]` | `GET /posts/{post_id}` | `Post` -> `content` 内解析 |
| Tab: 团队信息 | L265-269 | placeholder `"团队信息内容区域"` | `GET /groups/{group_id}` + `GET /groups/{group_id}/members` | `Group`, `Member[]` |
| Tab: 评论区 | L271-275 | placeholder `"评论区内容区域"` | `GET /posts/{post_id}/comments` | `Comment[]` |
| Tab: 版本历史 | L277-281 | placeholder `"版本历史内容区域"` | 无端点（API 缺口） | 需新增版本历史 API |
| 点赞操作 | L145-148 | `<Heart>` 图标 | `POST /posts/{post_id}/like` | -- |

---

## 8. event-detail.tsx — 赛事详情

**文件**: `components/pages/event-detail.tsx`

| Mock 数据 / UI 区域 | 行号 | 变量/元素 | API 端点 | 对应 Schema |
|---------------------|------|----------|---------|------------|
| 赛事封面图 | L62-64 | `<div ... bg-[var(--nf-dark-bg)]" />` | `GET /events/{event_id}` | `Event` -> `cover_image` |
| 赛事名称 | L66-68 | `"西建·滇水源 \| 上海..."` | `GET /events/{event_id}` | `Event` -> `name` |
| 奖金金额 | L73 | `"880万元"` | `GET /events/{event_id}` | `Event` -> `content` 内解析 |
| 日期 | L75-78 | `"2025/01/28"` 等 | `GET /events/{event_id}` | `Event` -> `start_date`, `end_date` |
| 组织者标签 | L79-81 | `"LIGHTNING鲸"` | `GET /users/{created_by}` | `User` -> `display_name` |
| Tab: 详情 | L98-102 | placeholder 内容区 | `GET /events/{event_id}` | `Event` -> `content`（Markdown） |
| Tab: 排榜 | 未实现 | -- | `GET /events/{event_id}/posts?relation_type=submission` 按评分排序 | `Post[]` -> `average_rating` |
| Tab: 讨论区 | 未实现 | -- | 无直接端点（API 缺口） | 建议 event 关联 post |
| Tab: 成员 | 未实现 | -- | `GET /events/{event_id}/groups` -> 各 group 的 members | `Group[]`, `Member[]` |
| Tab: 赛程安排 | 未实现 | -- | `GET /events/{event_id}/rules` | `Rule[]` -> `submission_start`, `submission_deadline` |
| Tab: 关联活动 | 未实现 | -- | 无端点（API 缺口） | 需新增 event 关联 |

---

## 9. user-profile.tsx — 用户主页

**文件**: `components/pages/user-profile.tsx`

| Mock 数据 / UI 区域 | 行号 | 变量/元素 | API 端点 | 对应 Schema |
|---------------------|------|----------|---------|------------|
| 用户头像 | L77 | `<div className="w-[90px]...bg-[var(--nf-dark-bg)]" />` | `GET /users/{user_id}` | `User` -> `avatar_url` |
| 用户名 | L81-83 | `"他人名字"` | `GET /users/{user_id}` | `User` -> `display_name` |
| 统计数据 | L14-18 | `const stats = [{value:"12"...}]` | 需多个接口聚合或新增统计端点 | `Post` count, follower/following count（API 缺口） |
| 关注按钮 | L101-102 | `<Button>关注</Button>` | 无端点（API 缺口） | 需新增 follow/unfollow API |
| 个人签名 | L111-113 | `"Personal Signature：..."` | `GET /users/{user_id}` | `User` -> `bio` |
| 资产卡片 | L20-24 | `const assets = [...]` | `GET /resources` (按用户过滤) | `Resource[]` 聚合统计 |
| Tab: 帖子 | L152-161 | 3 个 placeholder 灰色块 | `GET /posts?created_by={user_id}` (API 缺口：缺 `created_by` 参数) | `Post[]` |
| Tab: 提案 | L163-167 | `"暂无提案"` | `GET /posts?type=proposal&created_by={user_id}` | `Post[]` |
| Tab: 收藏 | L169-173 | `"暂无收藏"` | 无端点（API 缺口） | 需新增收藏 API |

---

## 10. team.tsx — 团队页

**文件**: `components/pages/team.tsx`

| Mock 数据 / UI 区域 | 行号 | 变量/元素 | API 端点 | 对应 Schema |
|---------------------|------|----------|---------|------------|
| 团队头像 | L67 | `<div className="w-[80px]...bg-[#555555]" />` | `GET /groups/{group_id}` | `Group`（无 avatar 字段，API 缺口） |
| 团队名称 | L71-73 | `"团队"` | `GET /groups/{group_id}` | `Group` -> `name` |
| 帖子/关注数 | L75-81 | `12 帖子`, `6 关注` | 需聚合统计（API 缺口） | -- |
| 团队描述 | L82-84 | `"未来的协会..."` | `GET /groups/{group_id}` | `Group` -> `description` |
| 队员头像列表 | L13-16 | `const members = [...]` | `GET /groups/{group_id}/members` | `Member[]` -> `user_id` -> `GET /users/{id}` -> `avatar_url` |
| 添加队员按钮 | L107-109 | `<Plus>` 按钮 | `POST /groups/{group_id}/members` | body: `{user_id, role?}` |
| 资产卡片 | L18-22 | `const assets = [...]` | `GET /resources` (按 group 过滤，API 缺口) | `Resource[]` 聚合统计 |
| Tab: 提案 | L165-168 | placeholder 灰色块 | `GET /posts?type=proposal` (按 group 过滤，API 缺口) | `Post[]` |
| Tab: 帖子 | L170-172 | `"暂无帖子"` | `GET /posts` (按 group 过滤，API 缺口) | `Post[]` |
| Tab: 收藏 | L174-176 | `"暂无收藏"` | 无端点（API 缺口） | -- |

---

## 11. assets.tsx — 资产页

**文件**: `components/pages/assets.tsx`

| Mock 数据 / UI 区域 | 行号 | 变量/元素 | API 端点 | 对应 Schema |
|---------------------|------|----------|---------|------------|
| 资源卡片列表 | L12-57 | `const assetCards = [...]` | `GET /resources?skip=0&limit=20` | `Resource` -> `filename`, `display_name`, `description` |
| 分类统计（AI/Agent, 证书, 文件）| L118-145 | 3 个分类 Card | `GET /resources` 按 `mime_type` 聚合统计 | `Resource[]` |
| 可用状态 / 截止日期 | L178-185 | `asset.available`, `asset.deadline` | `GET /resources/{id}` | `Resource` 当前无 `available` / `deadline` 字段（API 缺口） |
| 标签 | L159-171 | `asset.tags` | `Resource` 无 tags 字段（API 缺口） | -- |

---

## 12. following-list.tsx — 关注列表

**文件**: `components/pages/following-list.tsx`

| Mock 数据 / UI 区域 | 行号 | 变量/元素 | API 端点 | 对应 Schema |
|---------------------|------|----------|---------|------------|
| 用户卡片 | L12-18 | `const userCards = [...]` | 无端点（API 缺口：需新增关注关系 API） | -- |
| 用户头像 | L93-94 | `<div...bg-[#555555]>` | `GET /users/{user_id}` | `User` -> `avatar_url` |
| 用户名 | L96-98 | `user.name` | `GET /users/{user_id}` | `User` -> `display_name` |
| 粉丝数 | L99-101 | `user.followers` | 无端点（API 缺口） | -- |
| 图片画廊 | L20-24 | `const galleryCards = [...]` | `GET /posts?created_by={user_id}&limit=3` | `Post[]` + resources |

---

## 13. API 缺口汇总

| 缺口 | 涉及组件 | 建议新增端点 |
|------|---------|------------|
| `created_by` 过滤 | user-profile, team | `GET /posts?created_by=xxx` 添加 query param |
| 关注/粉丝关系 | following-list, user-profile | `POST/DELETE /users/{id}/follow`, `GET /users/{id}/following`, `GET /users/{id}/followers` |
| 搜索 | 所有页面 header | `GET /search?q=xxx&type=post\|user\|event` |
| 通知 | 所有页面 header | `GET /notifications`, `PATCH /notifications/{id}` |
| 收藏 | user-profile, team | `POST/DELETE /posts/{id}/favorite`, `GET /users/me/favorites` |
| 版本历史 | proposal-detail | `GET /posts/{id}/versions` |
| 资源扩展字段 | assets | `Resource` 增加 `tags`, `available`, `deadline` |
| 团队头像 | team | `Group` 增加 `avatar_url` 字段 |
| 按 group 过滤帖子 | team | `GET /posts?group_id=xxx` 或 `GET /groups/{id}/posts` |
| 文件上传 | assets | `POST /resources` 增加 `multipart/form-data` |
| 赛事关联活动 | event-detail | `GET /events/{id}/related` 或类似端点 |
| 用户统计聚合 | user-profile, team | `GET /users/{id}/stats` 返回帖子数/关注数/粉丝数 |

---

## 14. 数据类型映射

| OpenAPI Schema | 前端用途 | 对应页面 |
|---------------|---------|---------|
| `Event` | 赛事/活动卡片 | home, proposal-list, event-detail |
| `Post` | 帖子/提案卡片 | home, post-list, post-detail, proposal-list, proposal-detail |
| `Resource` | 附件/资产卡片 | assets, post-detail |
| `Rule` | 规则展示 | event-detail |
| `User` | 用户头像、信息 | user-profile, following-list, team |
| `Group` | 团队信息 | team, event-detail |
| `Comment` | 评论列表 | post-detail, proposal-detail |
| `Rating` | 评分记录 | post-detail, proposal-detail |
| `Member` | 团队成员 | team |

---

## 15. 枚举值对应

| 枚举 | 值 | 前端 UI 对应 |
|------|----|-------------|
| `PostType` | `profile`, `team`, `event`, `proposal`, `certificate`, `general` | 帖子分类 tab / 筛选器 |
| `PostStatus` | `draft`, `pending_review`, `published`, `rejected` | 帖子状态 badge |
| `CategoryType` | `competition`, `operation` | 赛事类型标签 |
| `CategoryStatus` | `draft`, `published`, `closed` | 赛事状态 badge |
| `UserRole` | `participant`, `organizer`, `admin` | 角色 badge / 权限控制 |
| `GroupVisibility` | `public`, `private` | 团队可见性标签 |
| `MemberRole` | `owner`, `admin`, `member` | 成员角色标识 |
| `MemberStatus` | `pending`, `accepted`, `rejected` | 成员审批状态 |
