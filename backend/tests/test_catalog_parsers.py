from datetime import date, datetime
from decimal import Decimal

from app.etl.leaflet_index_parser import parse_leaflet_index
from app.etl.medicine_catalog_parser import parse_medicine_catalog
from app.etl.price_table_parser import parse_price_table
from tests.catalog_samples import write_leaflet_index, write_medicine_catalog, write_price_table


def test_medicine_catalog_keeps_one_record_per_registration(tmp_path):
    parsed = parse_medicine_catalog(write_medicine_catalog(tmp_path))

    assert parsed.rows_read == 4
    assert [record["registration_number"] for record in parsed.records] == ["012345678", "100430001"]


def test_medicine_catalog_prefers_active_and_most_recent_row(tmp_path):
    parsed = parse_medicine_catalog(write_medicine_catalog(tmp_path))
    dipirona = next(record for record in parsed.records if record["registration_number"] == "100430001")

    assert dipirona["is_active"] is True
    assert dipirona["process_finished_on"] == date(2020, 3, 15)
    assert dipirona["registration_expires_on"] == date(2030, 3, 1)
    assert dipirona["active_ingredient"] == "dipirona monoidratada"
    assert dipirona["holder_cnpj"] == "11111111000111"
    assert dipirona["holder_name"] == "FARMA UM LTDA"


def test_medicine_catalog_restores_leading_zero_and_fixes_category(tmp_path):
    parsed = parse_medicine_catalog(write_medicine_catalog(tmp_path))
    losartana = next(record for record in parsed.records if record["registration_number"] == "012345678")

    assert losartana["regulatory_category"] == "Fitoterápico"
    assert losartana["active_ingredient"] == "losartana potássica"


def test_leaflet_index_parses_american_dates_and_skips_missing_registration(tmp_path):
    parsed = parse_leaflet_index(write_leaflet_index(tmp_path))

    assert parsed.rows_read == 2
    assert len(parsed.records) == 1
    leaflet = parsed.records[0]
    assert leaflet["registration_number"] == "100430001"
    assert leaflet["bulario_product_id"] == "599975"
    assert leaflet["published_at"] == datetime(2025, 11, 3, 15, 9, 27)


def test_price_table_parses_brazilian_decimals_and_tax_rates(tmp_path):
    parsed = parse_price_table(write_price_table(tmp_path))
    dipirona = next(record for record in parsed.records if record["ggrem_code"] == "538912020009303")

    assert dipirona["medicine_registration_number"] == "100430001"
    assert dipirona["factory_price_without_taxes"] == Decimal("1027.44")
    assert dipirona["consumer_prices"] == {"0%": 9.1, "18%": 12.3, "18% ALC": 12.1}
    assert dipirona["factory_prices"]["18% ALC"] == 1033.46
    assert dipirona["ean_codes"] == ["7891106000956"]
    assert dipirona["prescription_label"] == "Sem Tarja"
    assert dipirona["hospital_restricted"] is False
    assert dipirona["marketed"] is True


def test_price_table_handles_missing_consumer_prices(tmp_path):
    parsed = parse_price_table(write_price_table(tmp_path))
    hospitalar = next(record for record in parsed.records if record["ggrem_code"] == "538912020009400")

    assert hospitalar["consumer_prices"] == {}
    assert hospitalar["consumer_price_without_taxes"] is None
    assert hospitalar["ean_codes"] == []
    assert hospitalar["hospital_restricted"] is True
    assert hospitalar["medicine_registration_number"] == "123456780"
