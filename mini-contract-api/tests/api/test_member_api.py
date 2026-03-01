"""用户管理 API 测试"""
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.anyio
async def test_get_user_requires_auth(client):
    """获取用户信息需要认证"""
    resp = await client.get("/app-api/member/user/get")
    data = resp.json()
    assert data.get("code") in (401, 1012005005, 1012005006)


@pytest.mark.anyio
async def test_update_user_requires_auth(client):
    """更新用户信息需要认证"""
    resp = await client.put("/app-api/member/user/update", json={"nickname": "test"})
    data = resp.json()
    assert data.get("code") in (401, 1012005005, 1012005006)


@pytest.mark.anyio
async def test_update_password_requires_auth(client):
    """修改密码需要认证"""
    resp = await client.put(
        "/app-api/member/user/update-password",
        json={"password": "123456", "confirmPassword": "123456"},
    )
    data = resp.json()
    assert data.get("code") in (401, 1012005005, 1012005006)


@pytest.mark.anyio
async def test_update_password_missing_confirm(client):
    """修改密码缺少 confirmPassword 应被拦截（认证优先于参数校验）"""
    resp = await client.put(
        "/app-api/member/user/update-password",
        json={"password": "123456"},
    )
    data = resp.json()
    # 未认证时，认证中间件先拦截，不会到达参数校验
    assert data.get("code") in (401, 1012005005, 1012005006)
