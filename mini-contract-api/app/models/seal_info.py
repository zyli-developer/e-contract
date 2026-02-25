from datetime import datetime

from sqlalchemy import BigInteger, DateTime, SmallInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SealInfo(Base):
    __tablename__ = "seal_info"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), comment="印章名称")
    type: Mapped[int] = mapped_column(SmallInteger, comment="类型: 11=个人签名, 12=个人印章")
    seal_data: Mapped[str] = mapped_column(String(500), comment="印章图片 URL")
    member_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, index=True, comment="个人印章归属用户")
    enterprise_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, index=True, comment="企业印章归属企业")
    status: Mapped[int] = mapped_column(SmallInteger, default=1, comment="状态: 1=正常, 2=已吊销")
    is_default: Mapped[int] = mapped_column(SmallInteger, default=0, comment="是否默认印章")
    tenant_id: Mapped[int] = mapped_column(BigInteger, default=1, comment="租户 ID")
    create_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    update_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
