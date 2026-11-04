from sqlalchemy.engine import URL

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
