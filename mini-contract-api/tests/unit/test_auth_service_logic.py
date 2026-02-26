"""认证服务业务逻辑单元测试（使用 mock DB）"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.core.exceptions import BusinessException, UnauthorizedException, ValidationException
from app.services.auth_service import (
    login_by_password,
    login_by_sms,
    refresh_token,
    logout,
    _get_or_create_member_by_mobile,
)


def _make_member(id=1, mobile="13800138000", password=None, status=1, nickname="test"):
    member = MagicMock()
    member.id = id
    member.mobile = mobile
    member.password = password
    member.status = status
    member.nickname = nickname
    return member


def _make_db(scalar_return=None):
    db = AsyncMock()
    db.add = MagicMock()  # add is sync
    result = MagicMock()
    result.scalar_one_or_none.return_value = scalar_return
    db.execute.return_value = result
    return db


# ---- login_by_password ----

@pytest.mark.anyio
async def test_login_by_password_success():
    """密码登录成功"""
    from app.core.security import hash_password
    hashed = hash_password("test123")
    member = _make_member(password=hashed)
    db = _make_db(scalar_return=member)

    with patch("app.services.auth_service._create_token_record", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = MagicMock(accessToken="at", refreshToken="rt", userId=1, expiresTime=0)
        await login_by_password(db, "13800138000", "test123")
        mock_create.assert_called_once_with(db, 1)


@pytest.mark.anyio
async def test_login_by_password_user_not_found():
    """用户不存在应报错"""
    db = _make_db(scalar_return=None)
    with pytest.raises(BusinessException) as exc_info:
        await login_by_password(db, "13800138000", "test123")
    assert "不存在" in exc_info.value.msg


@pytest.mark.anyio
async def test_login_by_password_user_disabled():
    """被禁用的账号应报错"""
    member = _make_member(status=0)
    db = _make_db(scalar_return=member)
    with pytest.raises(BusinessException) as exc_info:
        await login_by_password(db, "13800138000", "test123")
    assert "禁用" in exc_info.value.msg


@pytest.mark.anyio
async def test_login_by_password_no_password_set():
    """未设置密码应提示用短信登录"""
    member = _make_member(password=None)
    db = _make_db(scalar_return=member)
    with pytest.raises(ValidationException) as exc_info:
        await login_by_password(db, "13800138000", "test123")
    assert "密码" in exc_info.value.msg


@pytest.mark.anyio
async def test_login_by_password_wrong_password():
    """密码错误应报错"""
    from app.core.security import hash_password
    member = _make_member(password=hash_password("correct_pwd"))
    db = _make_db(scalar_return=member)
    with pytest.raises(ValidationException) as exc_info:
        await login_by_password(db, "13800138000", "wrong_pwd")
    assert "密码错误" in exc_info.value.msg


# ---- login_by_sms ----

@pytest.mark.anyio
async def test_login_by_sms_success():
    """短信登录成功"""
    member = _make_member()
    db = _make_db(scalar_return=member)

    with patch("app.services.auth_service.get_sms_code", new_callable=AsyncMock, return_value="123456"), \
         patch("app.services.auth_service.delete_sms_code", new_callable=AsyncMock), \
         patch("app.services.auth_service._create_token_record", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = MagicMock()
        await login_by_sms(db, "13800138000", "123456")
        mock_create.assert_called_once()


@pytest.mark.anyio
async def test_login_by_sms_wrong_code():
    """短信验证码错误"""
    with patch("app.services.auth_service.get_sms_code", new_callable=AsyncMock, return_value="123456"):
        db = AsyncMock()
        with pytest.raises(BusinessException) as exc_info:
            await login_by_sms(db, "13800138000", "000000")
        assert "验证码" in exc_info.value.msg


@pytest.mark.anyio
async def test_login_by_sms_expired_code():
    """短信验证码已过期"""
    with patch("app.services.auth_service.get_sms_code", new_callable=AsyncMock, return_value=None):
        db = AsyncMock()
        with pytest.raises(BusinessException) as exc_info:
            await login_by_sms(db, "13800138000", "123456")
        assert "验证码" in exc_info.value.msg


# ---- refresh_token ----

@pytest.mark.anyio
async def test_refresh_token_invalid_token():
    """无效的 refresh token"""
    db = AsyncMock()
    with pytest.raises(UnauthorizedException) as exc_info:
        await refresh_token(db, "invalid_token")
    assert "无效" in exc_info.value.msg


@pytest.mark.anyio
async def test_refresh_token_access_token_type():
    """用 access token 做 refresh 应报错"""
    from app.core.security import create_access_token
    at = create_access_token(42)
    db = AsyncMock()
    with pytest.raises(UnauthorizedException) as exc_info:
        await refresh_token(db, at)
    assert "类型" in exc_info.value.msg


@pytest.mark.anyio
async def test_refresh_token_already_used():
    """已使用的 refresh token 应报错"""
    from app.core.security import create_refresh_token
    rt = create_refresh_token(42)
    db = _make_db(scalar_return=None)
    with pytest.raises(UnauthorizedException) as exc_info:
        await refresh_token(db, rt)
    assert "已使用" in exc_info.value.msg or "不存在" in exc_info.value.msg


# ---- logout ----

@pytest.mark.anyio
async def test_logout_success():
    """退出登录应标记所有 token 为已使用"""
    db = AsyncMock()
    await logout(db, user_id=42)
    db.execute.assert_called_once()


# ---- _get_or_create_member_by_mobile ----

@pytest.mark.anyio
async def test_get_or_create_existing_member():
    """手机号已存在时直接返回"""
    member = _make_member()
    db = _make_db(scalar_return=member)
    result = await _get_or_create_member_by_mobile(db, "13800138000")
    assert result.id == 1


@pytest.mark.anyio
async def test_get_or_create_disabled_member():
    """已禁用的账号应报错"""
    member = _make_member(status=0)
    db = _make_db(scalar_return=member)
    with pytest.raises(BusinessException) as exc_info:
        await _get_or_create_member_by_mobile(db, "13800138000")
    assert "禁用" in exc_info.value.msg


@pytest.mark.anyio
async def test_get_or_create_new_member():
    """手机号不存在时自动注册"""
    db = AsyncMock()
    db.add = MagicMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    db.execute.return_value = result

    await _get_or_create_member_by_mobile(db, "13900139000")
    db.add.assert_called_once()
