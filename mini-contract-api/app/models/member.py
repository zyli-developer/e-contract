from datetime import datetime

from sqlalchemy import BigInteger, DateTime, String, SmallInteger, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Member(Base):
    __tablename__ = "member"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    mobile: Mapped[str] = mapped_column(String(20), unique=True, index=True, comment="手机号")
    password: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="加密密码")
    nickname: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="昵称")
    avatar: Mapped[str | None] = mapped_column(String(500), nullable=True, comment="头像 URL")
    status: Mapped[int] = mapped_column(SmallInteger, default=1, comment="状态: 0=禁用, 1=正常")
    create_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    update_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
