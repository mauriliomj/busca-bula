from sqlalchemy.orm import Session

from app.models.catalog.catalog_import import CatalogImportStatus
from app.repositories.catalog_import_repository import CatalogImportRepository
from app.repositories.catalog_summary_repository import CatalogSummaryRepository
from app.schemas.catalog_schema import (
    CatalogCoverageResponse,
    CatalogImportResponse,
    CatalogSummaryResponse,
)


def calculate_percentage(part: int, total: int) -> float:
    return round(part * 100 / total, 1) if total else 0.0


class CatalogSummaryService:
    def __init__(self, catalog_reader_session: Session) -> None:
        self.summary_repository = CatalogSummaryRepository(catalog_reader_session)
        self.catalog_import_repository = CatalogImportRepository(catalog_reader_session)

    def build_summary(self) -> CatalogSummaryResponse:
        active_medicines = self.summary_repository.count_active_medicines()
        with_leaflet = self.summary_repository.count_active_medicines_with_leaflet()
        with_price = self.summary_repository.count_active_medicines_with_price()
        latest_imports = self.catalog_import_repository.list_latest_per_source()
        return CatalogSummaryResponse(
            medicines_total=self.summary_repository.count_medicines(),
            active_medicines_total=active_medicines,
            leaflets_total=self.summary_repository.count_leaflets(),
            presentations_total=self.summary_repository.count_presentations(),
            coverage=CatalogCoverageResponse(
                active_medicines_with_leaflet=with_leaflet,
                active_medicines_with_price=with_price,
                leaflet_percentage=calculate_percentage(with_leaflet, active_medicines),
                price_percentage=calculate_percentage(with_price, active_medicines),
            ),
            latest_imports=[CatalogImportResponse.model_validate(item) for item in latest_imports],
            is_importing=any(item.status == CatalogImportStatus.RUNNING for item in latest_imports),
        )
