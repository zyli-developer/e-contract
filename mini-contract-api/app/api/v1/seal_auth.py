from fastapi import APIRouter, Depends

from app.core.response import ApiResponse
from app.dependencies import get_current_user_id

router = APIRouter(prefix="/seal/auth", tags=["Seal Token"])


@router.post("/exchange-token")
async def exchange_token(user_id: int = Depends(get_current_user_id)):
    """用 Access Token 换取 Seal Token"""
    # TODO: Phase 2 实现
    return ApiResponse.success()
