"""证据链服务单元测试"""
import hashlib

import pytest

from app.services.evidence_service import EvidenceAction, compute_file_hash


def test_evidence_action_constants():
    """验证所有证据操作类型常量存在"""
    actions = [
        EvidenceAction.CONTRACT_CREATED,
        EvidenceAction.CONTRACT_SENT,
        EvidenceAction.SIGNER_VIEWED,
        EvidenceAction.CONTRACT_SIGNED,
        EvidenceAction.CONTRACT_COMPLETED,
        EvidenceAction.CONTRACT_CANCELLED,
        EvidenceAction.CONTRACT_REJECTED,
    ]
    assert len(actions) == 7
    # 每个 action 应该是字符串
    for action in actions:
        assert isinstance(action, str)
        assert len(action) > 0
    # 不应包含 SMS 相关操作
    assert not hasattr(EvidenceAction, "SIGN_CODE_SENT")
    assert not hasattr(EvidenceAction, "SIGN_CODE_VERIFIED")


def test_evidence_action_unique():
    """所有证据操作类型应唯一"""
    actions = [
        EvidenceAction.CONTRACT_CREATED,
        EvidenceAction.CONTRACT_SENT,
        EvidenceAction.SIGNER_VIEWED,
        EvidenceAction.CONTRACT_SIGNED,
        EvidenceAction.CONTRACT_COMPLETED,
        EvidenceAction.CONTRACT_CANCELLED,
        EvidenceAction.CONTRACT_REJECTED,
    ]
    assert len(set(actions)) == 7


def test_compute_file_hash():
    """SHA-256 哈希计算应正确"""
    content = b"hello world"
    expected = hashlib.sha256(content).hexdigest()
    assert compute_file_hash(content) == expected
    assert len(compute_file_hash(content)) == 64


def test_compute_file_hash_deterministic():
    """同一内容的哈希应一致"""
    content = b"test file content"
    h1 = compute_file_hash(content)
    h2 = compute_file_hash(content)
    assert h1 == h2


def test_compute_file_hash_different_content():
    """不同内容的哈希应不同"""
    h1 = compute_file_hash(b"content A")
    h2 = compute_file_hash(b"content B")
    assert h1 != h2


def test_compute_file_hash_empty():
    """空内容也应能计算哈希"""
    h = compute_file_hash(b"")
    assert len(h) == 64
    assert h == hashlib.sha256(b"").hexdigest()
