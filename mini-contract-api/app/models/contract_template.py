from datetime import datetime

from sqlalchemy import JSON, BigInteger, DateTime, Integer, SmallInteger, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ContractTemplate(Base):
    __tablename__ = "contract_template"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), comment="模板名称")
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="模板描述")
    category: Mapped[str] = mapped_column(String(20), default="other", comment="分类: loan/lease/labor/purchase/sales/other")
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True, comment="模板封面图")
    content: Mapped[str | None] = mapped_column(Text, nullable=True, comment="模板 HTML 内容")
    variables: Mapped[list | None] = mapped_column(JSON, nullable=True, comment="模板变量定义")
    signatories: Mapped[list | None] = mapped_column(JSON, nullable=True, comment="签署方配置")
    use_count: Mapped[int] = mapped_column(Integer, default=0, comment="使用次数")
    status: Mapped[int] = mapped_column(SmallInteger, default=1, comment="状态: 1=上架, 0=下架")
    tenant_id: Mapped[int] = mapped_column(BigInteger, default=1, comment="租户 ID")
    create_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
