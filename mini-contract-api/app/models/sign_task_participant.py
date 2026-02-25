from datetime import datetime

from sqlalchemy import JSON, BigInteger, DateTime, Integer, SmallInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SignTaskParticipant(Base):
    __tablename__ = "sign_task_participant"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(BigInteger, index=True, comment="关联签署任务 ID")
    member_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, index=True, comment="签署方用户 ID")
    name: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="签署方姓名")
    mobile: Mapped[str] = mapped_column(String(20), index=True, comment="签署方手机号")
    status: Mapped[int] = mapped_column(SmallInteger, default=0, comment="状态: 0=待处理, 2=已签署, 3=已拒签")
    order_num: Mapped[int] = mapped_column(Integer, default=1, comment="签署顺序")
    seal_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, comment="使用的印章 ID")
    sign_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="签署时间")
    sign_position: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment="签署位置坐标")
    create_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
