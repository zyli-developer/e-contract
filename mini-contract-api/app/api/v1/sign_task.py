from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.response import ApiResponse
from app.database import get_db
from app.dependencies import get_current_user_id
from app.schemas.contract import SignTaskCreateRequest
from app.services import sign_task_service

router = APIRouter(prefix="/seal/sign-task", tags=["合同签署"])


@router.get("/statistics")
async def get_statistics(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """合同统计"""
    result = await sign_task_service.get_statistics(db, user_id)
    return ApiResponse.success(data=result)


@router.get("/page")
async def list_tasks(
    status: int | None = None,
    pageNo: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=50),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """合同列表（分页）"""
    result = await sign_task_service.list_tasks(db, user_id, status, pageNo, pageSize)
    return ApiResponse.success(data=result.model_dump())


@router.get("/get")
async def get_task(
    id: int = Query(...),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """合同详情"""
    result = await sign_task_service.get_task_detail(db, id, user_id)
    return ApiResponse.success(data=result)


@router.post("/create")
async def create_task(
    req: SignTaskCreateRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """创建合同"""
    result = await sign_task_service.create_sign_task(
        db,
        creator_id=user_id,
        name=req.name,
        template_id=req.template_id,
        file_url=req.file_url,
        remark=req.remark,
        participants=req.participants,
    )
    return ApiResponse.success(data=result)


@router.delete("/cancel")
async def cancel_task(
    id: int = Query(...),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """取消合同"""
    await sign_task_service.cancel_task(db, id, user_id)
    return ApiResponse.success()


@router.delete("/delete")
async def delete_task(
    id: int = Query(...),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """删除合同"""
    await sign_task_service.delete_task(db, id, user_id)
    return ApiResponse.success()


@router.post("/{task_id}/urge")
async def urge_sign(
    task_id: int,
    user_id: int = Depends(get_current_user_id),
):
    """催签（MVP 阶段仅返回成功，后续接入通知服务）"""
    # TODO: Phase 4 接入通知服务
    return ApiResponse.success()
