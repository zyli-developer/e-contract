"""印章管理 API 端点测试"""
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.anyio
async def test_seal_list_requires_auth(client):
    """印章列表需要认证"""
    resp = await client.get("/app-api/seal/seal-info/page")
    data = resp.json()
    assert data["code"] in (401, 1012005005, 1012005006)


@pytest.mark.anyio
async def test_seal_create_requires_auth(client):
    """创建印章需要认证"""
    resp = await client.post(
        "/app-api/seal/seal-info/create",
        json={"name": "签名", "type": 11, "seal_data": "http://img.png"},
    )
    data = resp.json()
    assert data["code"] in (401, 1012005005, 1012005006)


@pytest.mark.anyio
async def test_seal_update_requires_auth(client):
    """更新印章需要认证"""
    resp = await client.put(
        "/app-api/seal/seal-info/update",
        json={"id": 1, "name": "新名称"},
    )
    data = resp.json()
    assert data["code"] in (401, 1012005005, 1012005006)


@pytest.mark.anyio
async def test_seal_delete_requires_auth(client):
    """删除印章需要认证"""
    resp = await client.delete("/app-api/seal/seal-info/delete?id=1")
    data = resp.json()
    assert data["code"] in (401, 1012005005, 1012005006)


@pytest.mark.anyio
async def test_seal_set_default_requires_auth(client):
    """设置默认印章需要认证"""
    resp = await client.put("/app-api/seal/seal-info/set-default?id=1")
    data = resp.json()
    assert data["code"] in (401, 1012005005, 1012005006)
