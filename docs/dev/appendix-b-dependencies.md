# 附录 B：MVP 技术依赖

## 后端 (Python)

```txt
# 核心框架
fastapi>=0.115.0
uvicorn[standard]
sqlalchemy[asyncio]>=2.0
aiomysql
alembic
redis[hiredis]
pydantic>=2.0.0

# 认证与安全
python-jose[cryptography]    # JWT
passlib[bcrypt]              # 密码哈希

# 外部服务
httpx                        # HTTP client
wechatpy>=2.1.0              # 微信 SDK（登录、模板消息）
python-minio                 # 文件存储（或 boto3）

# 测试
pytest
pytest-asyncio
respx                        # HTTP mock
pytest-cov
```

## 前端 (TypeScript)

```txt
# 核心框架
@tarojs/cli@4.x
@tarojs/taro
@tarojs/components
react@18
react-dom@18

# 状态管理 & UI
zustand
@nutui/nutui-react-taro

# 测试
jest
@testing-library/react
@testing-library/jest-dom
msw
```
