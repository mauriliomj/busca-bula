from fastapi import APIRouter, BackgroundTasks, Depends, Path, status
from sqlalchemy.orm import Session

from app.core.catalog_database import get_catalog_reader_session, get_catalog_writer_session
from app.dependencies.authentication import require_platform_admin
from app.dependencies.pdf_upload import read_leaflet_pdf_upload
from app.schemas.catalog_schema import CatalogImportResponse, CatalogSummaryResponse
from app.schemas.leaflet_text_schema import LeafletUploadResponse
from app.services.catalog_import_service import CatalogImportService, run_catalog_imports_in_background
from app.services.catalog_summary_service import CatalogSummaryService
from app.services.leaflet_text_service import LeafletTextService

router = APIRouter(
    prefix="/api/platform/catalog",
    tags=["catalog"],
    dependencies=[Depends(require_platform_admin)],
)


@router.get("", response_model=CatalogSummaryResponse)
def show_catalog_summary(catalog_reader_session: Session = Depends(get_catalog_reader_session)):
    return CatalogSummaryService(catalog_reader_session).build_summary()


@router.post("/imports", response_model=list[CatalogImportResponse], status_code=status.HTTP_202_ACCEPTED)
def start_catalog_import(
    background_tasks: BackgroundTasks,
    catalog_writer_session: Session = Depends(get_catalog_writer_session),
):
    catalog_imports = CatalogImportService(catalog_writer_session).start_imports()
    background_tasks.add_task(
        run_catalog_imports_in_background, [catalog_import.id for catalog_import in catalog_imports]
    )
    return catalog_imports


@router.put("/leaflets/{registration_number}/pdf", response_model=LeafletUploadResponse)
def upload_leaflet_pdf(
    registration_number: str = Path(pattern=r"^\d{9}$"),
    pdf_content: bytes = Depends(read_leaflet_pdf_upload),
    catalog_writer_session: Session = Depends(get_catalog_writer_session),
):
    return LeafletTextService(catalog_writer_session).replace_with_pdf(registration_number, pdf_content)
