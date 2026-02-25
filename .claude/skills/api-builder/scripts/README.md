# API Builder Scripts

这些脚本用于从 OpenAPI 规范生成 FastAPI 代码。

## 核心脚本

### 1. `validate_spec.py`
验证 OpenAPI spec 的格式、版本和必需字段。

**用法**：
```bash
python3 validate_spec.py <spec-file>
```

**示例**：
```bash
python3 validate_spec.py petstore.yaml
```

**输出**：
- ✅ 验证通过 (exit code 0)
- ❌ 验证失败 (exit code 1)

---

### 2. `parse_openapi.py`
解析 OpenAPI YAML/JSON 文件，提取 schemas 和 paths 信息，输出结构化 JSON。

**用法**：
```bash
python3 parse_openapi.py <spec-file> [--output parsed.json]
```

**示例**：
```bash
# 输出到 stdout
python3 parse_openapi.py petstore.yaml

# 输出到文件
python3 parse_openapi.py petstore.yaml --output parsed.json
```

**输出格式**：
```json
{
  "openapi_version": "3.0.0",
  "info": {...},
  "schemas": {...},
  "paths": {...}
}
```

---

### 3. `generate_code.py`
使用 Jinja2 模板生成 FastAPI 代码文件（models, schemas, routers）。

**用法**：
```bash
python3 generate_code.py \
  --parsed-data parsed.json \
  --output-dir ./app \
  --templates-dir ../assets/templates
```

**示例**：
```bash
python3 generate_code.py \
  --parsed-data parsed.json \
  --output-dir ./generated \
  --templates-dir ../assets/templates
```

**生成内容**：
- `models/` - SQLAlchemy 模型
- `schemas/` - Pydantic schemas
- `routers/` - FastAPI 路由

---

### 4. `generate_client.py`
生成 Next.js TypeScript API 客户端。

**用法**：
```bash
python3 generate_client.py \
  --parsed-data parsed.json \
  --output api-client.ts \
  --templates-dir ../assets/templates
```

**示例**：
```bash
python3 generate_client.py \
  --parsed-data parsed.json \
  --output ./frontend/lib/api/api-client.ts
```

**生成内容**：
- TypeScript接口定义
- API调用方法
- 错误处理
- 客户端实例

---

### 5. `cli.py` (推荐使用)
完整的 API 生成流程编排工具，整合上述所有脚本。

**用法**：
```bash
python3 cli.py --spec <spec-file> --output <output-dir> [options]
```

**选项**：
- `--spec FILE` - OpenAPI 规范文件（必需）
- `--output DIR` - 输出目录（默认：./generated）
- `--templates DIR` - 模板目录（默认：../assets/templates）
- `--skip-validation` - 跳过验证
- `--resources LIST` - 只生成指定资源（逗号分隔）
- `--generate-client` - 生成 Next.js TypeScript 客户端
- `--client-output FILE` - 客户端输出文件（默认：<output>/api-client.ts）
- `--setup-alembic` - 配置 Alembic 数据库迁移
- `--run-migrations` - 运行 Alembic 数据库迁移
- `--migration-message TEXT` - 迁移消息（默认："Auto-generated migration"）

**示例**：
```bash
# 生成全部 endpoints
python3 cli.py --spec petstore.yaml --output ./app

# 只生成 users 和 posts
python3 cli.py --spec api.yaml --output ./app --resources users,posts

# 跳过验证
python3 cli.py --spec api.yaml --output ./app --skip-validation

# 生成后端 + 前端client
python3 cli.py --spec api.yaml --output ./backend --generate-client

# 指定client输出位置
python3 cli.py --spec api.yaml --output ./backend --generate-client --client-output ../frontend/lib/api/api-client.ts

# 生成后端 + 配置数据库迁移
python3 cli.py --spec api.yaml --output ./backend --setup-alembic

# 生成后端 + 自动运行迁移
python3 cli.py --spec api.yaml --output ./backend --setup-alembic --run-migrations
```

**执行流程**：
1. 验证 OpenAPI spec
2. 解析 spec
3. 过滤资源（如果指定）
4. 生成后端代码（models, schemas, routers）
5. 创建 __init__.py 文件
6. 生成前端client（如果启用 --generate-client）
7. 配置 Alembic（如果启用 --setup-alembic）
8. 运行数据库迁移（如果启用 --run-migrations）
9. 打印摘要

---

## 测试

### `test_scripts.py`
完整的测试套件，验证所有脚本功能。

**用法**：
```bash
python3 test_scripts.py
```

**测试内容**：
1. validate_spec.py - 验证功能
2. parse_openapi.py - 解析功能
3. generate_code.py - 后端代码生成
4. cli.py - 端到端测试
5. generate_client.py - TypeScript客户端生成
6. cli.py with --generate-client - 集成测试
7. cli.py with --setup-alembic - Alembic配置测试

**测试结果**：
- ✅ 7/7 测试通过 (exit code 0)
- ❌ 有测试失败 (exit code 1)

---

## 依赖

