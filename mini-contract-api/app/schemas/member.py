from pydantic import BaseModel, Field


class UserInfoResponse(BaseModel):
    id: int
    mobile: str
    nickname: str | None = None
    avatar: str | None = None
    real_name_verified: int = 0
    real_name: str | None = None
    role: str = "landlord"


class UpdateUserRequest(BaseModel):
    nickname: str | None = None
    avatar: str | None = None


class RealNameVerifyRequest(BaseModel):
    real_name: str = Field(..., min_length=1, max_length=50, description="真实姓名")
    id_card: str = Field(..., min_length=18, max_length=18, description="身份证号")
    id_card_front_url: str = Field(..., description="身份证正面照片 URL")
    id_card_back_url: str = Field(..., description="身份证背面照片 URL")
