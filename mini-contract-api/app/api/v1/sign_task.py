from fastapi import APIRouter, Depends

from app.core.response import ApiResponse
from app.dependencies import get_current_user_id

router = APIRouter(prefix="/seal/sign-task", tags=["合同签署"])


@router.get("/statistics")
async def get_statistics(user_id: int = Depends(get_current_user_id)):
    """合同统计"""
    # TODO: Phase 4 实现
    return ApiResponse.success()


@router.get("/page")
async def list_tasks(user_id: int = Depends(get_current_user_id)):
    """合同列表（分页）"""
    # TODO: Phase 4 实现
    return ApiResponse.success()


@router.get("/get")
async def get_task(user_id: int = Depends(get_current_user_id)):
    """合同详情"""
    # TODO: Phase 4 实现
    return ApiResponse.success()


@router.post("/create")
async def create_task(user_id: int = Depends(get_current_user_id)):
    """创建合同"""
    # TODO: Phase 3 实现
    return ApiResponse.success()


@router.delete("/cancel")
async def cancel_task(user_id: int = Depends(get_current_user_id)):
    """取消合同"""
    # TODO: Phase 4 实现
    return ApiResponse.success()


@router.delete("/delete")
async def delete_task(user_id: int = Depends(get_current_user_id)):
    """删除合同"""
    # TODO: Phase 4 实现
    return ApiResponse.success()


@router.post("/{task_id}/urge")
async def urge_sign(task_id: int, user_id: int = Depends(get_current_user_id)):
    """催签"""
    # TODO: Phase 4 实现
    return ApiResponse.success()
