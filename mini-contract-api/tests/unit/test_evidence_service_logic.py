"""证据链服务业务逻辑单元测试（使用 mock DB）"""
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from app.services.evidence_service import (
    EvidenceAction,
    log_evidence,
    get_evidence_list,
    compute_file_hash,
)


def _make_evidence_log(id=1, task_id=100, action="CONTRACT_CREATED", user_id=1,
                       ip="127.0.0.1", device="test", data_hash=None, detail=None):
    log = MagicMock()
    log.id = id
    log.task_id = task_id
    log.action = action
    log.user_id = user_id
    log.ip = ip
    log.device = device
    log.data_hash = data_hash
    log.detail = detail
    log.create_time = datetime.now()
    return log


# ---- log_evidence ----

@pytest.mark.anyio
async def test_log_evidence_creates_record():
    """记录证据日志"""
    db = AsyncMock()

    await log_evidence(
        db,
        task_id=100,
        action=EvidenceAction.CONTRACT_CREATED,
        user_id=1,
        ip="192.168.1.1",
        device="WeChat MiniProgram",
        data_hash="abc123",
        detail={"name": "test"},
    )
    db.add.assert_called_once()
    db.flush.assert_called_once()
    db.refresh.assert_called_once()


@pytest.mark.anyio
async def test_log_evidence_optional_fields():
    """可选字段可以省略"""
    db = AsyncMock()

    await log_evidence(
        db,
        task_id=100,
        action=EvidenceAction.SIGNER_VIEWED,
    )
    db.add.assert_called_once()
    # 检查创建的记录
    created_log = db.add.call_args[0][0]
    assert created_log.task_id == 100
    assert created_log.action == "SIGNER_VIEWED"
    assert created_log.user_id is None
    assert created_log.ip is None


@pytest.mark.anyio
async def test_log_evidence_all_action_types():
    """所有操作类型都能记录"""
    actions = [
        EvidenceAction.CONTRACT_CREATED,
        EvidenceAction.CONTRACT_SENT,
        EvidenceAction.SIGNER_VIEWED,
        EvidenceAction.SIGN_CODE_SENT,
        EvidenceAction.SIGN_CODE_VERIFIED,
        EvidenceAction.CONTRACT_SIGNED,
        EvidenceAction.CONTRACT_COMPLETED,
        EvidenceAction.CONTRACT_CANCELLED,
        EvidenceAction.CONTRACT_REJECTED,
    ]

    for action in actions:
        db = AsyncMock()
        await log_evidence(db, task_id=1, action=action)
        db.add.assert_called_once()


# ---- get_evidence_list ----

@pytest.mark.anyio
async def test_get_evidence_list_success():
    """获取证据链列表"""
    log1 = _make_evidence_log(id=1, action="CONTRACT_CREATED")
    log2 = _make_evidence_log(id=2, action="CONTRACT_SENT")

    db = AsyncMock()
    result = MagicMock()
    scalars = MagicMock()
    scalars.all.return_value = [log1, log2]
    result.scalars.return_value = scalars
    db.execute.return_value = result

    evidence_list = await get_evidence_list(db, task_id=100)
    assert len(evidence_list) == 2
    assert evidence_list[0]["action"] == "CONTRACT_CREATED"
    assert evidence_list[1]["action"] == "CONTRACT_SENT"


@pytest.mark.anyio
async def test_get_evidence_list_empty():
    """空证据链"""
    db = AsyncMock()
    result = MagicMock()
    scalars = MagicMock()
    scalars.all.return_value = []
    result.scalars.return_value = scalars
    db.execute.return_value = result

    evidence_list = await get_evidence_list(db, task_id=999)
    assert evidence_list == []


@pytest.mark.anyio
async def test_get_evidence_list_has_all_fields():
    """证据记录包含所有字段"""
    log = _make_evidence_log(
        ip="10.0.0.1",
        device="iPhone",
        data_hash="hash123",
        detail={"key": "value"},
    )

    db = AsyncMock()
    result = MagicMock()
    scalars = MagicMock()
    scalars.all.return_value = [log]
    result.scalars.return_value = scalars
    db.execute.return_value = result

    evidence_list = await get_evidence_list(db, task_id=100)
    entry = evidence_list[0]
    assert "id" in entry
    assert "task_id" in entry
    assert "action" in entry
    assert "user_id" in entry
    assert "ip" in entry
    assert "device" in entry
    assert "data_hash" in entry
    assert "detail" in entry
    assert "create_time" in entry


# ---- compute_file_hash ----

def test_compute_file_hash_deterministic():
    """相同内容哈希一致"""
    content = b"hello world"
    h1 = compute_file_hash(content)
    h2 = compute_file_hash(content)
    assert h1 == h2


def test_compute_file_hash_different_content():
    """不同内容哈希不同"""
    h1 = compute_file_hash(b"content A")
    h2 = compute_file_hash(b"content B")
    assert h1 != h2


def test_compute_file_hash_format():
    """哈希格式为 64 位十六进制"""
    h = compute_file_hash(b"test")
    assert len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)
