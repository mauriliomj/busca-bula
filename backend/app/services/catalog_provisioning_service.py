from sqlalchemy import text

from app.core.catalog_credentials import (
    build_catalog_reader_role_name,
    build_catalog_writer_role_name,
    derive_catalog_role_password,
)
from app.core.catalog_database import get_catalog_writer_engine
from app.core.database_administration import DatabaseAdministrator
from app.core.database_migrations import upgrade_catalog_database
from app.core.settings import get_settings

CATALOG_EXTENSIONS = ("vector", "pg_trgm")


class CatalogProvisioningService:
    def __init__(self, database_administrator: DatabaseAdministrator | None = None) -> None:
        self.database_administrator = database_administrator or DatabaseAdministrator()

    def ensure_catalog_database(self) -> None:
        database_name = get_settings().catalog_database_name
        writer_role = build_catalog_writer_role_name()
        reader_role = build_catalog_reader_role_name()
        self.ensure_role(writer_role)
        self.ensure_role(reader_role)
        if not self.database_administrator.database_exists(database_name):
            self.database_administrator.create_database(database_name, owner=writer_role)
            self.database_administrator.revoke_public_access(database_name)
        for extension_name in CATALOG_EXTENSIONS:
            self.database_administrator.create_extension(database_name, extension_name)
        upgrade_catalog_database()
        self.grant_read_only_access(database_name, writer_role, reader_role)

    def ensure_role(self, role_name: str) -> None:
        if not self.database_administrator.role_exists(role_name):
            self.database_administrator.create_role(role_name, derive_catalog_role_password(role_name))

    def grant_read_only_access(self, database_name: str, writer_role: str, reader_role: str) -> None:
        with get_catalog_writer_engine().begin() as connection:
            connection.execute(text(f'GRANT CONNECT ON DATABASE "{database_name}" TO "{reader_role}"'))
            connection.execute(text(f'GRANT USAGE ON SCHEMA public TO "{reader_role}"'))
            connection.execute(text(f'GRANT SELECT ON ALL TABLES IN SCHEMA public TO "{reader_role}"'))
            connection.execute(
                text(
                    f'ALTER DEFAULT PRIVILEGES FOR ROLE "{writer_role}" IN SCHEMA public '
                    f'GRANT SELECT ON TABLES TO "{reader_role}"'
                )
            )
