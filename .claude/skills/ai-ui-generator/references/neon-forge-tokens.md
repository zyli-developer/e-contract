# Neon Forge Design Tokens

Synnovator 项目的设计系统 Token 映射，用于 AI UI 生成时保持视觉一致性。

## 颜色系统

### 主色

| Token | 值 | Tailwind 类 | 用途 |
|-------|-----|------------|------|
| `nf-lime` | `#BBFD3B` | `bg-nf-lime` / `text-nf-lime` | 主要强调色、CTA 按钮 |
| `nf-cyan` | `#00D4FF` | `bg-nf-cyan` / `text-nf-cyan` | 次要强调色、链接 |
| `nf-pink` | `#FF6B9D` | `bg-nf-pink` / `text-nf-pink` | 活跃状态、通知 |

### 背景色

| Token | 值 | Tailwind 类 | 用途 |
|-------|-----|------------|------|
| `nf-near-black` | `#0A0A0A` | `bg-nf-near-black` | 最深背景 |
| `nf-dark` | `#181818` | `bg-nf-dark` | 页面背景 |
| `nf-surface` | `#222222` | `bg-nf-surface` | 卡片、组件背景 |
| `nf-secondary` | `#333333` | `bg-nf-secondary` | 次级背景、边框 |
| `nf-card-bg` | `#1A1A1A` | `bg-nf-card-bg` | 卡片背景变体 |
| `nf-dark-bg` | `#121212` | `bg-nf-dark-bg` | 深色背景变体 |

### 文字色

| Token | 值 | Tailwind 类 | 用途 |
|-------|-----|------------|------|
| `nf-white` | `#FFFFFF` | `text-nf-white` | 主要文字 |
| `nf-light-gray` | `#E5E5E5` | `text-nf-light-gray` | 次要文字 |
| `nf-muted` | `#888888` | `text-nf-muted` | 辅助文字、占位符 |

### 功能色

| Token | 值 | Tailwind 类 | 用途 |
|-------|-----|------------|------|
| `nf-success` | `#22C55E` | `text-nf-success` | 成功状态 |
| `nf-warning` | `#F59E0B` | `text-nf-warning` | 警告状态 |
| `nf-error` | `#EF4444` | `text-nf-error` | 错误状态 |
| `nf-info` | `#3B82F6` | `text-nf-info` | 信息提示 |

---

## 间距系统

| Token | 值 | Tailwind 类 | 用途 |
|-------|-----|------------|------|
| `xs` | `4px` | `p-1` / `gap-1` | 最小间距 |
| `sm` | `8px` | `p-2` / `gap-2` | 小间距 |
| `md` | `16px` | `p-4` / `gap-4` | 中等间距（默认） |
| `lg` | `24px` | `p-6` / `gap-6` | 大间距 |
| `xl` | `32px` | `p-8` / `gap-8` | 超大间距 |
| `2xl` | `48px` | `p-12` / `gap-12` | 区块间距 |

---

## 圆角系统

| Token | 值 | Tailwind 类 | 用途 |
|-------|-----|------------|------|
| `sm` | `4px` | `rounded-sm` | 按钮、输入框 |
| `md` | `8px` | `rounded-md` | 卡片、对话框 |
| `lg` | `12px` | `rounded-lg` | 大卡片 |
| `xl` | `21px` | `rounded-xl` | 特殊容器 |
| `pill` | `50px` | `rounded-full` | 标签、头像 |

---

## 字体系统

### 字体家族

| Token | 字体 | Tailwind 类 | 用途 |
|-------|------|------------|------|
| `heading` | Space Grotesk | `font-heading` | 标题 |
| `body` | Inter | `font-body` | 正文 |
| `mono` | Poppins | `font-mono` | 代码、数字 |
| `chinese` | Noto Sans SC | (fallback) | 中文 |

### 字体大小

