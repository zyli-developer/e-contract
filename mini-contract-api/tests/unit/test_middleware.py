"""中间件单元测试"""
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.anyio
async def test_process_time_header():
    """响应应包含 X-Process-Time header"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/health")
        assert "x-process-time" in resp.headers
        # 值应为数字（毫秒）
        process_time = float(resp.headers["x-process-time"])
        assert process_time >= 0


@pytest.mark.anyio
async def test_process_time_header_on_404():
    """404 请求也应有 X-Process-Time"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/nonexistent-path")
        assert "x-process-time" in resp.headers


@pytest.mark.anyio
async def test_process_time_header_on_api_endpoint():
    """API 端点也应有 X-Process-Time"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/app-api/member/user/get")
        assert "x-process-time" in resp.headers
