"""Redis 操作封装"""
from typing import Optional

import redis.asyncio as redis
from loguru import logger

from app.config import settings

_pool: Optional[redis.Redis] = None


async def get_redis() -> redis.Redis:
    """获取 Redis 连接（懒加载单例）"""
    global _pool
    if _pool is None:
        logger.info("初始化 Redis 连接: %s", settings.REDIS_URL)
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
        logger.info("Redis 连接已关闭")


async def set_sms_code(mobile: str, scene: int, code: str, ttl: int = 300):
    """存储短信验证码，默认 5 分钟过期"""
    r = await get_redis()
    key = f"sms:code:{scene}:{mobile}"
    await r.set(key, code, ex=ttl)
    logger.debug("验证码已存储: key=%s, ttl=%d", key, ttl)


async def get_sms_code(mobile: str, scene: int) -> Optional[str]:
    """获取短信验证码"""
    r = await get_redis()
    key = f"sms:code:{scene}:{mobile}"
    code = await r.get(key)
    logger.debug("获取验证码: key=%s, found=%s", key, code is not None)
    return code


async def delete_sms_code(mobile: str, scene: int):
    """删除已使用的验证码"""
    r = await get_redis()
    key = f"sms:code:{scene}:{mobile}"
    await r.delete(key)
    logger.debug("验证码已删除: key=%s", key)


async def check_sms_rate_limit(mobile: str, scene: int, interval: int = 60) -> bool:
    """检查短信发送频率限制，interval 秒内只能发 1 次，返回 True 表示可以发送"""
    r = await get_redis()
    key = f"sms:rate:{scene}:{mobile}"
    if await r.exists(key):
        logger.warning("短信发送频率限制: mobile=%s, scene=%d", mobile, scene)
        return False
    await r.set(key, "1", ex=interval)
    return True
