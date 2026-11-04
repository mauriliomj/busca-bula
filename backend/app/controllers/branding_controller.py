from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.logo_validation import LogoUpload
from app.dependencies.authentication import require_organization_admin
from app.dependencies.logo_upload import read_logo_upload
from app.dependencies.tenant import get_current_organization, get_tenant_session
from app.models.platform.organization import Organization
from app.schemas.branding_schema import BrandingColorsRequest, BrandingResponse
from app.services.branding_service import BrandingService

router = APIRouter(
    prefix="/api/organization/branding",
    tags=["branding"],
    dependencies=[Depends(require_organization_admin)],
)


def get_branding_service(
    organization: Organization = Depends(get_current_organization),
    tenant_session: Session = Depends(get_tenant_session),
) -> BrandingService:
    return BrandingService(tenant_session, organization.slug)


@router.get("", response_model=BrandingResponse)
def show_branding(branding_service: BrandingService = Depends(get_branding_service)):
    return branding_service.get_branding()


@router.put("", response_model=BrandingResponse)
def update_branding_colors(
    request: BrandingColorsRequest,
    branding_service: BrandingService = Depends(get_branding_service),
):
    return branding_service.update_colors(request)


@router.put("/logo", response_model=BrandingResponse)
def replace_branding_logo(
    upload: LogoUpload = Depends(read_logo_upload),
    branding_service: BrandingService = Depends(get_branding_service),
):
    return branding_service.replace_logo(upload)


@router.delete("/logo", response_model=BrandingResponse)
def remove_branding_logo(branding_service: BrandingService = Depends(get_branding_service)):
    return branding_service.remove_logo()
