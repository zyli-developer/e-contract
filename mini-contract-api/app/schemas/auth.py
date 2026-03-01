from pydantic import BaseModel


class LoginRequest(BaseModel):
    mobile: str
    password: str


class RegisterRequest(BaseModel):
    mobile: str
    password: str
    nickname: str | None = None


class RefreshTokenRequest(BaseModel):
    refreshToken: str


class UpdatePasswordRequest(BaseModel):
    password: str
    confirmPassword: str


class AuthTokenResponse(BaseModel):
    accessToken: str
    refreshToken: str
    userId: int
    expiresTime: int
