# Phase 2：个人签名与 Seal Token

**目标**：实现个人签名的创建与管理、Seal Token 认证链路（签署合同的前提）。

**前置依赖**：Phase 1

## 后端任务

| # | 任务 | 说明 |
|---|------|------|
| 2.1 | Seal Token 交换 | `POST /seal/auth/exchange-token`，用 Access Token 换取 Seal Token；TTL：移动端 30 天 / PC 2 小时 |
| 2.2 | Seal Token 中间件 | 解析 `Seal-Token` header，注入 seal_user；Seal 相关接口使用此中间件 |
| 2.3 | 个人签名 CRUD | `POST/GET/PUT/DELETE /seal/seal-info/*`，限定 type=11(签名) 和 type=12(印章) |
| 2.4 | 签名创建方式 | 手绘上传（图片 base64/URL）、图片上传 |
| 2.5 | 默认签名 | `PUT /seal/seal-info/set-default`，每种类型只能有一个默认，签署时自动选中 |
| 2.6 | 签名模板 | `GET /seal/seal-template/page`，提供预设签名模板供选择 |

**Pydantic Schemas**：`SealCreateReq`, `SealResp`, `SealTokenExchangeReq`, `SealTokenResp`

**数据表**：`seal_info`, `seal_template`

## 前端任务

| # | 任务 | 说明 |
|---|------|------|
| 2.7 | useSealToken Hook | 自动获取/缓存/刷新 Seal Token，到期前 10 分钟预刷新 |
| 2.8 | Seal API 层 | `api/seal.ts`：CRUD、模板列表、Token 交换（请求 header 用 `Seal-Token`） |
| 2.9 | 签名管理页 | 签名列表、设为默认、删除 |
| 2.10 | 创建签名页 | 手绘签名（Canvas）、图片上传，预览确认 |
| 2.11 | 手绘签名组件 | Canvas 手写签名板，支持撤销/清除/保存为图片 |

## 测试任务

| 测试文件 | 覆盖内容 |
|----------|---------|
| `test_seal_token.py` | Token 交换成功、TTL 正确（移动/PC）、过期拒绝、无效 Access Token 拒绝 |
| `test_seal_service.py` | 签名 CRUD、类型校验（只允许 11/12）、默认签名切换逻辑 |
| `test_seal_api.py` | Seal Token 认证（用 Authorization header 返回 401）、CRUD 接口完整 |
| `useSealToken.test.ts` | Token 获取/缓存/预刷新/过期处理 |
| `seal-signature.test.tsx` | 手绘签名组件交互（画/撤销/清除/保存） |
| `seal-manage.test.tsx` | 签名列表渲染、设为默认、删除确认 |

### 集成测试

- `test_seal_flow.py`：登录 → 获取 Seal Token → 创建手绘签名 → 设为默认 → 查询签名列表

## 交付物

- [ ] Seal Token 认证链路通畅（Access Token → Seal Token）
- [ ] 个人签名创建（手绘/上传）和管理完整可用
- [ ] 默认签名设置正常
- [ ] 手绘签名 Canvas 组件可用
