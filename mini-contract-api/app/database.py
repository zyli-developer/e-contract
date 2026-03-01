import logging
from urllib.parse import urlparse, urlunparse

import asyncpg
import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

logger = logging.getLogger(__name__)

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """SQLAlchemy 声明式基类"""
    pass


async def _ensure_database_exists():
    """检查目标数据库是否存在，不存在则自动创建"""
    parsed = urlparse(settings.DATABASE_URL)
    db_name = parsed.path.lstrip("/")  # e.g. "mini_contract"
    # 连接到默认的 postgres 库来执行 CREATE DATABASE
    default_url = urlunparse(parsed._replace(
        scheme="postgresql",  # asyncpg 原生连接不需要 +asyncpg 前缀
        path="/postgres",
    ))
    try:
        conn = await asyncpg.connect(default_url)
        try:
            exists = await conn.fetchval(
                "SELECT 1 FROM pg_database WHERE datname = $1", db_name
            )
            if not exists:
                await conn.execute(f'CREATE DATABASE "{db_name}"')
                logger.info("数据库 '%s' 不存在，已自动创建", db_name)
            else:
                logger.info("数据库 '%s' 已存在", db_name)
        finally:
            await conn.close()
    except Exception as e:
        logger.warning("检查/创建数据库失败: %s", e)


async def init_db():
    """自动创建数据库（如不存在）和所有数据表"""
    import app.models  # noqa: F401 — 确保所有模型注册到 Base.metadata
    try:
        await _ensure_database_exists()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            # 补充 create_all 无法自动添加的新列 / 修正已有列约束
            await conn.execute(
                sqlalchemy.text(
                    "ALTER TABLE member ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE"
                )
            )
            # 微信登录用户可能没有手机号，mobile 需允许 NULL
            await conn.execute(
                sqlalchemy.text(
                    "ALTER TABLE member ALTER COLUMN mobile DROP NOT NULL"
                )
            )
            # 合同变量值列
            await conn.execute(
                sqlalchemy.text(
                    "ALTER TABLE sign_task ADD COLUMN IF NOT EXISTS variables JSON"
                )
            )
            # 实名认证字段
            await conn.execute(
                sqlalchemy.text(
                    "ALTER TABLE member ADD COLUMN IF NOT EXISTS real_name VARCHAR(50)"
                )
            )
            await conn.execute(
                sqlalchemy.text(
                    "ALTER TABLE member ADD COLUMN IF NOT EXISTS id_card VARCHAR(50)"
                )
            )
            await conn.execute(
                sqlalchemy.text(
                    "ALTER TABLE member ADD COLUMN IF NOT EXISTS real_name_verified SMALLINT DEFAULT 0"
                )
            )
            await conn.execute(
                sqlalchemy.text(
                    "ALTER TABLE member ADD COLUMN IF NOT EXISTS wx_openid VARCHAR(128)"
                )
            )
        logger.info("数据库表初始化完成")
    except Exception as e:
        logger.warning("数据库连接失败，跳过自动建表: %s", e)
        logger.warning("请确保 PostgreSQL 已启动，或执行: docker-compose up -d postgres redis")


async def seed_admin():
    """初始化管理员账号（如不存在）"""
    from sqlalchemy import select
    from app.models.member import Member
    from app.core.security import hash_password

    admin_mobile = "15679132250"

    try:
        async with async_session_factory() as session:
            result = await session.execute(
                select(Member).where(Member.mobile == admin_mobile)
            )
            if result.scalar_one_or_none() is None:
                admin = Member(
                    mobile=admin_mobile,
                    password=hash_password("15679132250"),
                    nickname="管理员",
                    status=1,
                    is_admin=True,
                )
                session.add(admin)
                await session.commit()
                logger.info("管理员账号已创建: %s", admin_mobile)
            else:
                logger.info("管理员账号已存在: %s", admin_mobile)
    except Exception as e:
        logger.warning("初始化管理员账号失败: %s", e)


async def get_db() -> AsyncSession:
    """获取数据库 Session（用于 FastAPI 依赖注入）"""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
