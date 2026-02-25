from pydantic import BaseModel


class SealCreateRequest(BaseModel):
    name: str
    type: int  # 11=个人签名, 12=个人印章
    seal_data: str  # 图片 URL


class SealUpdateRequest(BaseModel):
    id: int
    name: str | None = None
    seal_data: str | None = None


class SealResponse(BaseModel):
    id: int
    name: str
    type: int
    seal_data: str
    is_default: int
    create_time: str | None = None
