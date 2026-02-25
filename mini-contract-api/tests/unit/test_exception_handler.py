"""异常处理器测试"""
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_business_exception_returns_json(client):
    """BusinessException 应返回 HTTP 200 + code/msg/data 结构"""
    # 访问需要认证的接口但不传 Token → 触发 UnauthorizedException
    resp = await client.get("/app-api/member/user/get")
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 401
    assert body["data"] is None
    assert "msg" in body


@pytest.mark.asyncio
async def test_unauthorized_without_token(client):
    """无 Token 访问受保护接口应返回 401 业务码"""
    resp = await client.get("/app-api/member/user/get")
    body = resp.json()
    assert body["code"] == 401


@pytest.mark.asyncio
async def test_unauthorized_with_invalid_token(client):
    """无效 Token 应返回 401 业务码"""
    resp = await client.get(
        "/app-api/member/user/get",
        headers={"Authorization": "Bearer invalid.token.here"},
    )
    body = resp.json()
    assert body["code"] == 401


@pytest.mark.asyncio
async def test_not_found_returns_404(client):
    """访问不存在的路由应返回 404"""
    resp = await client.get("/app-api/nonexistent/path")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_health_no_auth_required(client):
    """health 接口是公开的，不需要认证"""
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
