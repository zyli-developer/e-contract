from fastapi import APIRouter, Depends, UploadFile, File

from app.core.exceptions import ValidationException
from app.core.response import ApiResponse
from app.dependencies import get_current_user_id
from app.schemas.file import FileUploadResponse
from app.services.file_service import (
    ALLOWED_TYPES,
    validate_file,
    generate_file_key,
    save_uploaded_file,
)

router = APIRouter(prefix="/infra/file", tags=["文件管理"])


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id),
):
    """上传文件（图片限 5MB，文档限 20MB）"""
    if not file.filename:
        raise ValidationException("文件名不能为空")

    content = await file.read()
    content_type = file.content_type or "application/octet-stream"

    validate_file(file.filename, content_type, len(content))

    file_key = generate_file_key(file.filename)
    url = await save_uploaded_file(content, file_key)

    return ApiResponse.success(data=FileUploadResponse(
        id=0,
        name=file.filename,
        url=url,
        size=len(content),
    ).model_dump())


@router.get("/presigned-url")
async def get_presigned_url(
    filename: str,
    content_type: str = "application/octet-stream",
    user_id: int = Depends(get_current_user_id),
):
    """获取预签名上传 URL（当配置了 S3/MinIO 时使用）"""
    if content_type not in ALLOWED_TYPES:
        raise ValidationException(f"不支持的文件类型: {content_type}")

    file_key = generate_file_key(filename)
    # 本地开发模式返回直传地址
    return ApiResponse.success(data={
        "upload_url": f"/api/v1/infra/file/upload",
        "file_key": file_key,
        "file_url": f"/static/uploads/{file_key}",
    })
