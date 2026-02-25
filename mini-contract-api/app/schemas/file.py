from pydantic import BaseModel


class FileCreateRequest(BaseModel):
    """创建文件记录请求"""
    name: str
    path: str
    url: str
    type: str | None = None
    size: int | None = None


class FileCreateResponse(BaseModel):
    """创建文件记录响应"""
    id: int
    name: str
    url: str


class PresignedUrlRequest(BaseModel):
    """获取预签名 URL 请求"""
    filename: str
    content_type: str = "application/octet-stream"


class PresignedUrlResponse(BaseModel):
    """预签名 URL 响应"""
    upload_url: str
    file_key: str
    file_url: str


class FileUploadResponse(BaseModel):
    """文件上传响应"""
    id: int
    name: str
    url: str
    size: int
