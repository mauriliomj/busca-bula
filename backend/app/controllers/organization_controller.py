from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.core.logo_validation import SVG_CONTENT_TYPE
from app.core.platform_database import get_platform_session
from app.core.tenant_database import open_tenant_session
from app.dependencies.tenant import get_current_organization, get_tenant_session
from app.models.platform.organization import Organization
from app.schemas.organization_schema import PublicOrganizationResponse
from app.services.branding_service import BrandingService
from app.services.organization_service import OrganizationService

router = APIRouter(prefix="/api/organizations", tags=["organizations"])

LOGO_RESPONSE_HEADERS = {
    "Cache-Control": "public, max-age=31536000, immutable",
    "X-Content-Type-Options": "nosniff",
    "Content-Security-Policy": "default-src 'none'; style-src 'unsafe-inline'; sandbox",
}


@router.get("/current", response_model=PublicOrganizationResponse)
def show_current_organization(
    organization: Organization = Depends(get_current_organization),
    tenant_session: Session = Depends(get_tenant_session),
):
    branding = BrandingService(tenant_session, organization.slug).get_branding()
    return PublicOrganizationResponse(
        name=organization.name,
        slug=organization.slug,
        **branding.model_dump(),
    )


@router.get("/{slug}/logo")
def show_organization_logo(
    slug: str,
    platform_session: Session = Depends(get_platform_session),
) -> Response:
    organization = OrganizationService(platform_session).find_active_organization(slug)
    with open_tenant_session(organization.slug) as tenant_session:
        logo = BrandingService(tenant_session, organization.slug).read_logo()
    headers = dict(LOGO_RESPONSE_HEADERS)
    if logo.content_type == SVG_CONTENT_TYPE:
        headers["Content-Disposition"] = "inline"
    return Response(content=logo.content, media_type=logo.content_type, headers=headers)
