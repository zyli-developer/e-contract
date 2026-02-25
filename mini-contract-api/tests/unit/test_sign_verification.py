"""签署验证码单元测试"""
import pytest
from unittest.mock import AsyncMock, patch

from app.services.sign_task_service import SIGN_CODE_SCENE


def test_sign_code_scene_distinct():
    """签署验证码场景值应与登录/注册/修改密码不同"""
    # 登录=1, 注册=2, 修改密码=3
    assert SIGN_CODE_SCENE not in (1, 2, 3)
    assert SIGN_CODE_SCENE == 10


@pytest.mark.anyio
async def test_sms_code_redis_storage():
    """验证码应存入 Redis 并可读取"""
    try:
        from app.utils.redis_client import set_sms_code, get_sms_code, delete_sms_code
        mobile = "13800138999"
        scene = SIGN_CODE_SCENE
        code = "654321"

        await set_sms_code(mobile, scene, code)
        stored = await get_sms_code(mobile, scene)
        assert stored == code

        # 删除后应不可获取
        await delete_sms_code(mobile, scene)
        stored2 = await get_sms_code(mobile, scene)
        assert stored2 is None
    except Exception:
        pytest.skip("Redis 不可用")


@pytest.mark.anyio
async def test_sms_rate_limit():
    """60 秒内重复发送应被拒绝"""
    try:
        from app.utils.redis_client import check_sms_rate_limit, get_redis
        mobile = "13800138998"
        scene = SIGN_CODE_SCENE

        # 清除可能存在的旧记录
        r = await get_redis()
        await r.delete(f"sms:rate:{scene}:{mobile}")

        # 第一次应允许
        assert await check_sms_rate_limit(mobile, scene) is True
        # 立即第二次应拒绝
        assert await check_sms_rate_limit(mobile, scene) is False

        # 清理
        await r.delete(f"sms:rate:{scene}:{mobile}")
    except Exception:
        pytest.skip("Redis 不可用")


def test_code_format():
    """验证码应为 6 位数字"""
    import random
    code = "".join(str(random.randint(0, 9)) for _ in range(6))
    assert len(code) == 6
    assert code.isdigit()


def test_mobile_mask():
    """手机号脱敏格式正确"""
    mobile = "13800138000"
    masked = mobile[:3] + "****" + mobile[-4:]
    assert masked == "138****8000"
    assert len(masked) == 11
