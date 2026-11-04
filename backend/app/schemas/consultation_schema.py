from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ConsultationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    registration_number: str
    product_name: str
    active_ingredient: str | None
    consulted_at: datetime


class ConsultationHistoryResponse(BaseModel):
    enabled: bool
    consented_at: datetime | None
    items: list[ConsultationResponse]


class ConsultationConsentRequest(BaseModel):
    enabled: bool
