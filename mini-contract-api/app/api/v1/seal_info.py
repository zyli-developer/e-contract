from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.response import ApiResponse
from app.database import get_db
from app.dependencies import get_current_user_id
from app.schemas.seal import SealCreateRequest, SealUpdateRequest
from app.services import seal_service

router = APIRouter(prefix="/seal/seal-info", tags=["印章管理"])


@router.get("/page")
async def list_seals(
    pageNo: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=50),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """印章列表（分页）"""
    result = await seal_service.list_seals(db, user_id, pageNo, pageSize)
    return ApiResponse.success(data=result.model_dump())


@router.post("/create")
async def create_seal(
    req: SealCreateRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """创建印章"""
    result = await seal_service.create_seal(db, user_id, req.name, req.type, req.seal_data)
    return ApiResponse.success(data=result)


@router.put("/update")
async def update_seal(
    req: SealUpdateRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """更新印章"""
    result = await seal_service.update_seal(db, user_id, req.id, req.name, req.seal_data)
    return ApiResponse.success(data=result)


@router.delete("/delete")
async def delete_seal(
    id: int = Query(...),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """删除印章"""
    await seal_service.delete_seal(db, user_id, id)
    return ApiResponse.success()


@router.put("/set-default")
async def set_default_seal(
    id: int = Query(...),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """设为默认印章"""
    await seal_service.set_default_seal(db, user_id, id)
    return ApiResponse.success()
