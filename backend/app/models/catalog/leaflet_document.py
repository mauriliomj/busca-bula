from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, ForeignKey, SmallInteger, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.catalog_database import CatalogBase


class LeafletDocumentSource(StrEnum):
    CHATBULARIO = "chatbulario"
    PDF_UPLOAD = "pdf_upload"


class LeafletDocument(CatalogBase):
    __tablename__ = "leaflet_documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    registration_number: Mapped[str] = mapped_column(String(9), unique=True)
    product_name: Mapped[str] = mapped_column(String(255))
    source: Mapped[str] = mapped_column(String(20))
    expedient_number: Mapped[str | None] = mapped_column(String(20))
    imported_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class LeafletSection(CatalogBase):
    __tablename__ = "leaflet_sections"
    __table_args__ = (UniqueConstraint("document_id", "section_number", name="uq_leaflet_sections_document_number"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("leaflet_documents.id", ondelete="CASCADE"), index=True)
    section_number: Mapped[int] = mapped_column(SmallInteger)
    content: Mapped[str] = mapped_column(Text)
