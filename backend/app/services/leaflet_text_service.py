from sqlalchemy.orm import Session

from app.core.patient_leaflet_sections import SECTION_TITLES_BY_NUMBER
from app.etl.patient_leaflet_pdf import extract_patient_leaflet_sections
from app.exceptions.domain_exceptions import LeafletTextNotFoundError, MedicineNotFoundError
from app.models.catalog.leaflet_document import LeafletDocument, LeafletDocumentSource, LeafletSection
from app.repositories.leaflet_text_repository import LeafletTextRepository
from app.repositories.medicine_search_repository import MedicineSearchRepository
from app.schemas.leaflet_text_schema import (
    LeafletAttributionResponse,
    LeafletSectionResponse,
    LeafletTextResponse,
    LeafletUploadResponse,
)

CHATBULARIO_ATTRIBUTION = LeafletAttributionResponse(
    text="Texto extraído do dataset ChatBulário (walmeidadf), licença CC BY 4.0, a partir do Bulário Eletrônico da ANVISA.",
    url="https://huggingface.co/datasets/walmeidadf/ChatBulario",
)


class LeafletTextService:
    def __init__(self, catalog_session: Session) -> None:
        self.leaflet_text_repository = LeafletTextRepository(catalog_session)
        self.medicine_repository = MedicineSearchRepository(catalog_session)

    def has_leaflet_text(self, registration_number: str) -> bool:
        return self.leaflet_text_repository.has_document(registration_number)

    def show_leaflet_text(self, registration_number: str) -> LeafletTextResponse:
        document = self.leaflet_text_repository.find_document(registration_number)
        if document is None:
            raise LeafletTextNotFoundError()
        index_entry = self.leaflet_text_repository.find_index_entry(registration_number)
        current_expedient = index_entry.expedient_number if index_entry else None
        sections = self.leaflet_text_repository.list_sections(document.id)
        return LeafletTextResponse(
            registration_number=document.registration_number,
            product_name=document.product_name,
            source=document.source,
            attribution=CHATBULARIO_ATTRIBUTION if document.source == LeafletDocumentSource.CHATBULARIO else None,
            expedient_number=document.expedient_number,
            current_expedient_number=current_expedient,
            is_outdated=bool(current_expedient and document.expedient_number != current_expedient),
            published_at=index_entry.published_at if index_entry else None,
            sections=[
                LeafletSectionResponse(
                    number=section.section_number,
                    title=SECTION_TITLES_BY_NUMBER[section.section_number],
                    content=section.content,
                )
                for section in sections
            ],
        )

    def replace_with_pdf(self, registration_number: str, pdf_content: bytes) -> LeafletUploadResponse:
        medicine = self.medicine_repository.find_by_registration(registration_number)
        if medicine is None:
            raise MedicineNotFoundError()
        extracted_sections = extract_patient_leaflet_sections(pdf_content)
        index_entry = self.leaflet_text_repository.find_index_entry(registration_number)
        document = LeafletDocument(
            registration_number=registration_number,
            product_name=medicine.product_name,
            source=LeafletDocumentSource.PDF_UPLOAD,
            expedient_number=index_entry.expedient_number if index_entry else None,
        )
        sections = [
            LeafletSection(section_number=section.section_number, content=section.content)
            for section in extracted_sections
        ]
        self.leaflet_text_repository.replace_document(document, sections)
        return LeafletUploadResponse(
            registration_number=registration_number,
            product_name=medicine.product_name,
            section_numbers=[section.section_number for section in extracted_sections],
        )
