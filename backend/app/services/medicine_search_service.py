import re
from dataclasses import replace

from sqlalchemy.orm import Session

from app.core.text_normalization import normalize_search_text, split_search_terms
from app.exceptions.domain_exceptions import MedicineNotFoundError, SearchCriteriaRequiredError
from app.models.catalog.medicine import Medicine
from app.repositories.medicine_search_repository import MedicineSearchCriteria, MedicineSearchRepository
from app.schemas.medicine_schema import (
    LeafletResponse,
    MedicineDetailResponse,
    MedicineSearchResponse,
    MedicineSummaryResponse,
    PresentationResponse,
    TherapeuticClassResponse,
)

MINIMUM_DIGITS_FOR_CODE_SEARCH = 4


def extract_code_digits(query: str) -> str | None:
    compact = re.sub(r"[\s.\-/]", "", query)
    return compact if compact.isdigit() and len(compact) >= MINIMUM_DIGITS_FOR_CODE_SEARCH else None


def sort_tax_rate_labels(labels: set[str]) -> list[str]:
    def sort_key(label: str) -> tuple[float, bool]:
        rate = float(label.split("%")[0].replace(",", "."))
        return rate, "ALC" in label

    return sorted(labels, key=sort_key)


class MedicineSearchService:
    def __init__(self, catalog_session: Session) -> None:
        self.repository = MedicineSearchRepository(catalog_session)

    def search(
        self,
        query: str | None,
        therapeutic_class: str | None,
        include_inactive: bool,
        page: int,
        page_size: int,
    ) -> MedicineSearchResponse:
        normalized_query = normalize_search_text(query or "")
        if not normalized_query and not therapeutic_class:
            raise SearchCriteriaRequiredError()
        criteria = MedicineSearchCriteria(
            normalized_query=normalized_query,
            terms=split_search_terms(normalized_query),
            digits=extract_code_digits(normalized_query),
            therapeutic_class=therapeutic_class,
            include_inactive=include_inactive,
            limit=page_size,
            offset=(page - 1) * page_size,
        )
        rows, total = self.repository.search(criteria)
        if total == 0 and criteria.terms and not criteria.digits:
            criteria = replace(criteria, approximate=True)
            rows, total = self.repository.search(criteria)
        items = [
            MedicineSummaryResponse(**self.summarize(row.medicine), has_leaflet=row.has_leaflet) for row in rows
        ]
        return MedicineSearchResponse(
            items=items, total=total, page=page, page_size=page_size, approximate=criteria.approximate
        )

    def summarize(self, medicine: Medicine) -> dict:
        return {
            "registration_number": medicine.registration_number,
            "product_name": medicine.product_name,
            "active_ingredient": medicine.active_ingredient,
            "therapeutic_class": medicine.therapeutic_class,
            "regulatory_category": medicine.regulatory_category,
            "holder_name": medicine.holder_name,
            "is_active": medicine.is_active,
        }

    def find_medicine(self, registration_number: str) -> Medicine:
        medicine = self.repository.find_by_registration(registration_number)
        if medicine is None:
            raise MedicineNotFoundError()
        return medicine

    def build_detail(self, medicine: Medicine) -> MedicineDetailResponse:
        leaflet = self.repository.find_leaflet(medicine.registration_number)
        presentations = self.repository.list_presentations(medicine.registration_number)
        tax_rates = {label for presentation in presentations for label in presentation.consumer_prices}
        return MedicineDetailResponse(
            **self.summarize(medicine),
            holder_cnpj=medicine.holder_cnpj,
            process_number=medicine.process_number,
            registration_expires_on=medicine.registration_expires_on,
            leaflet=LeafletResponse.model_validate(leaflet) if leaflet else None,
            presentations=[PresentationResponse.model_validate(item) for item in presentations],
            consumer_price_tax_rates=sort_tax_rate_labels(tax_rates),
        )

    def list_therapeutic_classes(self) -> list[TherapeuticClassResponse]:
        return [
            TherapeuticClassResponse(name=name, medicines_count=count)
            for name, count in self.repository.list_therapeutic_classes()
        ]
