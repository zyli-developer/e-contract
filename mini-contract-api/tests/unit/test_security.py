"""安全模块单元测试 - 补充边界情况"""
import time

import pytest
from jose import jwt, JWTError

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.config import settings


def test_hash_password_returns_bcrypt():
    """hash_password 应返回 bcrypt 格式的哈希"""
    hashed = hash_password("test123")
    assert hashed.startswith("$2b$")


def test_hash_password_different_each_time():
    """相同密码每次哈希结果应不同（salt 不同）"""
    h1 = hash_password("same_password")
    h2 = hash_password("same_password")
    assert h1 != h2


def test_verify_password_correct():
    """正确密码应验证通过"""
    hashed = hash_password("my_secret")
    assert verify_password("my_secret", hashed) is True


def test_verify_password_wrong():
    """错误密码应验证失败"""
    hashed = hash_password("my_secret")
    assert verify_password("wrong_password", hashed) is False


def test_verify_password_empty():
    """空密码验证"""
    hashed = hash_password("")
    assert verify_password("", hashed) is True
    assert verify_password("non_empty", hashed) is False


def test_access_token_payload():
    """access token 应包含正确的 payload"""
    token = create_access_token(user_id=42)
    payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    assert payload["sub"] == "42"
    assert payload["type"] == "access"
    assert "exp" in payload


def test_refresh_token_payload():
    """refresh token 应包含正确的 payload"""
    token = create_refresh_token(user_id=99)
    payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    assert payload["sub"] == "99"
    assert payload["type"] == "refresh"
    assert "exp" in payload


def test_access_and_refresh_tokens_different_type():
    """access 和 refresh token 的 type 字段应不同"""
    access = create_access_token(1)
    refresh = create_refresh_token(1)
    p1 = decode_token(access)
    p2 = decode_token(refresh)
    assert p1["type"] == "access"
    assert p2["type"] == "refresh"


def test_decode_token_valid():
    """decode_token 应能正确解码有效 token"""
    token = create_access_token(123)
    payload = decode_token(token)
    assert payload["sub"] == "123"


def test_decode_token_invalid():
    """decode_token 对无效 token 应抛出 JWTError"""
    with pytest.raises(JWTError):
        decode_token("invalid.token.here")


def test_decode_token_wrong_secret():
    """使用错误 secret 签名的 token 应解码失败"""
    token = jwt.encode(
        {"sub": "1", "type": "access"},
        "wrong-secret",
        algorithm="HS256",
    )
    with pytest.raises(JWTError):
        decode_token(token)


def test_decode_token_expired():
    """过期 token 应解码失败"""
    expired_token = jwt.encode(
        {"sub": "1", "type": "access", "exp": int(time.time()) - 3600},
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )
    with pytest.raises(JWTError):
        decode_token(expired_token)


def test_access_token_expiry_in_future():
    """access token 的过期时间应在未来"""
    token = create_access_token(1)
    payload = decode_token(token)
    assert payload["exp"] > int(time.time())


def test_refresh_token_expiry_longer_than_access():
    """refresh token 的过期时间应比 access token 更长"""
    access = create_access_token(1)
    refresh = create_refresh_token(1)
    p_access = decode_token(access)
    p_refresh = decode_token(refresh)
    assert p_refresh["exp"] > p_access["exp"]
