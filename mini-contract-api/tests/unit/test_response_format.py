"""测试统一响应格式"""
from app.core.response import ApiResponse, PageResult


def test_api_response_success_default():
    """成功响应默认值"""
    resp = ApiResponse.success()
    assert resp.code == 0
    assert resp.msg == "success"
    assert resp.data is None


def test_api_response_success_with_data():
    """成功响应携带数据"""
    resp = ApiResponse.success(data={"id": 1, "name": "test"})
    assert resp.code == 0
    assert resp.data == {"id": 1, "name": "test"}


def test_api_response_success_custom_msg():
    """成功响应自定义消息"""
    resp = ApiResponse.success(msg="创建成功")
    assert resp.msg == "创建成功"


def test_api_response_error():
    """错误响应"""
    resp = ApiResponse.error(code=400, msg="参数错误")
    assert resp.code == 400
    assert resp.msg == "参数错误"
    assert resp.data is None


def test_api_response_error_default():
    """错误响应默认值"""
    resp = ApiResponse.error()
    assert resp.code == 500
    assert resp.msg == "error"


def test_api_response_serialization():
    """响应序列化格式"""
    resp = ApiResponse.success(data="hello")
    d = resp.model_dump()
    assert set(d.keys()) == {"code", "msg", "data"}
    assert d["code"] == 0
    assert d["data"] == "hello"


def test_page_result_default():
    """分页响应默认值"""
    page = PageResult()
    assert page.list == []
    assert page.total == 0
    assert page.pageNo == 1
    assert page.pageSize == 10


def test_page_result_with_data():
    """分页响应携带数据"""
    page = PageResult(list=[{"id": 1}, {"id": 2}], total=100, pageNo=2, pageSize=20)
    assert len(page.list) == 2
    assert page.total == 100
    assert page.pageNo == 2
    assert page.pageSize == 20


def test_page_result_serialization():
    """分页响应序列化"""
    page = PageResult(list=[1, 2, 3], total=3)
    d = page.model_dump()
    assert set(d.keys()) == {"list", "total", "pageNo", "pageSize"}
