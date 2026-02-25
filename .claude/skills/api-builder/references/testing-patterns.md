# 测试模式和最佳实践

## 测试结构

```
tests/
├── __init__.py
├── conftest.py                 # pytest 配置和共享 fixtures
├── test_api/                   # API 集成测试
│   ├── __init__.py
│   ├── test_users_api.py
│   └── test_posts_api.py
└── test_crud/                  # CRUD 单元测试
    ├── __init__.py
    ├── test_user_crud.py
    └── test_post_crud.py
```

## Conftest.py 配置

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app import models, schemas, crud

# 使用 in-memory SQLite 数据库进行测试
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def engine():
    """创建测试数据库引擎"""
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # 保持 in-memory 数据库不被关闭
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db(engine):
    """创建测试数据库 session"""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function")
def client(db):
    """创建测试客户端"""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture
def sample_user_data():
    """示例用户数据"""
    return {
        "name": "Test User",
        "email": "test@example.com",
        "age": 25
    }

@pytest.fixture
def create_sample_user(db, sample_user_data):
    """创建示例用户（fixture）"""
    user = crud.user.create(
        db,
        obj_in=schemas.UserCreate(**sample_user_data)
    )
    return user
```

## API 集成测试模式

### 基础 CRUD 测试

```python
# tests/test_api/test_users_api.py
from fastapi import status