| Token | 值 | Tailwind 类 | 用途 |
|-------|-----|------------|------|
| `xs` | `12px` | `text-xs` | 辅助文字 |
| `sm` | `14px` | `text-sm` | 小号正文 |
| `base` | `16px` | `text-base` | 正文 |
| `lg` | `18px` | `text-lg` | 大号正文 |
| `xl` | `20px` | `text-xl` | 小标题 |
| `2xl` | `24px` | `text-2xl` | 中标题 |
| `3xl` | `30px` | `text-3xl` | 大标题 |
| `4xl` | `36px` | `text-4xl` | 页面标题 |

---

## 组件样式规范

### Button

```tsx
// Primary (CTA)
<Button className="bg-nf-lime text-nf-near-black hover:bg-nf-lime/90">
  主要操作
</Button>

// Secondary
<Button variant="outline" className="border-nf-secondary text-nf-white hover:bg-nf-secondary">
  次要操作
</Button>

// Ghost
<Button variant="ghost" className="text-nf-light-gray hover:text-nf-white hover:bg-nf-secondary">
  幽灵按钮
</Button>

// Destructive
<Button variant="destructive" className="bg-nf-error hover:bg-nf-error/90">
  危险操作
</Button>
```

### Card

```tsx
<Card className="bg-nf-surface border-nf-secondary">
  <CardHeader>
    <CardTitle className="text-nf-white">标题</CardTitle>
    <CardDescription className="text-nf-muted">描述</CardDescription>
  </CardHeader>
  <CardContent className="text-nf-light-gray">
    内容
  </CardContent>
</Card>
```

### Input

```tsx
<Input
  className="bg-nf-dark border-nf-secondary text-nf-white
             placeholder:text-nf-muted
             focus:border-nf-lime focus:ring-nf-lime/20"
  placeholder="输入..."
/>
```

### Badge

```tsx
// Default
<Badge className="bg-nf-secondary text-nf-light-gray">标签</Badge>

// Accent
<Badge className="bg-nf-lime/20 text-nf-lime">强调</Badge>

// Status
<Badge className="bg-nf-success/20 text-nf-success">成功</Badge>
<Badge className="bg-nf-error/20 text-nf-error">错误</Badge>
```

### Dialog

```tsx
<DialogContent className="bg-nf-surface border-nf-secondary">
  <DialogHeader>
    <DialogTitle className="text-nf-white">标题</DialogTitle>
    <DialogDescription className="text-nf-muted">描述</DialogDescription>
  </DialogHeader>
  {/* 内容 */}
  <DialogFooter>
    <Button variant="outline" className="border-nf-secondary">取消</Button>
    <Button className="bg-nf-lime text-nf-near-black">确认</Button>
  </DialogFooter>
</DialogContent>
```

---

## 动效规范

### 过渡时间

| Token | 值 | 用途 |
|-------|-----|------|
| `fast` | `150ms` | 按钮悬停 |
| `normal` | `200ms` | 通用过渡 |
| `slow` | `300ms` | 模态框、抽屉 |

### 缓动函数

| Token | 值 | 用途 |
|-------|-----|------|
| `ease-out` | `cubic-bezier(0, 0, 0.2, 1)` | 展开动画 |
| `ease-in` | `cubic-bezier(0.4, 0, 1, 1)` | 收起动画 |
| `ease-in-out` | `cubic-bezier(0.4, 0, 0.2, 1)` | 通用过渡 |

---

## 阴影规范

| Token | 值 | 用途 |
|-------|-----|------|
| `sm` | `0 1px 2px rgba(0,0,0,0.3)` | 按钮、输入框 |
| `md` | `0 4px 6px rgba(0,0,0,0.3)` | 卡片、下拉菜单 |
| `lg` | `0 10px 15px rgba(0,0,0,0.4)` | 模态框 |
| `glow-lime` | `0 0 20px rgba(187,253,59,0.3)` | 强调状态 |

---

## 响应式断点

| 断点 | 宽度 | 布局说明 |
|------|------|----------|
| `sm` | `640px` | 移动端优化 |
| `md` | `768px` | 平板适配 |
| `lg` | `1024px` | 桌面端 |
| `xl` | `1280px` | 大屏优化 |
| `2xl` | `1536px` | 超大屏 |
