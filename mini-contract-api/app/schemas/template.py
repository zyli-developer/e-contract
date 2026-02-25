from typing import Any, List, Optional

from pydantic import BaseModel


class TemplateSearchRequest(BaseModel):
    keyword: str | None = None
    category: str | None = None
    pageNo: int = 1
    pageSize: int = 10


class TemplateResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    category: str
    image_url: str | None = None
    use_count: int = 0


class TemplateDetailResponse(TemplateResponse):
    content: str | None = None
    variables: list | None = None
    signatories: list | None = None
