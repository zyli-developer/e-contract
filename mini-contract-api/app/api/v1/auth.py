from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.response import ApiResponse
from app.database import get_db
from app.dependencies import get_current_user_id
from app.schemas.auth import (
    LoginRequest,
    RefreshTokenRequest,
    SendSmsCodeRequest,
    SmsLoginRequest,
)
from app.services import auth_service
from app.services.sms_service import send_sms_code as sms_send

router = APIRouter(prefix="/member/auth", tags=["认证"])


@router.post("/login")
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    """密码登录"""
    result = await auth_service.login_by_password(db, req.mobile, req.password)
    return ApiResponse.success(data=result.model_dump())


@router.post("/sms-login")
async def sms_login(req: SmsLoginRequest, db: AsyncSession = Depends(get_db)):
    """短信验证码登录（登录即注册）"""
    result = await auth_service.login_by_sms(db, req.mobile, req.code)
    return ApiResponse.success(data=result.model_dump())


@router.post("/send-sms-code")
async def send_sms_code(req: SendSmsCodeRequest):
    """发送短信验证码"""
    await sms_send(req.mobile, req.scene)
    return ApiResponse.success()


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
