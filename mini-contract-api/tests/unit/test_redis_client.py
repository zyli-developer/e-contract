"""Redis 客户端工具单元测试"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.utils import redis_client


@pytest.fixture(autouse=True)
def reset_redis_pool():
    """每个测试前重置全局 _pool"""
    redis_client._pool = None
    yield
    redis_client._pool = None


@pytest.mark.asyncio
async def test_get_redis_lazy_init():
    """get_redis 应懒加载初始化 Redis 连接"""
    mock_redis = MagicMock()
    with patch('app.utils.redis_client.redis.from_url', return_value=mock_redis) as mock_from_url:
        r = await redis_client.get_redis()
        assert r is mock_redis
        mock_from_url.assert_called_once()


@pytest.mark.asyncio
async def test_get_redis_singleton():
    """多次调用 get_redis 应返回同一实例"""
    mock_redis = MagicMock()
    with patch('app.utils.redis_client.redis.from_url', return_value=mock_redis) as mock_from_url:
        r1 = await redis_client.get_redis()
        r2 = await redis_client.get_redis()
        assert r1 is r2
        # from_url 应只调用一次
        mock_from_url.assert_called_once()


@pytest.mark.asyncio
async def test_close_redis():
    """close_redis 应关闭连接并重置 _pool"""
    mock_redis = AsyncMock()
    redis_client._pool = mock_redis

    await redis_client.close_redis()
    mock_redis.close.assert_called_once()
    assert redis_client._pool is None


@pytest.mark.asyncio
async def test_close_redis_when_none():
    """close_redis 在 _pool 为 None 时应不做任何操作"""
    redis_client._pool = None
    await redis_client.close_redis()
    assert redis_client._pool is None


@pytest.mark.asyncio
async def test_set_sms_code():
    """set_sms_code 应用正确的 key 和 TTL 存储"""
    mock_redis = AsyncMock()
    with patch.object(redis_client, 'get_redis', return_value=mock_redis):
        await redis_client.set_sms_code("13800138000", 1, "123456", ttl=300)
        mock_redis.set.assert_called_once_with("sms:code:1:13800138000", "123456", ex=300)


@pytest.mark.asyncio
async def test_set_sms_code_default_ttl():
    """set_sms_code 默认 TTL 为 300 秒"""
    mock_redis = AsyncMock()
    with patch.object(redis_client, 'get_redis', return_value=mock_redis):
        await redis_client.set_sms_code("13800138000", 2, "654321")
        mock_redis.set.assert_called_once_with("sms:code:2:13800138000", "654321", ex=300)


@pytest.mark.asyncio
async def test_get_sms_code():
    """get_sms_code 应从正确的 key 获取"""
    mock_redis = AsyncMock()
    mock_redis.get.return_value = "123456"
    with patch.object(redis_client, 'get_redis', return_value=mock_redis):
        code = await redis_client.get_sms_code("13800138000", 1)
        assert code == "123456"
        mock_redis.get.assert_called_once_with("sms:code:1:13800138000")


@pytest.mark.asyncio
async def test_get_sms_code_not_found():
    """get_sms_code 在验证码不存在时应返回 None"""
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None
    with patch.object(redis_client, 'get_redis', return_value=mock_redis):
        code = await redis_client.get_sms_code("13800138000", 1)
        assert code is None


@pytest.mark.asyncio
async def test_delete_sms_code():
    """delete_sms_code 应删除正确的 key"""
    mock_redis = AsyncMock()
    with patch.object(redis_client, 'get_redis', return_value=mock_redis):
        await redis_client.delete_sms_code("13800138000", 1)
        mock_redis.delete.assert_called_once_with("sms:code:1:13800138000")


@pytest.mark.asyncio
async def test_check_sms_rate_limit_allowed():
    """check_sms_rate_limit 首次发送应返回 True"""
    mock_redis = AsyncMock()
    mock_redis.exists.return_value = False
    with patch.object(redis_client, 'get_redis', return_value=mock_redis):
        result = await redis_client.check_sms_rate_limit("13800138000", 1)
        assert result is True
        mock_redis.set.assert_called_once_with("sms:rate:1:13800138000", "1", ex=60)


@pytest.mark.asyncio
async def test_check_sms_rate_limit_blocked():
    """check_sms_rate_limit 频率限制内应返回 False"""
    mock_redis = AsyncMock()
    mock_redis.exists.return_value = True
    with patch.object(redis_client, 'get_redis', return_value=mock_redis):
        result = await redis_client.check_sms_rate_limit("13800138000", 1)
        assert result is False
        mock_redis.set.assert_not_called()


@pytest.mark.asyncio
async def test_check_sms_rate_limit_custom_interval():
    """check_sms_rate_limit 应支持自定义间隔"""
    mock_redis = AsyncMock()
    mock_redis.exists.return_value = False
    with patch.object(redis_client, 'get_redis', return_value=mock_redis):
        await redis_client.check_sms_rate_limit("13800138000", 1, interval=120)
        mock_redis.set.assert_called_once_with("sms:rate:1:13800138000", "1", ex=120)


@pytest.mark.asyncio
async def test_sms_code_key_format():
    """SMS code key 格式应为 sms:code:{scene}:{mobile}"""
    mock_redis = AsyncMock()
    with patch.object(redis_client, 'get_redis', return_value=mock_redis):
        await redis_client.set_sms_code("15612345678", 3, "111111")
        key = mock_redis.set.call_args[0][0]
        assert key == "sms:code:3:15612345678"


@pytest.mark.asyncio
async def test_sms_rate_key_format():
    """SMS rate limit key 格式应为 sms:rate:{scene}:{mobile}"""
    mock_redis = AsyncMock()
    mock_redis.exists.return_value = True
    with patch.object(redis_client, 'get_redis', return_value=mock_redis):
        await redis_client.check_sms_rate_limit("15612345678", 2)
        key = mock_redis.exists.call_args[0][0]
        assert key == "sms:rate:2:15612345678"
