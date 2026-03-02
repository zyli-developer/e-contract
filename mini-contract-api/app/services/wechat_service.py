"""微信 API 服务：access_token 管理、jscode2session、城市服务实名校验"""
import time

import httpx
from loguru import logger

from app.config import settings

# access_token 缓存（进程级别）
_access_token_cache: dict = {"token": "", "expires_at": 0}

# 微信城市服务实名校验授权小程序 AppID
WECHAT_REALNAME_AUTH_APPID = "wx308bd2aeb83d3345"


async def get_access_token() -> str:
    """
    获取小程序全局 access_token（带内存缓存）。
    有效期 7200s，提前 300s 刷新。
    """
    now = time.time()
    if _access_token_cache["token"] and _access_token_cache["expires_at"] > now + 300:
        return _access_token_cache["token"]

    url = "https://api.weixin.qq.com/cgi-bin/token"
    params = {
        "grant_type": "client_credential",
        "appid": settings.WECHAT_APP_ID,
        "secret": settings.WECHAT_APP_SECRET,
    }

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url, params=params)
        data = resp.json()

    if "access_token" not in data:
        errcode = data.get("errcode", "unknown")
        errmsg = data.get("errmsg", "unknown")
        logger.error("获取微信 access_token 失败: errcode=%s, errmsg=%s", errcode, errmsg)
        raise RuntimeError(f"获取微信 access_token 失败: {errmsg}")

    _access_token_cache["token"] = data["access_token"]
    _access_token_cache["expires_at"] = now + data.get("expires_in", 7200)
    return data["access_token"]


async def jscode2session(code: str) -> dict:
    """
    通过 wx.login() 获得的 code 换取 openid 和 session_key。
    返回 {"openid": "...", "session_key": "...", "unionid": "..."(可选)}
    """
    url = "https://api.weixin.qq.com/sns/jscode2session"
    params = {
        "appid": settings.WECHAT_APP_ID,
        "secret": settings.WECHAT_APP_SECRET,
        "js_code": code,
        "grant_type": "authorization_code",
    }

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url, params=params)
        data = resp.json()

    if "openid" not in data:
        errcode = data.get("errcode", "unknown")
        errmsg = data.get("errmsg", "unknown")
        logger.error("jscode2session 失败: errcode=%s, errmsg=%s", errcode, errmsg)
        raise RuntimeError(f"微信登录凭证校验失败: {errmsg}")

    return data


async def check_realname_info(
    openid: str,
    real_name: str,
    cred_id: str,
    auth_code: str,
) -> dict:
    """
    调用微信城市服务实名信息校验 API (checkrealnameinfo)。

    参数:
        openid:    用户在本小程序下的 openid
        real_name: 待校验真实姓名
        cred_id:   待校验身份证号
        auth_code: 前端跳转微信授权小程序后获得的授权 code

    返回:
        {"errcode": 0, "verify_openid": "V_OP_NM_MA", "verify_real_name": "V_NM_ID_MA"}

    verify_openid 取值:
        V_OP_NM_MA  — 微信支付实名与提供的姓名一致
        V_OP_NM_UM  — 微信支付实名与提供的姓名不一致
        V_OP_NA     — 用户未完成微信支付实名认证

    verify_real_name 取值（仅 verify_openid=V_OP_NM_MA 时返回）:
        V_NM_ID_MA  — 姓名与身份证号匹配
        V_NM_ID_UM  — 姓名与身份证号不匹配
    """
    access_token = await get_access_token()

    url = f"https://api.weixin.qq.com/intp/realname/checkrealnameinfo?access_token={access_token}"
    payload = {
        "openid": openid,
        "real_name": real_name,
        "cred_id": cred_id,
        "cred_type": "1",  # 大陆身份证
        "code": auth_code,
    }

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(url, json=payload)
        data = resp.json()

    logger.info(
        "checkrealnameinfo 结果: openid=%s, errcode=%s, verify_openid=%s, verify_real_name=%s",
        openid,
        data.get("errcode"),
        data.get("verify_openid"),
        data.get("verify_real_name"),
    )

    return data
