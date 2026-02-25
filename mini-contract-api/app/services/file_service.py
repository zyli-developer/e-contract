"""文件上传服务"""
import os
import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.exceptions import BusinessException, ValidationException
from app.models.infra_file import InfraFile

# 文件大小限制（字节）
IMAGE_MAX_SIZE = 5 * 1024 * 1024      # 5MB
DOCUMENT_MAX_SIZE = 20 * 1024 * 1024   # 20MB

# 允许的 MIME 类型
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
ALLOWED_DOC_TYPES = {"application/pdf", "application/msword",
                     "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
ALLOWED_TYPES = ALLOWED_IMAGE_TYPES | ALLOWED_DOC_TYPES


def validate_file(filename: str, content_type: str, size: int) -> None:
    """校验文件类型和大小"""
    if content_type not in ALLOWED_TYPES:
        raise ValidationException(f"不支持的文件类型: {content_type}")

    if content_type in ALLOWED_IMAGE_TYPES and size > IMAGE_MAX_SIZE:
        raise ValidationException(f"图片大小不能超过 {IMAGE_MAX_SIZE // 1024 // 1024}MB")

    if content_type in ALLOWED_DOC_TYPES and size > DOCUMENT_MAX_SIZE:
        raise ValidationException(f"文档大小不能超过 {DOCUMENT_MAX_SIZE // 1024 // 1024}MB")


def generate_file_key(filename: str) -> str:
    """生成唯一文件存储路径"""
    ext = os.path.splitext(filename)[1]
    date_prefix = datetime.now().strftime("%Y/%m/%d")
    unique_name = uuid.uuid4().hex
    return f"{date_prefix}/{unique_name}{ext}"


async def create_file_record(
    db: AsyncSession,
    *,
    name: str,
    path: str,
    url: str,
    file_type: str | None = None,
    size: int | None = None,
) -> InfraFile:
    """创建文件记录"""
    file_record = InfraFile(
        name=name,
        path=path,
        url=url,
        type=file_type,
        size=size,
    )
    db.add(file_record)
    await db.flush()
    await db.refresh(file_record)
    return file_record


async def save_uploaded_file(content: bytes, file_key: str) -> str:
    """保存文件到本地存储，返回访问 URL"""
    upload_dir = os.path.join("uploads", os.path.dirname(file_key))
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join("uploads", file_key)
    with open(file_path, "wb") as f:
        f.write(content)

    return f"/static/uploads/{file_key}"
