"""实名认证单元测试"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.core.exceptions import BusinessException, ValidationException
from app.services.member_service import (
    verify_real_name,
    get_user_info,
    validate_id_card,
    mask_real_name,
    mask_id_card,
)


def _make_member(
    id=1,
    mobile="13800138000",
    nickname="test",
    avatar=None,
    status=1,
    real_name=None,
    id_card=None,
    real_name_verified=0,
    wx_openid=None,
    role="landlord",
):
    member = MagicMock()
    member.id = id
    member.mobile = mobile
    member.nickname = nickname
    member.avatar = avatar
    member.status = status
    member.real_name = real_name
    member.id_card = id_card
    member.real_name_verified = real_name_verified
    member.wx_openid = wx_openid
    member.role = role
    return member


def _make_db(scalar_return=None):
    db = AsyncMock()
    db.add = MagicMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = scalar_return
    db.execute.return_value = result
    return db


# ---- validate_id_card ----

class TestValidateIdCard:
    """身份证号校验"""

    def test_valid_id_card(self):
        """有效身份证号（校验码正确）"""
        assert validate_id_card("110101199003070070") is True

    def test_invalid_length(self):
        """长度不是 18 位"""
        assert validate_id_card("12345") is False
        assert validate_id_card("1234567890123456789") is False

    def test_invalid_format(self):
        """包含非法字符"""
        assert validate_id_card("11010119900307ABCD") is False

    def test_invalid_check_digit(self):
        """校验码错误"""
        assert validate_id_card("110101199003070071") is False

    def test_x_check_digit(self):
        """校验码为 X 的身份证号"""
        assert validate_id_card("11010119900307002X") is True

    def test_lowercase_x(self):
        """小写 x 也应通过"""
        assert validate_id_card("11010119900307002x") is True


# ---- mask_real_name ----

class TestMaskRealName:
    """姓名脱敏"""

    def test_single_char(self):
        assert mask_real_name("李") == "李"

    def test_two_chars(self):
        assert mask_real_name("李明") == "李*"

    def test_three_chars(self):
        assert mask_real_name("李小明") == "李*明"

    def test_four_chars(self):
        assert mask_real_name("欧阳小明") == "欧**明"


# ---- mask_id_card ----

class TestMaskIdCard:
    """身份证号脱敏"""

    def test_normal(self):
        result = mask_id_card("110101199003070070")
        assert result == "110***********0070"
        assert len(result) == 18

    def test_short(self):
        """短字符串不脱敏"""
        assert mask_id_card("1234567") == "1234567"


# ---- verify_real_name（OCR 校验） ----

@pytest.mark.anyio
@patch("app.services.member_service.check_id_card_expired", return_value=False)
@patch("app.services.member_service.extract_id_card_validity")
@patch("app.services.member_service.os.path.isfile", return_value=True)
@patch("builtins.open", create=True)
@patch("app.services.member_service.extract_id_card_info")
async def test_verify_success_with_ocr(mock_ocr, mock_open, mock_isfile, mock_validity, mock_expired):
    """OCR 识别成功且信息匹配"""
    mock_ocr.return_value = {
        "name": "张三",
        "id_number": "110101199003070070",
        "raw_texts": ["姓名张三", "身份号码110101199003070070"],
    }
    mock_open.return_value.__enter__ = lambda s: MagicMock(read=lambda: b"fake_image")
    mock_open.return_value.__exit__ = MagicMock(return_value=False)

    member = _make_member(real_name_verified=0)
    db = _make_db(scalar_return=member)

    result = await verify_real_name(
        db, user_id=1, real_name="张三", id_card="110101199003070070",
        id_card_front_url="/static/uploads/2025/01/01/front.jpg",
        id_card_back_url="/static/uploads/2025/01/01/back.jpg",
    )

    assert result["real_name_verified"] == 1
    assert result["real_name"] == "张*"
    assert "***" in result["id_card"]
    assert member.real_name == "张三"
    assert member.id_card == "110101199003070070"
    assert member.real_name_verified == 1
    db.flush.assert_called_once()


@pytest.mark.anyio
async def test_verify_user_not_found():
    """用户不存在"""
    db = _make_db(scalar_return=None)
    with pytest.raises(BusinessException) as exc_info:
        await verify_real_name(
            db, user_id=999, real_name="张三", id_card="110101199003070070",
            id_card_front_url="/static/uploads/front.jpg",
            id_card_back_url="/static/uploads/back.jpg",
        )
    assert exc_info.value.code == 1012001001


@pytest.mark.anyio
async def test_verify_already_verified():
    """已认证用户重复认证"""
    member = _make_member(real_name_verified=1, real_name="张三")
    db = _make_db(scalar_return=member)

    with pytest.raises(BusinessException) as exc_info:
        await verify_real_name(
            db, user_id=1, real_name="李四", id_card="110101199003070070",
            id_card_front_url="/static/uploads/front.jpg",
            id_card_back_url="/static/uploads/back.jpg",
        )
    assert "已完成实名认证" in exc_info.value.msg


@pytest.mark.anyio
async def test_verify_empty_name():
    """姓名为空"""
    member = _make_member(real_name_verified=0)
    db = _make_db(scalar_return=member)

    with pytest.raises(ValidationException) as exc_info:
        await verify_real_name(
            db, user_id=1, real_name="  ", id_card="110101199003070070",
            id_card_front_url="/static/uploads/front.jpg",
            id_card_back_url="/static/uploads/back.jpg",
        )
    assert "姓名" in exc_info.value.msg


@pytest.mark.anyio
async def test_verify_invalid_id_card():
    """身份证号格式不正确"""
    member = _make_member(real_name_verified=0)
    db = _make_db(scalar_return=member)

    with pytest.raises(ValidationException) as exc_info:
        await verify_real_name(
            db, user_id=1, real_name="张三", id_card="123456789012345678",
            id_card_front_url="/static/uploads/front.jpg",
            id_card_back_url="/static/uploads/back.jpg",
        )
    assert "身份证号" in exc_info.value.msg


@pytest.mark.anyio
async def test_verify_short_id_card():
    """身份证号长度不够"""
    member = _make_member(real_name_verified=0)
    db = _make_db(scalar_return=member)

    with pytest.raises(ValidationException) as exc_info:
        await verify_real_name(
            db, user_id=1, real_name="张三", id_card="12345",
            id_card_front_url="/static/uploads/front.jpg",
            id_card_back_url="/static/uploads/back.jpg",
        )
    assert "身份证号" in exc_info.value.msg


@pytest.mark.anyio
@patch("app.services.member_service.os.path.isfile", return_value=False)
async def test_verify_front_image_not_found(mock_isfile):
    """正面照片不存在"""
    member = _make_member(real_name_verified=0)
    db = _make_db(scalar_return=member)

    with pytest.raises(ValidationException) as exc_info:
        await verify_real_name(
            db, user_id=1, real_name="张三", id_card="110101199003070070",
            id_card_front_url="/static/uploads/front.jpg",
            id_card_back_url="/static/uploads/back.jpg",
        )
    assert "照片不存在" in exc_info.value.msg


@pytest.mark.anyio
@patch("app.services.member_service.os.path.isfile", return_value=True)
@patch("builtins.open", create=True)
@patch("app.services.member_service.extract_id_card_info")
async def test_verify_ocr_unrecognizable(mock_ocr, mock_open, mock_isfile):
    """OCR 无法识别身份证信息"""
    mock_ocr.return_value = {"name": None, "id_number": None, "raw_texts": []}
    mock_open.return_value.__enter__ = lambda s: MagicMock(read=lambda: b"fake_image")
    mock_open.return_value.__exit__ = MagicMock(return_value=False)

    member = _make_member(real_name_verified=0)
    db = _make_db(scalar_return=member)

    with pytest.raises(ValidationException) as exc_info:
        await verify_real_name(
            db, user_id=1, real_name="张三", id_card="110101199003070070",
            id_card_front_url="/static/uploads/front.jpg",
            id_card_back_url="/static/uploads/back.jpg",
        )
    assert "无法识别" in exc_info.value.msg


@pytest.mark.anyio
@patch("app.services.member_service.os.path.isfile", return_value=True)
@patch("builtins.open", create=True)
@patch("app.services.member_service.extract_id_card_info")
async def test_verify_ocr_id_mismatch(mock_ocr, mock_open, mock_isfile):
    """OCR 识别的身份证号与输入不一致"""
    mock_ocr.return_value = {
        "name": "张三",
        "id_number": "110101199003070070",
        "raw_texts": [],
    }
    mock_open.return_value.__enter__ = lambda s: MagicMock(read=lambda: b"fake_image")
    mock_open.return_value.__exit__ = MagicMock(return_value=False)

    member = _make_member(real_name_verified=0)
    db = _make_db(scalar_return=member)

    with pytest.raises(ValidationException) as exc_info:
        await verify_real_name(
            db, user_id=1, real_name="张三", id_card="11010119900307002X",
            id_card_front_url="/static/uploads/front.jpg",
            id_card_back_url="/static/uploads/back.jpg",
        )
    assert "身份证号" in exc_info.value.msg and "不一致" in exc_info.value.msg


@pytest.mark.anyio
@patch("app.services.member_service.os.path.isfile", return_value=True)
@patch("builtins.open", create=True)
@patch("app.services.member_service.extract_id_card_info")
async def test_verify_ocr_name_mismatch(mock_ocr, mock_open, mock_isfile):
    """OCR 识别的姓名与输入不一致"""
    mock_ocr.return_value = {
        "name": "李四",
        "id_number": "110101199003070070",
        "raw_texts": [],
    }
    mock_open.return_value.__enter__ = lambda s: MagicMock(read=lambda: b"fake_image")
    mock_open.return_value.__exit__ = MagicMock(return_value=False)

    member = _make_member(real_name_verified=0)
    db = _make_db(scalar_return=member)

    with pytest.raises(ValidationException) as exc_info:
        await verify_real_name(
            db, user_id=1, real_name="张三", id_card="110101199003070070",
            id_card_front_url="/static/uploads/front.jpg",
            id_card_back_url="/static/uploads/back.jpg",
        )
    assert "姓名" in exc_info.value.msg and "不一致" in exc_info.value.msg


@pytest.mark.anyio
@patch("app.services.member_service.os.path.isfile", side_effect=lambda p: "front" in p)
@patch("builtins.open", create=True)
@patch("app.services.member_service.extract_id_card_info")
async def test_verify_back_image_not_found(mock_ocr, mock_open, mock_isfile):
    """背面照片不存在"""
    mock_ocr.return_value = {
        "name": "张三",
        "id_number": "110101199003070070",
        "raw_texts": [],
    }
    mock_open.return_value.__enter__ = lambda s: MagicMock(read=lambda: b"fake_image")
    mock_open.return_value.__exit__ = MagicMock(return_value=False)

    member = _make_member(real_name_verified=0)
    db = _make_db(scalar_return=member)

    with pytest.raises(ValidationException) as exc_info:
        await verify_real_name(
            db, user_id=1, real_name="张三", id_card="110101199003070070",
            id_card_front_url="/static/uploads/front.jpg",
            id_card_back_url="/static/uploads/back.jpg",
        )
    assert "背面照片不存在" in exc_info.value.msg


@pytest.mark.anyio
@patch("app.services.member_service.check_id_card_expired", return_value=True)
@patch("app.services.member_service.extract_id_card_validity")
@patch("app.services.member_service.os.path.isfile", return_value=True)
@patch("builtins.open", create=True)
@patch("app.services.member_service.extract_id_card_info")
async def test_verify_id_card_expired(mock_ocr, mock_open, mock_isfile, mock_validity, mock_expired):
    """身份证已过期"""
    mock_ocr.return_value = {
        "name": "张三",
        "id_number": "110101199003070070",
        "raw_texts": [],
    }
    mock_open.return_value.__enter__ = lambda s: MagicMock(read=lambda: b"fake_image")
    mock_open.return_value.__exit__ = MagicMock(return_value=False)

    member = _make_member(real_name_verified=0)
    db = _make_db(scalar_return=member)

    with pytest.raises(ValidationException) as exc_info:
        await verify_real_name(
            db, user_id=1, real_name="张三", id_card="110101199003070070",
            id_card_front_url="/static/uploads/front.jpg",
            id_card_back_url="/static/uploads/back.jpg",
        )
    assert "已过期" in exc_info.value.msg


# ---- get_user_info with real_name fields ----

@pytest.mark.anyio
async def test_get_user_info_verified():
    """已认证用户返回脱敏姓名"""
    member = _make_member(real_name_verified=1, real_name="张三")
    db = _make_db(scalar_return=member)

    info = await get_user_info(db, user_id=1)
    assert info.real_name_verified == 1
    assert info.real_name == "张*"


@pytest.mark.anyio
async def test_get_user_info_not_verified():
    """未认证用户不返回真实姓名"""
    member = _make_member(real_name_verified=0, real_name=None)
    db = _make_db(scalar_return=member)

    info = await get_user_info(db, user_id=1)
    assert info.real_name_verified == 0
    assert info.real_name is None
