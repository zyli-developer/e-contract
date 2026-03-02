from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.response import ApiResponse
from app.core.security import rsa_decrypt
from app.database import get_db
from app.dependencies import get_current_user_id
from app.schemas.auth import UpdatePasswordRequest
from app.schemas.member import UpdateUserRequest, RealNameVerifyRequest
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
    password = rsa_decrypt(req.password)
    confirm = rsa_decrypt(req.confirmPassword)
    await member_service.update_password(db, user_id, password, confirm)
    return ApiResponse.success()


@router.post("/verify-realname")
async def verify_realname(
    req: RealNameVerifyRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """实名认证"""
    result = await member_service.verify_real_name(
        db, user_id,
        real_name=req.real_name,
        id_card=req.id_card,
        id_card_front_url=req.id_card_front_url,
        id_card_back_url=req.id_card_back_url,
    )
    return ApiResponse.success(data=result)
