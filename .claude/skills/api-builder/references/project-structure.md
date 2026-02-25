# FastAPI 项目结构

## 推荐的模块化结构

```
project/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 应用入口
│   ├── database.py             # 数据库配置和 session
│   ├── dependencies.py         # 依赖注入
│   ├── config.py               # 配置管理
│   │
│   ├── models/                 # SQLAlchemy 模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── post.py
│   │   └── ...
│   │
│   ├── schemas/                # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── post.py
│   │   └── ...
│   │
│   ├── routers/                # API 路由
│   │   ├── __init__.py
│   │   ├── users.py
│   │   ├── posts.py
│   │   └── ...
│   │
│   └── crud/                   # CRUD 操作
│       ├── __init__.py
│       ├── base.py             # CRUD 基类
│       ├── user.py
│       ├── post.py
│       └── ...
│
├── alembic/                    # 数据库迁移
│   ├── versions/
│   │   └── xxxx_initial.py
│   ├── env.py
│   └── script.py.mako
│
├── tests/                      # 测试
│   ├── __init__.py
│   ├── conftest.py             # pytest 配置和 fixtures
│   ├── test_users.py
│   ├── test_posts.py
│   └── ...
│
├── .env                        # 环境变量（不提交）
├── .env.example                # 环境变量示例
├── alembic.ini                 # Alembic 配置
├── pyproject.toml              # 项目配置（uv）
└── README.md
```

## 文件说明

### `app/main.py`
FastAPI 应用入口，注册路由和中间件。

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import users, posts
from app.database import engine, Base

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="My API",
    description="Generated from OpenAPI spec",
    version="1.0.0"
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(users.router, prefix="/api", tags=["users"])
app.include_router(posts.router, prefix="/api", tags=["posts"])

@app.get("/")
def root():
    return {"message": "API is running"}
```

### `app/database.py`
数据库连接和 session 管理。

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./app.db"
)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite only
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """数据库依赖注入"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### `app/dependencies.py`
通用依赖注入。

```python
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db

# 示例：认证依赖
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    # TODO: Implement authentication
    pass
```

### `app/config.py`
配置管理（使用 pydantic-settings）。

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "My API"
    database_url: str = "sqlite:///./app.db"
    secret_key: str = "your-secret-key"

    class Config:
        env_file = ".env"

settings = Settings()
```

## 目录组织原则

### 按资源分组
每个资源（如 User, Post）有对应的：
- `models/user.py` - 数据库模型
- `schemas/user.py` - API schemas
- `routers/user.py` - API 路由
- `crud/user.py` - CRUD 操作

### 命名约定
- **Models**: 单数，大写开头（`User`, `Post`）
- **Schemas**:
  - `UserBase` - 共享属性
  - `UserCreate` - 创建请求
  - `UserUpdate` - 更新请求
  - `User` - 响应（包含 id 等）
- **Routers**: 复数，小写（`users.py`, `posts.py`）
- **CRUD**: 单数，小写（`user.py`, `post.py`）

### 导入约定
```python
# models/user.py
from app.database import Base  # 相对根目录

# routers/users.py
from app import models, schemas, crud
from app.dependencies import get_db
```

## 集成到现有项目

### 检测现有结构
1. 查找 `app/` 或 `src/` 目录
2. 检查是否已有 `database.py`
3. 检查是否已有 `routers/` 目录

### 集成策略
- **已有 `app/routers/`**：直接添加新路由文件
- **已有 `database.py`**：复用现有配置
- **不同结构**：询问用户是否调整或适配

### 避免冲突
- 生成前检查文件是否存在
- 如果存在，询问用户：
  - 覆盖
  - 合并（追加内容）
  - 跳过
  - 重命名（如 `users_v2.py`）

## Next.js Client 集成

生成的 TypeScript client 建议放置：

```
nextjs-project/
├── lib/
│   └── api/
│       ├── client.ts          # API client 配置
│       ├── types.ts           # TypeScript 类型定义
│       └── endpoints/         # 各个 endpoint 的函数
│           ├── users.ts
│           └── posts.ts
│
└── app/                       # App Router
    └── (routes)/
```

### 使用示例
```typescript
// app/users/page.tsx
import { getUsers } from '@/lib/api/endpoints/users';

export default async function UsersPage() {
  const users = await getUsers();
  return <div>{/* render users */}</div>;
}
```

## 测试结构

```
tests/
├── conftest.py                # pytest 配置
├── test_api/                  # API 集成测试
│   ├── test_users.py
│   └── test_posts.py
└── test_crud/                 # CRUD 单元测试
    ├── test_user_crud.py
    └── test_post_crud.py
```

### conftest.py
```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)
```
