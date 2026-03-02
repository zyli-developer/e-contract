import os
from contextlib import asynccontextmanager

from loguru import logger

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.config import settings
from app.core.exceptions import (
    BusinessException,
    business_exception_handler,
    generic_exception_handler,
)
from app.core.logging_config import setup_logging
from app.core.middleware import RequestLoggingMiddleware

# 在应用启动前初始化日志
setup_logging(debug=settings.DEBUG)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时：自动建表
    logger.info("应用启动中: %s (DEBUG=%s)", settings.APP_NAME, settings.DEBUG)
    from app.database import engine, init_db, seed_admin
    from app.seed_templates import seed_templates
    await init_db()
    await seed_admin()
    await seed_templates()
    logger.info("应用启动完成，服务就绪")
    yield
    # 关闭时：释放连接池
    logger.info("应用关闭中，释放资源...")
    from app.utils.redis_client import close_redis
    await close_redis()
    await engine.dispose()
    logger.info("应用已关闭")


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

# --- 静态文件 ---
os.makedirs("uploads", exist_ok=True)
app.mount("/static/uploads", StaticFiles(directory="uploads"), name="static-uploads")

# --- 路由 ---
app.include_router(api_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
