from datetime import datetime

from sqlalchemy import BigInteger, DateTime, SmallInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class MemberToken(Base):
    __tablename__ = "member_token"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    member_id: Mapped[int] = mapped_column(BigInteger, index=True, comment="关联用户 ID")
    access_token: Mapped[str] = mapped_column(String(500), comment="Access Token")
    refresh_token: Mapped[str] = mapped_column(String(500), comment="Refresh Token")
    access_token_expire_time: Mapped[datetime] = mapped_column(DateTime, comment="Access Token 过期时间")
    refresh_token_expire_time: Mapped[datetime] = mapped_column(DateTime, comment="Refresh Token 过期时间")
    refresh_token_used: Mapped[int] = mapped_column(SmallInteger, default=0, comment="是否已使用（一次性）")
    tenant_id: Mapped[int] = mapped_column(BigInteger, default=1, comment="租户 ID")
    create_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
