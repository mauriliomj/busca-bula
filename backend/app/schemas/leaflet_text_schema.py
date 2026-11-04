from datetime import datetime

from pydantic import BaseModel


class LeafletSectionResponse(BaseModel):
    number: int
    title: str
    content: str


class LeafletAttributionResponse(BaseModel):
    text: str
    url: str


class LeafletTextResponse(BaseModel):
    registration_number: str
    product_name: str
    source: str
    attribution: LeafletAttributionResponse | None
    expedient_number: str | None
    current_expedient_number: str | None
    is_outdated: bool
    published_at: datetime | None
    sections: list[LeafletSectionResponse]


class LeafletUploadResponse(BaseModel):
    registration_number: str
    product_name: str
    section_numbers: list[int]
