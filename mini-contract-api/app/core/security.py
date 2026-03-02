import base64
from datetime import datetime, timedelta, timezone

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from jose import JWTError, jwt
from loguru import logger
from passlib.context import CryptContext

from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
    payload = {"sub": str(user_id), "exp": expire, "type": "access"}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=settings.REFRESH_TOKEN_EXPIRE_HOURS)
    payload = {"sub": str(user_id), "exp": expire, "type": "refresh"}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """解码 JWT Token，失败时抛出 JWTError"""
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])


def rsa_decrypt(encrypted_base64: str) -> str:
    """
    使用 RSA 私钥解密前端加密的密码。
    前端用公钥加密后 base64 编码传输，后端 base64 解码后用私钥解密。
    如果解密失败（如传入的是明文），则原样返回以保持向后兼容。
    """
    try:
        private_key = serialization.load_pem_private_key(
            settings.RSA_PRIVATE_KEY.encode(), password=None
        )
        encrypted_bytes = base64.b64decode(encrypted_base64)
        decrypted = private_key.decrypt(encrypted_bytes, asym_padding.PKCS1v15())
        return decrypted.decode("utf-8")
    except Exception:
        # 解密失败时原样返回（兼容未加密的请求，如测试环境）
        logger.debug("RSA 解密失败，使用原始值（可能是明文密码）")
        return encrypted_base64
