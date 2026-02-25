from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class MemberSocialUser(Base):
    __tablename__ = "member_social_user"
    __table_args__ = (
        UniqueConstraint("type", "openid", name="uq_type_openid"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    member_id: Mapped[int] = mapped_column(BigInteger, index=True, comment="关联用户 ID")
    type: Mapped[int] = mapped_column(Integer, comment="社交类型: 31=公众号, 32=开放平台, 34=小程序")
    openid: Mapped[str] = mapped_column(String(100), comment="微信 openid")
    unionid: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="微信 unionid")
    nickname: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="社交平台昵称")
    avatar: Mapped[str | None] = mapped_column(String(500), nullable=True, comment="社交平台头像")
    tenant_id: Mapped[int] = mapped_column(BigInteger, default=1, comment="租户 ID")
    create_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
