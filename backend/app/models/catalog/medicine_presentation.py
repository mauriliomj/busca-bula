from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.catalog_database import CatalogBase


class MedicinePresentation(CatalogBase):
    __tablename__ = "medicine_presentations"

    id: Mapped[int] = mapped_column(primary_key=True)
    ggrem_code: Mapped[str] = mapped_column(String(20), unique=True)
    registration_number: Mapped[str | None] = mapped_column(String(13))
    medicine_registration_number: Mapped[str | None] = mapped_column(String(9), index=True)
    product_name: Mapped[str] = mapped_column(String(255))
    presentation: Mapped[str | None] = mapped_column(Text)
    active_ingredient: Mapped[str | None] = mapped_column(Text)
    laboratory_cnpj: Mapped[str | None] = mapped_column(String(14))
    laboratory_name: Mapped[str | None] = mapped_column(String(255))
    therapeutic_class: Mapped[str | None] = mapped_column(String(255))
    product_type: Mapped[str | None] = mapped_column(String(60))
    price_regime: Mapped[str | None] = mapped_column(String(30))
    prescription_label: Mapped[str | None] = mapped_column(String(60))
    ean_codes: Mapped[list[str]] = mapped_column(ARRAY(String(14)), default=list)
    hospital_restricted: Mapped[bool | None]
    marketed: Mapped[bool | None]
    factory_price_without_taxes: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    consumer_price_without_taxes: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    factory_prices: Mapped[dict[str, float]] = mapped_column(JSONB, default=dict)
    consumer_prices: Mapped[dict[str, float]] = mapped_column(JSONB, default=dict)
    imported_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
