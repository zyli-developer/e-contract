"""合同模板 Schema 单元测试"""
import pytest

from app.schemas.template import (
    TemplateSearchRequest,
    TemplateResponse,
    TemplateDetailResponse,
)


def test_template_search_defaults():
    """搜索请求默认参数"""
    req = TemplateSearchRequest()
    assert req.keyword is None
    assert req.category is None
    assert req.pageNo == 1
    assert req.pageSize == 10


def test_template_search_with_keyword():
    """搜索请求带关键词"""
    req = TemplateSearchRequest(keyword="租赁", category="lease")
    assert req.keyword == "租赁"
    assert req.category == "lease"


def test_template_response():
    """模板响应基本字段"""
    resp = TemplateResponse(
        id=1, name="租赁合同", category="lease",
        description="标准租赁合同模板",
        image_url="http://img.png", use_count=42,
    )
    assert resp.name == "租赁合同"
    assert resp.use_count == 42


def test_template_response_defaults():
    """模板响应默认值"""
    resp = TemplateResponse(id=1, name="测试", category="other")
    assert resp.description is None
    assert resp.image_url is None
    assert resp.use_count == 0


def test_template_detail_response():
    """模板详情应包含内容和变量"""
    resp = TemplateDetailResponse(
        id=1, name="借款合同", category="loan",
        content="<p>甲方：{{partyA}}</p>",
        variables=[{"name": "partyA", "label": "甲方名称", "type": "text"}],
        signatories=[{"role": "甲方"}, {"role": "乙方"}],
    )
    assert resp.content is not None
    assert len(resp.variables) == 1
    assert len(resp.signatories) == 2


def test_template_detail_inherits_base():
    """详情响应继承基础模板字段"""
    resp = TemplateDetailResponse(
        id=1, name="劳动合同", category="labor", use_count=10,
    )
    assert resp.name == "劳动合同"
    assert resp.use_count == 10
    assert resp.content is None
    assert resp.variables is None


def test_categories():
    """验证预定义分类"""
    from app.services.template_service import CATEGORIES
    codes = [c["code"] for c in CATEGORIES]
    assert "loan" in codes
    assert "lease" in codes
    assert "labor" in codes
    assert "purchase" in codes
    assert "sales" in codes
    assert "other" in codes
    assert len(CATEGORIES) == 6
