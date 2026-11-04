from sqlalchemy import delete, insert, select
from sqlalchemy.orm import Session

from app.core.catalog_database import CatalogBase
from app.models.catalog.leaflet_document import LeafletDocument, LeafletDocumentSource, LeafletSection

INSERT_BATCH_SIZE = 2000


def insert_in_batches(session: Session, model: type[CatalogBase], records: list[dict]) -> None:
    for start in range(0, len(records), INSERT_BATCH_SIZE):
        session.execute(insert(model), records[start:start + INSERT_BATCH_SIZE])


def replace_catalog_rows(session: Session, model: type[CatalogBase], records: list[dict]) -> int:
    session.execute(delete(model))
    insert_in_batches(session, model, records)
    return len(records)


def find_uploaded_leaflet_registrations(session: Session) -> set[str]:
    statement = select(LeafletDocument.registration_number).where(
        LeafletDocument.source == LeafletDocumentSource.PDF_UPLOAD
    )
    return set(session.scalars(statement))


def replace_dataset_leaflet_documents(session: Session, records: list[dict]) -> int:
    uploaded_registrations = find_uploaded_leaflet_registrations(session)
    session.execute(delete(LeafletDocument).where(LeafletDocument.source == LeafletDocumentSource.CHATBULARIO))
    dataset_records = [record for record in records if record["registration_number"] not in uploaded_registrations]
    documents = [
        {
            "registration_number": record["registration_number"],
            "product_name": record["product_name"],
            "expedient_number": record["expedient_number"],
            "source": LeafletDocumentSource.CHATBULARIO,
        }
        for record in dataset_records
    ]
    document_ids = {}
    for start in range(0, len(documents), INSERT_BATCH_SIZE):
        inserted = session.execute(
            insert(LeafletDocument).returning(LeafletDocument.id, LeafletDocument.registration_number),
            documents[start:start + INSERT_BATCH_SIZE],
        )
        document_ids.update({registration: document_id for document_id, registration in inserted})
    sections = [
        {"document_id": document_ids[record["registration_number"]], **section}
        for record in dataset_records
        for section in record["sections"]
    ]
    insert_in_batches(session, LeafletSection, sections)
    return len(documents)
