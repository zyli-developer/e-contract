"""主应用模块单元测试"""
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_endpoint(client):
    """health 端点应返回 ok"""
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_cors_headers(client):
    """CORS 应允许跨域请求"""
    resp = await client.options(
        "/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert "access-control-allow-origin" in resp.headers


@pytest.mark.asyncio
async def test_api_prefix(client):
    """API 路由应在 /app-api 前缀下"""
    resp = await client.get("/app-api/member/user/get")
    # 应触发 401 而非 404（说明路由存在）
    body = resp.json()
    assert body["code"] == 401


@pytest.mark.asyncio
async def test_nonexistent_route_404(client):
    """不存在的路由应返回 404"""
    resp = await client.get("/app-api/nonexistent/endpoint")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_auth_endpoints_accessible(client):
    """认证端点应可访问（不需要 token）"""
    resp = await client.post("/app-api/member/auth/login", json={})
    # 应返回 422 (参数不全) 而非 401
    assert resp.status_code in [200, 422]


@pytest.mark.asyncio
async def test_app_metadata():
    """应用元数据应正确设置"""
    assert app.title is not None
    assert app.version == "1.0.0"
