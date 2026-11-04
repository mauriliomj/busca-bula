from tests.conftest import login_as_organization_admin, organization_headers, register_and_login


def test_members_list_is_restricted_to_organization_admin(client, create_organization):
    create_organization("farmaciax")
    member_token = register_and_login(client, "farmaciax")

    response = client.get("/api/members", headers=organization_headers("farmaciax", member_token))

    assert response.status_code == 403


def test_members_list_contains_only_own_organization(client, create_organization):
    create_organization("farmaciax")
    create_organization("farmaciay")
    register_and_login(client, "farmaciax", "maria@email.com")
    register_and_login(client, "farmaciay", "joao@email.com")
    admin_token = login_as_organization_admin(client, "farmaciax")

    response = client.get("/api/members", headers=organization_headers("farmaciax", admin_token))

    emails = [member["email"] for member in response.json()]
    assert sorted(emails) == ["admin@farmaciax.com.br", "maria@email.com"]


def test_organization_admin_removes_member(client, create_organization):
    create_organization("farmaciax")
    register_and_login(client, "farmaciax")
    admin_token = login_as_organization_admin(client, "farmaciax")
    headers = organization_headers("farmaciax", admin_token)
    member_id = next(m["id"] for m in client.get("/api/members", headers=headers).json() if m["role"] == "member")

    response = client.delete(f"/api/members/{member_id}", headers=headers)

    assert response.status_code == 204
    assert len(client.get("/api/members", headers=headers).json()) == 1


def test_organization_admin_cannot_be_removed(client, create_organization):
    create_organization("farmaciax")
    admin_token = login_as_organization_admin(client, "farmaciax")
    headers = organization_headers("farmaciax", admin_token)
    admin_id = client.get("/api/members", headers=headers).json()[0]["id"]

    response = client.delete(f"/api/members/{admin_id}", headers=headers)

    assert response.status_code == 403


def test_removing_unknown_member_returns_not_found(client, create_organization):
    create_organization("farmaciax")
    admin_token = login_as_organization_admin(client, "farmaciax")

    response = client.delete("/api/members/999", headers=organization_headers("farmaciax", admin_token))

    assert response.status_code == 404
