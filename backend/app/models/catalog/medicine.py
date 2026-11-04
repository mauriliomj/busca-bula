from datetime import date, datetime

from sqlalchemy import Computed, Date, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.catalog_database import CatalogBase
from app.core.text_normalization import ACCENTED_CHARACTERS, UNACCENTED_CHARACTERS


def build_normalized_expression(*columns: str) -> str:
    joined = " || ' ' || ".join(f"coalesce({column}, '')" for column in columns)
    return f"lower(translate({joined}, '{ACCENTED_CHARACTERS}', '{UNACCENTED_CHARACTERS}'))"


SEARCH_NAME_EXPRESSION = build_normalized_expression("product_name")
SEARCH_TEXT_EXPRESSION = build_normalized_expression(
    "product_name", "active_ingredient", "therapeutic_class", "holder_name"
)


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
    search_name: Mapped[str] = mapped_column(Text, Computed(SEARCH_NAME_EXPRESSION, persisted=True))
    search_text: Mapped[str] = mapped_column(Text, Computed(SEARCH_TEXT_EXPRESSION, persisted=True))
