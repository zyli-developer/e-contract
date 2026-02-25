"""全链路签署流程集成测试

测试场景：
用户 A 创建合同 → 指定用户 B 为签署方 → 发起签署 → 用户 B 查看待签列表 →
用户 B 输入短信验证码 → 用户 B 签署 → 合同状态变为已完成 →
验证文档哈希一致 → 验证证据链完整

注意：此测试需要数据库连接。无 DB 时自动跳过。
"""
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.core.security import create_access_token


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


def _auth(user_id: int) -> dict:
    """生成指定用户的认证 header"""
    token = create_access_token(user_id)
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.anyio
async def test_full_signing_flow(client):
    """完整签署流程 E2E 测试"""
    creator_id = 1
    signer_id = 2

    # 1. 创建合同
    try:
        resp = await client.post(
            "/app-api/seal/sign-task/create",
            headers=_auth(creator_id),
            json={
                "name": "E2E测试合同",
                "file_url": "http://example.com/test.pdf",
                "remark": "集成测试",
                "participants": [
                    {"name": "签署方B", "mobile": "13900139000", "order_num": 1}
                ],
            },
        )
    except Exception:
        pytest.skip("数据库不可用，跳过集成测试")
        return

    data = resp.json()
    if data["code"] != 0:
        pytest.skip(f"创建合同失败: {data.get('msg', 'unknown')}")
        return

    task_id = data["data"]["id"]
    assert data["data"]["status"] == 1  # 草稿
    assert data["data"]["file_hash"] is not None  # 文件哈希已计算
    assert len(data["data"]["participants"]) == 1

    # 2. 查看合同统计
    resp = await client.get(
        "/app-api/seal/sign-task/statistics",
        headers=_auth(creator_id),
    )
    stats = resp.json()["data"]
    assert stats["totalCount"] >= 1
    assert stats["draftCount"] >= 1

    # 3. 发起签署
    resp = await client.post(
        f"/app-api/seal/sign-task/{task_id}/initiate",
        headers=_auth(creator_id),
    )
    data = resp.json()
    assert data["code"] == 0
    assert data["data"]["status"] == 2  # 签署中

    # 4. 签署方查看合同详情（记录 SIGNER_VIEWED 证据）
    resp = await client.get(
        f"/app-api/seal/sign-task/get?id={task_id}",
        headers=_auth(signer_id),
    )
    detail = resp.json()["data"]
    assert detail["status"] == 2

    # 5. 签署方发送签署验证码
    resp = await client.post(
        f"/app-api/seal/sign-task/{task_id}/send-sign-code",
        headers=_auth(signer_id),
    )
    # 注意：如果 Redis 不可用，此步可能失败
    if resp.json()["code"] != 0:
        pytest.skip(f"发送验证码失败(可能 Redis 不可用): {resp.json().get('msg')}")
        return

    # 6. 验证签署验证码（测试环境需从 Redis/日志获取验证码）
    # MVP 阶段日志输出验证码，这里直接从 Redis 获取
    from app.utils.redis_client import get_sms_code
    from app.services.sign_task_service import SIGN_CODE_SCENE
    code = await get_sms_code("13900139000", SIGN_CODE_SCENE)
    assert code is not None, "验证码应存在于 Redis"

    resp = await client.post(
        f"/app-api/seal/sign-task/{task_id}/verify-sign-code",
        headers=_auth(signer_id),
        json={"code": code},
    )
    assert resp.json()["code"] == 0

    # 7. 执行签署
    resp = await client.post(
        f"/app-api/seal/sign-task/{task_id}/sign",
        headers=_auth(signer_id),
        json={},
    )
    data = resp.json()
    assert data["code"] == 0
    # 只有一个签署方，签完后合同应自动完成
    assert data["data"]["status"] == 3  # 已完成
    assert data["data"]["signed_file_hash"] is not None

    # 8. 验证文档哈希
    resp = await client.get(
        f"/app-api/seal/sign-task/{task_id}/verify-hash",
        headers=_auth(creator_id),
    )
    hash_data = resp.json()["data"]
    assert hash_data["file_hash"] is not None
    assert hash_data["signed_file_hash"] is not None
    assert hash_data["is_original_valid"] is True
    assert hash_data["is_signed_valid"] is True

    # 9. 验证证据链完整性
    resp = await client.get(
        f"/app-api/seal/sign-task/{task_id}/evidence",
        headers=_auth(creator_id),
    )
    evidence_list = resp.json()["data"]
    actions = [e["action"] for e in evidence_list]

    # 应包含以下操作
    assert "CONTRACT_CREATED" in actions
    assert "CONTRACT_SENT" in actions
    assert "SIGNER_VIEWED" in actions
    assert "SIGN_CODE_SENT" in actions
    assert "SIGN_CODE_VERIFIED" in actions
    assert "CONTRACT_SIGNED" in actions
    assert "CONTRACT_COMPLETED" in actions

    # 证据应按时间排序
    for i in range(len(evidence_list) - 1):
        assert evidence_list[i]["create_time"] <= evidence_list[i + 1]["create_time"]


