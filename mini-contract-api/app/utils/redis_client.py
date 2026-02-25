"""Redis 操作封装"""
from typing import Optional

import redis.asyncio as redis

from app.config import settings

_pool: Optional[redis.Redis] = None


async def get_redis() -> redis.Redis:
    """获取 Redis 连接（懒加载单例）"""
    global _pool
    if _pool is None:
        _pool = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
        )
    return _pool


async def close_redis():
    """关闭 Redis 连接"""
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


async def set_sms_code(mobile: str, scene: int, code: str, ttl: int = 300):
    """存储短信验证码，默认 5 分钟过期"""
    r = await get_redis()
    key = f"sms:code:{scene}:{mobile}"
    await r.set(key, code, ex=ttl)


async def get_sms_code(mobile: str, scene: int) -> Optional[str]:
    """获取短信验证码"""
    r = await get_redis()
    key = f"sms:code:{scene}:{mobile}"
    return await r.get(key)


async def delete_sms_code(mobile: str, scene: int):
    """删除已使用的验证码"""
    r = await get_redis()
    key = f"sms:code:{scene}:{mobile}"
    await r.delete(key)


async def check_sms_rate_limit(mobile: str, scene: int, interval: int = 60) -> bool:
    """检查短信发送频率限制，interval 秒内只能发 1 次，返回 True 表示可以发送"""
    r = await get_redis()
    key = f"sms:rate:{scene}:{mobile}"
    if await r.exists(key):
        return False
    await r.set(key, "1", ex=interval)
    return True
