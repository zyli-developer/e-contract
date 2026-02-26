"""异常类和错误码单元测试"""
import pytest
from unittest.mock import MagicMock, AsyncMock

from app.core.exceptions import (
    BusinessException,
    ValidationException,
    UnauthorizedException,
    ForbiddenException,
    ErrorCode,
    business_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
)


# --- Exception classes ---

def test_business_exception_defaults():
    """BusinessException 默认 code=500, msg='业务异常'"""
    exc = BusinessException()
    assert exc.code == 500
    assert exc.msg == "业务异常"


def test_business_exception_custom():
    """BusinessException 支持自定义 code 和 msg"""
    exc = BusinessException(code=1001, msg="自定义错误")
    assert exc.code == 1001
    assert exc.msg == "自定义错误"


def test_validation_exception():
    """ValidationException code 固定为 400"""
    exc = ValidationException()
    assert exc.code == 400
    assert exc.msg == "参数校验失败"


def test_validation_exception_custom_msg():
    """ValidationException 支持自定义 msg"""
    exc = ValidationException(msg="手机号格式不正确")
    assert exc.code == 400
    assert exc.msg == "手机号格式不正确"


def test_unauthorized_exception():
    """UnauthorizedException code 固定为 401"""
    exc = UnauthorizedException()
    assert exc.code == 401
    assert exc.msg == "未登录或 Token 已过期"


def test_unauthorized_exception_custom_msg():
    """UnauthorizedException 支持自定义 msg"""
    exc = UnauthorizedException(msg="Token 类型无效")
    assert exc.code == 401
    assert exc.msg == "Token 类型无效"


def test_forbidden_exception():
    """ForbiddenException code 固定为 403"""
    exc = ForbiddenException()
    assert exc.code == 403
    assert exc.msg == "无权限访问"


def test_forbidden_exception_custom_msg():
    """ForbiddenException 支持自定义 msg"""
    exc = ForbiddenException(msg="仅管理员可操作")
    assert exc.code == 403
    assert exc.msg == "仅管理员可操作"


def test_exception_inheritance():
    """所有异常应继承 BusinessException"""
    assert issubclass(ValidationException, BusinessException)
    assert issubclass(UnauthorizedException, BusinessException)
    assert issubclass(ForbiddenException, BusinessException)


def test_exception_is_exception():
    """BusinessException 应继承 Exception"""
    assert issubclass(BusinessException, Exception)


# --- Error codes ---

def test_error_code_token_invalid():
    assert ErrorCode.TOKEN_INVALID == 1012005005


def test_error_code_token_expired():
    assert ErrorCode.TOKEN_EXPIRED == 1012005006


def test_error_code_user_not_found():
    assert ErrorCode.USER_NOT_FOUND == 1012001001


def test_error_code_mobile_already_exists():
    assert ErrorCode.MOBILE_ALREADY_EXISTS == 1012001002


def test_error_code_sms_code_invalid():
    assert ErrorCode.SMS_CODE_INVALID == 1012002001


def test_error_code_sms_code_expired():
    assert ErrorCode.SMS_CODE_EXPIRED == 1012002002


def test_error_codes_unique():
    """所有错误码应互不相同"""
    codes = [
        ErrorCode.TOKEN_INVALID,
        ErrorCode.TOKEN_EXPIRED,
        ErrorCode.USER_NOT_FOUND,
        ErrorCode.MOBILE_ALREADY_EXISTS,
        ErrorCode.SMS_CODE_INVALID,
        ErrorCode.SMS_CODE_EXPIRED,
    ]
    assert len(codes) == len(set(codes))


# --- Exception handlers ---

@pytest.mark.asyncio
async def test_business_exception_handler_response():
    """business_exception_handler 应返回 HTTP 200 + 错误结构"""
    request = MagicMock()
    exc = BusinessException(code=1001, msg="test error")
    resp = await business_exception_handler(request, exc)
    assert resp.status_code == 200
    import json
    body = json.loads(resp.body)
    assert body["code"] == 1001
    assert body["msg"] == "test error"
    assert body["data"] is None


@pytest.mark.asyncio
async def test_validation_exception_handler_response():
    """validation_exception_handler 应返回 HTTP 200 + code=400"""
    request = MagicMock()
    exc = ValueError("bad input")
    resp = await validation_exception_handler(request, exc)
    assert resp.status_code == 200
    import json
    body = json.loads(resp.body)
    assert body["code"] == 400
    assert body["msg"] == "bad input"


@pytest.mark.asyncio
async def test_generic_exception_handler_response():
    """generic_exception_handler 应返回 HTTP 500 + 通用消息"""
    request = MagicMock()
    exc = RuntimeError("unexpected")
    resp = await generic_exception_handler(request, exc)
    assert resp.status_code == 500
    import json
    body = json.loads(resp.body)
    assert body["code"] == 500
    assert body["msg"] == "服务器内部错误"
    assert body["data"] is None
