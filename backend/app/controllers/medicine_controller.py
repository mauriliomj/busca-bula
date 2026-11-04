from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from app.core.catalog_database import get_catalog_reader_session
from app.dependencies.authentication import get_current_member
from app.dependencies.tenant import get_tenant_session
from app.models.tenant.user import User
from app.schemas.leaflet_text_schema import LeafletTextResponse
from app.schemas.medicine_schema import MedicineDetailResponse, MedicineSearchResponse, TherapeuticClassResponse
from app.services.consultation_history_service import ConsultationHistoryService
from app.services.leaflet_text_service import LeafletTextService
from app.services.medicine_search_service import MedicineSearchService

router = APIRouter(prefix="/api/medicines", tags=["medicines"], dependencies=[Depends(get_current_member)])


@router.get("", response_model=MedicineSearchResponse)
def search_medicines(
    q: str | None = Query(default=None, max_length=100),
    therapeutic_class: str | None = Query(default=None, max_length=255),
    include_inactive: bool = False,
    page: int = Query(default=1, ge=1, le=500),
    page_size: int = Query(default=20, ge=1, le=50),
    catalog_session: Session = Depends(get_catalog_reader_session),
):
    return MedicineSearchService(catalog_session).search(q, therapeutic_class, include_inactive, page, page_size)


@router.get("/therapeutic-classes", response_model=list[TherapeuticClassResponse])
def list_therapeutic_classes(catalog_session: Session = Depends(get_catalog_reader_session)):
    return MedicineSearchService(catalog_session).list_therapeutic_classes()


@router.get("/{registration_number}", response_model=MedicineDetailResponse)
def show_medicine(
    registration_number: str = Path(pattern=r"^\d{9}$"),
    current_member: User = Depends(get_current_member),
    tenant_session: Session = Depends(get_tenant_session),
    catalog_session: Session = Depends(get_catalog_reader_session),
):
    search_service = MedicineSearchService(catalog_session)
    medicine = search_service.find_medicine(registration_number)
    ConsultationHistoryService(tenant_session).record_consultation(current_member, medicine)
    return search_service.build_detail(medicine)


@router.get("/{registration_number}/leaflet", response_model=LeafletTextResponse)
def show_medicine_leaflet(
    registration_number: str = Path(pattern=r"^\d{9}$"),
    catalog_session: Session = Depends(get_catalog_reader_session),
):
    return LeafletTextService(catalog_session).show_leaflet_text(registration_number)
