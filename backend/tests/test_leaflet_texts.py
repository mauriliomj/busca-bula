import pytest

from app.core.catalog_database import open_catalog_writer_session
from app.etl.chatbulario_parser import parse_chatbulario_dataset
from app.etl.catalog_sources import CatalogSource
from app.etl.patient_leaflet_pdf import extract_patient_leaflet_sections, segment_patient_leaflet
from app.exceptions.domain_exceptions import ProfessionalLeafletError, UnrecognizedLeafletError
from app.services import catalog_import_service
from app.services.catalog_import_service import CatalogImportService
from tests.catalog_samples import write_chatbulario_dataset
from tests.conftest import organization_headers, register_and_login
from tests.pdf_samples import PATIENT_LEAFLET_LINES, PROFESSIONAL_LEAFLET_LINES, build_text_pdf

PATIENT_LEAFLET_PDF = build_text_pdf(PATIENT_LEAFLET_LINES)


@pytest.fixture
def member_headers(client, create_organization):
    create_organization("farmaciax")
    return organization_headers("farmaciax", register_and_login(client, "farmaciax"))


@pytest.fixture
def imported_leaflet_texts(seeded_catalog, tmp_path, monkeypatch):
    dataset_path = write_chatbulario_dataset(tmp_path)
    monkeypatch.setattr(catalog_import_service, "download_catalog_source_files", lambda definition: [dataset_path])
    with open_catalog_writer_session() as session:
        service = CatalogImportService(session)
        service.run_imports([item.id for item in service.start_imports([CatalogSource.LEAFLET_TEXTS])])


def upload_pdf(client, headers, content: bytes, registration_number: str = "100430001"):
    return client.put(
        f"/api/platform/catalog/leaflets/{registration_number}/pdf",
        headers=headers | {"Content-Type": "application/pdf"},
        content=content,
    )


def test_dataset_parser_groups_sections_and_cleans_text(tmp_path):
    parsed = parse_chatbulario_dataset([write_chatbulario_dataset(tmp_path)])

    dipirona = next(record for record in parsed.records if record["registration_number"] == "100430001")
    sections = {section["section_number"]: section["content"] for section in dipirona["sections"]}
    assert parsed.rows_read == 5
    assert len(parsed.records) == 2
    assert sections == {
        1: "Indicado como analgésico e antitérmico.",
        6: "Adultos: 1 comprimido até 4 vezes ao dia.\nNão exceda a dose.",
        9: "Procure socorro médico.",
    }


def test_pdf_pipeline_extracts_the_nine_patient_sections():
    sections = extract_patient_leaflet_sections(PATIENT_LEAFLET_PDF)

    assert [section.section_number for section in sections] == list(range(1, 10))
    assert sections[0].content == "Este medicamento é indicado como analgésico e antitérmico."
    assert sections[8].content == "Procure socorro médico imediatamente."


def test_segmentation_rejects_professional_leaflet():
    with pytest.raises(ProfessionalLeafletError):
        segment_patient_leaflet("\n".join(PROFESSIONAL_LEAFLET_LINES))


def test_segmentation_rejects_unrelated_text():
    with pytest.raises(UnrecognizedLeafletError):
        segment_patient_leaflet("Relatório financeiro anual\n" * 30)


def test_member_reads_dataset_leaflet_with_attribution_and_outdated_flag(client, member_headers, imported_leaflet_texts):
    detail = client.get("/api/medicines/100430001", headers=member_headers).json()
    leaflet = client.get("/api/medicines/100430001/leaflet", headers=member_headers).json()

    assert detail["leaflet_text_available"] is True
    assert leaflet["source"] == "chatbulario"
    assert "CC BY 4.0" in leaflet["attribution"]["text"]
    assert leaflet["is_outdated"] is True
    assert leaflet["current_expedient_number"] == "1453197257"
    assert [section["number"] for section in leaflet["sections"]] == [1, 6, 9]
    assert leaflet["sections"][0]["title"] == "Para que este medicamento é indicado?"


def test_leaflet_text_requires_login_and_existing_text(client, member_headers, seeded_catalog):
    without_login = client.get("/api/medicines/100430001/leaflet", headers=organization_headers("farmaciax"))
    without_text = client.get("/api/medicines/100430001/leaflet", headers=member_headers)
    detail = client.get("/api/medicines/100430001", headers=member_headers).json()

    assert without_login.status_code == 401
    assert without_text.status_code == 404
    assert detail["leaflet_text_available"] is False


def test_platform_admin_uploads_current_leaflet_pdf(
    client, platform_admin_headers, member_headers, imported_leaflet_texts
):
    response = upload_pdf(client, platform_admin_headers, PATIENT_LEAFLET_PDF)
    leaflet = client.get("/api/medicines/100430001/leaflet", headers=member_headers).json()

    assert response.status_code == 200
    assert response.json()["section_numbers"] == list(range(1, 10))
    assert leaflet["source"] == "pdf_upload"
    assert leaflet["attribution"] is None
    assert leaflet["is_outdated"] is False
    assert len(leaflet["sections"]) == 9


def test_dataset_reimport_keeps_uploaded_pdf(client, platform_admin_headers, member_headers, imported_leaflet_texts, tmp_path, monkeypatch):
    upload_pdf(client, platform_admin_headers, PATIENT_LEAFLET_PDF)
    dataset_path = write_chatbulario_dataset(tmp_path)
    monkeypatch.setattr(catalog_import_service, "download_catalog_source_files", lambda definition: [dataset_path])

    with open_catalog_writer_session() as session:
        service = CatalogImportService(session)
        service.run_imports([item.id for item in service.start_imports([CatalogSource.LEAFLET_TEXTS])])

    leaflet = client.get("/api/medicines/100430001/leaflet", headers=member_headers).json()
    other = client.get("/api/medicines/012345678/leaflet", headers=member_headers).json()
    assert leaflet["source"] == "pdf_upload"
    assert other["source"] == "chatbulario"


def test_upload_rejects_invalid_files(client, platform_admin_headers, seeded_catalog):
    not_pdf = upload_pdf(client, platform_admin_headers, b"texto qualquer")
    professional = upload_pdf(client, platform_admin_headers, build_text_pdf(PROFESSIONAL_LEAFLET_LINES))
    unknown_medicine = upload_pdf(client, platform_admin_headers, PATIENT_LEAFLET_PDF, "999999999")

    assert not_pdf.status_code == 415
    assert professional.status_code == 422
    assert professional.json()["detail"] == "Este PDF parece ser a bula do profissional. Envie a bula do paciente."
    assert unknown_medicine.status_code == 404


def test_upload_requires_platform_admin(client, member_headers, seeded_catalog):
    response = upload_pdf(client, member_headers, PATIENT_LEAFLET_PDF)

    assert response.status_code == 401
