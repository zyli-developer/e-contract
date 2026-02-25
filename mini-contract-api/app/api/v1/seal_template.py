from fastapi import APIRouter, Depends

from app.core.response import ApiResponse
from app.dependencies import get_current_user_id

router = APIRouter(prefix="/seal/seal-template", tags=["合同模板"])


@router.get("/search")
async def search_templates(user_id: int = Depends(get_current_user_id)):
    """搜索模板"""
    # TODO: Phase 3 实现
    return ApiResponse.success()


@router.get("/get")
async def get_template(user_id: int = Depends(get_current_user_id)):
    """模板详情"""
    # TODO: Phase 3 实现
    return ApiResponse.success()


@router.get("/categories")
async def get_categories(user_id: int = Depends(get_current_user_id)):
    """分类列表"""
    # TODO: Phase 3 实现
    return ApiResponse.success()


@router.get("/hot")
async def get_hot_templates(user_id: int = Depends(get_current_user_id)):
    """热门模板"""
    # TODO: Phase 3 实现
    return ApiResponse.success()


@router.get("/frequently-used")
async def get_frequently_used(user_id: int = Depends(get_current_user_id)):
    """常用模板"""
    # TODO: Phase 3 实现
    return ApiResponse.success()
