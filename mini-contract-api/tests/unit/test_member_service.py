"""用户服务单元测试（使用 mock DB）"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.core.exceptions import BusinessException, ValidationException
from app.services.member_service import get_user_info, update_user_info, update_password


def _make_member(id=1, mobile="13800138000", nickname="test", avatar=None, status=1, password=None):
    member = MagicMock()
    member.id = id
    member.mobile = mobile
    member.nickname = nickname
    member.avatar = avatar
    member.status = status
    member.password = password
    return member


def _make_db(scalar_return=None):
    db = AsyncMock()
    db.add = MagicMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = scalar_return
    db.execute.return_value = result
    return db


# ---- get_user_info ----

@pytest.mark.anyio
async def test_get_user_info_success():
    """获取用户信息成功"""
    member = _make_member()
    db = _make_db(scalar_return=member)

    info = await get_user_info(db, user_id=1)
    assert info.id == 1
    assert info.mobile == "13800138000"
    assert info.nickname == "test"


@pytest.mark.anyio
async def test_get_user_info_not_found():
    """用户不存在"""
    db = _make_db(scalar_return=None)
    with pytest.raises(BusinessException) as exc_info:
        await get_user_info(db, user_id=999)
    assert exc_info.value.code == 1012001001


@pytest.mark.anyio
async def test_get_user_info_with_avatar():
    """用户有头像"""
    member = _make_member(avatar="https://example.com/avatar.jpg")
    db = _make_db(scalar_return=member)

    info = await get_user_info(db, user_id=1)
    assert info.avatar == "https://example.com/avatar.jpg"


# ---- update_user_info ----

@pytest.mark.anyio
async def test_update_nickname():
    """更新昵称"""
    member = _make_member()
    db = _make_db(scalar_return=member)

    await update_user_info(db, user_id=1, nickname="new_name")
    assert member.nickname == "new_name"
    db.flush.assert_called_once()


@pytest.mark.anyio
async def test_update_avatar():
    """更新头像"""
    member = _make_member()
    db = _make_db(scalar_return=member)

    await update_user_info(db, user_id=1, avatar="https://new-avatar.jpg")
    assert member.avatar == "https://new-avatar.jpg"


@pytest.mark.anyio
async def test_update_both():
    """同时更新昵称和头像"""
    member = _make_member()
    db = _make_db(scalar_return=member)

    await update_user_info(db, user_id=1, nickname="new", avatar="https://new.jpg")
    assert member.nickname == "new"
    assert member.avatar == "https://new.jpg"


@pytest.mark.anyio
async def test_update_user_not_found():
    """更新不存在的用户"""
    db = _make_db(scalar_return=None)
    with pytest.raises(BusinessException) as exc_info:
        await update_user_info(db, user_id=999, nickname="new")
    assert exc_info.value.code == 1012001001


@pytest.mark.anyio
async def test_update_none_values_no_change():
    """不传任何参数时不修改"""
    member = _make_member(nickname="original", avatar="original_avatar")
    db = _make_db(scalar_return=member)

    await update_user_info(db, user_id=1)
    assert member.nickname == "original"
    assert member.avatar == "original_avatar"


# ---- update_password ----

@pytest.mark.anyio
async def test_update_password_success():
    """修改密码成功"""
    member = _make_member(mobile="13800138000")
    db = _make_db(scalar_return=member)

    with patch("app.services.member_service.get_sms_code", new_callable=AsyncMock, return_value="666666"), \
         patch("app.services.member_service.delete_sms_code", new_callable=AsyncMock):
        await update_password(db, user_id=1, new_password="newpwd123", code="666666")
        assert member.password is not None
        assert member.password != "newpwd123"  # should be hashed


@pytest.mark.anyio
async def test_update_password_user_not_found():
    """用户不存在"""
    db = _make_db(scalar_return=None)
    with pytest.raises(BusinessException) as exc_info:
        await update_password(db, user_id=999, new_password="newpwd", code="123456")
    assert exc_info.value.code == 1012001001


@pytest.mark.anyio
async def test_update_password_wrong_code():
    """验证码错误"""
    member = _make_member()
    db = _make_db(scalar_return=member)

    with patch("app.services.member_service.get_sms_code", new_callable=AsyncMock, return_value="123456"):
        with pytest.raises(BusinessException) as exc_info:
            await update_password(db, user_id=1, new_password="newpwd", code="000000")
        assert "验证码" in exc_info.value.msg


@pytest.mark.anyio
async def test_update_password_expired_code():
    """验证码已过期"""
    member = _make_member()
    db = _make_db(scalar_return=member)

    with patch("app.services.member_service.get_sms_code", new_callable=AsyncMock, return_value=None):
        with pytest.raises(BusinessException) as exc_info:
            await update_password(db, user_id=1, new_password="newpwd", code="123456")
        assert "验证码" in exc_info.value.msg


@pytest.mark.anyio
async def test_update_password_too_short():
    """密码太短"""
    member = _make_member()
    db = _make_db(scalar_return=member)

    with patch("app.services.member_service.get_sms_code", new_callable=AsyncMock, return_value="123456"), \
         patch("app.services.member_service.delete_sms_code", new_callable=AsyncMock):
        with pytest.raises(ValidationException) as exc_info:
            await update_password(db, user_id=1, new_password="123", code="123456")
        assert "6" in exc_info.value.msg
