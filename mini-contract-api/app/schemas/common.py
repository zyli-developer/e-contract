from pydantic import BaseModel


class PageRequest(BaseModel):
    """通用分页请求"""
    pageNo: int = 1
    pageSize: int = 10
