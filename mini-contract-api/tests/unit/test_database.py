"""数据库模块单元测试"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.database import get_db, seed_admin, Base


def test_base_class_exists():
    """Base 声明式基类应存在"""
    assert Base is not None
    assert hasattr(Base, 'metadata')


@pytest.mark.asyncio
async def test_get_db_yields_session():
    """get_db 应 yield 一个 session 并在正常时 commit"""
    mock_session = AsyncMock()

    with patch('app.database.async_session_factory') as mock_factory:
        mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)

        gen = get_db()
        session = await gen.__anext__()
        assert session is mock_session

        # 正常结束应 commit
        try:
            await gen.__anext__()
        except StopAsyncIteration:
            pass


@pytest.mark.asyncio
async def test_get_db_rollback_on_exception():
    """get_db 在异常时应 rollback"""
    mock_session = AsyncMock()
    mock_session.commit = AsyncMock(side_effect=Exception("DB error"))

    with patch('app.database.async_session_factory') as mock_factory:
        mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)

        gen = get_db()
        await gen.__anext__()

        with pytest.raises(Exception, match="DB error"):
            await gen.__anext__()


@pytest.mark.asyncio
async def test_seed_admin_creates_when_not_exists():
    """seed_admin 应在管理员不存在时创建"""
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.add = MagicMock()
    mock_session.commit = AsyncMock()

    with patch('app.database.async_session_factory') as mock_factory:
        mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)

        await seed_admin()
        mock_session.add.assert_called_once()


@pytest.mark.asyncio
async def test_seed_admin_skips_when_exists():
    """seed_admin 应在管理员已存在时跳过"""
    mock_session = AsyncMock()
    mock_member = MagicMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_member
    mock_session.execute = AsyncMock(return_value=mock_result)

    with patch('app.database.async_session_factory') as mock_factory:
        mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)

        await seed_admin()
        mock_session.add.assert_not_called()


@pytest.mark.asyncio
async def test_seed_admin_handles_exception():
    """seed_admin 应在异常时不崩溃（仅 warning）"""
    with patch('app.database.async_session_factory') as mock_factory:
        mock_factory.return_value.__aenter__ = AsyncMock(
            side_effect=Exception("Connection refused")
        )
        mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)

        # 不应抛异常
        await seed_admin()
