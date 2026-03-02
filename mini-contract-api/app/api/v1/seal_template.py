from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.response import ApiResponse
from app.database import get_db
from app.dependencies import require_landlord
from app.services import template_service

router = APIRouter(prefix="/seal/seal-template", tags=["合同模板"])


@router.get("/search")
async def search_templates(
    keyword: str | None = None,
    category: str | None = None,
    pageNo: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=50),
    user_id: int = Depends(require_landlord),
    db: AsyncSession = Depends(get_db),
):
    """搜索模板"""
    result = await template_service.search_templates(db, keyword, category, pageNo, pageSize)
    return ApiResponse.success(data=result.model_dump())


@router.get("/get")
async def get_template(
    id: int = Query(...),
    user_id: int = Depends(require_landlord),
    db: AsyncSession = Depends(get_db),
):
    """模板详情"""
    result = await template_service.get_template_detail(db, id)
    return ApiResponse.success(data=result)


@router.get("/categories")
async def get_categories(
    user_id: int = Depends(require_landlord),
):
    """分类列表"""
    return ApiResponse.success(data=template_service.CATEGORIES)


@router.get("/hot")
async def get_hot_templates(
    limit: int = Query(6, ge=1, le=20),
    user_id: int = Depends(require_landlord),
    db: AsyncSession = Depends(get_db),
):
    """热门模板"""
    result = await template_service.get_hot_templates(db, limit)
    return ApiResponse.success(data=result)


@router.get("/frequently-used")
async def get_frequently_used(
    limit: int = Query(8, ge=1, le=20),
    user_id: int = Depends(require_landlord),
    db: AsyncSession = Depends(get_db),
):
    """常用模板"""
    result = await template_service.get_frequently_used(db, limit)
    return ApiResponse.success(data=result)
