from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.catalog.catalog_import import CatalogImport, CatalogImportStatus


class CatalogImportRepository:
    def __init__(self, catalog_session: Session) -> None:
        self.session = catalog_session

    def find_by_ids(self, import_ids: list[int]) -> list[CatalogImport]:
        statement = select(CatalogImport).where(CatalogImport.id.in_(import_ids)).order_by(CatalogImport.id)
        return list(self.session.scalars(statement))

    def list_running(self) -> list[CatalogImport]:
        statement = select(CatalogImport).where(CatalogImport.status == CatalogImportStatus.RUNNING)
        return list(self.session.scalars(statement))

    def list_latest_per_source(self) -> list[CatalogImport]:
        latest_ids = select(func.max(CatalogImport.id)).group_by(CatalogImport.source)
        statement = select(CatalogImport).where(CatalogImport.id.in_(latest_ids)).order_by(CatalogImport.source)
        return list(self.session.scalars(statement))

    def mark_finished(
        self,
        catalog_import: CatalogImport,
        status: CatalogImportStatus,
        finished_at: datetime,
        error_message: str | None = None,
    ) -> None:
        catalog_import.status = status
        catalog_import.finished_at = finished_at
        catalog_import.error_message = error_message

    def save_all(self, catalog_imports: list[CatalogImport]) -> list[CatalogImport]:
        self.session.add_all(catalog_imports)
        self.session.commit()
        for catalog_import in catalog_imports:
            self.session.refresh(catalog_import)
        return catalog_imports
