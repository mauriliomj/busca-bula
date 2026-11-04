from alembic import context
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

from app.core.catalog_database import CatalogBase
from app.core.database_urls import build_catalog_writer_url
from app.models.catalog import catalog_import, leaflet, leaflet_document, medicine, medicine_presentation

config = context.config


def resolve_database_url():
    return config.attributes.get("database_url") or build_catalog_writer_url()


def run_migrations() -> None:
    engine = create_engine(resolve_database_url(), poolclass=NullPool)
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=CatalogBase.metadata)
        with context.begin_transaction():
            context.run_migrations()


run_migrations()
