from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.orm import Session

from app.core.catalog_database import get_catalog_reader_session, get_catalog_writer_session
from app.dependencies.authentication import require_platform_admin
from app.schemas.catalog_schema import CatalogImportResponse, CatalogSummaryResponse
from app.services.catalog_import_service import CatalogImportService, run_catalog_imports_in_background
from app.services.catalog_summary_service import CatalogSummaryService

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
