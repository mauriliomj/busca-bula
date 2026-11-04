from collections.abc import Iterator

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.core.platform_database import get_platform_session
from app.core.tenant_database import open_tenant_session
from app.exceptions.domain_exceptions import MissingOrganizationError
from app.models.platform.organization import Organization
from app.services.organization_service import OrganizationService


def get_requested_organization_slug(
    x_organization: str | None = Header(default=None),
) -> str:
    slug = (x_organization or "").strip().lower()
    if not slug:
        raise MissingOrganizationError()
    return slug


def get_current_organization(
    slug: str = Depends(get_requested_organization_slug),
    platform_session: Session = Depends(get_platform_session),
) -> Organization:
    return OrganizationService(platform_session).find_active_organization(slug)


def get_tenant_session(
    organization: Organization = Depends(get_current_organization),
) -> Iterator[Session]:
    with open_tenant_session(organization.slug) as tenant_session:
        yield tenant_session