确保安装了以下 Python 包：
```bash
pip install pyyaml jinja2
# 或使用 uv
uv pip install pyyaml jinja2
```

---

## 工作流程

### 方式 1：使用 CLI（推荐）
```bash
# 一键生成
python3 cli.py --spec your-api.yaml --output ./generated
```

### 方式 2：分步执行
```bash
# 1. 验证
python3 validate_spec.py your-api.yaml

# 2. 解析
python3 parse_openapi.py your-api.yaml --output parsed.json

# 3. 生成代码
python3 generate_code.py \
  --parsed-data parsed.json \
  --output-dir ./generated \
  --templates-dir ../assets/templates
```

---

## 数据库迁移

### 自动迁移（推荐）

生成代码时自动配置并运行迁移：
```bash
python3 cli.py \
  --spec api.yaml \
  --output ./backend \
  --setup-alembic \
  --run-migrations
```

这会：
1. 复制 Alembic 配置文件到输出目录
2. 自动生成迁移脚本（基于生成的models）
3. 应用迁移到数据库

### 手动迁移

如果只想配置 Alembic（稍后手动运行迁移）：
```bash
# 1. 配置 Alembic
python3 cli.py --spec api.yaml --output ./backend --setup-alembic

# 2. 进入项目目录
cd backend

# 3. 生成迁移
alembic revision --autogenerate -m "Initial migration"

# 4. 应用迁移
alembic upgrade head
```

### 迁移场景

#### 场景1：全新项目
```bash
# 生成代码并立即创建数据库
python3 cli.py --spec api.yaml --output ./backend --setup-alembic --run-migrations
```

#### 场景2：已有项目，添加新字段
```bash
# 1. 修改 OpenAPI 规范（添加新字段）
vim api.yaml

# 2. 重新生成代码
python3 cli.py --spec api.yaml --output ./backend

# 3. 生成并运行迁移
cd backend
alembic revision --autogenerate -m "Add new fields"
alembic upgrade head
```

#### 场景3：Schema 变更
当你修改 OpenAPI 规范后：
- 添加字段：Alembic 自动添加列
- 删除字段：Alembic 生成 drop column
- 修改类型：Alembic 生成 alter column
- 重命名表/列：需要手动编辑迁移文件

### 迁移文件位置
```
backend/
├── alembic/
│   ├── versions/          # 迁移文件目录
│   │   └── xxxx_initial.py
│   ├── env.py
│   └── script.py.mako
├── alembic.ini            # Alembic 配置
└── models/                # SQLAlchemy 模型
```

---

## TypeScript Client 使用

### Next.js集成
```typescript
// app/users/page.tsx
import { apiClient } from '@/lib/api/api-client'

export default async function UsersPage() {
  const users = await apiClient.list_users()

  return (
    <div>
      {users.map(user => (
        <div key={user.id}>
          <h3>{user.name}</h3>
          <p>{user.email}</p>
        </div>
      ))}
    </div>
  )
}
```

### 环境配置
```bash
# frontend/.env.development (开发环境)
API_URL=http://localhost:8000/api

# frontend/.env.local (本地覆盖，可选)
API_URL=https://custom-api.example.com/api
```

> 注意：API_URL 通过 `lib/env.ts` 在服务端读取，并通过 `layout.tsx` 注入到客户端的 `window.__ENV__`。

### 类型映射
| OpenAPI | TypeScript |
|---------|------------|
| string | string |
| integer/number | number |
| boolean | boolean |
| array | Array<T> |
| nullable | T \| null |

---

## 设计原则

这些脚本遵循 **确定性自动化** 原则：
- ✅ 相同输入 → 相同输出
- ✅ 可测试、可调试
- ✅ Token 高效（避免重复编写）
- ✅ 独立可运行

Claude 在使用 api-builder skill 时会调用这些脚本，而不是动态生成解析逻辑。

---

## 示例输出

查看 `test_spec.yaml` 和运行 `test_scripts.py` 可以看到完整的测试示例。

### 后端代码结构
```
generated/
├── models/
│   ├── __init__.py
│   ├── user.py          # SQLAlchemy 模型
│   └── usercreate.py
├── schemas/
│   ├── __init__.py
│   ├── user.py          # Pydantic schemas
│   └── usercreate.py
├── routers/
│   ├── __init__.py
│   └── users.py         # FastAPI 路由（3个endpoints）
└── parsed.json          # 解析后的spec数据
```

### TypeScript客户端（使用 --generate-client）
```typescript
// api-client.ts
export interface User {
  id: number;
  name: string;
  email: string;
  created_at?: string;
}

class ApiClient {
  async list_users(): Promise<User[]> { ... }
  async create_user(body: UserCreate): Promise<User> { ... }
  async get_user(id: number): Promise<User> { ... }
}

export const apiClient = new ApiClient();
```

### 代码统计
- **核心脚本**: 5个文件，约1860行Python代码
- **生成代码**: 从test_spec.yaml生成
  - 后端: 2 models + 2 schemas + 1 router
  - 前端: 1 TypeScript client（可选）
- **测试覆盖**: 6个测试，100%通过
