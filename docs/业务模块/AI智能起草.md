# 模块：AI 智能起草

## 一、模块概述

AI 智能起草模块提供对话式合同生成能力。用户通过与 AI 多轮对话描述合同需求，AI 自动生成完整合同文本，支持编辑修改后直接创建签署任务。

## 二、核心流程

```
选择推荐话术/自由输入 → 创建 AI 对话
     │
     ├── 多轮对话交互（描述合同需求、修改细节）
     │
     ├── AI 生成完整合同文本
     │
     ├── 用户编辑修改合同内容
     │
     ├── 预览最终合同
     │
     └── 二选一：
           ├── 导出 PDF → 下载保存
           └── 创建签署任务 → 指定签署方 → 发起签署
```

## 三、功能详细说明

### 3.1 推荐话术模板

系统提供分类的推荐话术帮助用户快速开始：

```
GET /seal/ai-draft/template/list → 获取所有模板
GET /seal/ai-draft/template/list-by-type → 按合同类型获取
```

**模板分类：** 借贷合同、租赁合同、劳动合同、采购合同、销售合同等

每个模板包含预设的对话开场白，用户选择后可直接开始对话。

### 3.2 对话管理

```
对话生命周期：
  创建对话 → 发送消息（多轮）→ 生成合同 → 归档

API：
  POST /conversation/create  → 创建新对话
  POST /message/send         → 发送消息给 AI
  GET  /message/list         → 获取对话消息列表
  GET  /conversation/page    → 对话历史列表
  GET  /conversation/get     → 对话详情
  GET  /conversation/detail  → 完整对话详情（含消息）
  DELETE /conversation/delete → 删除对话
```

### 3.3 合同生成

```
对话完成后，一键生成合同：
  POST /contract/generate → AI 根据对话内容生成合同文本

超时配置：180 秒（3分钟），因为 AI 生成需要较长时间
```

### 3.4 合同编辑

生成后的合同支持在编辑器中修改：

```
GET  /contract/get     → 获取生成的合同内容
PUT  /contract/update  → 保存编辑后的内容
```

### 3.5 导出与签署

| 操作 | API | 说明 |
|------|-----|------|
| 导出 PDF | `POST /contract/export-pdf` | 将合同内容导出为 PDF 文件 |
| 创建签署 | `POST /contract/create-signing` | 从 AI 合同直接创建签署任务 |

## 四、用户旅程

### 4.1 新建 AI 合同

```
1. 进入 AI 起草首页（pages/ai-draft/index）
2. 浏览推荐话术模板，选择合适的类型
3. 进入对话页面（pages/ai-draft/chat）
4. 输入合同需求，与 AI 多轮交互
5. 点击"生成合同"
6. 进入编辑器（pages/ai-draft/editor）修改内容
7. 预览确认（pages/ai-draft/preview）
8. 选择"创建签署任务"或"导出 PDF"
```

### 4.2 查看历史对话

```
1. 进入 AI 起草首页
2. 查看"最近对话"列表
3. 点击对话进入详情（pages/ai-draft/detail）
4. 可继续对话或查看已生成的合同
```

## 五、相关页面

| 页面 | 路由 | 功能 |
|------|------|------|
| AI 起草首页 | `pages/ai-draft/index` | 推荐话术 + 最近对话 |
| 对话页 | `pages/ai-draft/chat` | 与 AI 多轮对话 |
| 对话历史 | `pages/ai-draft/history` | 历史对话列表 |
| 对话详情 | `pages/ai-draft/detail` | 完整对话内容 |
| 合同编辑 | `pages/ai-draft/editor` | 编辑 AI 生成的合同 |
| 合同预览 | `pages/ai-draft/preview` | 预览最终合同 |

## 六、相关 API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/seal/ai-draft/template/list` | GET | 推荐话术模板列表 |
| `/seal/ai-draft/template/list-by-type` | GET | 按类型获取模板 |
| `/seal/ai-draft/template/increment-use/{id}` | POST | 记录模板使用次数 |
| `/seal/ai-draft/conversation/create` | POST | 创建对话 |
| `/seal/ai-draft/conversation/page` | GET | 对话列表（分页） |
| `/seal/ai-draft/conversation/get` | GET | 对话详情 |
| `/seal/ai-draft/conversation/detail` | GET | 完整对话详情 |
| `/seal/ai-draft/conversation/delete` | DELETE | 删除对话 |
| `/seal/ai-draft/message/send` | POST | 发送消息 |
| `/seal/ai-draft/message/list` | GET | 消息列表 |
| `/seal/ai-draft/contract/generate` | POST | 生成合同（180s超时） |
| `/seal/ai-draft/contract/get` | GET | 获取生成的合同 |
| `/seal/ai-draft/contract/update` | PUT | 编辑合同 |
| `/seal/ai-draft/contract/export-pdf` | POST | 导出 PDF |
| `/seal/ai-draft/contract/create-signing` | POST | 创建签署任务 |
