from sqlalchemy import delete, exists, select
from sqlalchemy.orm import Session

from app.models.catalog.leaflet import Leaflet
from app.models.catalog.leaflet_document import LeafletDocument, LeafletSection


class LeafletTextRepository:
    def __init__(self, catalog_session: Session) -> None:
        self.session = catalog_session

    def find_document(self, registration_number: str) -> LeafletDocument | None:
        return self.session.scalar(
            select(LeafletDocument).where(LeafletDocument.registration_number == registration_number)
        )

    def list_sections(self, document_id: int) -> list[LeafletSection]:
        statement = (
            select(LeafletSection)
            .where(LeafletSection.document_id == document_id)
            .order_by(LeafletSection.section_number)
        )
        return list(self.session.scalars(statement))

    def find_index_entry(self, registration_number: str) -> Leaflet | None:
        return self.session.scalar(select(Leaflet).where(Leaflet.registration_number == registration_number))

    def has_document(self, registration_number: str) -> bool:
        return bool(
            self.session.scalar(
                select(exists().where(LeafletDocument.registration_number == registration_number))
            )
        )

    def replace_document(self, document: LeafletDocument, sections: list[LeafletSection]) -> LeafletDocument:
        self.session.execute(
            delete(LeafletDocument).where(LeafletDocument.registration_number == document.registration_number)
        )
        self.session.add(document)
        self.session.flush()
        for section in sections:
            section.document_id = document.id
        self.session.add_all(sections)
        self.session.commit()
        return document
