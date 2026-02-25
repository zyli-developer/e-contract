# OpenAPI 到 Python/TypeScript 类型映射

## OpenAPI 到 Python (Pydantic/SQLAlchemy)

### 基础类型

| OpenAPI Type | Format | Pydantic | SQLAlchemy | 说明 |
|--------------|--------|----------|------------|------|
| string | - | str | String | 字符串 |
| string | date | date | Date | 日期 (YYYY-MM-DD) |
| string | date-time | datetime | DateTime | 日期时间 (ISO 8601) |
| string | email | EmailStr | String | 邮箱（需要 pydantic[email]） |
| string | uri | AnyUrl | String | URL |
| string | uuid | UUID | String(36) | UUID |
| string | password | SecretStr | String | 密码（不在响应中显示） |
| integer | - | int | Integer | 整数 |
| integer | int32 | int | Integer | 32位整数 |
| integer | int64 | int | BigInteger | 64位整数 |
| number | - | float | Float | 浮点数 |
| number | float | float | Float | 单精度浮点 |
| number | double | float | Double | 双精度浮点 |
| boolean | - | bool | Boolean | 布尔值 |
| array | - | List[T] | ARRAY (PostgreSQL) or JSON | 数组 |
| object | - | Dict[str, Any] | JSON | 对象/字典 |

### 特殊类型

| OpenAPI | Pydantic | SQLAlchemy | 说明 |
|---------|----------|------------|------|
| nullable: true | Optional[T] | nullable=True | 可空字段 |
| enum | Enum | Enum | 枚举类型 |
| anyOf/oneOf | Union[A, B] | - | 联合类型 |
| allOf | 继承 | - | 组合模式 |

### 约束映射

| OpenAPI 约束 | Pydantic | SQLAlchemy |
|--------------|----------|------------|
| minLength | Field(min_length=N) | String(N) |
| maxLength | Field(max_length=N) | String(N) |
| minimum | Field(ge=N) | - |
| maximum | Field(le=N) | - |
| pattern | Field(regex="...") | - |
| default | Field(default=X) | default=X |
| required | (必填) | nullable=False |

## OpenAPI 到 TypeScript (Next.js Client)

### 基础类型

| OpenAPI Type | Format | TypeScript |
|--------------|--------|------------|
| string | - | string |
| string | date | string |
| string | date-time | string |
| string | email | string |
| string | uri | string |
| string | uuid | string |
| integer | - | number |
| number | - | number |
| boolean | - | boolean |
| array | - | Array<T> |
| object | - | object / Record<string, any> |
| nullable | - | T \| null |
| enum | - | enum 或 union type |

### 示例映射

#### OpenAPI Schema
```yaml
components:
  schemas:
    User:
      type: object
      required:
        - name
        - email
      properties:
        id:
          type: integer
          format: int64
        name:
          type: string
          minLength: 1
          maxLength: 100
        email:
          type: string
          format: email
        age:
          type: integer
          minimum: 0
          maximum: 150
        created_at:
          type: string
          format: date-time
        status:
          type: string
          enum: [active, inactive, banned]
```

#### Pydantic Schema
```python
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from enum import Enum
from typing import Optional

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BANNED = "banned"

class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    age: Optional[int] = Field(None, ge=0, le=150)
    status: UserStatus = UserStatus.ACTIVE

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    age: Optional[int] = Field(None, ge=0, le=150)
    status: Optional[UserStatus] = None

class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
```

#### SQLAlchemy Model
```python
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from .database import Base
import enum

class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BANNED = "banned"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    age = Column(Integer, nullable=True)
    status = Column(SQLEnum(UserStatus), default=UserStatus.ACTIVE, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
```

#### TypeScript Type
```typescript
export enum UserStatus {
  ACTIVE = "active",
  INACTIVE = "inactive",
  BANNED = "banned",
}

export interface UserBase {
  name: string;
  email: string;
  age?: number;
  status?: UserStatus;
}

export interface UserCreate extends UserBase {}

export interface UserUpdate {
  name?: string;
  email?: string;
  age?: number;
  status?: UserStatus;
}

export interface User extends UserBase {
  id: number;
  created_at: string;
  status: UserStatus;
}
```

## 数据库索引建议

根据 OpenAPI schema 自动生成索引：

| 场景 | 添加索引 |
|------|----------|
| `uniqueItems: true` (array) | UNIQUE 约束 |
| `format: email` | INDEX (用于查询) |
| 外键字段 | INDEX |
| `x-indexed: true` (自定义扩展) | INDEX |
| primary key | PRIMARY KEY, INDEX |

## 默认值处理

| OpenAPI | Pydantic | SQLAlchemy | 说明 |
|---------|----------|------------|------|
| default: "value" | Field(default="value") | default="value" | 静态默认值 |
| - | Field(default_factory=list) | default=[] | 动态默认值 |
| - | - | server_default=func.now() | 数据库级默认 |

## 关系映射

OpenAPI 本身不支持关系定义，但可通过 `x-` 扩展或约定：

```yaml
# 使用 x-relationship 扩展
User:
  properties:
    posts:
      type: array
      items:
        $ref: '#/components/schemas/Post'
      x-relationship:
        type: one-to-many
        foreign_key: user_id
```

生成 SQLAlchemy：
```python
class User(Base):
    posts = relationship("Post", back_populates="user")

class Post(Base):
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="posts")
```
