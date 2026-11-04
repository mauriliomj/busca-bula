from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.catalog_database import CatalogBase


class Leaflet(CatalogBase):
    __tablename__ = "leaflets"

    id: Mapped[int] = mapped_column(primary_key=True)
    registration_number: Mapped[str] = mapped_column(String(9), unique=True)
    bulario_product_id: Mapped[str] = mapped_column(String(20))
    product_name: Mapped[str] = mapped_column(String(255))
    process_number: Mapped[str | None] = mapped_column(String(30))
    company_cnpj: Mapped[str | None] = mapped_column(String(14))
    company_name: Mapped[str | None] = mapped_column(String(255))
    document_id: Mapped[str | None] = mapped_column(String(20))
    expedient_number: Mapped[str | None] = mapped_column(String(20))
    published_at: Mapped[datetime | None] = mapped_column(DateTime)
    imported_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
