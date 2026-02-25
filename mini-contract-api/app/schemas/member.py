from pydantic import BaseModel


class UserInfoResponse(BaseModel):
    id: int
    mobile: str
    nickname: str | None = None
    avatar: str | None = None


class UpdateUserRequest(BaseModel):
    nickname: str | None = None
    avatar: str | None = None
