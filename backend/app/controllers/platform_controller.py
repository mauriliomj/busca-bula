from collections.abc import Iterator

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.logo_validation import LogoUpload
from app.core.platform_database import get_platform_session
from app.core.tenant_database import open_tenant_session
from app.dependencies.authentication import require_platform_admin
from app.dependencies.logo_upload import read_logo_upload
from app.models.platform.organization import Organization
from app.schemas.auth_schema import AccessTokenResponse, LoginRequest
from app.schemas.branding_schema import BrandingColorsRequest, BrandingResponse
from app.schemas.organization_schema import (
    OrganizationCreateRequest,
    OrganizationResponse,
    OrganizationUpdateRequest,
)
from app.services.branding_service import BrandingService
from app.services.organization_service import OrganizationService
from app.services.platform_admin_auth_service import PlatformAdminAuthService
from app.services.tenant_provisioning_service import TenantProvisioningService

router = APIRouter(prefix="/api/platform", tags=["platform"])


def get_managed_organization(
    organization_id: int,
    platform_session: Session = Depends(get_platform_session),
) -> Organization:
    return OrganizationService(platform_session).find_provisioned_organization(organization_id)


def get_managed_branding_service(
    organization: Organization = Depends(get_managed_organization),
) -> Iterator[BrandingService]:
    with open_tenant_session(organization.slug) as tenant_session:
        yield BrandingService(tenant_session, organization.slug)


@router.post("/auth/login", response_model=AccessTokenResponse)
def login_platform_admin(
    request: LoginRequest,
    platform_session: Session = Depends(get_platform_session),
):
    return PlatformAdminAuthService(platform_session).authenticate_platform_admin(request)


@router.get(
    "/organizations",
    response_model=list[OrganizationResponse],
    dependencies=[Depends(require_platform_admin)],
)
def list_organizations(platform_session: Session = Depends(get_platform_session)):
    return OrganizationService(platform_session).list_organizations()


@router.post(
    "/organizations",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_platform_admin)],
)
def create_organization(
    request: OrganizationCreateRequest,
    platform_session: Session = Depends(get_platform_session),
):
    return TenantProvisioningService(platform_session).provision_organization(request)


@router.patch(
    "/organizations/{organization_id}",
    response_model=OrganizationResponse,
    dependencies=[Depends(require_platform_admin)],
)
def update_organization(
    organization_id: int,
    request: OrganizationUpdateRequest,
    platform_session: Session = Depends(get_platform_session),
):
    return OrganizationService(platform_session).update_organization(organization_id, request)


@router.delete(
    "/organizations/{organization_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_platform_admin)],
)
def delete_organization(
    organization_id: int,
    platform_session: Session = Depends(get_platform_session),
) -> None:
    TenantProvisioningService(platform_session).delete_organization(organization_id)


@router.get(
    "/organizations/{organization_id}/branding",
    response_model=BrandingResponse,
    dependencies=[Depends(require_platform_admin)],
)
def show_organization_branding(
    branding_service: BrandingService = Depends(get_managed_branding_service),
):
    return branding_service.get_branding()


@router.put(
    "/organizations/{organization_id}/branding",
    response_model=BrandingResponse,
    dependencies=[Depends(require_platform_admin)],
)
def update_organization_branding_colors(
    request: BrandingColorsRequest,
    branding_service: BrandingService = Depends(get_managed_branding_service),
):
    return branding_service.update_colors(request)


@router.put(
    "/organizations/{organization_id}/branding/logo",
    response_model=BrandingResponse,
    dependencies=[Depends(require_platform_admin)],
)
def replace_organization_branding_logo(
    upload: LogoUpload = Depends(read_logo_upload),
    branding_service: BrandingService = Depends(get_managed_branding_service),
):
    return branding_service.replace_logo(upload)


@router.delete(
    "/organizations/{organization_id}/branding/logo",
    response_model=BrandingResponse,
    dependencies=[Depends(require_platform_admin)],
)
def remove_organization_branding_logo(
    branding_service: BrandingService = Depends(get_managed_branding_service),
):
    return branding_service.remove_logo()
