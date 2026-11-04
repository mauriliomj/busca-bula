from datetime import date, datetime

from sqlalchemy import Date, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.catalog_database import CatalogBase


class Medicine(CatalogBase):
    __tablename__ = "medicines"

    id: Mapped[int] = mapped_column(primary_key=True)
    registration_number: Mapped[str] = mapped_column(String(9), unique=True)
    product_name: Mapped[str] = mapped_column(String(255))
    active_ingredient: Mapped[str | None] = mapped_column(Text)
    therapeutic_class: Mapped[str | None] = mapped_column(String(255))
    regulatory_category: Mapped[str | None] = mapped_column(String(60))
    holder_cnpj: Mapped[str | None] = mapped_column(String(14))
    holder_name: Mapped[str | None] = mapped_column(String(255))
    process_number: Mapped[str | None] = mapped_column(String(30))
    is_active: Mapped[bool]
    registration_expires_on: Mapped[date | None] = mapped_column(Date)
    process_finished_on: Mapped[date | None] = mapped_column(Date)
    imported_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
