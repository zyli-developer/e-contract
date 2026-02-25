# Phase 2：个人签名管理

**目标**：实现个人签名的创建、管理，为合同签署提供签名能力。

**前置依赖**：Phase 1

## 后端任务

| # | 任务 | 说明 |
|---|------|------|
| 2.1 | 个人签名 CRUD | `POST/GET/PUT/DELETE /seal/seal-info/*`，限定 type=11(签名) 和 type=12(印章)，使用 Access Token 认证 |
| 2.2 | 签名创建方式 | 手绘上传（图片 base64/URL）、图片上传 |
| 2.3 | 默认签名 | `PUT /seal/seal-info/set-default`，每种类型只能有一个默认，签署时自动选中 |
| 2.4 | 签名模板 | `GET /seal/seal-template/page`，提供预设签名模板供选择 |

**Pydantic Schemas**：`SealCreateReq`, `SealResp`

**数据表**：`seal_info`, `seal_template`

## 前端任务

| # | 任务 | 说明 |
|---|------|------|
| 2.5 | Seal API 层 | `api/seal.ts`：CRUD、模板列表（请求 header 用 Authorization Bearer Token） |
| 2.6 | 签名管理页 | 签名列表、设为默认、删除 |
| 2.7 | 创建签名页 | 手绘签名（Canvas）、图片上传，预览确认 |
| 2.8 | 手绘签名组件 | Canvas 手写签名板，支持撤销/清除/保存为图片 |

## 测试任务

| 测试文件 | 覆盖内容 |
|----------|---------|
| `test_seal_service.py` | 签名 CRUD、类型校验（只允许 11/12）、默认签名切换逻辑 |
| `test_seal_api.py` | Access Token 认证、CRUD 接口完整 |
| `seal-signature.test.tsx` | 手绘签名组件交互（画/撤销/清除/保存） |
| `seal-manage.test.tsx` | 签名列表渲染、设为默认、删除确认 |

### 集成测试

- `test_seal_flow.py`：登录 → 创建手绘签名 → 设为默认 → 查询签名列表

## 交付物

- [ ] 个人签名创建（手绘/上传）和管理完整可用
- [ ] 默认签名设置正常
- [ ] 手绘签名 Canvas 组件可用
