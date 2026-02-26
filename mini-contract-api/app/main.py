from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.config import settings
from app.core.exceptions import (
    BusinessException,
    business_exception_handler,
    generic_exception_handler,
)
from app.core.middleware import RequestLoggingMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时：自动建表
    from app.database import engine, init_db, seed_admin
    await init_db()
    await seed_admin()
    yield
    # 关闭时：释放连接池
    from app.utils.redis_client import close_redis
    await close_redis()
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    description="Mini Contract Pro - 电子合同签署平台 API。支持用户认证、签名管理、合同模板、合同签署（含意愿验证）、证据链追踪。",
    version="1.0.0",
    lifespan=lifespan,
)

# --- 中间件 ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)

# --- 异常处理 ---
app.add_exception_handler(BusinessException, business_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# --- 路由 ---
app.include_router(api_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
