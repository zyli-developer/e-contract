from fastapi import APIRouter, Depends

from app.core.response import ApiResponse
from app.dependencies import get_seal_user_id

router = APIRouter(prefix="/seal/seal-info", tags=["印章管理"])


@router.get("/page")
async def list_seals(user_id: int = Depends(get_seal_user_id)):
    """印章列表（分页）"""
    # TODO: Phase 2 实现
    return ApiResponse.success()


@router.post("/create")
async def create_seal(user_id: int = Depends(get_seal_user_id)):
    """创建印章"""
    # TODO: Phase 2 实现
    return ApiResponse.success()


@router.put("/update")
async def update_seal(user_id: int = Depends(get_seal_user_id)):
    """更新印章"""
    # TODO: Phase 2 实现
    return ApiResponse.success()


@router.delete("/delete")
async def delete_seal(user_id: int = Depends(get_seal_user_id)):
    """删除印章"""
    # TODO: Phase 2 实现
    return ApiResponse.success()


@router.put("/set-default")
async def set_default_seal(user_id: int = Depends(get_seal_user_id)):
    """设为默认印章"""
    # TODO: Phase 2 实现
    return ApiResponse.success()
