from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.response import ApiResponse
from app.database import get_db
from app.dependencies import get_current_user_id
from app.schemas.auth import UpdatePasswordRequest
from app.schemas.member import UpdateUserRequest
from app.services import member_service

router = APIRouter(prefix="/member/user", tags=["用户信息"])


@router.get("/get")
async def get_user_info(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """获取当前用户信息"""
    result = await member_service.get_user_info(db, user_id)
    return ApiResponse.success(data=result.model_dump())


@router.put("/update")
async def update_user_info(
    req: UpdateUserRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """更新用户信息"""
    result = await member_service.update_user_info(
        db, user_id, nickname=req.nickname, avatar=req.avatar
    )
    return ApiResponse.success(data=result.model_dump())


@router.put("/update-password")
async def update_password(
    req: UpdatePasswordRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """修改密码"""
    await member_service.update_password(db, user_id, req.password, req.code)
    return ApiResponse.success()
