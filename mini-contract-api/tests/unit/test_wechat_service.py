"""微信服务单元测试"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.services import wechat_service


@pytest.mark.anyio
@patch("app.services.wechat_service.httpx.AsyncClient")
async def test_get_access_token_success(mock_client_cls):
    """成功获取 access_token"""
    # 清除缓存
    wechat_service._access_token_cache["token"] = ""
    wechat_service._access_token_cache["expires_at"] = 0

    mock_resp = MagicMock()
    mock_resp.json.return_value = {"access_token": "test_token_123", "expires_in": 7200}

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_resp
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client_cls.return_value = mock_client

    token = await wechat_service.get_access_token()
    assert token == "test_token_123"


@pytest.mark.anyio
@patch("app.services.wechat_service.httpx.AsyncClient")
async def test_get_access_token_cached(mock_client_cls):
    """缓存未过期时直接返回"""
    import time
    wechat_service._access_token_cache["token"] = "cached_token"
    wechat_service._access_token_cache["expires_at"] = time.time() + 3600

    token = await wechat_service.get_access_token()
    assert token == "cached_token"
    mock_client_cls.assert_not_called()

    # 清理
    wechat_service._access_token_cache["token"] = ""
    wechat_service._access_token_cache["expires_at"] = 0


@pytest.mark.anyio
@patch("app.services.wechat_service.httpx.AsyncClient")
async def test_get_access_token_failure(mock_client_cls):
    """获取 access_token 失败"""
    wechat_service._access_token_cache["token"] = ""
    wechat_service._access_token_cache["expires_at"] = 0

    mock_resp = MagicMock()
    mock_resp.json.return_value = {"errcode": 40013, "errmsg": "invalid appid"}

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_resp
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client_cls.return_value = mock_client

    with pytest.raises(RuntimeError, match="access_token"):
        await wechat_service.get_access_token()


@pytest.mark.anyio
@patch("app.services.wechat_service.httpx.AsyncClient")
async def test_jscode2session_success(mock_client_cls):
    """成功获取 openid"""
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "openid": "o1234567890",
        "session_key": "sk_test",
    }

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_resp
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client_cls.return_value = mock_client

    data = await wechat_service.jscode2session("test_code")
    assert data["openid"] == "o1234567890"


@pytest.mark.anyio
@patch("app.services.wechat_service.httpx.AsyncClient")
async def test_jscode2session_failure(mock_client_cls):
    """code 无效"""
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"errcode": 40029, "errmsg": "invalid code"}

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_resp
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client_cls.return_value = mock_client

    with pytest.raises(RuntimeError, match="登录凭证校验失败"):
        await wechat_service.jscode2session("invalid_code")


@pytest.mark.anyio
@patch("app.services.wechat_service.get_access_token", new_callable=AsyncMock)
@patch("app.services.wechat_service.httpx.AsyncClient")
async def test_check_realname_match(mock_client_cls, mock_get_token):
    """姓名和身份证号匹配"""
    mock_get_token.return_value = "test_token"

    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "errcode": 0,
        "errmsg": "ok",
        "verify_openid": "V_OP_NM_MA",
        "verify_real_name": "V_NM_ID_MA",
    }

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_resp
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client_cls.return_value = mock_client

    result = await wechat_service.check_realname_info(
        openid="o1234567890",
        real_name="张三",
        cred_id="110101199003070070",
        auth_code="auth_code_test",
    )

    assert result["errcode"] == 0
    assert result["verify_openid"] == "V_OP_NM_MA"
    assert result["verify_real_name"] == "V_NM_ID_MA"


@pytest.mark.anyio
@patch("app.services.wechat_service.get_access_token", new_callable=AsyncMock)
@patch("app.services.wechat_service.httpx.AsyncClient")
async def test_check_realname_name_mismatch(mock_client_cls, mock_get_token):
    """姓名与微信实名信息不一致"""
    mock_get_token.return_value = "test_token"

    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "errcode": 0,
        "errmsg": "ok",
        "verify_openid": "V_OP_NM_UM",
    }

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_resp
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client_cls.return_value = mock_client

    result = await wechat_service.check_realname_info(
        openid="o1234567890",
        real_name="李震与",
        cred_id="110101199003070070",
        auth_code="auth_code_test",
    )

    assert result["verify_openid"] == "V_OP_NM_UM"


@pytest.mark.anyio
@patch("app.services.wechat_service.get_access_token", new_callable=AsyncMock)
@patch("app.services.wechat_service.httpx.AsyncClient")
async def test_check_realname_id_mismatch(mock_client_cls, mock_get_token):
    """姓名匹配但身份证号不匹配"""
    mock_get_token.return_value = "test_token"

    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "errcode": 0,
        "errmsg": "ok",
        "verify_openid": "V_OP_NM_MA",
        "verify_real_name": "V_NM_ID_UM",
    }

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_resp
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client_cls.return_value = mock_client

    result = await wechat_service.check_realname_info(
        openid="o1234567890",
        real_name="张三",
        cred_id="110101199003070070",
        auth_code="auth_code_test",
    )

    assert result["verify_openid"] == "V_OP_NM_MA"
    assert result["verify_real_name"] == "V_NM_ID_UM"
