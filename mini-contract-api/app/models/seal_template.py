from datetime import datetime

from sqlalchemy import JSON, BigInteger, DateTime, SmallInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SealTemplate(Base):
    __tablename__ = "seal_template"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), comment="模板名称")
    type: Mapped[int] = mapped_column(SmallInteger, comment="适用印章类型")
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True, comment="模板预览图")
    form_fields: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment="模板表单字段定义")
    tenant_id: Mapped[int] = mapped_column(BigInteger, default=1, comment="租户 ID")
    create_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
