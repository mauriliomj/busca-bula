import pytest

from tests.conftest import organization_headers, register_and_login

@pytest.fixture
def member_headers(client, create_organization):
    create_organization("farmaciax")
    return organization_headers("farmaciax", register_and_login(client, "farmaciax"))


def search(client, headers, **params):
    return client.get("/api/medicines", headers=headers, params=params)


def product_names(response) -> list[str]:
    return [item["product_name"] for item in response.json()["items"]]


def test_search_requires_login(client, create_organization, seeded_catalog):
    create_organization("farmaciax")

    response = search(client, organization_headers("farmaciax"), q="dipirona")

    assert response.status_code == 401


def test_search_requires_criteria(client, member_headers, seeded_catalog):
    response = search(client, member_headers)

    assert response.status_code == 400


def test_search_ignores_accents_and_case(client, member_headers, seeded_catalog):
    response = search(client, member_headers, q="LOSARTANA POTASSICA")

    assert product_names(response) == ["LOSARTANA"]


def test_search_matches_every_term_in_name_ingredient_or_class(client, member_headers, seeded_catalog):
    response = search(client, member_headers, q="dipirona analgesicos")

    body = response.json()
    assert product_names(response) == ["DIPIRONA MONOIDRATADA"]
    assert body["items"][0]["has_leaflet"] is True
    assert body["approximate"] is False


def test_search_hides_inactive_registrations_unless_requested(client, member_headers, seeded_catalog):
    default = search(client, member_headers, q="dipirona")
    with_inactive = search(client, member_headers, q="dipirona", include_inactive=True)

    assert product_names(default) == ["DIPIRONA MONOIDRATADA"]
    assert product_names(with_inactive) == ["DIPIRONA MONOIDRATADA", "DIPIRONA ANTIGA"]


def test_search_by_registration_prefix_and_barcode(client, member_headers, seeded_catalog):
    by_registration = search(client, member_headers, q="1004.3")
    by_barcode = search(client, member_headers, q="7891106000956")
    by_inactive_registration = search(client, member_headers, q="155550001")

    assert product_names(by_registration) == ["DIPIRONA MONOIDRATADA"]
    assert product_names(by_barcode) == ["DIPIRONA MONOIDRATADA"]
    assert product_names(by_inactive_registration) == ["DIPIRONA ANTIGA"]


def test_search_by_therapeutic_class(client, member_headers, seeded_catalog):
    response = search(client, member_headers, therapeutic_class="ANTI-HIPERTENSIVOS")
    classes = client.get("/api/medicines/therapeutic-classes", headers=member_headers).json()

    assert product_names(response) == ["LOSARTANA"]
    assert {"name": "ANALGESICOS", "medicines_count": 1} in classes


def test_search_falls_back_to_approximate_match(client, member_headers, seeded_catalog):
    response = search(client, member_headers, q="dipiroma monoidratada")

    assert product_names(response) == ["DIPIRONA MONOIDRATADA"]
    assert response.json()["approximate"] is True


def test_search_paginates_results(client, member_headers, seeded_catalog):
    first_page = search(client, member_headers, q="a", include_inactive=True, page_size=2)
    second_page = search(client, member_headers, q="a", include_inactive=True, page_size=2, page=2)

    assert first_page.json()["total"] == 3
    assert len(first_page.json()["items"]) == 2
    assert len(second_page.json()["items"]) == 1


def test_medicine_detail_includes_leaflet_and_prices(client, member_headers, seeded_catalog):
    response = client.get("/api/medicines/100430001", headers=member_headers)

    body = response.json()
    assert response.status_code == 200
    assert body["leaflet"]["bulario_product_id"] == "599975"
    assert body["presentations"][0]["ean_codes"] == ["7891106000956"]
    assert body["presentations"][0]["consumer_prices"]["18%"] == 12.3
    assert body["consumer_price_tax_rates"] == ["0%", "18%", "18% ALC"]


def test_unknown_medicine_returns_not_found(client, member_headers, seeded_catalog):
    assert client.get("/api/medicines/999999999", headers=member_headers).status_code == 404
    assert client.get("/api/medicines/abc", headers=member_headers).status_code == 422
