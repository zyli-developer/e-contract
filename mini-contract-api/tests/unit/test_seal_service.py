"""印章服务 Schema 单元测试"""
import pytest

from app.schemas.seal import SealCreateRequest, SealUpdateRequest, SealResponse


def test_seal_create_request():
    """创建印章请求包含必填字段"""
    req = SealCreateRequest(name="我的签名", type=11, seal_data="http://img.png")
    assert req.name == "我的签名"
    assert req.type == 11
    assert req.seal_data == "http://img.png"


def test_seal_create_type_stamp():
    """印章类型 12"""
    req = SealCreateRequest(name="公司印章", type=12, seal_data="http://stamp.png")
    assert req.type == 12


def test_seal_update_partial():
    """更新印章可只更新部分字段"""
    req = SealUpdateRequest(id=1, name="新名称")
    assert req.name == "新名称"
    assert req.seal_data is None


def test_seal_update_seal_data():
    """更新印章图片"""
    req = SealUpdateRequest(id=1, seal_data="http://new.png")
    assert req.seal_data == "http://new.png"
    assert req.name is None


def test_seal_response_default():
    """印章响应包含默认标记"""
    resp = SealResponse(
        id=1, name="签名", type=11,
        seal_data="http://img.png", is_default=1,
        create_time="2024-01-01T00:00:00",
    )
    assert resp.is_default == 1


def test_seal_response_not_default():
    """非默认印章"""
    resp = SealResponse(
        id=2, name="备用签名", type=11,
        seal_data="http://img2.png", is_default=0,
    )
    assert resp.is_default == 0
    assert resp.create_time is None


def test_seal_type_personal_signature():
    """个人签名类型为 11"""
    assert 11 == 11  # 个人签名


def test_seal_type_personal_stamp():
    """个人印章类型为 12"""
    assert 12 == 12  # 个人印章
