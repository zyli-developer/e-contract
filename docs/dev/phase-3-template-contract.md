# Phase 3：合同模板与创建

**目标**：实现简化版模板市场、合同创建（模板创建 + 文件上传）、指定签署方。

**前置依赖**：Phase 1

## 后端任务

| # | 任务 | 说明 |
|---|------|------|
| 3.1 | 模板搜索 | `GET /seal/seal-template/search`，支持分页、分类（loan/lease/labor/purchase/sales/other）、关键词搜索 |
| 3.2 | 模板详情 | `GET /seal/seal-template/get`，返回完整模板：content(HTML)、variables(JSON)、signatories(JSON) |
| 3.3 | 分类列表 | `GET /seal/seal-template/categories` |
| 3.4 | 热门/常用 | `GET .../hot`（按 use_count）、`GET .../frequently-used`（当前用户最近使用） |
| 3.5 | 使用计数 | `POST /seal/seal-template/{id}/usage`，递增 use_count |
| 3.6 | 合同创建 | `POST /seal/sign-task/create`，支持模板创建和文件上传两种方式 |
| 3.7 | 签署方指定 | 创建时通过手机号指定签署方，存入 `sign_task_participant` 表 |

**Pydantic Schemas**：`TemplateSearchReq`, `TemplateResp`, `TemplateVariable`, `SignTaskCreateReq`, `ParticipantReq`

**数据表**：`contract_template`, `sign_task`, `sign_task_participant`

## 前端任务

| # | 任务 | 说明 |
|---|------|------|
| 3.8 | Template API 层 | `api/template.ts`：search、get、categories、hot、frequently-used |
| 3.9 | Contract API 层（创建部分） | `api/contract.ts`：create |
| 3.10 | 模板市场页 | 分类 tab + 搜索框 + 列表展示 + 热门推荐 |
| 3.11 | 模板详情页 | 模板预览、变量填写表单（text/number/date/select/money 类型）、"使用此模板"按钮 |
| 3.12 | 合同创建入口页 | 两种入口：从模板创建 / 上传文件创建 |
| 3.13 | 指定签署方组件 | 添加签署方（输入手机号+姓名）、设置签署顺序、删除签署方 |
| 3.14 | 文件上传页 | 上传 PDF/Word 文件 → 预览 → 指定签署方 → 创建 |
| 3.15 | H5 创建页 | WebView 嵌入 Seal Core H5（mode=create / create-file），完成后回调 |
| 3.16 | usePagination Hook | 通用分页 Hook：pageNo/pageSize/hasMore/loadMore |

## 测试任务

| 测试文件 | 覆盖内容 |
|----------|---------|
| `test_template_service.py` | 搜索（分类+关键词）、热门排序、常用记录、use_count 递增 |
| `test_template_api.py` | 搜索分页、详情返回完整模板、分类列表 |
| `test_contract_create.py` | 模板创建、文件上传创建、签署方指定（手机号校验、至少一个签署方） |
| `template-market.test.tsx` | 分类切换、搜索、列表渲染、加载更多 |
| `template-detail.test.tsx` | 变量表单渲染（各类型）、必填校验、提交 |
| `signer-picker.test.tsx` | 添加/删除签署方、手机号格式校验、顺序调整 |
| `usePagination.test.ts` | 分页逻辑、边界条件（空列表、最后一页） |

### 集成测试

- `test_contract_create_flow.py`：浏览模板 → 选择 → 填写变量 → 指定签署方 → 创建合同 → 合同状态=草稿

## 交付物

- [ ] 模板市场分类搜索可用
- [ ] 模板变量表单支持 5 种字段类型
- [ ] 两种创建方式（模板/文件上传）正常
- [ ] 签署方指定（手机号 + 姓名 + 顺序）正常
- [ ] 创建后合同状态为草稿
