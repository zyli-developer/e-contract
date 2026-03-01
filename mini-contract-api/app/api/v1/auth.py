from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.response import ApiResponse
from app.core.security import rsa_decrypt
from app.database import get_db
from app.dependencies import get_current_user_id
from app.schemas.auth import (
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
)
from app.services import auth_service

router = APIRouter(prefix="/member/auth", tags=["认证"])


@router.get("/public-key")
async def get_public_key():
    """获取 RSA 公钥（前端加密密码用）"""
    return ApiResponse.success(data={"publicKey": settings.RSA_PUBLIC_KEY})


@router.post("/login")
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    """密码登录"""
    password = rsa_decrypt(req.password)
    result = await auth_service.login_by_password(db, req.mobile, password)
    return ApiResponse.success(data=result.model_dump())


@router.post("/register")
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """用户注册"""
    password = rsa_decrypt(req.password)
    result = await auth_service.register(db, req.mobile, password, req.nickname)
    return ApiResponse.success(data=result.model_dump())


@router.post("/refresh-token")
async def refresh_token(req: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """刷新 Token"""
    result = await auth_service.refresh_token(db, req.refreshToken)
    return ApiResponse.success(data=result.model_dump())


@router.post("/logout")
async def logout(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """退出登录"""
    await auth_service.logout(db, user_id)
    return ApiResponse.success()
