import base64

import pytest

from tests.conftest import login_as_organization_admin, organization_headers, register_and_login

PNG_LOGO = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
)
SVG_LOGO = b'<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10"><rect width="10" height="10"/></svg>'


def admin_headers(client, slug: str) -> dict[str, str]:
    return organization_headers(slug, login_as_organization_admin(client, slug))


def upload_logo(client, headers: dict[str, str], content: bytes, content_type: str, path: str = "/api/organization/branding/logo"):
    return client.put(path, headers=headers | {"Content-Type": content_type}, content=content)


def test_current_organization_starts_without_branding(client, create_organization):
    create_organization("farmaciax", "Farmácia X")

    response = client.get("/api/organizations/current", headers=organization_headers("farmaciax"))

    assert response.json() == {
        "name": "Farmácia X",
        "slug": "farmaciax",
        "primary_color": None,
        "secondary_color": None,
        "logo_url": None,
    }


def test_organization_admin_updates_colors(client, create_organization):
    create_organization("farmaciax")

    response = client.put(
        "/api/organization/branding",
        headers=admin_headers(client, "farmaciax"),
        json={"primary_color": "#E30613", "secondary_color": "#1A1A1A"},
    )
    current = client.get("/api/organizations/current", headers=organization_headers("farmaciax")).json()

    assert response.status_code == 200
    assert current["primary_color"] == "#e30613"
    assert current["secondary_color"] == "#1a1a1a"


def test_invalid_color_is_rejected(client, create_organization):
    create_organization("farmaciax")

    response = client.put(
        "/api/organization/branding",
        headers=admin_headers(client, "farmaciax"),
        json={"primary_color": "vermelho"},
    )

    assert response.status_code == 422
    assert response.json()["fields"] == ["primary_color"]


def test_member_cannot_change_branding(client, create_organization):
    create_organization("farmaciax")
    member_token = register_and_login(client, "farmaciax")

    response = client.put(
        "/api/organization/branding",
        headers=organization_headers("farmaciax", member_token),
        json={"primary_color": "#000000"},
    )

    assert response.status_code == 403


@pytest.mark.parametrize(
    ("content", "content_type"),
    [(PNG_LOGO, "image/png"), (SVG_LOGO, "image/svg+xml")],
)
def test_uploaded_logo_is_served_publicly(client, create_organization, content, content_type):
    create_organization("farmaciax")

    response = upload_logo(client, admin_headers(client, "farmaciax"), content, content_type)
    logo_url = client.get("/api/organizations/current", headers=organization_headers("farmaciax")).json()["logo_url"]
    logo = client.get(logo_url)

    assert response.status_code == 200
    assert logo_url.startswith("/api/organizations/farmaciax/logo?v=")
    assert logo.content == content
    assert logo.headers["content-type"].startswith(content_type)
    assert "default-src 'none'" in logo.headers["content-security-policy"]


def test_logo_with_unsupported_type_is_rejected(client, create_organization):
    create_organization("farmaciax")

    response = upload_logo(client, admin_headers(client, "farmaciax"), b"texto", "text/plain")

    assert response.status_code == 415


def test_logo_with_mismatched_content_is_rejected(client, create_organization):
    create_organization("farmaciax")

    response = upload_logo(client, admin_headers(client, "farmaciax"), b"nao sou png", "image/png")

    assert response.status_code == 415


def test_logo_above_size_limit_is_rejected(client, create_organization):
    create_organization("farmaciax")
    oversized_logo = PNG_LOGO + b"0" * (512 * 1024)

    response = upload_logo(client, admin_headers(client, "farmaciax"), oversized_logo, "image/png")

    assert response.status_code == 413


def test_removed_logo_is_no_longer_served(client, create_organization):
    create_organization("farmaciax")
    headers = admin_headers(client, "farmaciax")
    upload_logo(client, headers, PNG_LOGO, "image/png")

    response = client.delete("/api/organization/branding/logo", headers=headers)
    logo = client.get("/api/organizations/farmaciax/logo")

    assert response.json()["logo_url"] is None
    assert logo.status_code == 404


def test_branding_is_isolated_between_organizations(client, create_organization):
    create_organization("farmaciax")
    create_organization("farmaciay")
    client.put(
        "/api/organization/branding",
        headers=admin_headers(client, "farmaciax"),
        json={"primary_color": "#e30613"},
    )
    upload_logo(client, admin_headers(client, "farmaciax"), PNG_LOGO, "image/png")

    other = client.get("/api/organizations/current", headers=organization_headers("farmaciay")).json()

    assert other["primary_color"] is None
    assert other["logo_url"] is None
    assert client.get("/api/organizations/farmaciay/logo").status_code == 404


def test_platform_admin_manages_organization_branding(client, platform_admin_headers, create_organization):
    organization = create_organization("farmaciax")
    branding_path = f"/api/platform/organizations/{organization['id']}/branding"

    colors = client.put(branding_path, headers=platform_admin_headers, json={"primary_color": "#123456"})
    logo = upload_logo(client, platform_admin_headers, PNG_LOGO, "image/png", f"{branding_path}/logo")
    current = client.get(branding_path, headers=platform_admin_headers).json()

    assert colors.status_code == 200
    assert logo.status_code == 200
    assert current["primary_color"] == "#123456"
    assert current["logo_url"] is not None


def test_platform_branding_routes_require_platform_admin(client, create_organization):
    organization = create_organization("farmaciax")

    response = client.get(f"/api/platform/organizations/{organization['id']}/branding")

    assert response.status_code == 401


def test_logo_of_inactive_organization_is_not_served(client, platform_admin_headers, create_organization):
    organization = create_organization("farmaciax")
    upload_logo(client, admin_headers(client, "farmaciax"), PNG_LOGO, "image/png")
    client.patch(
        f"/api/platform/organizations/{organization['id']}",
        headers=platform_admin_headers,
        json={"is_active": False},
    )

    response = client.get("/api/organizations/farmaciax/logo")

    assert response.status_code == 404
