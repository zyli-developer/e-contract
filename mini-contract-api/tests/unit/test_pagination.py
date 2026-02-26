"""分页工具单元测试"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.utils.pagination import paginate
from app.core.response import PageResult


@pytest.mark.asyncio
async def test_paginate_basic():
    """基本分页应返回正确结构"""
    mock_db = AsyncMock()

    # mock count 查询
    mock_count_result = MagicMock()
    mock_count_result.scalar.return_value = 25

    # mock 数据查询
    mock_data_result = MagicMock()
    mock_data_result.scalars.return_value.all.return_value = [
        {"id": 1}, {"id": 2}, {"id": 3}
    ]

    mock_db.execute = AsyncMock(side_effect=[mock_count_result, mock_data_result])

    mock_query = MagicMock()
    mock_query.subquery = MagicMock()
    mock_query.offset = MagicMock(return_value=mock_query)
    mock_query.limit = MagicMock(return_value=mock_query)

    with patch('app.utils.pagination.select') as mock_select, \
         patch('app.utils.pagination.func') as mock_func:
        mock_select.return_value.select_from.return_value = MagicMock()

        result = await paginate(mock_db, mock_query, page_no=1, page_size=10)

    assert isinstance(result, PageResult)
    assert result.total == 25
    assert result.pageNo == 1
    assert result.pageSize == 10
    assert len(result.list) == 3


@pytest.mark.asyncio
async def test_paginate_offset_calculation():
    """分页偏移量应正确计算"""
    mock_db = AsyncMock()
    mock_count_result = MagicMock()
    mock_count_result.scalar.return_value = 100

    mock_data_result = MagicMock()
    mock_data_result.scalars.return_value.all.return_value = []

    mock_db.execute = AsyncMock(side_effect=[mock_count_result, mock_data_result])

    mock_query = MagicMock()
    mock_query.subquery = MagicMock()
    mock_query.offset = MagicMock(return_value=mock_query)
    mock_query.limit = MagicMock(return_value=mock_query)

    with patch('app.utils.pagination.select') as mock_select, \
         patch('app.utils.pagination.func') as mock_func:
        mock_select.return_value.select_from.return_value = MagicMock()

        await paginate(mock_db, mock_query, page_no=3, page_size=20)

    # page_no=3, page_size=20 → offset = (3-1)*20 = 40
    mock_query.offset.assert_called_with(40)
    mock_query.limit.assert_called_with(20)


@pytest.mark.asyncio
async def test_paginate_empty_result():
    """空结果应返回正确的 PageResult"""
    mock_db = AsyncMock()
    mock_count_result = MagicMock()
    mock_count_result.scalar.return_value = 0

    mock_data_result = MagicMock()
    mock_data_result.scalars.return_value.all.return_value = []

    mock_db.execute = AsyncMock(side_effect=[mock_count_result, mock_data_result])

    mock_query = MagicMock()
    mock_query.subquery = MagicMock()
    mock_query.offset = MagicMock(return_value=mock_query)
    mock_query.limit = MagicMock(return_value=mock_query)

    with patch('app.utils.pagination.select') as mock_select, \
         patch('app.utils.pagination.func') as mock_func:
        mock_select.return_value.select_from.return_value = MagicMock()

        result = await paginate(mock_db, mock_query)

    assert result.total == 0
    assert result.list == []
    assert result.pageNo == 1
    assert result.pageSize == 10


@pytest.mark.asyncio
async def test_paginate_null_count():
    """count 返回 None 应被处理为 0"""
    mock_db = AsyncMock()
    mock_count_result = MagicMock()
    mock_count_result.scalar.return_value = None

    mock_data_result = MagicMock()
    mock_data_result.scalars.return_value.all.return_value = []

    mock_db.execute = AsyncMock(side_effect=[mock_count_result, mock_data_result])

    mock_query = MagicMock()
    mock_query.subquery = MagicMock()
    mock_query.offset = MagicMock(return_value=mock_query)
    mock_query.limit = MagicMock(return_value=mock_query)

    with patch('app.utils.pagination.select') as mock_select, \
         patch('app.utils.pagination.func') as mock_func:
        mock_select.return_value.select_from.return_value = MagicMock()

        result = await paginate(mock_db, mock_query)

    assert result.total == 0


@pytest.mark.asyncio
async def test_paginate_default_params():
    """默认分页参数应为 page_no=1, page_size=10"""
    mock_db = AsyncMock()
    mock_count_result = MagicMock()
    mock_count_result.scalar.return_value = 5

    mock_data_result = MagicMock()
    mock_data_result.scalars.return_value.all.return_value = [1, 2, 3, 4, 5]

    mock_db.execute = AsyncMock(side_effect=[mock_count_result, mock_data_result])

    mock_query = MagicMock()
    mock_query.subquery = MagicMock()
    mock_query.offset = MagicMock(return_value=mock_query)
    mock_query.limit = MagicMock(return_value=mock_query)

    with patch('app.utils.pagination.select') as mock_select, \
         patch('app.utils.pagination.func') as mock_func:
        mock_select.return_value.select_from.return_value = MagicMock()

        result = await paginate(mock_db, mock_query)

    mock_query.offset.assert_called_with(0)
    mock_query.limit.assert_called_with(10)
    assert result.pageNo == 1
    assert result.pageSize == 10
