"""微信登录服务"""
import logging

import httpx

from app.config import settings
from app.core.exceptions import BusinessException

logger = logging.getLogger(__name__)

WECHAT_CODE2SESSION_URL = "https://api.weixin.qq.com/sns/jscode2session"


async def code2session(code: str) -> dict:
    """调用微信 code2Session 接口获取 openid 和 session_key

    Args:
        code: 微信小程序 wx.login() 获取的临时登录凭证

    Returns:
        dict: {"openid": "...", "session_key": "...", "unionid": "..."}
    """
    if not settings.WECHAT_MINI_APP_ID or not settings.WECHAT_MINI_APP_SECRET:
        raise BusinessException(code=500, msg="微信小程序配置缺失")

    params = {
        "appid": settings.WECHAT_MINI_APP_ID,
        "secret": settings.WECHAT_MINI_APP_SECRET,
        "js_code": code,
        "grant_type": "authorization_code",
    }

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(WECHAT_CODE2SESSION_URL, params=params)
        data = resp.json()

    if "errcode" in data and data["errcode"] != 0:
        logger.error(f"微信 code2Session 失败: {data}")
        raise BusinessException(code=1012003001, msg=f"微信登录失败: {data.get('errmsg', '未知错误')}")

    return {
        "openid": data["openid"],
        "session_key": data.get("session_key", ""),
        "unionid": data.get("unionid"),
    }
