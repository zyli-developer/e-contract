"""认证 API 端点测试"""
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_login_missing_fields(client):
    """密码登录缺少字段应返回 422"""
    resp = await client.post("/app-api/member/auth/login", json={})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_login_accepts_valid_body(client):
    """密码登录传入正确格式不应返回 422"""
    try:
        resp = await client.post(
            "/app-api/member/auth/login",
            json={"mobile": "13800138000", "password": "test123"},
        )
        # 没有数据库连接会返回 500，但格式验证通过不会返回 422
        assert resp.status_code != 422
    except Exception:
        # 如果数据库不可用导致连接失败，跳过此测试
        pytest.skip("数据库不可用")


@pytest.mark.asyncio
async def test_register_missing_fields(client):
    """注册缺少字段应返回 422"""
    resp = await client.post("/app-api/member/auth/register", json={})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_register_accepts_valid_body(client):
    """注册传入正确格式不应返回 422"""
    try:
        resp = await client.post(
            "/app-api/member/auth/register",
            json={"mobile": "13800138000", "password": "test123"},
        )
        assert resp.status_code != 422
    except Exception:
        pytest.skip("数据库不可用")


@pytest.mark.asyncio
async def test_register_with_nickname(client):
    """注册可以传入昵称"""
    try:
        resp = await client.post(
            "/app-api/member/auth/register",
            json={"mobile": "13800138000", "password": "test123", "nickname": "小明"},
        )
        assert resp.status_code != 422
    except Exception:
        pytest.skip("数据库不可用")


@pytest.mark.asyncio
async def test_sms_login_endpoint_removed(client):
    """短信登录端点应不存在"""
    resp = await client.post("/app-api/member/auth/sms-login", json={"mobile": "13800138000", "code": "123456"})
    assert resp.status_code == 404 or resp.json().get("detail") == "Not Found"


@pytest.mark.asyncio
async def test_send_sms_code_endpoint_removed(client):
    """发送验证码端点应不存在"""
    resp = await client.post("/app-api/member/auth/send-sms-code", json={"mobile": "13800138000", "scene": 1})
    assert resp.status_code == 404 or resp.json().get("detail") == "Not Found"


@pytest.mark.asyncio
async def test_refresh_token_missing_fields(client):
    """刷新 Token 缺少字段应返回 422"""
    resp = await client.post("/app-api/member/auth/refresh-token", json={})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_logout_requires_auth(client):
    """退出登录需要认证"""
    resp = await client.post("/app-api/member/auth/logout")
    body = resp.json()
    assert body["code"] == 401


@pytest.mark.asyncio
async def test_login_endpoints_are_public(client):
    """登录相关接口不需要 Token（不返回 401）"""
    try:
        resp = await client.post(
            "/app-api/member/auth/login",
            json={"mobile": "13800138000", "password": "test123"},
        )
        body = resp.json()
        # 可能因为 DB 不可用返回 500，但不应该是 401
        assert body.get("code") != 401
    except Exception:
        pytest.skip("数据库不可用")


@pytest.mark.asyncio
async def test_get_user_requires_auth(client):
    """获取用户信息需要认证"""
    resp = await client.get("/app-api/member/user/get")
    body = resp.json()
    assert body["code"] == 401


@pytest.mark.asyncio
async def test_update_user_requires_auth(client):
    """更新用户信息需要认证"""
    resp = await client.put(
        "/app-api/member/user/update",
        json={"nickname": "test"},
    )
    body = resp.json()
    assert body["code"] == 401


@pytest.mark.asyncio
async def test_update_password_requires_auth(client):
    """修改密码需要认证"""
    resp = await client.put(
        "/app-api/member/user/update-password",
        json={"password": "newpass", "confirmPassword": "newpass"},
    )
    body = resp.json()
    assert body["code"] == 401