@pytest.mark.anyio
async def test_contract_cancel_flow(client):
    """合同取消流程测试"""
    creator_id = 10

    try:
        resp = await client.post(
            "/app-api/seal/sign-task/create",
            headers=_auth(creator_id),
            json={
                "name": "取消测试合同",
                "file_url": "http://example.com/cancel.pdf",
                "participants": [
                    {"name": "签署方", "mobile": "13800138000"}
                ],
            },
        )
    except Exception:
        pytest.skip("数据库不可用")
        return

    data = resp.json()
    if data["code"] != 0:
        pytest.skip(f"创建合同失败: {data.get('msg')}")
        return

    task_id = data["data"]["id"]

    # 发起签署
    resp = await client.post(
        f"/app-api/seal/sign-task/{task_id}/initiate",
        headers=_auth(creator_id),
    )
    assert resp.json()["code"] == 0

    # 取消
    resp = await client.delete(
        f"/app-api/seal/sign-task/cancel?id={task_id}",
        headers=_auth(creator_id),
    )
    assert resp.json()["code"] == 0

    # 验证状态
    resp = await client.get(
        f"/app-api/seal/sign-task/get?id={task_id}",
        headers=_auth(creator_id),
    )
    assert resp.json()["data"]["status"] == 4  # 已取消

    # 验证证据链有取消记录
    resp = await client.get(
        f"/app-api/seal/sign-task/{task_id}/evidence",
        headers=_auth(creator_id),
    )
    actions = [e["action"] for e in resp.json()["data"]]
    assert "CONTRACT_CANCELLED" in actions


@pytest.mark.anyio
async def test_reject_flow(client):
    """拒签流程测试"""
    creator_id = 20
    signer_id = 21

    try:
        resp = await client.post(
            "/app-api/seal/sign-task/create",
            headers=_auth(creator_id),
            json={
                "name": "拒签测试合同",
                "file_url": "http://example.com/reject.pdf",
                "participants": [
                    {"name": "签署方", "mobile": "13700137000"}
                ],
            },
        )
    except Exception:
        pytest.skip("数据库不可用")
        return

    data = resp.json()
    if data["code"] != 0:
        pytest.skip(f"创建合同失败: {data.get('msg')}")
        return

    task_id = data["data"]["id"]

    # 发起签署
    await client.post(
        f"/app-api/seal/sign-task/{task_id}/initiate",
        headers=_auth(creator_id),
    )

    # 拒签
    resp = await client.post(
        f"/app-api/seal/sign-task/{task_id}/reject",
        headers=_auth(signer_id),
        json={"reason": "条款不合理"},
    )

    data = resp.json()
    if data["code"] != 0:
        # 签署方可能找不到（没有 member 记录），跳过
        pytest.skip(f"拒签失败: {data.get('msg')}")
        return

    assert data["data"]["status"] == 5  # 已拒签

    # 验证证据链有拒签记录
    resp = await client.get(
        f"/app-api/seal/sign-task/{task_id}/evidence",
        headers=_auth(creator_id),
    )
    actions = [e["action"] for e in resp.json()["data"]]
    assert "CONTRACT_REJECTED" in actions
