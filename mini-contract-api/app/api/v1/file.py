from fastapi import APIRouter, Depends

from app.core.response import ApiResponse
from app.dependencies import get_current_user_id

router = APIRouter(prefix="/infra/file", tags=["文件管理"])


@router.get("/presigned-url")
async def get_presigned_url(user_id: int = Depends(get_current_user_id)):
    """获取预签名上传 URL"""
    # TODO: Phase 0 实现
    return ApiResponse.success()


@router.post("/create")
async def create_file_record(user_id: int = Depends(get_current_user_id)):
    """创建文件记录"""
    # TODO: Phase 0 实现
    return ApiResponse.success()
