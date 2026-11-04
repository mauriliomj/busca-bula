from sqlalchemy.engine import URL

from app.core.catalog_credentials import (
    build_catalog_reader_role_name,
    build_catalog_writer_role_name,
    derive_catalog_role_password,
)
from app.core.settings import get_settings
from app.core.tenant_credentials import (
    build_tenant_database_name,
    build_tenant_role_name,
    derive_tenant_password,
)

DRIVER_NAME = "postgresql+psycopg"


def build_platform_database_url() -> URL:
    settings = get_settings()
    return URL.create(
        DRIVER_NAME,
        username=settings.database_admin_user,
        password=settings.database_admin_password,
        host=settings.database_host,
        port=settings.database_port,
        database=settings.platform_database_name,
    )


def build_tenant_database_url(slug: str) -> URL:
    settings = get_settings()
    return URL.create(
        DRIVER_NAME,
        username=build_tenant_role_name(slug),
        password=derive_tenant_password(slug),
        host=settings.database_host,
        port=settings.database_port,
        database=build_tenant_database_name(slug),
    )


def build_catalog_database_url(role_name: str) -> URL:
    settings = get_settings()
    return URL.create(
        DRIVER_NAME,
        username=role_name,
        password=derive_catalog_role_password(role_name),
        host=settings.database_host,
        port=settings.database_port,
        database=settings.catalog_database_name,
    )


def build_catalog_writer_url() -> URL:
    return build_catalog_database_url(build_catalog_writer_role_name())


def build_catalog_reader_url() -> URL:
    return build_catalog_database_url(build_catalog_reader_role_name())
