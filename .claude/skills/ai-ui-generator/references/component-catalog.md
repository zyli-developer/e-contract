# Component Catalog

shadcn/ui 可用组件清单，用于 AI UI 生成时的组件选择。

## 布局组件

| 组件 | 用途 | 适用场景 |
|------|------|----------|
| `Card` | 内容卡片 | 展示帖子、活动、团队等信息 |
| `Sheet` | 侧边抽屉 | 详情面板、移动端菜单 |
| `Dialog` | 模态对话框 | 表单、确认框、提示 |
| `Drawer` | 底部/侧边抽屉 | 移动端操作面板 |
| `Tabs` | 选项卡 | 内容分类切换 |
| `Accordion` | 折叠面板 | FAQ、分组展开 |
| `Collapsible` | 可折叠区域 | 简单的展开/收起 |
| `Separator` | 分隔线 | 区域分隔 |
| `ScrollArea` | 滚动区域 | 固定高度内容 |
| `AspectRatio` | 固定宽高比 | 图片、视频容器 |
| `Resizable` | 可调整大小 | 分栏布局 |

## 表单组件

| 组件 | 用途 | 适用场景 |
|------|------|----------|
| `Form` | 表单容器 | 所有表单 (基于 react-hook-form) |
| `Input` | 文本输入 | 标题、用户名、搜索 |
| `Textarea` | 多行文本 | 描述、内容、评论 |
| `Select` | 下拉选择 | 单选列表 |
| `Checkbox` | 复选框 | 多选、同意条款 |
| `RadioGroup` | 单选组 | 互斥选项 |
| `Switch` | 开关 | 布尔设置 |
| `Slider` | 滑块 | 范围值、评分 |
| `DatePicker` | 日期选择 | 开始/结束日期 |
| `Calendar` | 日历 | 日期范围选择 |
| `InputOTP` | 验证码输入 | 验证码、PIN |

## 数据展示

| 组件 | 用途 | 适用场景 |
|------|------|----------|
| `Table` | 数据表格 | 列表数据 |
| `DataTable` | 高级表格 | 排序、筛选、分页 |
| `Avatar` | 头像 | 用户头像 |
| `Badge` | 徽章 | 状态标签、计数 |
| `Progress` | 进度条 | 加载进度、完成度 |
| `Skeleton` | 骨架屏 | 加载占位 |
| `HoverCard` | 悬浮卡片 | 预览信息 |
| `Carousel` | 轮播 | 图片/卡片轮播 |
| `Chart` | 图表 | 数据可视化 |

## 导航组件

| 组件 | 用途 | 适用场景 |
|------|------|----------|
| `NavigationMenu` | 导航菜单 | 顶部导航 |
| `Menubar` | 菜单栏 | 应用菜单 |
| `DropdownMenu` | 下拉菜单 | 操作菜单 |
| `ContextMenu` | 右键菜单 | 上下文操作 |
| `Breadcrumb` | 面包屑 | 页面路径 |
| `Pagination` | 分页 | 列表分页 |
| `Command` | 命令面板 | 搜索、快捷命令 |

## 反馈组件

| 组件 | 用途 | 适用场景 |
|------|------|----------|
| `Toast` | 轻提示 | 操作反馈 |
| `Sonner` | Toast 替代 | 更丰富的提示 |
| `Alert` | 警告提示 | 页内提示 |
| `AlertDialog` | 确认对话框 | 危险操作确认 |
| `Tooltip` | 悬浮提示 | 帮助说明 |

## 操作组件

| 组件 | 用途 | 适用场景 |
|------|------|----------|
| `Button` | 按钮 | 所有操作 |
| `Toggle` | 切换按钮 | 模式切换 |
| `ToggleGroup` | 切换组 | 多选切换 |
| `Popover` | 弹出层 | 操作面板 |

---

## 组件组合模式

### 帖子卡片

```
Card
├── CardHeader
│   ├── Avatar (作者头像)
│   └── CardTitle / CardDescription
├── CardContent
│   └── 正文内容
└── CardFooter
    ├── Badge[] (标签)
    ├── Button (点赞)
    └── Button (评论)
```

### 列表筛选

```
div.filter-bar
├── Input (搜索)
├── Select (类型筛选)
├── Popover
│   └── Checkbox[] (多选筛选)
└── Button (重置)
```

### 创建表单

```
Form
├── FormField (标题)
│   └── Input
├── FormField (内容)
│   └── Textarea / MarkdownEditor
├── FormField (标签)
│   └── TagInput (基于 Command)
└── Button[type=submit]
```

### 详情页

```
PageLayout
├── header
│   ├── Breadcrumb
│   └── Button[] (操作按钮)
├── main
│   ├── Card (主内容)
│   └── Tabs (相关内容)
└── aside (可选)
    └── Card (侧边信息)
```
