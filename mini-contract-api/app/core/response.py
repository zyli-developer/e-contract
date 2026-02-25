from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """统一 API 响应格式"""
    code: int = 0
    msg: str = "success"
    data: Optional[T] = None

    @classmethod
    def success(cls, data: Any = None, msg: str = "success") -> "ApiResponse":
        return cls(code=0, data=data, msg=msg)

    @classmethod
    def error(cls, code: int = 500, msg: str = "error") -> "ApiResponse":
        return cls(code=code, msg=msg, data=None)


class PageResult(BaseModel, Generic[T]):
    """分页响应格式"""
    list: list[T] = []
    total: int = 0
    pageNo: int = 1
    pageSize: int = 10
