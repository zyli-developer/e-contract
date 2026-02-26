"""印章服务业务逻辑单元测试（使用 mock DB）"""
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from app.core.exceptions import BusinessException, ValidationException
from app.services.seal_service import (
    VALID_SEAL_TYPES,
    create_seal,
    update_seal,
    delete_seal,
    set_default_seal,
    list_seals,
)


def _make_seal(id=1, name="my_seal", type=11, seal_data="https://img.jpg",
               member_id=1, status=1, is_default=0, create_time=None):
    seal = MagicMock()
    seal.id = id
    seal.name = name
    seal.type = type
    seal.seal_data = seal_data
    seal.member_id = member_id
    seal.status = status
    seal.is_default = is_default
    seal.create_time = create_time or datetime.now()
    return seal


def _make_db(scalar_return=None):
    db = AsyncMock()
    db.add = MagicMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = scalar_return
    db.execute.return_value = result
    return db


# ---- constants ----

def test_valid_seal_types():
    assert VALID_SEAL_TYPES == {11, 12}


# ---- create_seal ----

@pytest.mark.anyio
async def test_create_seal_signature():
    """创建个人签名印章"""
    db = AsyncMock()
    db.add = MagicMock()
    # mock refresh to set id on the SealInfo object
    async def _mock_refresh(obj):
        obj.id = 100
        obj.create_time = datetime.now()
    db.refresh = _mock_refresh

    result = await create_seal(db, member_id=1, name="seal", seal_type=11, seal_data="https://img.jpg")
    db.add.assert_called_once()
    assert result["id"] == 100
    assert result["type"] == 11


@pytest.mark.anyio
async def test_create_seal_stamp():
    """创建个人印章"""
    db = AsyncMock()
    db.add = MagicMock()
    async def _mock_refresh(obj):
        obj.id = 200
        obj.create_time = datetime.now()
    db.refresh = _mock_refresh

    result = await create_seal(db, member_id=1, name="stamp", seal_type=12, seal_data="https://stamp.jpg")
    assert result["type"] == 12


@pytest.mark.anyio
async def test_create_seal_invalid_type():
    db = AsyncMock()
    with pytest.raises(ValidationException) as exc_info:
        await create_seal(db, member_id=1, name="test", seal_type=99, seal_data="https://img.jpg")
    assert "无效" in exc_info.value.msg


# ---- update_seal ----

@pytest.mark.anyio
async def test_update_seal_name():
    seal = _make_seal()
    db = _make_db(scalar_return=seal)
    await update_seal(db, member_id=1, seal_id=1, name="new_name", seal_data=None)
    assert seal.name == "new_name"


@pytest.mark.anyio
async def test_update_seal_data():
    seal = _make_seal()
    db = _make_db(scalar_return=seal)
    await update_seal(db, member_id=1, seal_id=1, name=None, seal_data="https://new.jpg")
    assert seal.seal_data == "https://new.jpg"


@pytest.mark.anyio
async def test_update_seal_not_found():
    db = _make_db(scalar_return=None)
    with pytest.raises(BusinessException) as exc_info:
        await update_seal(db, member_id=1, seal_id=999, name="x", seal_data=None)
    assert exc_info.value.code == 404


# ---- delete_seal ----

@pytest.mark.anyio
async def test_delete_seal_success():
    seal = _make_seal()
    db = _make_db(scalar_return=seal)
    await delete_seal(db, member_id=1, seal_id=1)
    assert seal.status == 2
    db.flush.assert_called_once()


@pytest.mark.anyio
async def test_delete_seal_not_found():
    db = _make_db(scalar_return=None)
    with pytest.raises(BusinessException) as exc_info:
        await delete_seal(db, member_id=1, seal_id=999)
    assert exc_info.value.code == 404


# ---- set_default_seal ----

@pytest.mark.anyio
async def test_set_default_seal_success():
    seal = _make_seal(type=11)
    db = _make_db(scalar_return=seal)
    await set_default_seal(db, member_id=1, seal_id=1)
    assert seal.is_default == 1


@pytest.mark.anyio
async def test_set_default_seal_not_found():
    db = _make_db(scalar_return=None)
    with pytest.raises(BusinessException) as exc_info:
        await set_default_seal(db, member_id=1, seal_id=999)
    assert exc_info.value.code == 404


# ---- list_seals ----

@pytest.mark.anyio
async def test_list_seals_calls_paginate():
    from app.core.response import PageResult
    db = AsyncMock()

    with patch("app.services.seal_service.paginate", new_callable=AsyncMock) as mock_paginate:
        mock_paginate.return_value = PageResult(list=[], total=0, pageNo=1, pageSize=10)
        result = await list_seals(db, member_id=1)
        mock_paginate.assert_called_once()
        assert result.total == 0


@pytest.mark.anyio
async def test_list_seals_with_items():
    from app.core.response import PageResult
    seal = _make_seal()
    db = AsyncMock()

    with patch("app.services.seal_service.paginate", new_callable=AsyncMock) as mock_paginate:
        mock_paginate.return_value = PageResult(list=[seal], total=1, pageNo=1, pageSize=10)
        result = await list_seals(db, member_id=1)
        assert result.total == 1
        assert len(result.list) == 1
        assert result.list[0]["name"] == "my_seal"
