# Mini Contract.Pro

> 电子合同签署微信小程序 — 创建合同 → 发送给签署方 → 签署方登录查看 → 签署 → 合同生效

## 技术栈

| 端 | 技术 |
|------|------|
| 后端 | Python 3.11+ / FastAPI / SQLAlchemy 2.0 / MySQL / Redis |
| 前端 | Taro 4.x / React 18 / TypeScript / Zustand / NutUI-React |
| 运行载体 | 微信小程序 / H5 |

## 项目结构

```
e-contract/
├── mini-contract-api/         ← 后端 (FastAPI)
│   ├── app/
│   │   ├── main.py            # 应用入口
│   │   ├── config.py          # 配置管理
│   │   ├── database.py        # 数据库连接
│   │   ├── dependencies.py    # 依赖注入
│   │   ├── models/            # SQLAlchemy 数据模型 (10 张 MVP 表)
│   │   ├── schemas/           # Pydantic 请求/响应模型
│   │   ├── api/v1/            # API 路由
│   │   ├── services/          # 业务逻辑层
│   │   ├── core/              # 基础设施 (JWT, 异常, 响应, 中间件)
│   │   └── utils/             # 工具函数
│   ├── alembic/               # 数据库迁移
│   ├── tests/                 # 测试 (unit/api/integration)
│   ├── requirements.txt
│   └── .env.example
│
├── mini-contract-taro/        ← 前端 (Taro + React)
│   ├── src/
│   │   ├── pages/             # 页面组件 (12 个页面)
│   │   ├── components/        # 通用组件
│   │   ├── api/               # API 请求层 (统一封装 + Token 刷新)
│   │   ├── store/             # Zustand 状态管理
│   │   ├── hooks/             # 自定义 Hooks
│   │   ├── utils/             # 工具函数
│   │   └── config/            # 应用配置
│   ├── config/                # Taro 编译配置
│   ├── project.config.json    # 微信小程序配置
│   ├── package.json
│   └── tsconfig.json
│
└── docs/                      ← 项目文档
    ├── dev/                   # 开发计划 (Phase 0-5)
    ├── 业务模块/               # 业务需求文档
    ├── 后端技术/               # 后端技术方案
    ├── 前端技术/               # 前端技术方案
    └── API参考/                # 接口清单
```

## 快速开始

### 后端

```bash
cd mini-contract-api

# 创建虚拟环境
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env，填入数据库、Redis、微信等配置

# 数据库迁移
alembic upgrade head

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# API 文档: http://localhost:8000/docs
```

### 前端

```bash
cd mini-contract-taro

# 安装依赖
pnpm install

# 微信小程序开发模式
pnpm run dev:weixin
# 在微信开发者工具中导入 dist/ 目录

# H5 开发模式
pnpm run dev:h5
```

### 测试

```bash
# 后端测试
cd mini-contract-api && pytest --cov

# 前端测试
cd mini-contract-taro && pnpm test
```

## 开发计划

详见 [docs/dev/README.md](./docs/dev/README.md)

| 阶段 | 名称 | 核心内容 |
|------|------|---------|
| Phase 0 | 基础设施搭建 | 项目骨架、数据库、CI/CD |
| Phase 1 | 用户认证 | 微信登录、短信登录、双 Token |
| Phase 2 | 个人签名与 Seal Token | 手绘签名、Seal Token 认证 |
| Phase 3 | 合同模板与创建 | 模板市场、合同创建、指定签署方 |
| Phase 4 | 合同签署与管理 | H5 签署、状态机、证据链 |
| Phase 5 | 集成测试与上线 | E2E 测试、微信提审发布 |

## 法律合规

- 签署意愿验证：签署前短信验证码确认
- 文档防篡改：SHA-256 哈希校验
- 签署证据链：操作时间戳 + 用户 + IP + 设备信息
