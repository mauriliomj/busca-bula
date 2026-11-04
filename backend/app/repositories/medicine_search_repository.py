from dataclasses import dataclass

from sqlalchemy import case, exists, func, or_, select
from sqlalchemy.orm import Session

from app.models.catalog.leaflet import Leaflet
from app.models.catalog.medicine import Medicine
from app.models.catalog.medicine_presentation import MedicinePresentation

EAN_LENGTH = 13
REGISTRATION_LENGTH = 9


@dataclass(frozen=True)
class MedicineSearchCriteria:
    normalized_query: str
    terms: list[str]
    digits: str | None
    therapeutic_class: str | None
    include_inactive: bool
    limit: int
    offset: int
    approximate: bool = False


@dataclass(frozen=True)
class MedicineSearchRow:
    medicine: Medicine
    has_leaflet: bool


def escape_like(term: str) -> str:
    return term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def contains_pattern(term: str) -> str:
    return f"%{escape_like(term)}%"


def has_leaflet_expression():
    return exists().where(Leaflet.registration_number == Medicine.registration_number)


class MedicineSearchRepository:
    def __init__(self, catalog_session: Session) -> None:
        self.session = catalog_session

    def build_digit_filter(self, digits: str):
        registration_prefix = digits[:REGISTRATION_LENGTH]
        registration_match = (
            Medicine.registration_number == registration_prefix
            if len(digits) >= REGISTRATION_LENGTH
            else Medicine.registration_number.startswith(digits)
        )
        if len(digits) != EAN_LENGTH:
            return registration_match
        registrations_with_barcode = select(MedicinePresentation.medicine_registration_number).where(
            MedicinePresentation.ean_codes.contains([digits])
        )
        return or_(registration_match, Medicine.registration_number.in_(registrations_with_barcode))

    def build_filters(self, criteria: MedicineSearchCriteria) -> list:
        filters = []
        if not criteria.include_inactive and not criteria.digits:
            filters.append(Medicine.is_active)
        if criteria.therapeutic_class:
            filters.append(Medicine.therapeutic_class == criteria.therapeutic_class)
        if criteria.digits:
            filters.append(self.build_digit_filter(criteria.digits))
        elif criteria.approximate:
            filters.append(Medicine.search_name.op("%")(criteria.normalized_query))
        else:
            filters.extend(
                Medicine.search_text.like(contains_pattern(term), escape="\\") for term in criteria.terms
            )
        return filters

    def build_ordering(self, criteria: MedicineSearchCriteria) -> list:
        if not criteria.normalized_query or criteria.digits:
            return [Medicine.is_active.desc(), Medicine.product_name, Medicine.registration_number]
        query = criteria.normalized_query
        match_quality = case(
            (Medicine.search_name == query, 0),
            (Medicine.search_name.like(f"{escape_like(query)}%", escape="\\"), 1),
            else_=2,
        )
        return [
            match_quality,
            Medicine.is_active.desc(),
            func.similarity(Medicine.search_name, query).desc(),
            Medicine.product_name,
            Medicine.registration_number,
        ]

    def search(self, criteria: MedicineSearchCriteria) -> tuple[list[MedicineSearchRow], int]:
        filters = self.build_filters(criteria)
        total = self.session.scalar(select(func.count()).select_from(Medicine).where(*filters)) or 0
        statement = (
            select(Medicine, has_leaflet_expression().label("has_leaflet"))
            .where(*filters)
            .order_by(*self.build_ordering(criteria))
            .limit(criteria.limit)
            .offset(criteria.offset)
        )
        rows = [MedicineSearchRow(medicine, has_leaflet) for medicine, has_leaflet in self.session.execute(statement)]
        return rows, total

    def find_by_registration(self, registration_number: str) -> Medicine | None:
        return self.session.scalar(select(Medicine).where(Medicine.registration_number == registration_number))

    def find_leaflet(self, registration_number: str) -> Leaflet | None:
        return self.session.scalar(select(Leaflet).where(Leaflet.registration_number == registration_number))

    def list_presentations(self, registration_number: str) -> list[MedicinePresentation]:
        statement = (
            select(MedicinePresentation)
            .where(MedicinePresentation.medicine_registration_number == registration_number)
            .order_by(MedicinePresentation.product_name, MedicinePresentation.presentation)
        )
        return list(self.session.scalars(statement))

    def list_therapeutic_classes(self) -> list[tuple[str, int]]:
        statement = (
            select(Medicine.therapeutic_class, func.count())
            .where(Medicine.is_active, Medicine.therapeutic_class.is_not(None))
            .group_by(Medicine.therapeutic_class)
            .order_by(Medicine.therapeutic_class)
        )
        return [(name, count) for name, count in self.session.execute(statement)]
