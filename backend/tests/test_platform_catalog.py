import psycopg
import pytest

from app.core.catalog_credentials import build_catalog_reader_role_name, derive_catalog_role_password
from app.core.settings import get_settings
from app.core.tenant_credentials import build_tenant_role_name, derive_tenant_password
from app.etl.catalog_sources import CatalogSource
from app.services import catalog_import_service
from tests.catalog_samples import write_leaflet_index, write_medicine_catalog, write_price_table

pytestmark = pytest.mark.usefixtures("clean_catalog")


@pytest.fixture
def sample_source_files(tmp_path, monkeypatch):
    files = {
        CatalogSource.MEDICINES: write_medicine_catalog(tmp_path),
        CatalogSource.LEAFLETS: write_leaflet_index(tmp_path),
        CatalogSource.PRICES: write_price_table(tmp_path),
    }
    monkeypatch.setattr(
        catalog_import_service,
        "download_catalog_source_file",
        lambda definition: files[definition.source],
    )
    return files


def connect_to_catalog(user: str, password: str) -> psycopg.Connection:
    settings = get_settings()
    return psycopg.connect(
        host=settings.database_host,
        port=settings.database_port,
        user=user,
        password=password,
        dbname=settings.catalog_database_name,
    )


def test_catalog_summary_starts_empty(client, platform_admin_headers):
    response = client.get("/api/platform/catalog", headers=platform_admin_headers)

    body = response.json()
    assert response.status_code == 200
    assert body["medicines_total"] == 0
    assert body["latest_imports"] == []
    assert body["is_importing"] is False


def test_catalog_import_loads_all_sources(client, platform_admin_headers, sample_source_files):
    started = client.post("/api/platform/catalog/imports", headers=platform_admin_headers)
    summary = client.get("/api/platform/catalog", headers=platform_admin_headers).json()

    assert started.status_code == 202
    assert sorted(item["source"] for item in started.json()) == ["leaflets", "medicines", "prices"]
    assert summary["medicines_total"] == 2
    assert summary["active_medicines_total"] == 2
    assert summary["leaflets_total"] == 1
    assert summary["presentations_total"] == 2
    assert summary["coverage"]["leaflet_percentage"] == 50.0
    assert summary["coverage"]["price_percentage"] == 50.0
    assert {item["status"] for item in summary["latest_imports"]} == {"succeeded"}
    assert summary["is_importing"] is False


def test_failed_source_is_recorded_without_blocking_others(
    client, platform_admin_headers, sample_source_files, monkeypatch
):
    def download_or_fail(definition):
        if definition.source == CatalogSource.PRICES:
            raise ConnectionError("servidor indisponível")
        return sample_source_files[definition.source]

    monkeypatch.setattr(catalog_import_service, "download_catalog_source_file", download_or_fail)

    client.post("/api/platform/catalog/imports", headers=platform_admin_headers)
    summary = client.get("/api/platform/catalog", headers=platform_admin_headers).json()

    statuses = {item["source"]: item for item in summary["latest_imports"]}
    assert statuses["medicines"]["status"] == "succeeded"
    assert statuses["prices"]["status"] == "failed"
    assert "servidor indisponível" in statuses["prices"]["error_message"]
    assert summary["presentations_total"] == 0


def test_reimport_replaces_previous_rows(client, platform_admin_headers, sample_source_files):
    client.post("/api/platform/catalog/imports", headers=platform_admin_headers)
    client.post("/api/platform/catalog/imports", headers=platform_admin_headers)

    summary = client.get("/api/platform/catalog", headers=platform_admin_headers).json()

    assert summary["medicines_total"] == 2
    assert summary["presentations_total"] == 2


def test_concurrent_import_is_rejected(client, platform_admin_headers, sample_source_files):
    from app.core.catalog_database import open_catalog_writer_session
    from app.services.catalog_import_service import CatalogImportService

    with open_catalog_writer_session() as session:
        CatalogImportService(session).start_imports([CatalogSource.MEDICINES])

    response = client.post("/api/platform/catalog/imports", headers=platform_admin_headers)

    assert response.status_code == 409


def test_catalog_routes_require_platform_admin(client, create_organization):
    create_organization("farmaciax")

    assert client.get("/api/platform/catalog").status_code == 401
    assert client.post("/api/platform/catalog/imports").status_code == 401


def test_catalog_reader_role_is_read_only():
    reader_role = build_catalog_reader_role_name()

    with connect_to_catalog(reader_role, derive_catalog_role_password(reader_role)) as connection:
        assert connection.execute("SELECT count(*) FROM medicines").fetchone()[0] == 0
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            connection.execute("DELETE FROM medicines")


def test_tenant_role_cannot_connect_to_catalog(create_organization):
    create_organization("farmaciax")

    with pytest.raises(psycopg.OperationalError):
        connect_to_catalog(build_tenant_role_name("farmaciax"), derive_tenant_password("farmaciax"))
