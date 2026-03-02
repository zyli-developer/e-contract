"""签署证据链服务"""
import hashlib
from typing import Optional

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sign_evidence_log import SignEvidenceLog


# 证据链操作类型
class EvidenceAction:
    CONTRACT_CREATED = "CONTRACT_CREATED"
    CONTRACT_SENT = "CONTRACT_SENT"
    SIGNER_VIEWED = "SIGNER_VIEWED"
    CONTRACT_SIGNED = "CONTRACT_SIGNED"
    CONTRACT_COMPLETED = "CONTRACT_COMPLETED"
    CONTRACT_CANCELLED = "CONTRACT_CANCELLED"
    CONTRACT_REJECTED = "CONTRACT_REJECTED"


async def log_evidence(
    db: AsyncSession,
    task_id: int,
    action: str,
    user_id: Optional[int] = None,
    ip: Optional[str] = None,
    device: Optional[str] = None,
    data_hash: Optional[str] = None,
    detail: Optional[dict] = None,
) -> SignEvidenceLog:
    """记录一条证据链日志"""
    logger.info("记录证据: task_id=%d, action=%s, user_id=%s, ip=%s",
                task_id, action, user_id, ip)
    log = SignEvidenceLog(
        task_id=task_id,
        action=action,
        user_id=user_id,
        ip=ip,
        device=device,
        data_hash=data_hash,
        detail=detail,
    )
    db.add(log)
    await db.flush()
    await db.refresh(log)
    return log


async def get_evidence_list(db: AsyncSession, task_id: int) -> list[dict]:
    """查询合同的完整证据链（按时间正序）"""
    result = await db.execute(
        select(SignEvidenceLog)
        .where(SignEvidenceLog.task_id == task_id)
        .order_by(SignEvidenceLog.create_time.asc())
    )
    logs = result.scalars().all()
    return [
        {
            "id": log.id,
            "task_id": log.task_id,
            "action": log.action,
            "user_id": log.user_id,
            "ip": log.ip,
            "device": log.device,
            "data_hash": log.data_hash,
            "detail": log.detail,
            "create_time": log.create_time.isoformat() if log.create_time else None,
        }
        for log in logs
    ]


def compute_file_hash(file_content: bytes) -> str:
    """计算文件 SHA-256 哈希"""
    return hashlib.sha256(file_content).hexdigest()
