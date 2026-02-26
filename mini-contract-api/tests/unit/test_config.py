"""配置模块单元测试"""
import os
from unittest.mock import patch

from app.config import Settings


def test_settings_defaults():
    """Settings 类应有正确的默认值"""
    s = Settings(
        _env_file=None,  # 不读取 .env
    )
    assert s.APP_NAME == "Mini Contract API"
    assert s.DEBUG is True
    assert s.API_PREFIX == "/app-api"
    assert s.JWT_ALGORITHM == "HS256"
    assert s.ACCESS_TOKEN_EXPIRE_HOURS == 2
    assert s.REFRESH_TOKEN_EXPIRE_HOURS == 720
    assert s.S3_BUCKET == "mini-contract"


def test_settings_env_override():
    """环境变量应覆盖默认值"""
    with patch.dict(os.environ, {
        "APP_NAME": "Test App",
        "DEBUG": "false",
        "ACCESS_TOKEN_EXPIRE_HOURS": "4",
    }):
        s = Settings(_env_file=None)
        assert s.APP_NAME == "Test App"
        assert s.DEBUG is False
        assert s.ACCESS_TOKEN_EXPIRE_HOURS == 4


def test_settings_jwt_defaults():
    """JWT 配置应有合理默认值"""
    s = Settings(_env_file=None)
    assert s.JWT_SECRET == "your-secret-key-change-in-production"
    assert s.JWT_ALGORITHM == "HS256"
    assert s.ACCESS_TOKEN_EXPIRE_HOURS > 0
    assert s.REFRESH_TOKEN_EXPIRE_HOURS > s.ACCESS_TOKEN_EXPIRE_HOURS


def test_settings_s3_defaults():
    """S3 配置默认为空"""
    s = Settings(_env_file=None)
    assert s.S3_ENDPOINT == ""
    assert s.S3_ACCESS_KEY == ""
    assert s.S3_SECRET_KEY == ""
    assert s.S3_BUCKET == "mini-contract"


def test_settings_sms_defaults():
    """SMS 配置默认为空"""
    s = Settings(_env_file=None)
    assert s.SMS_ACCESS_KEY == ""
    assert s.SMS_SECRET_KEY == ""
    assert s.SMS_SIGN_NAME == ""
    assert s.SMS_TEMPLATE_CODE == ""


def test_settings_database_url_default():
    """数据库 URL 有默认值"""
    s = Settings(_env_file=None)
    assert "postgresql" in s.DATABASE_URL
    assert "asyncpg" in s.DATABASE_URL


def test_settings_redis_url_default():
    """Redis URL 有默认值"""
    s = Settings(_env_file=None)
    assert s.REDIS_URL.startswith("redis://")


def test_get_settings_returns_settings_instance():
    """get_settings 应返回 Settings 实例"""
    from app.config import get_settings
    s = get_settings()
    assert isinstance(s, Settings)


def test_settings_module_level_instance():
    """模块级别的 settings 应是 Settings 实例"""
    from app.config import settings
    assert isinstance(settings, Settings)
