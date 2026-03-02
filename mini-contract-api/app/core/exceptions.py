from fastapi import Request
from fastapi.responses import JSONResponse
from loguru import logger


class BusinessException(Exception):
    """业务异常"""
    def __init__(self, code: int = 500, msg: str = "业务异常"):
        self.code = code
        self.msg = msg


class ValidationException(BusinessException):
    """参数校验异常"""
    def __init__(self, msg: str = "参数校验失败"):
        super().__init__(code=400, msg=msg)


class UnauthorizedException(BusinessException):
    """认证异常"""
    def __init__(self, msg: str = "未登录或 Token 已过期"):
        super().__init__(code=401, msg=msg)


class ForbiddenException(BusinessException):
    """权限异常"""
    def __init__(self, msg: str = "无权限访问"):
        super().__init__(code=403, msg=msg)


# --- 错误码常量 ---

class ErrorCode:
    TOKEN_INVALID = 1012005005
    TOKEN_EXPIRED = 1012005006
    USER_NOT_FOUND = 1012001001
    MOBILE_ALREADY_EXISTS = 1012001002
    SMS_CODE_INVALID = 1012002001
    SMS_CODE_EXPIRED = 1012002002


# --- 全局异常处理器 ---

async def business_exception_handler(request: Request, exc: BusinessException):
    logger.warning(
        "BusinessException: code=%s msg=%s path=%s",
        exc.code, exc.msg, request.url.path,
    )
    return JSONResponse(
        status_code=200,
        content={"code": exc.code, "msg": exc.msg, "data": None},
    )


async def validation_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=200,
        content={"code": 400, "msg": str(exc), "data": None},
    )


async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(
        "Unhandled exception: path=%s error=%s",
        request.url.path, exc, exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={"code": 500, "msg": "服务器内部错误", "data": None},
    )
