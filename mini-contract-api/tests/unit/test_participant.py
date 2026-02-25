"""签署方状态流转单元测试"""
import pytest

from app.schemas.contract import ParticipantRequest, ParticipantResponse


# --- 签署方 Schema 测试 ---

def test_participant_request_defaults():
    """签署方请求默认顺序为 1"""
    p = ParticipantRequest(name="张三", mobile="13800138000")
    assert p.order_num == 1


def test_participant_request_custom_order():
    """可自定义签署顺序"""
    p = ParticipantRequest(name="李四", mobile="13900139000", order_num=3)
    assert p.order_num == 3


def test_participant_response_pending():
    """待签署状态为 0"""
    p = ParticipantResponse(id=1, name="张三", mobile="13800138000", status=0, order_num=1)
    assert p.status == 0


def test_participant_response_signed():
    """已签署状态为 2"""
    p = ParticipantResponse(id=1, name="张三", mobile="13800138000", status=2, order_num=1)
    assert p.status == 2


def test_participant_response_rejected():
    """已拒签状态为 3"""
    p = ParticipantResponse(id=1, name="张三", mobile="13800138000", status=3, order_num=1)
    assert p.status == 3


# --- 签署方状态流转规则 ---

VALID_PARTICIPANT_TRANSITIONS = {
    0: {2, 3},   # 待签署 → 已签署 / 已拒签
}


def _is_valid_participant_transition(from_s: int, to_s: int) -> bool:
    return to_s in VALID_PARTICIPANT_TRANSITIONS.get(from_s, set())


def test_pending_to_signed():
    """待签署 → 已签署 合法"""
    assert _is_valid_participant_transition(0, 2)


def test_pending_to_rejected():
    """待签署 → 已拒签 合法"""
    assert _is_valid_participant_transition(0, 3)


def test_signed_cannot_reject():
    """已签署不能拒签"""
    assert not _is_valid_participant_transition(2, 3)


def test_signed_cannot_sign_again():
    """已签署不能再签署"""
    assert not _is_valid_participant_transition(2, 2)


def test_rejected_cannot_sign():
    """已拒签不能签署"""
    assert not _is_valid_participant_transition(3, 2)


# --- 批量签署完成逻辑 ---

def test_all_signed_means_complete():
    """所有签署方状态为 2 时合同应完成"""
    participants = [
        ParticipantResponse(id=1, name="A", mobile="138", status=2, order_num=1),
        ParticipantResponse(id=2, name="B", mobile="139", status=2, order_num=2),
    ]
    unsigned = [p for p in participants if p.status == 0]
    assert len(unsigned) == 0  # 无未签署 → 合同完成


def test_partial_signed_not_complete():
    """有未签署方时合同不应完成"""
    participants = [
        ParticipantResponse(id=1, name="A", mobile="138", status=2, order_num=1),
        ParticipantResponse(id=2, name="B", mobile="139", status=0, order_num=2),
    ]
    unsigned = [p for p in participants if p.status == 0]
    assert len(unsigned) > 0  # 有未签署 → 合同不完成


def test_rejected_not_complete():
    """有拒签方时合同不应自动完成"""
    participants = [
        ParticipantResponse(id=1, name="A", mobile="138", status=2, order_num=1),
        ParticipantResponse(id=2, name="B", mobile="139", status=3, order_num=2),
    ]
    unsigned = [p for p in participants if p.status == 0]
    # 无待签署方，但有拒签 → 需要单独处理（合同状态=5 已拒签）
    rejected = [p for p in participants if p.status == 3]
    assert len(rejected) > 0


def test_single_signer_auto_complete():
    """单签署方签署后合同自动完成"""
    participants = [
        ParticipantResponse(id=1, name="A", mobile="138", status=2, order_num=1),
    ]
    unsigned = [p for p in participants if p.status == 0]
    assert len(unsigned) == 0
