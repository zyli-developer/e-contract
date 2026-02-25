# Layout Patterns

常见页面布局模式，用于 AI UI 生成时的布局选择。

## 全局布局

### 1. Header-Sidebar-Main (Dashboard)

适用于：管理后台、个人中心

```
┌──────────────────────────────────────┐
│              Header (60px)           │
├──────────┬───────────────────────────┤
│          │                           │
│ Sidebar  │         Main              │
│ (240px)  │                           │
│          │                           │
│          │                           │
└──────────┴───────────────────────────┘
```

```tsx
<div className="min-h-screen">
  <Header />
  <div className="flex">
    <Sidebar className="w-60 fixed" />
    <main className="ml-60 flex-1 p-6">
      {children}
    </main>
  </div>
</div>
```

### 2. Header-Main-Footer (Public Page)

适用于：首页、着陆页、公开页面

```
┌──────────────────────────────────────┐
│              Header (60px)           │
├──────────────────────────────────────┤
│                                      │
│               Main                   │
│          (flex-1, 自动高度)           │
│                                      │
├──────────────────────────────────────┤
│              Footer                  │
└──────────────────────────────────────┘
```

```tsx
<div className="min-h-screen flex flex-col">
  <Header />
  <main className="flex-1 pt-[60px]">
    {children}
  </main>
  <Footer />
</div>
```

### 3. Centered Content (Auth Pages)

适用于：登录、注册、错误页

```
┌──────────────────────────────────────┐
│              Header (可选)            │
├──────────────────────────────────────┤
│                                      │
│         ┌────────────┐               │
│         │   Card     │               │
│         │  (居中)     │               │
│         └────────────┘               │
│                                      │
└──────────────────────────────────────┘
```

```tsx
<div className="min-h-screen flex items-center justify-center">
  <Card className="w-full max-w-md">
    {children}
  </Card>
</div>
```

---

## 页面内布局

### 4. Split View (List + Detail)

适用于：消息列表、团队成员、资源管理

```
┌─────────────────┬────────────────────┐
│                 │                    │
│   列表 (固定)    │      详情          │
│   (300-400px)   │    (flex-1)        │
│                 │                    │
│                 │                    │
└─────────────────┴────────────────────┘
```

```tsx
<div className="flex h-[calc(100vh-60px)]">
  <aside className="w-80 border-r overflow-y-auto">
    <List />
  </aside>
  <main className="flex-1 overflow-y-auto">
    <Detail />
  </main>
</div>
```

### 5. Grid Layout (Card Gallery)

适用于：活动列表、帖子列表、团队列表

```
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│  Card  │ │  Card  │ │  Card  │ │  Card  │
└────────┘ └────────┘ └────────┘ └────────┘
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│  Card  │ │  Card  │ │  Card  │ │  Card  │
└────────┘ └────────┘ └────────┘ └────────┘
```

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
  {items.map(item => <Card key={item.id} {...item} />)}
</div>
```

### 6. Main + Sidebar (Detail Page)

适用于：帖子详情、活动详情

```
┌────────────────────────┬───────────────┐
│                        │               │
│     Main Content       │   Sidebar     │
│        (2/3)           │    (1/3)      │
│                        │               │
│                        │               │
└────────────────────────┴───────────────┘
```

```tsx
<div className="max-w-6xl mx-auto px-4">
  <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
    <main className="lg:col-span-2">
      <PostContent />
    </main>
    <aside className="lg:col-span-1">
      <RelatedInfo />
    </aside>
  </div>
</div>
```

### 7. Wizard / Stepper (Multi-step Form)

适用于：注册流程、创建活动、报名

```
┌──────────────────────────────────────┐
│  Step 1   →   Step 2   →   Step 3    │
├──────────────────────────────────────┤
│                                      │
│          Step Content                │
│                                      │
├──────────────────────────────────────┤
│  [Back]                    [Next]    │
└──────────────────────────────────────┘
```

```tsx
<div className="max-w-2xl mx-auto">
  <Stepper currentStep={step} />
  <Card className="mt-6">
    <CardContent>
      {renderStep(step)}
    </CardContent>
    <CardFooter className="justify-between">
      <Button variant="outline" onClick={prev}>上一步</Button>
      <Button onClick={next}>下一步</Button>
    </CardFooter>
  </Card>
</div>
```

---

## 响应式断点

| 断点 | 宽度 | 布局调整 |
|------|------|----------|
| `sm` | 640px | 单列，隐藏侧边栏 |
| `md` | 768px | 2 列网格 |
| `lg` | 1024px | 显示侧边栏，3 列网格 |
| `xl` | 1280px | 4 列网格 |
| `2xl` | 1536px | 最大宽度限制 |

---

## 容器宽度

| 场景 | 类名 | 说明 |
|------|------|------|
| 全宽 | `w-full` | 列表、仪表盘 |
| 标准 | `max-w-6xl mx-auto` | 详情页、文章 |
| 窄 | `max-w-2xl mx-auto` | 表单、设置 |
| 超窄 | `max-w-md mx-auto` | 登录、对话框 |
