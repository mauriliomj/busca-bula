import psycopg
import pytest

from app.core.settings import get_settings
from app.core.tenant_credentials import (
    build_tenant_database_name,
    build_tenant_role_name,
    derive_tenant_password,
)
from app.services import tenant_provisioning_service
from tests.conftest import (
    PLATFORM_ADMIN_EMAIL,
    PLATFORM_ADMIN_PASSWORD,
    build_member_payload,
    organization_headers,
)


def connect_as_tenant(role_slug: str, database_slug: str) -> psycopg.Connection:
    settings = get_settings()
    return psycopg.connect(
        host=settings.database_host,
        port=settings.database_port,
        user=build_tenant_role_name(role_slug),
        password=derive_tenant_password(role_slug),
        dbname=build_tenant_database_name(database_slug),
    )


def test_platform_admin_login_rejects_wrong_password(client, platform_admin_headers):
    response = client.post(
        "/api/platform/auth/login",
        json={"email": PLATFORM_ADMIN_EMAIL, "password": "senha-errada"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "E-mail ou senha inválidos."


def test_platform_admin_login_returns_platform_role(client, platform_admin_headers):
    response = client.post(
        "/api/platform/auth/login",
        json={"email": PLATFORM_ADMIN_EMAIL, "password": PLATFORM_ADMIN_PASSWORD},
    )

    assert response.status_code == 200
    assert response.json()["role"] == "platform_admin"


def test_provisioning_creates_dedicated_database_and_role(create_organization, database_administrator):
    organization = create_organization("farmaciax")

    assert organization["status"] == "active"
    assert database_administrator.database_exists(build_tenant_database_name("farmaciax"))
    assert database_administrator.role_exists(build_tenant_role_name("farmaciax"))


def test_tenant_role_cannot_connect_to_another_tenant_database(create_organization):
    create_organization("farmaciax")
    create_organization("farmaciay")

    with connect_as_tenant("farmaciax", "farmaciax") as connection:
        assert connection.execute("SELECT count(*) FROM users").fetchone()[0] == 1

    with pytest.raises(psycopg.OperationalError):
        connect_as_tenant("farmaciax", "farmaciay")


def test_slug_already_in_use_is_rejected(client, platform_admin_headers, create_organization):
    create_organization("farmaciax")

    response = client.post(
        "/api/platform/organizations",
        headers=platform_admin_headers,
        json={
            "name": "Outra Farmácia",
            "slug": "farmaciax",
            "admin_name": "Outro Admin",
            "admin_email": "outro@farmacia.com.br",
            "admin_password": "senha-org-123",
        },
    )

    assert response.status_code == 409


@pytest.mark.parametrize("slug", ["admin", "Farmacia", "farmacia_x", "ab", "-farmacia"])
def test_invalid_or_reserved_slug_is_rejected(client, platform_admin_headers, slug):
    response = client.post(
        "/api/platform/organizations",
        headers=platform_admin_headers,
        json={
            "name": "Farmácia",
            "slug": slug,
            "admin_name": "Admin",
            "admin_email": "admin@farmacia.com.br",
            "admin_password": "senha-org-123",
        },
    )

    assert response.status_code == 422
    assert "slug" in response.json()["fields"]


def test_failed_provisioning_leaves_no_orphan_database(
    client, platform_admin_headers, database_administrator, monkeypatch
):
    def fail_migration(slug: str) -> None:
        raise RuntimeError("falha simulada")

    monkeypatch.setattr(tenant_provisioning_service, "upgrade_tenant_database", fail_migration)

    with pytest.raises(RuntimeError):
        client.post(
            "/api/platform/organizations",
            headers=platform_admin_headers,
            json={
                "name": "Farmácia Falha",
                "slug": "farmacia-falha",
                "admin_name": "Admin",
                "admin_email": "admin@falha.com.br",
                "admin_password": "senha-org-123",
            },
        )

    assert not database_administrator.database_exists(build_tenant_database_name("farmacia-falha"))
    assert not database_administrator.role_exists(build_tenant_role_name("farmacia-falha"))
    listing = client.get("/api/platform/organizations", headers=platform_admin_headers)
    assert listing.json() == []


def test_organization_routes_require_platform_admin(client, create_organization):
    create_organization("farmaciax")
    client.post("/api/auth/register", headers=organization_headers("farmaciax"), json=build_member_payload())
    member_token = client.post(
        "/api/auth/login",
        headers=organization_headers("farmaciax"),
        json={"email": "maria@email.com", "password": "senha-segura-1"},
    ).json()["access_token"]

    without_token = client.get("/api/platform/organizations")
    with_member_token = client.get(
        "/api/platform/organizations", headers={"Authorization": f"Bearer {member_token}"}
    )

    assert without_token.status_code == 401
    assert with_member_token.status_code == 401


def test_deactivated_organization_is_not_found(client, platform_admin_headers, create_organization):
    organization = create_organization("farmaciax")

    response = client.patch(
        f"/api/platform/organizations/{organization['id']}",
        headers=platform_admin_headers,
        json={"is_active": False},
    )
    current = client.get("/api/organizations/current", headers=organization_headers("farmaciax"))

    assert response.json()["status"] == "inactive"
    assert current.status_code == 404
    assert current.json()["detail"] == "Organização não encontrada."


def test_list_organizations_returns_created_ones(client, platform_admin_headers, create_organization):
    create_organization("farmaciax", "Farmácia X")
    create_organization("farmaciay", "Farmácia Y")

    response = client.get("/api/platform/organizations", headers=platform_admin_headers)

    assert [organization["slug"] for organization in response.json()] == ["farmaciay", "farmaciax"]


def test_active_organization_cannot_be_deleted(client, platform_admin_headers, create_organization):
    organization = create_organization("farmaciax")

    response = client.delete(f"/api/platform/organizations/{organization['id']}", headers=platform_admin_headers)

    assert response.status_code == 409


def test_deleting_inactive_organization_drops_database_and_role(
    client, platform_admin_headers, create_organization, database_administrator
):
    organization = create_organization("farmaciax")
    client.patch(
        f"/api/platform/organizations/{organization['id']}",
        headers=platform_admin_headers,
        json={"is_active": False},
    )

    response = client.delete(f"/api/platform/organizations/{organization['id']}", headers=platform_admin_headers)

    assert response.status_code == 204
    assert not database_administrator.database_exists(build_tenant_database_name("farmaciax"))
    assert not database_administrator.role_exists(build_tenant_role_name("farmaciax"))
    assert client.get("/api/platform/organizations", headers=platform_admin_headers).json() == []
