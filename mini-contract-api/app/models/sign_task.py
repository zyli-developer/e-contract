from datetime import datetime

from sqlalchemy import BigInteger, DateTime, JSON, SmallInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SignTask(Base):
    __tablename__ = "sign_task"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), comment="合同名称")
    status: Mapped[int] = mapped_column(SmallInteger, default=1, comment="状态: 1=草稿, 2=签署中, 3=已完成, 4=已取消, 5=已拒签, 6=已过期")
    file_url: Mapped[str | None] = mapped_column(String(500), nullable=True, comment="原始合同文件 URL")
    signed_file_url: Mapped[str | None] = mapped_column(String(500), nullable=True, comment="已签署合同文件 URL")
    file_hash: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="原始文件 SHA-256 哈希")
    signed_file_hash: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="签署后文件 SHA-256 哈希")
    template_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, comment="使用的模板 ID")
    variables: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment="合同变量值")
    creator_id: Mapped[int] = mapped_column(BigInteger, index=True, comment="发起方用户 ID")
    enterprise_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, index=True, comment="发起方企业 ID")
    deadline: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="签署截止时间")
    remark: Mapped[str | None] = mapped_column(String(500), nullable=True, comment="备注")
    create_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    update_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    complete_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="完成时间")
