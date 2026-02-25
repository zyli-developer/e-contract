from pydantic import BaseModel


class LoginRequest(BaseModel):
    mobile: str
    password: str


class SmsLoginRequest(BaseModel):
    mobile: str
    code: str


class SendSmsCodeRequest(BaseModel):
    mobile: str
    scene: int  # 1=登录, 2=注册, 3=修改密码


class SocialLoginRequest(BaseModel):
    type: int  # 31=公众号, 32=开放平台, 34=小程序
    code: str
    state: str = "default"


class RefreshTokenRequest(BaseModel):
    refreshToken: str


class UpdatePasswordRequest(BaseModel):
    password: str
    code: str


class AuthTokenResponse(BaseModel):
    accessToken: str
    refreshToken: str
    userId: int
    expiresTime: int
