# Mini Contract.Pro — MVP 开发计划

> 聚焦核心签署闭环：**创建合同 → 发送给签署方 → 签署方登录查看 → 签署 → 合同生效**
>
> 技术栈：Python (FastAPI) + React (Taro 4.x)，微信小程序为主要运行载体。
>
> 法律合规：采用基础合规方案（签署意愿验证 + 文档哈希防篡改 + 签署证据链），确保合同具备基本法律效力。

## 总览

| 阶段 | 名称 | 核心内容 | 前置依赖 |
|------|------|---------|---------|
| [Phase 0](./phase-0-infrastructure.md) | 基础设施搭建 | 项目骨架、数据库、CI/CD、测试框架 | 无 |
| [Phase 1](./phase-1-authentication.md) | 用户认证 | 微信登录、短信登录、双 Token、基础 Profile | Phase 0 |
| [Phase 2](./phase-2-seal-signature.md) | 个人签名管理 | 手绘签名、签名管理 | Phase 1 |
| [Phase 3](./phase-3-template-contract.md) | 合同模板与创建 | 模板浏览、合同创建（模板/上传）、指定签署方 | Phase 1 |
| [Phase 4](./phase-4-signing-management.md) | 合同签署与管理 | H5 签署集成、合同列表、状态机、通知签署方 | Phase 2+3 |
| [Phase 5](./phase-5-testing-launch.md) | 集成测试与上线 | E2E 测试、性能优化、微信提审发布 | 全部 |

## 测试策略

| 层级 | 工具 | 说明 |
|------|------|------|
| 后端单元测试 | pytest + pytest-asyncio | Service 层逻辑、数据模型验证，覆盖率 ≥ 85% |
| 后端接口测试 | httpx.AsyncClient + TestClient | API 端点请求/响应/鉴权/错误码验证 |
| 后端 Mock | respx (HTTP mock) | 微信 API、短信 API |
| 前端单元测试 | Jest + React Testing Library | 组件渲染、交互、状态管理，覆盖率 ≥ 75% |
| 前端 API Mock | MSW (Mock Service Worker) | API 请求模拟，拦截 Taro.request |
| 前端 Hook 测试 | @testing-library/react-hooks | useAuth、usePagination 等 |
| CI 流水线 | GitHub Actions | 每次 push 执行 `pytest --cov` + `jest --coverage` |

### 测试目录约定

```
# 后端
mini-contract-api/
├── tests/
│   ├── conftest.py              ← pytest fixtures（DB session、test client、mock user）
│   ├── unit/
│   │   ├── test_auth_service.py
│   │   ├── test_seal_service.py
│   │   ├── test_contract_service.py
│   │   └── test_template_service.py
│   ├── api/
│   │   ├── test_auth_api.py
│   │   ├── test_seal_api.py
│   │   ├── test_contract_api.py
│   │   └── test_template_api.py
│   └── integration/
│       └── test_contract_signing_flow.py

# 前端
mini-contract-taro/
├── src/
│   ├── __tests__/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── pages/
│   │   └── stores/
│   └── ...
```

## 附录

- [附录 A：MVP 数据库表清单](./appendix-a-database.md)
- [附录 B：MVP 技术依赖](./appendix-b-dependencies.md)
- [附录 C：后续版本路线图](./appendix-c-roadmap.md)
