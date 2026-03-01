"""合同状态机单元测试"""
import pytest

from app.schemas.contract import (
    ParticipantRequest,
    ParticipantResponse,
    SignRequest,
    RejectRequest,
    SignTaskCreateRequest,
    SignTaskResponse,
    SignTaskStatistics,
    EvidenceLogResponse,
)


# --- Schema 验证 ---

def test_sign_task_create_request_minimal():
    """创建合同只需名称和模板/文件"""
    req = SignTaskCreateRequest(name="测试合同", template_id=1)
    assert req.name == "测试合同"
    assert req.template_id == 1
    assert req.file_url is None
    assert req.participants == []


def test_sign_task_create_request_with_participants():
    """创建合同可包含签署方"""
    req = SignTaskCreateRequest(
        name="测试合同",
        file_url="http://file.pdf",
        participants=[
            ParticipantRequest(name="张三", mobile="13800138000"),
            ParticipantRequest(name="李四", mobile="13900139000", order_num=2),
        ],
    )
    assert len(req.participants) == 2
    assert req.participants[0].order_num == 1  # 默认值
    assert req.participants[1].order_num == 2


def test_sign_task_response_all_fields():
    """SignTaskResponse 应包含所有字段"""
    resp = SignTaskResponse(
        id=1,
        name="合同",
        status=2,
        file_hash="abc123",
        signed_file_hash="def456",
        creator_id=100,
        create_time="2024-01-01T00:00:00",
        complete_time="2024-01-02T00:00:00",
        participants=[],
    )
    assert resp.file_hash == "abc123"
    assert resp.signed_file_hash == "def456"
    assert resp.complete_time == "2024-01-02T00:00:00"


def test_sign_request_default():
    """签署请求默认无印章"""
    req = SignRequest()
    assert req.seal_id is None


def test_sign_request_with_seal():
    """签署请求可指定印章"""
    req = SignRequest(seal_id=42)
    assert req.seal_id == 42


def test_reject_request():
    """拒签请求可包含原因"""
    req = RejectRequest(reason="条款不合理")
    assert req.reason == "条款不合理"


def test_reject_request_no_reason():
    """拒签请求原因可选"""
    req = RejectRequest()
    assert req.reason is None


def test_statistics():
    """统计响应应包含四个计数"""
    stats = SignTaskStatistics(
        totalCount=10,
        draftCount=3,
        signingCount=4,
        completedCount=3,
    )
    assert stats.totalCount == 10
    assert stats.draftCount + stats.signingCount + stats.completedCount <= stats.totalCount


def test_evidence_log_response():
    """证据链响应应包含所有字段"""
    log = EvidenceLogResponse(
        id=1,
        task_id=100,
        action="CONTRACT_CREATED",
        user_id=42,
        ip="192.168.1.1",
        device="WeChat/8.0",
        data_hash="abc",
        detail={"name": "test"},
        create_time="2024-01-01T00:00:00",
    )
    assert log.action == "CONTRACT_CREATED"
    assert log.ip == "192.168.1.1"


def test_participant_response():
    """签署方响应应包含状态"""
    p = ParticipantResponse(
        id=1,
        name="张三",
        mobile="13800138000",
        status=0,
        order_num=1,
    )
    assert p.status == 0  # 待签署


# --- 状态机规则验证 ---

def test_valid_status_transitions():
    """合法状态转换"""
    # 草稿→签署中
    assert _is_valid_transition(1, 2)
    # 签署中→已完成
    assert _is_valid_transition(2, 3)
    # 草稿→已取消
    assert _is_valid_transition(1, 4)
    # 签署中→已取消
    assert _is_valid_transition(2, 4)
    # 签署中→已拒签
    assert _is_valid_transition(2, 5)


def test_invalid_status_transitions():
    """非法状态转换"""
    # 已完成不能取消
    assert not _is_valid_transition(3, 4)
    # 已取消不能签署
    assert not _is_valid_transition(4, 2)
    # 已完成不能拒签
    assert not _is_valid_transition(3, 5)
    # 已拒签不能签署
    assert not _is_valid_transition(5, 2)
    # 草稿不能直接完成
    assert not _is_valid_transition(1, 3)


def test_cancel_only_from_draft_or_signing():
    """取消只能从草稿或签署中状态"""
    assert _can_cancel(1)
    assert _can_cancel(2)
    assert not _can_cancel(3)
    assert not _can_cancel(4)
    assert not _can_cancel(5)
    assert not _can_cancel(6)


def test_delete_only_from_draft_or_cancelled():
    """删除只能从草稿或已取消状态"""
    assert _can_delete(1)
    assert not _can_delete(2)
    assert not _can_delete(3)
    assert _can_delete(4)
    assert not _can_delete(5)
    assert not _can_delete(6)


def test_initiate_only_from_draft():
    """发起签署只能从草稿状态"""
    assert _can_initiate(1)
    assert not _can_initiate(2)
    assert not _can_initiate(3)


# --- 辅助函数 ---

# 合法状态转换表
_VALID_TRANSITIONS = {
    1: {2, 4},       # 草稿 → 签署中 / 已取消
    2: {3, 4, 5},    # 签署中 → 已完成 / 已取消 / 已拒签
}


def _is_valid_transition(from_status: int, to_status: int) -> bool:
    """检查状态转换是否合法"""
    allowed = _VALID_TRANSITIONS.get(from_status, set())
    return to_status in allowed


def _can_cancel(status: int) -> bool:
    return status in (1, 2)


def _can_delete(status: int) -> bool:
    return status in (1, 4)


def _can_initiate(status: int) -> bool:
    return status == 1
