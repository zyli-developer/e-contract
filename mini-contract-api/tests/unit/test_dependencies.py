"""依赖注入单元测试"""
import pytest
from unittest.mock import MagicMock

from app.core.exceptions import UnauthorizedException
from app.core.security import create_access_token, create_refresh_token
from app.dependencies import get_current_user_id


@pytest.mark.anyio
async def test_get_current_user_id_success():
    """有效的 Access Token 应返回 user_id"""
    token = create_access_token(42)
    credentials = MagicMock()
    credentials.credentials = token

    user_id = await get_current_user_id(credentials)
    assert user_id == 42


@pytest.mark.anyio
async def test_get_current_user_id_no_credentials():
    """无认证信息应抛出 UnauthorizedException"""
    with pytest.raises(UnauthorizedException):
        await get_current_user_id(None)


@pytest.mark.anyio
async def test_get_current_user_id_invalid_token():
    """无效 Token 应抛出 UnauthorizedException"""
    credentials = MagicMock()
    credentials.credentials = "invalid.token.string"

    with pytest.raises(UnauthorizedException):
        await get_current_user_id(credentials)


@pytest.mark.anyio
async def test_get_current_user_id_refresh_token_rejected():
    """Refresh Token 不能作为 Access Token 使用"""
    token = create_refresh_token(42)
    credentials = MagicMock()
    credentials.credentials = token

    with pytest.raises(UnauthorizedException, match="Token 类型无效"):
        await get_current_user_id(credentials)


@pytest.mark.anyio
async def test_get_current_user_id_returns_int():
    """返回值应为 int 类型"""
    token = create_access_token(100)
    credentials = MagicMock()
    credentials.credentials = token

    user_id = await get_current_user_id(credentials)
    assert isinstance(user_id, int)
    assert user_id == 100
