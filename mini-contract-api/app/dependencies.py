from fastapi import Depends, Header, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UnauthorizedException
from app.core.security import decode_token
from app.database import get_db

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> int:
    """从 Authorization header 中解析 Access Token，返回 user_id"""
    if not credentials:
        raise UnauthorizedException()
    try:
        payload = decode_token(credentials.credentials)
        if payload.get("type") != "access":
            raise UnauthorizedException("Token 类型无效")
        return int(payload["sub"])
    except JWTError:
        raise UnauthorizedException()


async def get_seal_user_id(
    request: Request,
) -> int:
    """从 Seal-Token header 中解析 Seal Token，返回 user_id"""
    seal_token = request.headers.get("Seal-Token")
    if not seal_token:
        raise UnauthorizedException("缺少 Seal-Token")
    try:
        payload = decode_token(seal_token)
        if payload.get("type") != "seal":
            raise UnauthorizedException("Seal Token 类型无效")
        return int(payload["sub"])
    except JWTError:
        raise UnauthorizedException("Seal Token 无效或已过期")


async def get_tenant_id(
    tenant_id: str = Header(alias="tenant-id", default="1"),
) -> int:
    return int(tenant_id)
