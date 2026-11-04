from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class MedicineSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    registration_number: str
    product_name: str
    active_ingredient: str | None
    therapeutic_class: str | None
    regulatory_category: str | None
    holder_name: str | None
    is_active: bool
    has_leaflet: bool


class MedicineSearchResponse(BaseModel):
    items: list[MedicineSummaryResponse]
    total: int
    page: int
    page_size: int
    approximate: bool


class LeafletResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    bulario_product_id: str
    company_name: str | None
    expedient_number: str | None
    published_at: datetime | None


class PresentationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ggrem_code: str
    presentation: str | None
    ean_codes: list[str]
    product_type: str | None
    prescription_label: str | None
    hospital_restricted: bool | None
    marketed: bool | None
    consumer_prices: dict[str, float]


class MedicineDetailResponse(BaseModel):
    registration_number: str
    product_name: str
    active_ingredient: str | None
    therapeutic_class: str | None
    regulatory_category: str | None
    holder_name: str | None
    holder_cnpj: str | None
    process_number: str | None
    is_active: bool
    registration_expires_on: date | None
    leaflet: LeafletResponse | None
    leaflet_text_available: bool
    presentations: list[PresentationResponse]
    consumer_price_tax_rates: list[str]


class TherapeuticClassResponse(BaseModel):
    name: str
    medicines_count: int
