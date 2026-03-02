from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.core.security import decode_token
from app.database import get_db
from app.models.member import Member

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> int:
    """从 Authorization header 中解析 Access Token，返回 user_id"""
    if not credentials:
        logger.warning("请求缺少 Authorization header")
        raise UnauthorizedException()
    try:
        payload = decode_token(credentials.credentials)
        if payload.get("type") != "access":
            logger.warning("Token 类型无效: type=%s", payload.get("type"))
            raise UnauthorizedException("Token 类型无效")
        user_id = int(payload["sub"])
        logger.debug("认证成功: user_id=%d", user_id)
        return user_id
    except JWTError as e:
        logger.warning("Token 解析失败: %s", e)
        raise UnauthorizedException()


async def require_landlord(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> int:
    """要求当前用户为房东角色，否则返回 403"""
    result = await db.execute(select(Member.role).where(Member.id == user_id))
    role = result.scalar_one_or_none() or "landlord"
    if role != "landlord":
        logger.warning("权限不足: user_id=%d, role=%s, 需要 landlord", user_id, role)
        raise ForbiddenException("租客角色无权执行此操作")
    return user_id
