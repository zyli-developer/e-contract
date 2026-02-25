from datetime import datetime

from sqlalchemy import BigInteger, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class InfraFile(Base):
    __tablename__ = "infra_file"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    config_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, comment="存储配置 ID")
    path: Mapped[str] = mapped_column(String(500), comment="文件路径")
    name: Mapped[str] = mapped_column(String(200), comment="文件名")
    url: Mapped[str] = mapped_column(String(500), comment="访问 URL")
    type: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="MIME 类型")
    size: Mapped[int | None] = mapped_column(BigInteger, nullable=True, comment="文件大小（字节）")
    tenant_id: Mapped[int] = mapped_column(BigInteger, default=1, comment="租户 ID")
    create_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
