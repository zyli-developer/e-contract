from typing import List, Optional

from pydantic import BaseModel


class ParticipantRequest(BaseModel):
    name: str
    mobile: str
    order_num: int = 1


class SignTaskCreateRequest(BaseModel):
    name: str
    template_id: int | None = None
    file_url: str | None = None
    remark: str | None = None
    participants: List[ParticipantRequest] = []


class ParticipantResponse(BaseModel):
    id: int
    name: str | None = None
    mobile: str
    status: int
    order_num: int


class SignTaskResponse(BaseModel):
    id: int
    name: str
    status: int
    file_url: str | None = None
    signed_file_url: str | None = None
    template_id: int | None = None
    creator_id: int
    remark: str | None = None
    create_time: str | None = None
    participants: List[ParticipantResponse] = []


class SignTaskStatistics(BaseModel):
    totalCount: int = 0
    draftCount: int = 0
    signingCount: int = 0
    completedCount: int = 0