class TestUserAPI:
    """用户 API 测试"""

    def test_create_user_success(self, client, sample_user_data):
        """测试创建用户 - 成功"""
        response = client.post("/api/users", json=sample_user_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == sample_user_data["name"]
        assert data["email"] == sample_user_data["email"]
        assert "id" in data
        assert "created_at" in data

    def test_create_user_invalid_email(self, client):
        """测试创建用户 - 无效邮箱"""
        response = client.post(
            "/api/users",
            json={"name": "Test", "email": "invalid-email"}
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_user_duplicate_email(self, client, create_sample_user, sample_user_data):
        """测试创建用户 - 邮箱重复"""
        response = client.post("/api/users", json=sample_user_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in response.json()["detail"].lower()

    def test_get_user_success(self, client, create_sample_user):
        """测试获取用户 - 成功"""
        user = create_sample_user
        response = client.get(f"/api/users/{user.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == user.id
        assert data["email"] == user.email

    def test_get_user_not_found(self, client):
        """测试获取用户 - 不存在"""
        response = client.get("/api/users/99999")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    def test_get_users_list(self, client, db):
        """测试获取用户列表"""
        # 创建多个用户
        for i in range(5):
            crud.user.create(
                db,
                obj_in=schemas.UserCreate(
                    name=f"User {i}",
                    email=f"user{i}@example.com"
                )
            )

        response = client.get("/api/users")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 5

    def test_get_users_pagination(self, client, db):
        """测试分页"""
        # 创建 10 个用户
        for i in range(10):
            crud.user.create(
                db,
                obj_in=schemas.UserCreate(
                    name=f"User {i}",
                    email=f"user{i}@example.com"
                )
            )

        response = client.get("/api/users?skip=5&limit=3")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3

    def test_update_user_success(self, client, create_sample_user):
        """测试更新用户 - 成功"""
        user = create_sample_user
        update_data = {"name": "Updated Name"}

        response = client.put(f"/api/users/{user.id}", json=update_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["email"] == user.email  # 未改变

    def test_update_user_not_found(self, client):
        """测试更新用户 - 不存在"""
        response = client.put("/api/users/99999", json={"name": "New"})

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_user_success(self, client, create_sample_user):
        """测试删除用户 - 成功"""
        user = create_sample_user

        response = client.delete(f"/api/users/{user.id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # 验证已删除
        get_response = client.get(f"/api/users/{user.id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_user_not_found(self, client):
        """测试删除用户 - 不存在"""
        response = client.delete("/api/users/99999")

        assert response.status_code == status.HTTP_404_NOT_FOUND
```

### 关系测试

```python
def test_get_user_with_posts(client, db):
    """测试获取用户及其帖子"""
    # 创建用户
    user = crud.user.create(
        db,
        obj_in=schemas.UserCreate(name="Test", email="test@test.com")
    )

    # 创建帖子
    for i in range(3):
        crud.post.create(
            db,
            obj_in=schemas.PostCreate(
                title=f"Post {i}",
                content=f"Content {i}",
                author_id=user.id
            )
        )

    response = client.get(f"/api/users/{user.id}?include=posts")

    assert response.status_code == 200
    data = response.json()
    assert len(data["posts"]) == 3
```

## CRUD 单元测试模式

```python
# tests/test_crud/test_user_crud.py
from app import crud, schemas

class TestUserCRUD:
    """用户 CRUD 测试"""

    def test_create_user(self, db):
        """测试创建用户"""
        user_in = schemas.UserCreate(
            name="Test User",
            email="test@example.com"
        )
        user = crud.user.create(db, obj_in=user_in)

        assert user.name == "Test User"
        assert user.email == "test@example.com"
        assert user.id is not None

    def test_get_user(self, db):
        """测试获取用户"""
        user_in = schemas.UserCreate(name="Test", email="test@test.com")
        created_user = crud.user.create(db, obj_in=user_in)

        fetched_user = crud.user.get(db, id=created_user.id)

        assert fetched_user is not None
        assert fetched_user.id == created_user.id
        assert fetched_user.email == created_user.email

    def test_get_user_not_found(self, db):
        """测试获取不存在的用户"""
        user = crud.user.get(db, id=99999)
        assert user is None

    def test_get_user_by_email(self, db):
        """测试通过邮箱获取用户"""
        user_in = schemas.UserCreate(name="Test", email="unique@test.com")
        created_user = crud.user.create(db, obj_in=user_in)

        fetched_user = crud.user.get_by_email(db, email="unique@test.com")

        assert fetched_user is not None
        assert fetched_user.id == created_user.id

    def test_get_multi_users(self, db):
        """测试获取多个用户"""
        # 创建 5 个用户
        for i in range(5):
            crud.user.create(
                db,
                obj_in=schemas.UserCreate(name=f"User {i}", email=f"user{i}@test.com")
            )

        users = crud.user.get_multi(db, skip=0, limit=10)

        assert len(users) == 5

    def test_get_multi_with_pagination(self, db):
        """测试分页"""
        # 创建 10 个用户
        for i in range(10):
            crud.user.create(
                db,
                obj_in=schemas.UserCreate(name=f"User {i}", email=f"user{i}@test.com")
            )

        users = crud.user.get_multi(db, skip=5, limit=3)

        assert len(users) == 3

    def test_update_user(self, db):
        """测试更新用户"""
        user_in = schemas.UserCreate(name="Original", email="test@test.com")
        user = crud.user.create(db, obj_in=user_in)

        update_data = schemas.UserUpdate(name="Updated")
        updated_user = crud.user.update(db, db_obj=user, obj_in=update_data)

        assert updated_user.name == "Updated"
        assert updated_user.email == "test@test.com"  # 未改变

    def test_delete_user(self, db):
        """测试删除用户"""
        user_in = schemas.UserCreate(name="Test", email="test@test.com")
        user = crud.user.create(db, obj_in=user_in)

        crud.user.remove(db, id=user.id)

        deleted_user = crud.user.get(db, id=user.id)
        assert deleted_user is None
```

## 参数化测试

```python
import pytest

@pytest.mark.parametrize("name,email,expected_valid", [
    ("Valid User", "valid@example.com", True),
    ("", "valid@example.com", False),  # 空名字
    ("Valid User", "invalid-email", False),  # 无效邮箱
    ("A" * 101, "valid@example.com", False),  # 名字过长
])
def test_user_validation(client, name, email, expected_valid):
    """参数化测试用户验证"""
    response = client.post(
        "/api/users",
        json={"name": name, "email": email}
    )

    if expected_valid:
        assert response.status_code == status.HTTP_201_CREATED
    else:
        assert response.status_code in [
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST
        ]
```

## Mock 和 Patch

```python
from unittest.mock import patch, MagicMock

def test_external_api_call(client):
    """测试外部 API 调用（使用 mock）"""
    with patch('app.services.external_api.call') as mock_call:
        mock_call.return_value = {"data": "mocked"}

        response = client.get("/api/external-data")

        assert response.status_code == 200
        assert response.json()["data"] == "mocked"
        mock_call.assert_called_once()
```

## 异步测试

```python
import pytest

@pytest.mark.asyncio
async def test_async_endpoint(client):
    """测试异步 endpoint"""
    response = await client.get("/api/async-data")
    assert response.status_code == 200
```

## 测试覆盖率

运行测试并生成覆盖率报告：

```bash
# 安装 pytest-cov
uv add --dev pytest-cov

# 运行测试并生成覆盖率
pytest --cov=app --cov-report=html tests/

# 查看覆盖率报告
open htmlcov/index.html
```

## 测试命名约定

- **测试类**: `Test<ResourceName><Type>`
  - 例如：`TestUserAPI`, `TestUserCRUD`

- **测试方法**: `test_<action>_<scenario>`
  - 例如：`test_create_user_success`, `test_get_user_not_found`

## 测试组织最佳实践

1. **Arrange-Act-Assert (AAA) 模式**
```python
def test_example(db):
    # Arrange（准备）
    user_in = schemas.UserCreate(name="Test", email="test@test.com")

    # Act（执行）
    user = crud.user.create(db, obj_in=user_in)

    # Assert（断言）
    assert user.email == "test@test.com"
```

2. **使用 Fixtures 减少重复代码**
3. **每个测试只测试一个功能点**
4. **测试名称要清晰描述测试内容**
5. **使用参数化测试处理多个类似场景**

## 持续集成示例

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          pip install uv
          uv sync
      - name: Run tests
        run: |
          uv run pytest --cov=app tests/
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```
