"""认证服务单元测试"""
import pytest

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_hash_password():
    """密码哈希应不可逆"""
    hashed = hash_password("test123")
    assert hashed != "test123"
    assert hashed.startswith("$2b$")


def test_verify_password_correct():
    """正确密码应验证通过"""
    hashed = hash_password("test123")
    assert verify_password("test123", hashed) is True


def test_verify_password_wrong():
    """错误密码应验证失败"""
    hashed = hash_password("test123")
    assert verify_password("wrong", hashed) is False


def test_create_access_token():
    """Access Token 应包含 user_id 和 type"""
    token = create_access_token(42)
    payload = decode_token(token)
    assert payload["sub"] == "42"
    assert payload["type"] == "access"
    assert "exp" in payload


def test_create_refresh_token():
    """Refresh Token 应包含 user_id 和 type"""
    token = create_refresh_token(42)
    payload = decode_token(token)
    assert payload["sub"] == "42"
    assert payload["type"] == "refresh"
    assert "exp" in payload


def test_access_and_refresh_tokens_are_different():
    """Access Token 和 Refresh Token 应不同"""
    access = create_access_token(42)
    refresh = create_refresh_token(42)
    assert access != refresh


def test_decode_invalid_token_raises():
    """无效 Token 应抛出异常"""
    from jose import JWTError
    with pytest.raises(JWTError):
        decode_token("invalid.token.here")


def test_different_users_get_different_tokens():
    """不同用户的 Token 应不同"""
    t1 = create_access_token(1)
    t2 = create_access_token(2)
    assert t1 != t2

    p1 = decode_token(t1)
    p2 = decode_token(t2)
    assert p1["sub"] == "1"
    assert p2["sub"] == "2"
