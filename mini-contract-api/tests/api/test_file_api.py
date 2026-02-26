"""文件管理 API 测试"""
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.anyio
async def test_upload_requires_auth(client):
    """上传文件需要认证"""
    resp = await client.post("/app-api/infra/file/upload")
    data = resp.json()
    assert data.get("code") in (401, 1012005005, 1012005006) or resp.status_code == 422


@pytest.mark.anyio
async def test_presigned_url_requires_auth(client):
    """获取预签名 URL 需要认证"""
    resp = await client.get("/app-api/infra/file/presigned-url", params={"filename": "test.pdf"})
    data = resp.json()
    assert data.get("code") in (401, 1012005005, 1012005006)
