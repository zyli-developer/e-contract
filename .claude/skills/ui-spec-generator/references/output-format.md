# pages.yaml 输出格式规范

## 文件位置
`specs/design/pages.yaml`

## 结构说明

```yaml
# 页面级别
pages:
  - id: home                    # 页面唯一标识
    name: 主页                   # 页面中文名称
    route: /                    # 路由路径
    pen_file: components/home.pen
    figma_url: https://...      # Figma 设计链接
    image: assets/images/首页.png
    description: 平台首页，展示热门活动和最新内容

    # 组件区块级别
    sections:
      - id: hot-activities-banner
        name: 热点活动横幅
        position: top           # top | left | right | bottom | center
        layout: horizontal-scroll

        # 子组件级别
        components:
          - id: activity-card
            name: 活动卡片
            type: card
            data_source: category  # 关联的数据类型
            fields:
              - cover_image
              - title
              - participant_count
            actions:
              - navigate_to: /categories/{id}
            notes: 可横向滑动，每次显示 2.5 个卡片

      - id: official-posts
        name: 官方最新帖子
        position: below:hot-activities-banner
        layout: vertical-list

        components:
          - id: post-item
            name: 帖子条目
            type: list-item
            data_source: post
            filter: created_by.role == 'admin'
            fields:
              - title
              - created_at
              - like_count
            actions:
              - navigate_to: /posts/{id}
```

## 字段说明

### 页面 (Page)
| 字段 | 必填 | 说明 |
|------|------|------|
| id | 是 | 唯一标识，用于路由和引用 |
| name | 是 | 中文名称 |
| route | 是 | 路由路径，支持参数如 `/posts/{id}` |
| pen_file | 否 | 对应的 .pen 设计文件 |
| figma_url | 否 | Figma 设计链接 |
| image | 否 | 效果图路径 |
| description | 是 | 页面功能描述 |
| sections | 是 | 页面包含的区块列表 |

### 区块 (Section)
| 字段 | 必填 | 说明 |
|------|------|------|
| id | 是 | 区块唯一标识 |
| name | 是 | 区块中文名称 |
| position | 是 | 位置：top/left/right/bottom/center 或 below:xxx/beside:xxx |
| layout | 否 | 布局方式：vertical-list/horizontal-scroll/grid/flex |
| components | 是 | 区块包含的组件列表 |

### 组件 (Component)
| 字段 | 必填 | 说明 |
|------|------|------|
| id | 是 | 组件唯一标识 |
| name | 是 | 组件中文名称 |
| type | 是 | 组件类型：card/list-item/button/form/modal/tabs 等 |
| data_source | 否 | 关联的数据类型：post/category/user/group 等 |
| filter | 否 | 数据过滤条件 |
| fields | 否 | 显示的数据字段列表 |
| actions | 否 | 用户交互动作 |
| notes | 否 | 补充说明 |

## 数据类型引用

支持的 data_source 值（对应 specs/data/types.md）：
- `category` - 活动/赛事
- `post` - 帖子/提案
- `user` - 用户
- `group` - 团队
- `resource` - 资源文件
- `rule` - 规则
- `interaction` - 互动（点赞/评论/评分）
