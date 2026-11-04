from sqlalchemy import delete, insert
from sqlalchemy.orm import Session

from app.core.catalog_database import CatalogBase

INSERT_BATCH_SIZE = 2000


def replace_catalog_rows(session: Session, model: type[CatalogBase], records: list[dict]) -> int:
    session.execute(delete(model))
    for start in range(0, len(records), INSERT_BATCH_SIZE):
        session.execute(insert(model), records[start:start + INSERT_BATCH_SIZE])
    return len(records)
