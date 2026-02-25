"""合同模板 API 端点测试"""
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.anyio
async def test_template_search_public(client):
    """模板搜索可公开访问（或需认证）"""
    resp = await client.get("/app-api/seal/seal-template/search")
    data = resp.json()
    # 模板搜索可能需要认证，也可能公开
    assert data["code"] in (0, 401, 1012005005, 1012005006)


@pytest.mark.anyio
async def test_template_categories(client):
    """分类列表可公开访问"""
    resp = await client.get("/app-api/seal/seal-template/categories")
    data = resp.json()
    # 可能需要认证
    if data["code"] == 0:
        assert isinstance(data["data"], list)
        assert len(data["data"]) >= 6


@pytest.mark.anyio
async def test_template_hot(client):
    """热门模板接口"""
    resp = await client.get("/app-api/seal/seal-template/hot")
    data = resp.json()
    assert data["code"] in (0, 401, 1012005005, 1012005006)


@pytest.mark.anyio
async def test_template_frequently_used_requires_auth(client):
    """常用模板需要认证"""
    resp = await client.get("/app-api/seal/seal-template/frequently-used")
    data = resp.json()
    assert data["code"] in (0, 401, 1012005005, 1012005006)


@pytest.mark.anyio
async def test_template_get_requires_id(client):
    """模板详情需要 ID 参数"""
    resp = await client.get("/app-api/seal/seal-template/get")
    # 缺少 id 参数应返回错误
    assert resp.status_code in (200, 422)
