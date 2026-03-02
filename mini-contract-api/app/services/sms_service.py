"""短信验证码发送服务"""
import random

from loguru import logger

from app.config import settings
from app.utils.redis_client import (
    check_sms_rate_limit,
    set_sms_code,
)


def _generate_code(length: int = 6) -> str:
    """生成数字验证码"""
    return "".join(str(random.randint(0, 9)) for _ in range(length))


async def send_sms_code(mobile: str, scene: int) -> None:
    """发送短信验证码

    Args:
        mobile: 手机号
        scene: 场景 1=登录, 2=注册, 3=修改密码
    """
    # 频率限制：60 秒内只能发 1 次
    can_send = await check_sms_rate_limit(mobile, scene)
    if not can_send:
        from app.core.exceptions import BusinessException
        raise BusinessException(code=1012002003, msg="发送太频繁，请 60 秒后重试")

    code = _generate_code()

    # 存储验证码到 Redis（5 分钟有效）
    await set_sms_code(mobile, scene, code)

    # MVP 阶段：仅日志输出验证码，不实际发送短信
    if settings.DEBUG or not settings.SMS_ACCESS_KEY:
        logger.info(f"[SMS Mock] mobile={mobile}, scene={scene}, code={code}")
        return

    # 正式环境：调用阿里云短信 API
    # TODO: 集成阿里云短信 SDK
    logger.info(f"[SMS] 发送验证码到 {mobile}, scene={scene}")
