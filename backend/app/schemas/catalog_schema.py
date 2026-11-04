from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CatalogImportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source: str
    status: str
    started_at: datetime
    finished_at: datetime | None
    rows_read: int | None
    rows_loaded: int | None
    error_message: str | None


class CatalogCoverageResponse(BaseModel):
    active_medicines_with_leaflet: int
    active_medicines_with_price: int
    leaflet_percentage: float
    price_percentage: float


class CatalogSummaryResponse(BaseModel):
    medicines_total: int
    active_medicines_total: int
    leaflets_total: int
    presentations_total: int
    coverage: CatalogCoverageResponse
    latest_imports: list[CatalogImportResponse]
    is_importing: bool
