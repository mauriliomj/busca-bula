import psycopg
import pytest

from app.core.settings import get_settings
from app.core.tenant_credentials import build_tenant_database_name, build_tenant_role_name, derive_tenant_password
from tests.conftest import organization_headers, register_and_login

pytestmark = pytest.mark.usefixtures("seeded_catalog")

HISTORY_PATH = "/api/users/me/consultations"


@pytest.fixture
def member_headers(client, create_organization):
    create_organization("farmaciax")
    return organization_headers("farmaciax", register_and_login(client, "farmaciax"))


def enable_history(client, headers) -> None:
    client.put(f"{HISTORY_PATH}/consent", headers=headers, json={"enabled": True})


def view_medicine(client, headers, registration_number: str = "100430001") -> None:
    client.get(f"/api/medicines/{registration_number}", headers=headers)


def count_consultations_in_tenant_database(slug: str) -> int:
    settings = get_settings()
    with psycopg.connect(
        host=settings.database_host,
        port=settings.database_port,
        user=build_tenant_role_name(slug),
        password=derive_tenant_password(slug),
        dbname=build_tenant_database_name(slug),
    ) as connection:
        return connection.execute("SELECT count(*) FROM consultations").fetchone()[0]


def test_history_is_disabled_by_default_and_records_nothing(client, member_headers):
    view_medicine(client, member_headers)

    history = client.get(HISTORY_PATH, headers=member_headers).json()

    assert history == {"enabled": False, "consented_at": None, "items": []}
    assert count_consultations_in_tenant_database("farmaciax") == 0


def test_history_records_consultations_after_consent(client, member_headers):
    enabled = client.put(f"{HISTORY_PATH}/consent", headers=member_headers, json={"enabled": True}).json()
    view_medicine(client, member_headers, "100430001")
    view_medicine(client, member_headers, "012345678")
    view_medicine(client, member_headers, "100430001")

    history = client.get(HISTORY_PATH, headers=member_headers).json()

    assert enabled["enabled"] is True
    assert enabled["consented_at"] is not None
    assert [item["product_name"] for item in history["items"]] == ["DIPIRONA MONOIDRATADA", "LOSARTANA"]


def test_revoking_consent_deletes_history(client, member_headers):
    enable_history(client, member_headers)
    view_medicine(client, member_headers)

    revoked = client.put(f"{HISTORY_PATH}/consent", headers=member_headers, json={"enabled": False}).json()

    assert revoked == {"enabled": False, "consented_at": None, "items": []}
    assert count_consultations_in_tenant_database("farmaciax") == 0


def test_member_removes_single_consultation_and_clears_history(client, member_headers):
    enable_history(client, member_headers)
    view_medicine(client, member_headers, "100430001")
    view_medicine(client, member_headers, "012345678")
    first_id = client.get(HISTORY_PATH, headers=member_headers).json()["items"][0]["id"]

    removed = client.delete(f"{HISTORY_PATH}/{first_id}", headers=member_headers)
    remaining = client.get(HISTORY_PATH, headers=member_headers).json()["items"]
    cleared = client.delete(HISTORY_PATH, headers=member_headers)

    assert removed.status_code == 204
    assert len(remaining) == 1
    assert cleared.status_code == 204
    assert client.get(HISTORY_PATH, headers=member_headers).json()["items"] == []


def test_member_cannot_remove_consultation_of_another_member(client, member_headers):
    enable_history(client, member_headers)
    view_medicine(client, member_headers)
    consultation_id = client.get(HISTORY_PATH, headers=member_headers).json()["items"][0]["id"]
    other_headers = organization_headers("farmaciax", register_and_login(client, "farmaciax", "joao@email.com"))

    response = client.delete(f"{HISTORY_PATH}/{consultation_id}", headers=other_headers)

    assert response.status_code == 404
    assert len(client.get(HISTORY_PATH, headers=member_headers).json()["items"]) == 1


def test_account_deletion_removes_history(client, member_headers):
    enable_history(client, member_headers)
    view_medicine(client, member_headers)

    client.request("DELETE", "/api/users/me", headers=member_headers, json={"password": "senha-segura-1"})

    assert count_consultations_in_tenant_database("farmaciax") == 0
