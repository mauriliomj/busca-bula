from tests.conftest import (
    build_member_payload,
    login,
    login_as_organization_admin,
    organization_headers,
    register_and_login,
)


def build_profile_update(**changes) -> dict:
    payload = build_member_payload()
    payload.pop("password")
    return payload | changes


def test_update_profile_saves_changes(client, create_organization):
    create_organization("farmaciax")
    token = register_and_login(client, "farmaciax")

    response = client.put(
        "/api/users/me",
        headers=organization_headers("farmaciax", token),
        json=build_profile_update(name="Maria Oliveira", city="Campinas", age=35),
    )
    profile = client.get("/api/users/me", headers=organization_headers("farmaciax", token)).json()

    assert response.status_code == 200
    assert profile["name"] == "Maria Oliveira"
    assert profile["city"] == "Campinas"
    assert profile["age"] == 35


def test_update_profile_accepts_empty_optional_fields(client, create_organization):
    create_organization("farmaciax")
    token = login_as_organization_admin(client, "farmaciax")

    response = client.put(
        "/api/users/me",
        headers=organization_headers("farmaciax", token),
        json={"name": "Administrador", "email": "admin@farmaciax.com.br", "age": None, "state": None},
    )

    assert response.status_code == 200
    assert response.json()["state"] is None


def test_update_profile_rejects_email_of_another_member(client, create_organization):
    create_organization("farmaciax")
    register_and_login(client, "farmaciax", "joao@email.com")
    token = register_and_login(client, "farmaciax")

    response = client.put(
        "/api/users/me",
        headers=organization_headers("farmaciax", token),
        json=build_profile_update(email="joao@email.com"),
    )

    assert response.status_code == 409


def test_change_password_requires_current_password(client, create_organization):
    create_organization("farmaciax")
    token = register_and_login(client, "farmaciax")

    response = client.put(
        "/api/users/me/password",
        headers=organization_headers("farmaciax", token),
        json={"current_password": "senha-errada", "new_password": "nova-senha-123"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Senha incorreta."


def test_change_password_replaces_old_password(client, create_organization):
    create_organization("farmaciax")
    token = register_and_login(client, "farmaciax")

    response = client.put(
        "/api/users/me/password",
        headers=organization_headers("farmaciax", token),
        json={"current_password": "senha-segura-1", "new_password": "nova-senha-123"},
    )

    assert response.status_code == 204
    assert login(client, "farmaciax", "maria@email.com", "senha-segura-1") is None
    assert login(client, "farmaciax", "maria@email.com", "nova-senha-123") is not None


def test_delete_account_requires_password(client, create_organization):
    create_organization("farmaciax")
    token = register_and_login(client, "farmaciax")

    response = client.request(
        "DELETE",
        "/api/users/me",
        headers=organization_headers("farmaciax", token),
        json={"password": "senha-errada"},
    )

    assert response.status_code == 400


def test_delete_account_removes_member_and_invalidates_token(client, create_organization):
    create_organization("farmaciax")
    token = register_and_login(client, "farmaciax")

    response = client.request(
        "DELETE",
        "/api/users/me",
        headers=organization_headers("farmaciax", token),
        json={"password": "senha-segura-1"},
    )
    profile = client.get("/api/users/me", headers=organization_headers("farmaciax", token))

    assert response.status_code == 204
    assert profile.status_code == 401
    assert login(client, "farmaciax", "maria@email.com", "senha-segura-1") is None


def test_organization_admin_cannot_delete_own_account(client, create_organization):
    create_organization("farmaciax")
    token = login_as_organization_admin(client, "farmaciax")

    response = client.request(
        "DELETE",
        "/api/users/me",
        headers=organization_headers("farmaciax", token),
        json={"password": "senha-org-123"},
    )

    assert response.status_code == 403
