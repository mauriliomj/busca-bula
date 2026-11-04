from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.tenant_database import TenantBase


class Consultation(TenantBase):
    __tablename__ = "consultations"
    __table_args__ = (UniqueConstraint("user_id", "registration_number", name="uq_consultations_user_registration"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    registration_number: Mapped[str] = mapped_column(String(9))
    product_name: Mapped[str] = mapped_column(String(255))
    active_ingredient: Mapped[str | None] = mapped_column(Text)
    consulted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
