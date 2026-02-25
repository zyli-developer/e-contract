# FastAPI 最佳实践模式

## Router 组织模式

### 基础 Router 结构

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import crud, schemas
from app.dependencies import get_db

router = APIRouter()

@router.get("/users", response_model=List[schemas.User])
def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取用户列表"""
    users = crud.user.get_multi(db, skip=skip, limit=limit)
    return users

@router.get("/users/{user_id}", response_model=schemas.User)
def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """获取单个用户"""
    user = crud.user.get(db, id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/users", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    """创建用户"""
    # TODO: Implement business logic
    user = crud.user.create(db, obj_in=user_in)
    return user

@router.put("/users/{user_id}", response_model=schemas.User)
def update_user(
    user_id: int,
    user_in: schemas.UserUpdate,
    db: Session = Depends(get_db)
):
    """更新用户"""
    user = crud.user.get(db, id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user = crud.user.update(db, db_obj=user, obj_in=user_in)
    return user

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """删除用户"""
    user = crud.user.get(db, id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    crud.user.remove(db, id=user_id)
    return None
```

## CRUD 模式

### 基础 CRUD 类

```python
from typing import Generic, TypeVar, Type, Optional, List, Any, Dict, Union
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from app.database import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> ModelType:
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj
```

### 特定资源的 CRUD

```python
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    # 添加其他特定于 User 的方法
    # TODO: Implement custom methods

user = CRUDUser(User)
```

## 依赖注入模式

### 数据库 Session
```python
from app.database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 分页
```python
from fastapi import Query

class CommonQueryParams:
    def __init__(
        self,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=100)
    ):
        self.skip = skip
        self.limit = limit

@router.get("/users")
def get_users(
    commons: CommonQueryParams = Depends(),
    db: Session = Depends(get_db)
):
    return crud.user.get_multi(db, skip=commons.skip, limit=commons.limit)
```

### 认证（占位符）
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def get_current_user(
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    # TODO: Implement JWT validation
    # credentials_exception = HTTPException(
    #     status_code=status.HTTP_401_UNAUTHORIZED,
    #     detail="Could not validate credentials",
    # )
    # Decode token, get user
    pass
```

## 错误处理模式

### 自定义异常
```python
class ItemNotFoundError(Exception):
    def __init__(self, item_id: int):
        self.item_id = item_id

@app.exception_handler(ItemNotFoundError)
async def item_not_found_handler(request, exc: ItemNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": f"Item {exc.item_id} not found"}
    )
```

### 统一错误响应
```python
from fastapi import HTTPException

def raise_not_found(item: str, id: int):
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{item} with id {id} not found"
    )

# 使用
user = crud.user.get(db, id=user_id)
if not user:
    raise_not_found("User", user_id)
```

## 响应模型模式

### 基础响应
```python
from pydantic import BaseModel
from typing import Generic, TypeVar

T = TypeVar('T')

class ResponseBase(BaseModel, Generic[T]):
    code: int = 200
    message: str = "Success"
    data: T

# 使用
@router.get("/users/{user_id}", response_model=ResponseBase[schemas.User])
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return ResponseBase(data=user)
```

### 分页响应
```python
class PaginatedResponse(BaseModel, Generic[T]):
    total: int
    skip: int
    limit: int
    items: List[T]

@router.get("/users", response_model=PaginatedResponse[schemas.User])
def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    total = db.query(models.User).count()
    items = crud.user.get_multi(db, skip=skip, limit=limit)
    return PaginatedResponse(total=total, skip=skip, limit=limit, items=items)
```

## 验证模式

### Schema 级别验证
```python
from pydantic import BaseModel, EmailStr, Field, validator

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    age: int = Field(..., ge=0, le=150)

    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Name must not be empty')
        return v.strip()
```

### Router 级别验证
```python
@router.post("/users", response_model=schemas.User)
def create_user(
    user_in: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    # 检查邮箱是否已存在
    existing_user = crud.user.get_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    return crud.user.create(db, obj_in=user_in)
```

## 关系处理模式

### 一对多
```python
# Model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    posts = relationship("Post", back_populates="author")

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    author_id = Column(Integer, ForeignKey("users.id"))
    author = relationship("User", back_populates="posts")

# Schema (响应)
class User(UserBase):
    id: int
    posts: List[Post] = []  # 包含关联的 posts

    class Config:
        from_attributes = True

# CRUD (eager loading)
def get_with_posts(db: Session, user_id: int):
    return db.query(User).options(joinedload(User.posts)).filter(User.id == user_id).first()
```

## 测试模式

### API 测试
```python
from fastapi.testclient import TestClient

def test_create_user(client: TestClient):
    response = client.post(
        "/api/users",
        json={"name": "Test User", "email": "test@example.com"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data

def test_get_user(client: TestClient, db: Session):
    # 创建测试数据
    user = crud.user.create(db, obj_in=UserCreate(name="Test", email="test@test.com"))

    # 测试获取
    response = client.get(f"/api/users/{user.id}")
    assert response.status_code == 200
    assert response.json()["email"] == "test@test.com"
```

### CRUD 测试
```python
def test_create_user(db: Session):
    user_in = UserCreate(name="Test", email="test@test.com")
    user = crud.user.create(db, obj_in=user_in)
    assert user.email == "test@test.com"
    assert user.id is not None

def test_get_user(db: Session):
    user_in = UserCreate(name="Test", email="test@test.com")
    user = crud.user.create(db, obj_in=user_in)
    fetched_user = crud.user.get(db, id=user.id)
    assert fetched_user
    assert fetched_user.email == user.email
```

## 性能优化模式

### 使用 select_in loading
```python
from sqlalchemy.orm import selectinload

# 避免 N+1 查询
users = db.query(User).options(selectinload(User.posts)).all()
```

### 批量操作
```python
def create_bulk(db: Session, *, objs_in: List[CreateSchemaType]) -> List[ModelType]:
    db_objs = [self.model(**jsonable_encoder(obj)) for obj in objs_in]
    db.bulk_save_objects(db_objs)
    db.commit()
    return db_objs
```

### 缓存
```python
from functools import lru_cache

@lru_cache()
def get_settings():
    return Settings()

# 使用
settings = get_settings()
```
