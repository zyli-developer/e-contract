from fastapi import APIRouter, Depends

from app.core.response import ApiResponse
from app.dependencies import get_current_user_id

router = APIRouter(prefix="/member/user", tags=["用户信息"])


@router.get("/get")
async def get_user_info(user_id: int = Depends(get_current_user_id)):
    """获取当前用户信息"""
    # TODO: Phase 1 实现
    return ApiResponse.success()


@router.put("/update")
async def update_user_info(user_id: int = Depends(get_current_user_id)):
    """更新用户信息"""
    # TODO: Phase 1 实现
    return ApiResponse.success()


@router.put("/update-password")
async def update_password(user_id: int = Depends(get_current_user_id)):
    """修改密码"""
    # TODO: Phase 1 实现
    return ApiResponse.success()
