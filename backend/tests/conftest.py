import os

os.environ["PLATFORM_DATABASE_NAME"] = "test_busca_bula_platform"
os.environ["TENANT_DATABASE_PREFIX"] = "test_tenant_"
os.environ["CATALOG_DATABASE_NAME"] = "test_busca_bula_catalog"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.core.catalog_credentials import build_catalog_reader_role_name, build_catalog_writer_role_name
from app.core.catalog_database import (
    dispose_catalog_engines,
    get_catalog_writer_engine,
    open_catalog_writer_session,
)
from app.core.database_administration import DatabaseAdministrator
from app.core.database_migrations import upgrade_platform_database
from app.core.platform_database import get_platform_engine, open_platform_session
from app.core.settings import get_settings
from app.core.tenant_database import tenant_engine_registry
from app.etl.catalog_loader import replace_catalog_rows
from app.etl.leaflet_index_parser import parse_leaflet_index
from app.etl.medicine_catalog_parser import parse_medicine_catalog
from app.etl.price_table_parser import parse_price_table
from app.main import app
from app.models.catalog.leaflet import Leaflet
from app.models.catalog.medicine import Medicine
from app.models.catalog.medicine_presentation import MedicinePresentation
from app.services.catalog_provisioning_service import CatalogProvisioningService
from app.services.platform_admin_auth_service import PlatformAdminAuthService
from tests.catalog_samples import write_leaflet_index, write_medicine_catalog, write_price_table

PLATFORM_ADMIN_EMAIL = "admin@buscabula.com.br"
PLATFORM_ADMIN_PASSWORD = "senha-admin-123"


def drop_tenant_databases_and_roles(administrator: DatabaseAdministrator) -> None:
    tenant_engine_registry.dispose_all_engines()
    prefix = get_settings().tenant_database_prefix
    for database_name in administrator.list_databases_with_prefix(prefix):
        administrator.drop_database(database_name)
    for role_name in administrator.list_roles_with_prefix(prefix):
        administrator.drop_role(role_name)


@pytest.fixture(scope="session")
def database_administrator() -> DatabaseAdministrator:
    return DatabaseAdministrator()


@pytest.fixture(scope="session", autouse=True)
def platform_database(database_administrator):
    platform_database_name = get_settings().platform_database_name
    drop_tenant_databases_and_roles(database_administrator)
    database_administrator.drop_database(platform_database_name)
    database_administrator.create_database(platform_database_name)
    upgrade_platform_database()
    yield
    drop_tenant_databases_and_roles(database_administrator)
    get_platform_engine().dispose()
    database_administrator.drop_database(platform_database_name)


def drop_catalog_database(administrator: DatabaseAdministrator) -> None:
    dispose_catalog_engines()
    administrator.drop_database(get_settings().catalog_database_name)
    administrator.drop_role(build_catalog_reader_role_name())
    administrator.drop_role(build_catalog_writer_role_name())


@pytest.fixture(scope="session")
def catalog_database(database_administrator):
    drop_catalog_database(database_administrator)
    CatalogProvisioningService(database_administrator).ensure_catalog_database()
    yield
    drop_catalog_database(database_administrator)


@pytest.fixture
def clean_catalog(catalog_database):
    yield
    with get_catalog_writer_engine().begin() as connection:
        connection.execute(
            text(
                "TRUNCATE medicines, leaflets, medicine_presentations, catalog_imports, "
                "leaflet_documents, leaflet_sections RESTART IDENTITY"
            )
        )


INACTIVE_MEDICINE = {
    "registration_number": "155550001",
    "product_name": "DIPIRONA ANTIGA",
    "active_ingredient": "dipirona",
    "therapeutic_class": "ANALGESICOS",
    "regulatory_category": "Similar",
    "holder_cnpj": None,
    "holder_name": "FARMA ANTIGA",
    "process_number": None,
    "is_active": False,
    "registration_expires_on": None,
    "process_finished_on": None,
}


@pytest.fixture
def seeded_catalog(clean_catalog, tmp_path):
    medicines = parse_medicine_catalog(write_medicine_catalog(tmp_path)).records + [INACTIVE_MEDICINE]
    with open_catalog_writer_session() as session:
        replace_catalog_rows(session, Medicine, medicines)
        replace_catalog_rows(session, Leaflet, parse_leaflet_index(write_leaflet_index(tmp_path)).records)
        replace_catalog_rows(session, MedicinePresentation, parse_price_table(write_price_table(tmp_path)).records)
        session.commit()


@pytest.fixture(autouse=True)
def clean_databases(database_administrator):
    yield
    drop_tenant_databases_and_roles(database_administrator)
    with get_platform_engine().begin() as connection:
        connection.execute(text("TRUNCATE organizations, platform_admins RESTART IDENTITY"))


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def platform_admin_headers(client) -> dict[str, str]:
    with open_platform_session() as platform_session:
        PlatformAdminAuthService(platform_session).create_platform_admin(
            "Administrador", PLATFORM_ADMIN_EMAIL, PLATFORM_ADMIN_PASSWORD
        )
    response = client.post(
        "/api/platform/auth/login",
        json={"email": PLATFORM_ADMIN_EMAIL, "password": PLATFORM_ADMIN_PASSWORD},
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
def create_organization(client, platform_admin_headers):
    def create(slug: str, name: str | None = None) -> dict:
        response = client.post(
            "/api/platform/organizations",
            headers=platform_admin_headers,
            json={
                "name": name or f"Organização {slug}",
                "slug": slug,
                "admin_name": "Administrador da Organização",
                "admin_email": f"admin@{slug}.com.br",
                "admin_password": "senha-org-123",
            },
        )
        assert response.status_code == 201, response.text
        return response.json()

    return create


def build_member_payload(email: str = "maria@email.com") -> dict:
    return {
        "name": "Maria Souza",
        "age": 34,
        "gender": "feminino",
        "email": email,
        "phone": "(11) 91234-5678",
        "address": "Rua das Flores, 100",
        "city": "São Paulo",
        "state": "SP",
        "password": "senha-segura-1",
    }


def organization_headers(slug: str, token: str | None = None) -> dict[str, str]:
    headers = {"X-Organization": slug}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def register_and_login(client, slug: str, email: str = "maria@email.com") -> str:
    client.post("/api/auth/register", headers=organization_headers(slug), json=build_member_payload(email))
    return login(client, slug, email, "senha-segura-1")


def login(client, slug: str, email: str, password: str) -> str | None:
    response = client.post(
        "/api/auth/login",
        headers=organization_headers(slug),
        json={"email": email, "password": password},
    )
    return response.json().get("access_token")


def login_as_organization_admin(client, slug: str) -> str:
    return login(client, slug, f"admin@{slug}.com.br", "senha-org-123")
