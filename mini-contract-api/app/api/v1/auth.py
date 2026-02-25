from fastapi import APIRouter, Depends

from app.core.response import ApiResponse
from app.dependencies import get_current_user_id

router = APIRouter(prefix="/member/auth", tags=["认证"])


@router.post("/login")
async def login():
    """密码登录"""
    # TODO: Phase 1 实现
    return ApiResponse.success()


@router.post("/sms-login")
async def sms_login():
    """短信验证码登录（登录即注册）"""
    # TODO: Phase 1 实现
    return ApiResponse.success()


@router.post("/send-sms-code")
async def send_sms_code():
    """发送短信验证码"""
    # TODO: Phase 1 实现
    return ApiResponse.success()


@router.post("/social-login")
async def social_login():
    """社交登录（微信小程序）"""
    # TODO: Phase 1 实现
    return ApiResponse.success()


@router.post("/refresh-token")
async def refresh_token():
    """刷新 Token"""
    # TODO: Phase 1 实现
    return ApiResponse.success()


@router.post("/logout")
async def logout(user_id: int = Depends(get_current_user_id)):
    """退出登录"""
    # TODO: Phase 1 实现
    return ApiResponse.success()
