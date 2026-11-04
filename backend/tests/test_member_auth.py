from tests.conftest import build_member_payload, organization_headers


def register_and_login(client, slug: str, email: str = "maria@email.com") -> str:
    client.post("/api/auth/register", headers=organization_headers(slug), json=build_member_payload(email))
    response = client.post(
        "/api/auth/login",
        headers=organization_headers(slug),
        json={"email": email, "password": "senha-segura-1"},
    )
    return response.json()["access_token"]


def test_health_check(client):
    assert client.get("/api/health").json() == {"status": "ok"}


def test_current_organization_returns_public_data(client, create_organization):
    create_organization("farmaciax", "Farmácia X")

    response = client.get("/api/organizations/current", headers=organization_headers("farmaciax"))

    assert response.json() == {"name": "Farmácia X", "slug": "farmaciax"}


def test_unknown_organization_is_not_found(client):
    response = client.get("/api/organizations/current", headers=organization_headers("inexistente"))

    assert response.status_code == 404


def test_tenant_routes_require_organization_header(client):
    response = client.post("/api/auth/register", json=build_member_payload())

    assert response.status_code == 400
    assert response.json()["detail"] == "Acesse pelo endereço da sua organização."


def test_member_registration_returns_profile_without_password(client, create_organization):
    create_organization("farmaciax")

    response = client.post(
        "/api/auth/register",
        headers=organization_headers("farmaciax"),
        json=build_member_payload("Maria@Email.com"),
    )

    body = response.json()
    assert response.status_code == 201
    assert body["email"] == "maria@email.com"
    assert body["role"] == "member"
    assert "password" not in body and "password_hash" not in body


def test_duplicated_email_in_same_organization_is_rejected(client, create_organization):
    create_organization("farmaciax")
    client.post("/api/auth/register", headers=organization_headers("farmaciax"), json=build_member_payload())

    response = client.post(
        "/api/auth/register", headers=organization_headers("farmaciax"), json=build_member_payload()
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "E-mail já cadastrado."


def test_same_email_can_register_in_different_organizations(client, create_organization):
    create_organization("farmaciax")
    create_organization("farmaciay")

    first = client.post("/api/auth/register", headers=organization_headers("farmaciax"), json=build_member_payload())
    second = client.post("/api/auth/register", headers=organization_headers("farmaciay"), json=build_member_payload())

    assert first.status_code == 201
    assert second.status_code == 201


def test_invalid_registration_lists_invalid_fields(client, create_organization):
    create_organization("farmaciax")
    payload = build_member_payload() | {"state": "XX", "password": "curta"}

    response = client.post("/api/auth/register", headers=organization_headers("farmaciax"), json=payload)

    assert response.status_code == 422
    assert response.json()["fields"] == ["password", "state"]


def test_login_rejects_wrong_password(client, create_organization):
    create_organization("farmaciax")
    client.post("/api/auth/register", headers=organization_headers("farmaciax"), json=build_member_payload())

    response = client.post(
        "/api/auth/login",
        headers=organization_headers("farmaciax"),
        json={"email": "maria@email.com", "password": "senha-errada"},
    )

    assert response.status_code == 401


def test_member_cannot_login_in_another_organization(client, create_organization):
    create_organization("farmaciax")
    create_organization("farmaciay")
    client.post("/api/auth/register", headers=organization_headers("farmaciax"), json=build_member_payload())

    response = client.post(
        "/api/auth/login",
        headers=organization_headers("farmaciay"),
        json={"email": "maria@email.com", "password": "senha-segura-1"},
    )

    assert response.status_code == 401


def test_organization_admin_can_login_in_own_organization(client, create_organization):
    create_organization("farmaciax")

    response = client.post(
        "/api/auth/login",
        headers=organization_headers("farmaciax"),
        json={"email": "admin@farmaciax.com.br", "password": "senha-org-123"},
    )

    assert response.json()["role"] == "org_admin"


def test_current_user_requires_token(client, create_organization):
    create_organization("farmaciax")

    response = client.get("/api/users/me", headers=organization_headers("farmaciax"))

    assert response.status_code == 401


def test_current_user_returns_profile(client, create_organization):
    create_organization("farmaciax")
    token = register_and_login(client, "farmaciax")

    response = client.get("/api/users/me", headers=organization_headers("farmaciax", token))

    assert response.status_code == 200
    assert response.json()["name"] == "Maria Souza"


def test_token_from_one_organization_is_rejected_in_another(client, create_organization):
    create_organization("farmaciax")
    create_organization("farmaciay")
    token = register_and_login(client, "farmaciax")
    register_and_login(client, "farmaciay")

    response = client.get("/api/users/me", headers=organization_headers("farmaciay", token))

    assert response.status_code == 401
