from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置，从环境变量或 .env 文件加载"""

    # 应用
    APP_NAME: str = "Mini Contract API"
    DEBUG: bool = True
    API_PREFIX: str = "/app-api"

    # 数据库
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/mini_contract"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    JWT_SECRET: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 2
    REFRESH_TOKEN_EXPIRE_HOURS: int = 720

    # 文件存储
    S3_ENDPOINT: str = ""
    S3_ACCESS_KEY: str = ""
    S3_SECRET_KEY: str = ""
    S3_BUCKET: str = "mini-contract"

    # 短信服务
    SMS_ACCESS_KEY: str = ""
    SMS_SECRET_KEY: str = ""
    SMS_SIGN_NAME: str = ""
    SMS_TEMPLATE_CODE: str = ""

    # RSA 密码加密（前端用公钥加密，后端用私钥解密）
    RSA_PUBLIC_KEY: str = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAuAcAZrFEy0wE2wlDreAd
gLs7k31XC2IeRO/HrNpTt8VwGNSWyAeIa+QX8TQhMZfcXMQGQRgppSQTwvnxMJ3+
sE6VkvNLuG6HHBCTJnurh1Atu0/87Cz3/dVL/yYxrvPybcA7X9LmsUxDQ2FiWZ2y
DDemKclDqZFQMRLgc4hTfJvtfScv6R/fZkfDd25Y33bUgRlVCRDETpWqAermDtCL
Y4OrWASC9lgj65oC6JRtQgE53V9g8G9hOJ6jGGqkBkq2oE6fMY2shceIjtq4ZuRM
HCZUOmvvnUNE+JzhVh8uDC3KiYLK+ATSa2F2mD0Wk2AO4xnoHxocMFCHj0Yg8iiI
GwIDAQAB
-----END PUBLIC KEY-----"""
    RSA_PRIVATE_KEY: str = """-----BEGIN PRIVATE KEY-----
MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQC4BwBmsUTLTATb
CUOt4B2AuzuTfVcLYh5E78es2lO3xXAY1JbIB4hr5BfxNCExl9xcxAZBGCmlJBPC
+fEwnf6wTpWS80u4boccEJMme6uHUC27T/zsLPf91Uv/JjGu8/JtwDtf0uaxTEND
YWJZnbIMN6YpyUOpkVAxEuBziFN8m+19Jy/pH99mR8N3bljfdtSBGVUJEMROlaoB
6uYO0Itjg6tYBIL2WCPrmgLolG1CATndX2Dwb2E4nqMYaqQGSragTp8xjayFx4iO
2rhm5EwcJlQ6a++dQ0T4nOFWHy4MLcqJgsr4BNJrYXaYPRaTYA7jGegfGhwwUIeP
RiDyKIgbAgMBAAECggEAV4ck/rMD2HnwuUl/wjyda7QiEvWDqCtj4D/3xdQWC4tB
1N2QVdWXYlGbvaKgwxjKu+iUXPOkIyK0r4D34brT/4FxDPLhKfiQFJ4hjyU1IWfW
SIgz8RU2YqnHurSs3tyyitbqppoGFYADYhH4mE0z+TGiu685mnY+IQksbmcB5nrp
DseQr5Tj2ebuwKeYoCqCV78gvYsEEcXQWCEaNDyS5LXGQvl3685bTYuYzFmrR8IW
tDlJTBaGK8mZrYzu3Tx8vR45e6x+6nFbddYKKQkBXl07jV6AjLLNvlEz0p/Rkhlz
d2aO+wrONi7e+g5IPErUmgzV5LGbCdBbjYF+X+2bkQKBgQDbigGNSK2aqhPjhqc2
uS6f5tEvpMtkc9D368cdoNAVfUlsN8W6cFaQJWmbjNTmHQmiiLmYEe9uBYii2Raa
odgA5IIJ/wMKBjxIuayCvM3g3cowdoX2NJK50/a0pYqOAXpuQsvST2Bv2laMnLRd
nyV6IvOZ7ijtkkqSU8dgyc9XEwKBgQDWlyrMGZimwZVx+ZynmcTQQ+eCvZprtyzZ
U9jH//X4xougiAg6De7s16Z1mYmB5Jetv7nFLbSEi+R1MAoPmY6gElImdRb4Nx8e
9JkygpU0R9+iimqxcnOiUY6UAfruEE9Muw53in6tm07S8kSYYKMB13hkd9KGq8r2
cNhHZuOD2QKBgGLFMy+KTDiyXiJWWXKgW96q7OA/hxZZmOGBnWKyEAwrAtaCPR5F
HlzZyCqocLxawhPy6XUGVK8uJCwH+Uh2mgTEydCPf6GJ7qNVjcx//yw0/JtTJ6/+
NSkPuQXLGIwNFDT5LlQfTCbml1vJwMgCKs1JXkmZwaYo1A4DTUc5ZGQrAoGAJe+/
jymPRRvAEdAxE6gplTAMA58FZ7mQYjNihakIkRx4nr6txaWk8ZYGRZAJMT96WSsl
6mf0G+KnVthRTwS0pDPY9heJIgSMqepQEw/m1MFIFfImfoxfSPjmHeBjviZ//m6r
VhLT5lkojD5sRgv/hVnUXN6aB1jjnsHAWo8j9bECgYAiEmWmXiqmif+Psekey5JI
23IbE3ywtb3MxP1+BpbqPSIsuKJX4EZLCw5e1KYlOg9254qVgaWu6uRMoVqRK9W9
FZeKnan7n/0eGvckp6ngIQ7PjQh03Uu0o5izEdACZJie4bwr4GUHZOdhMrhqnXyM
MD01gvM1KugUgjbjnM64iA==
-----END PRIVATE KEY-----"""

    # 微信小程序
    WECHAT_APP_ID: str = "wxff976eb0ac6d7f97"
    WECHAT_APP_SECRET: str = "cdb7f2e5565e1897ede37dfddc48ab21"
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
