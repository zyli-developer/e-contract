"""模板服务业务逻辑单元测试（使用 mock DB）"""
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from app.core.exceptions import BusinessException
from app.services.template_service import (
    CATEGORIES,
    search_templates,
    get_template_detail,
    get_hot_templates,
    get_frequently_used,
    increment_use_count,
)


def _make_template(id=1, name="loan_template", description="standard", category="loan",
                   image_url=None, content="<p>content</p>", use_count=10,
                   status=1, variables=None, signatories=None, create_time=None):
    t = MagicMock()
    t.id = id
    t.name = name
    t.description = description
    t.category = category
    t.image_url = image_url
    t.content = content
    t.use_count = use_count
    t.status = status
    t.variables = variables or []
    t.signatories = signatories or []
    t.create_time = create_time or datetime.now()
    return t


def _make_db(scalar_return=None, scalars_return=None):
    db = AsyncMock()
    db.add = MagicMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = scalar_return
    if scalars_return is not None:
        scalars = MagicMock()
        scalars.all.return_value = scalars_return
        result.scalars.return_value = scalars
    db.execute.return_value = result
    return db


# ---- CATEGORIES ----

def test_categories_count():
    assert len(CATEGORIES) == 6


def test_categories_codes():
    codes = [c["code"] for c in CATEGORIES]
    assert set(codes) == {"loan", "lease", "labor", "purchase", "sales", "other"}


def test_categories_have_names():
    for c in CATEGORIES:
        assert "name" in c and len(c["name"]) > 0


# ---- search_templates ----

@pytest.mark.anyio
async def test_search_templates():
    from app.core.response import PageResult
    db = AsyncMock()
    t = _make_template()

    with patch("app.services.template_service.paginate", new_callable=AsyncMock) as mock_paginate:
        mock_paginate.return_value = PageResult(list=[t], total=1, pageNo=1, pageSize=10)
        result = await search_templates(db)
        mock_paginate.assert_called_once()
        assert result.total == 1


@pytest.mark.anyio
async def test_search_templates_with_keyword():
    from app.core.response import PageResult
    db = AsyncMock()

    with patch("app.services.template_service.paginate", new_callable=AsyncMock) as mock_paginate:
        mock_paginate.return_value = PageResult(list=[], total=0, pageNo=1, pageSize=10)
        result = await search_templates(db, keyword="loan")
        assert result.total == 0


@pytest.mark.anyio
async def test_search_templates_with_category():
    from app.core.response import PageResult
    db = AsyncMock()

    with patch("app.services.template_service.paginate", new_callable=AsyncMock) as mock_paginate:
        mock_paginate.return_value = PageResult(list=[], total=0, pageNo=1, pageSize=10)
        result = await search_templates(db, category="loan")
        assert result.total == 0


# ---- get_template_detail ----

@pytest.mark.anyio
async def test_get_template_detail_success():
    t = _make_template(content="<p>contract</p>", variables=["party_a"], signatories=["signer_a"])
    db = _make_db(scalar_return=t)

    detail = await get_template_detail(db, template_id=1)
    assert detail["name"] == "loan_template"
    assert detail["content"] == "<p>contract</p>"
    assert detail["variables"] is not None
    assert detail["signatories"] is not None


@pytest.mark.anyio
async def test_get_template_detail_not_found():
    db = _make_db(scalar_return=None)
    with pytest.raises(BusinessException) as exc_info:
        await get_template_detail(db, template_id=999)
    assert exc_info.value.code == 404


# ---- get_hot_templates ----

@pytest.mark.anyio
async def test_get_hot_templates():
    t1 = _make_template(id=1, use_count=100)
    t2 = _make_template(id=2, use_count=50)
    db = _make_db(scalars_return=[t1, t2])

    result = await get_hot_templates(db, limit=6)
    assert len(result) == 2
    assert result[0]["use_count"] == 100


@pytest.mark.anyio
async def test_get_hot_templates_empty():
    db = _make_db(scalars_return=[])
    result = await get_hot_templates(db)
    assert len(result) == 0


# ---- get_frequently_used ----

@pytest.mark.anyio
async def test_get_frequently_used_delegates():
    t1 = _make_template()
    db = _make_db(scalars_return=[t1])
    result = await get_frequently_used(db, limit=8)
    assert len(result) == 1


# ---- increment_use_count ----

@pytest.mark.anyio
async def test_increment_use_count():
    db = AsyncMock()
    await increment_use_count(db, template_id=1)
    db.execute.assert_called_once()
