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
    file_hash: str | None = None
    signed_file_hash: str | None = None
    template_id: int | None = None
    creator_id: int
    remark: str | None = None
    create_time: str | None = None
    complete_time: str | None = None
    participants: List[ParticipantResponse] = []


class SignTaskStatistics(BaseModel):
    totalCount: int = 0
    draftCount: int = 0
    signingCount: int = 0
    completedCount: int = 0


class SignCodeRequest(BaseModel):
    """签署验证码请求"""
    pass  # task_id 从 URL path 获取


class SignCodeVerifyRequest(BaseModel):
    """签署验证码验证"""
    code: str


class SignRequest(BaseModel):
    """执行签署请求"""
    seal_id: int | None = None


class RejectRequest(BaseModel):
    """拒签请求"""
    reason: str | None = None


class EvidenceLogResponse(BaseModel):
    id: int
    task_id: int
    action: str
    user_id: int | None = None
    ip: str | None = None
    device: str | None = None
    data_hash: str | None = None
    detail: dict | None = None
    create_time: str | None = None
