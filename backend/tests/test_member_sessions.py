from sqlalchemy import text

from app.core.settings import get_settings
from app.core.tenant_database import open_tenant_session
from tests.conftest import build_member_payload, organization_headers

SESSION_COOKIE = get_settings().session_cookie_name


def login_member(client, slug: str, email: str = "maria@email.com", password: str = "senha-segura-1"):
    return client.post("/api/auth/login", headers=organization_headers(slug), json={"email": email, "password": password})


def register_member(client, slug: str, email: str = "maria@email.com") -> None:
    client.post("/api/auth/register", headers=organization_headers(slug), json=build_member_payload(email))


def use_session_cookie(client, refresh_token: str) -> None:
    client.cookies.clear()
    client.cookies.set(SESSION_COOKIE, refresh_token)


def refresh_session(client, slug: str):
    return client.post("/api/auth/refresh", headers=organization_headers(slug))


def test_login_sets_http_only_session_cookie(client, create_organization):
    create_organization("farmaciax")
    register_member(client, "farmaciax")

    response = login_member(client, "farmaciax")

    set_cookie = response.headers["set-cookie"]
    assert response.status_code == 200
    assert response.cookies.get(SESSION_COOKIE)
    assert "HttpOnly" in set_cookie
    assert "Path=/api/auth" in set_cookie
    assert "samesite=lax" in set_cookie.lower()


def test_refresh_issues_new_access_token_and_rotates_session(client, create_organization):
    create_organization("farmaciax")
    register_member(client, "farmaciax")
    original_token = login_member(client, "farmaciax").cookies.get(SESSION_COOKIE)

    use_session_cookie(client, original_token)
    response = refresh_session(client, "farmaciax")
    rotated_token = response.cookies.get(SESSION_COOKIE)

    assert response.status_code == 200
    assert response.json()["role"] == "member"
    assert rotated_token and rotated_token != original_token
    profile = client.get(
        "/api/users/me", headers=organization_headers("farmaciax", response.json()["access_token"])
    )
    assert profile.json()["email"] == "maria@email.com"

    use_session_cookie(client, original_token)
    assert refresh_session(client, "farmaciax").status_code == 401


def test_refresh_without_cookie_is_rejected(client, create_organization):
    create_organization("farmaciax")

    response = refresh_session(client, "farmaciax")

    assert response.status_code == 401


def test_logout_closes_session_and_clears_cookie(client, create_organization):
    create_organization("farmaciax")
    register_member(client, "farmaciax")
    refresh_token = login_member(client, "farmaciax").cookies.get(SESSION_COOKIE)

    use_session_cookie(client, refresh_token)
    response = client.post("/api/auth/logout", headers=organization_headers("farmaciax"))

    assert response.status_code == 204
    assert "Max-Age=0" in response.headers["set-cookie"]
    use_session_cookie(client, refresh_token)
    assert refresh_session(client, "farmaciax").status_code == 401


def test_expired_session_is_rejected(client, create_organization):
    create_organization("farmaciax")
    register_member(client, "farmaciax")
    refresh_token = login_member(client, "farmaciax").cookies.get(SESSION_COOKIE)
    with open_tenant_session("farmaciax") as tenant_session:
        tenant_session.execute(text("UPDATE user_sessions SET expires_at = now() - interval '1 minute'"))
        tenant_session.commit()

    use_session_cookie(client, refresh_token)

    assert refresh_session(client, "farmaciax").status_code == 401


def test_session_from_one_organization_is_rejected_in_another(client, create_organization):
    create_organization("farmaciax")
    create_organization("farmaciay")
    register_member(client, "farmaciax")
    refresh_token = login_member(client, "farmaciax").cookies.get(SESSION_COOKIE)

    use_session_cookie(client, refresh_token)

    assert refresh_session(client, "farmaciay").status_code == 401


def test_password_change_closes_other_sessions(client, create_organization):
    create_organization("farmaciax")
    register_member(client, "farmaciax")
    other_device_token = login_member(client, "farmaciax").cookies.get(SESSION_COOKIE)
    current_login = login_member(client, "farmaciax")
    current_token = current_login.cookies.get(SESSION_COOKIE)

    use_session_cookie(client, current_token)
    response = client.put(
        "/api/users/me/password",
        headers=organization_headers("farmaciax", current_login.json()["access_token"]),
        json={"current_password": "senha-segura-1", "new_password": "nova-senha-segura-2"},
    )

    assert response.status_code == 204
    use_session_cookie(client, other_device_token)
    assert refresh_session(client, "farmaciax").status_code == 401
    use_session_cookie(client, current_token)
    assert refresh_session(client, "farmaciax").status_code == 200
