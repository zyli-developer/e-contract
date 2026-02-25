from datetime import datetime

from sqlalchemy import JSON, BigInteger, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SignEvidenceLog(Base):
    __tablename__ = "sign_evidence_log"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(BigInteger, index=True, comment="关联合同 ID")
    action: Mapped[str] = mapped_column(String(50), comment="操作类型")
    user_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, comment="操作用户 ID")
    ip: Mapped[str | None] = mapped_column(String(45), nullable=True, comment="操作 IP 地址")
    device: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="设备信息")
    data_hash: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="操作时的文档 SHA-256 哈希")
    detail: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment="操作详情")
    tenant_id: Mapped[int] = mapped_column(BigInteger, default=1, comment="租户 ID")
    create_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
