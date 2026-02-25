"""合同签署 API 端点测试"""
import pytest
from unittest.mock import patch, AsyncMock

from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


def _auth_header(token="test"):
    return {"Authorization": f"Bearer {token}"}


# --- 无需认证的异常测试 ---

@pytest.mark.anyio
async def test_statistics_requires_auth(client):
    """统计接口需要认证"""
    resp = await client.get("/app-api/seal/sign-task/statistics")
    data = resp.json()
    assert data["code"] in (401, 1012005005, 1012005006)


@pytest.mark.anyio
async def test_list_requires_auth(client):
    """列表接口需要认证"""
    resp = await client.get("/app-api/seal/sign-task/page")
    data = resp.json()
    assert data["code"] in (401, 1012005005, 1012005006)


@pytest.mark.anyio
async def test_get_detail_requires_auth(client):
    """详情接口需要认证"""
    resp = await client.get("/app-api/seal/sign-task/get?id=1")
    data = resp.json()
    assert data["code"] in (401, 1012005005, 1012005006)


@pytest.mark.anyio
async def test_create_requires_auth(client):
    """创建接口需要认证"""
    resp = await client.post("/app-api/seal/sign-task/create", json={"name": "test"})
    data = resp.json()
    assert data["code"] in (401, 1012005005, 1012005006)


@pytest.mark.anyio
async def test_initiate_requires_auth(client):
    """发起签署接口需要认证"""
    resp = await client.post("/app-api/seal/sign-task/1/initiate")
    data = resp.json()
    assert data["code"] in (401, 1012005005, 1012005006)


@pytest.mark.anyio
async def test_send_sign_code_requires_auth(client):
    """发送签署验证码需要认证"""
    resp = await client.post("/app-api/seal/sign-task/1/send-sign-code")
    data = resp.json()
    assert data["code"] in (401, 1012005005, 1012005006)


@pytest.mark.anyio
async def test_verify_sign_code_requires_auth(client):
    """验证签署验证码需要认证"""
    resp = await client.post(
        "/app-api/seal/sign-task/1/verify-sign-code",
        json={"code": "123456"},
    )
    data = resp.json()
    assert data["code"] in (401, 1012005005, 1012005006)


@pytest.mark.anyio
async def test_sign_requires_auth(client):
    """执行签署需要认证"""
    resp = await client.post("/app-api/seal/sign-task/1/sign", json={})
    data = resp.json()
    assert data["code"] in (401, 1012005005, 1012005006)


@pytest.mark.anyio
async def test_reject_requires_auth(client):
    """拒签需要认证"""
    resp = await client.post("/app-api/seal/sign-task/1/reject", json={})
    data = resp.json()
    assert data["code"] in (401, 1012005005, 1012005006)


@pytest.mark.anyio
async def test_verify_hash_requires_auth(client):
    """哈希校验需要认证"""
    resp = await client.get("/app-api/seal/sign-task/1/verify-hash")
    data = resp.json()
    assert data["code"] in (401, 1012005005, 1012005006)


@pytest.mark.anyio
async def test_evidence_requires_auth(client):
    """证据链需要认证"""
    resp = await client.get("/app-api/seal/sign-task/1/evidence")
    data = resp.json()
    assert data["code"] in (401, 1012005005, 1012005006)


@pytest.mark.anyio
async def test_validate_permission_requires_auth(client):
    """权限验证需要认证"""
    resp = await client.get("/app-api/seal/sign-task/validate-permission?id=1")
    data = resp.json()
    assert data["code"] in (401, 1012005005, 1012005006)


@pytest.mark.anyio
async def test_cancel_requires_auth(client):
    """取消接口需要认证"""
    resp = await client.delete("/app-api/seal/sign-task/cancel?id=1")
    data = resp.json()
    assert data["code"] in (401, 1012005005, 1012005006)


@pytest.mark.anyio
async def test_delete_requires_auth(client):
    """删除接口需要认证"""
    resp = await client.delete("/app-api/seal/sign-task/delete?id=1")
    data = resp.json()
    assert data["code"] in (401, 1012005005, 1012005006)


@pytest.mark.anyio
async def test_urge_requires_auth(client):
    """催签接口需要认证"""
    resp = await client.post("/app-api/seal/sign-task/1/urge")
    data = resp.json()
    assert data["code"] in (401, 1012005005, 1012005006)
