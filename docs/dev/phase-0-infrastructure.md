# Phase 0：基础设施搭建

**目标**：搭建前后端项目骨架、数据库（仅 MVP 所需表）、CI/CD 流水线和测试基础设施。

**前置依赖**：无

## 后端任务

| # | 任务 | 说明 |
|---|------|------|
| 0.1 | 初始化 FastAPI 项目 | 创建 `mini-contract-api/`，安装核心依赖（fastapi, uvicorn, sqlalchemy[asyncio], aiomysql, redis, pydantic>=2.0） |
| 0.2 | 配置数据库连接 | SQLAlchemy 2.0 async engine + session factory，环境变量管理（python-dotenv） |
| 0.3 | 自动建表 | 使用 `Base.metadata.create_all()` 在应用启动时自动创建表 |
| 0.4 | 统一响应格式 | `ApiResponse(code, msg, data)` + `PageResult(list, total, pageNo, pageSize)` |
| 0.5 | 全局异常处理 | BusinessException、ValidationException、统一错误码体系 |
| 0.7 | 创建 MVP 数据库表 | 10 张表（见下方清单），SQLAlchemy models + create_all 自动建表 |
| 0.8 | pytest 测试框架 | conftest.py（async test DB、TestClient fixture）、pytest-asyncio 配置 |
| 0.9 | 文件上传基础 | `POST /infra/file/upload` 接口，支持 S3/MinIO/本地存储，限制：图片 5MB、文档 20MB |

### MVP 数据库表（10 张）

| 表名 | 用途 |
|------|------|
| `member` | 用户基本信息（手机号、密码、昵称、头像） |
| `member_social_user` | 微信 OpenID/UnionID 绑定关系 |
| `member_token` | Access Token / Refresh Token 存储 |
| `seal_info` | 个人签名/印章数据（type=11 签名, type=12 印章） |
| `seal_template` | 签名/印章模板 |
| `contract_template` | 合同模板（内容、变量、签署方配置） |
| `sign_task` | 合同/签署任务（状态、文件、创建人、**file_hash、signed_file_hash**） |
| `sign_task_participant` | 签署方（手机号、签署状态、顺序） |
| `sign_evidence_log` | **签署证据链**（task_id、action、user_id、timestamp、ip、device、data_hash、detail） |
| `infra_file` | 上传文件记录 |

## 前端任务

| # | 任务 | 说明 |
|---|------|------|
| 0.10 | 初始化 Taro 项目 | `taro init`，配置 React 18 + TypeScript + pnpm |
| 0.11 | 页面路由框架 | `app.config.ts` 配置 3 个 tabBar（首页/合同管理/我的）+ 基础路由 |
| 0.12 | UI 组件库集成 | NutUI-React 或 Taro UI，配置主题色 `#00C28A` |
| 0.13 | 请求层封装 | 基于 Taro.request 封装 `request()`，统一 header（Authorization） |
| 0.14 | 环境配置 | dev/test/prod 环境切换，API baseURL 和 Seal Core H5 URL |
| 0.15 | Jest 测试配置 | jest.config.ts、setupTests.ts、MSW mock server |

## 测试任务

| 测试 | 覆盖内容 |
|------|---------|
| `test_health.py` | 应用启动、health check 端点返回 200 |
| `test_response_format.py` | ApiResponse/PageResult 序列化格式正确 |
| `test_exception_handler.py` | 各异常类型返回正确错误码和 HTTP 状态 |
| `test_file_upload.py` | 文件上传成功、超限拒绝、类型校验 |
| `request.test.ts` | 请求拦截器添加正确 header、401 触发 token 刷新 |

## 交付物

- [ ] 后端项目可 `uvicorn app.main:app` 启动，`/health` 返回 200
- [ ] 10 张数据库表通过 create_all 自动创建成功
- [ ] 前端项目可 `pnpm run dev:weixin` 启动，微信开发者工具中 tabBar 显示 3 个 tab
- [ ] CI 流水线：push 触发 pytest + jest
- [ ] 后端基础设施层测试 100% 通过
