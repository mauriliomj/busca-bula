from sqlalchemy.orm import Session

from app.core.tenant_database import tenant_engine_registry
from app.exceptions.domain_exceptions import (
    OrganizationNotFoundError,
    OrganizationStillProvisioningError,
)
from app.models.platform.organization import Organization, OrganizationStatus
from app.repositories.organization_repository import OrganizationRepository
from app.schemas.organization_schema import OrganizationUpdateRequest


class OrganizationService:
    def __init__(self, platform_session: Session) -> None:
        self.organization_repository = OrganizationRepository(platform_session)

    def find_active_organization(self, slug: str) -> Organization:
        organization = self.organization_repository.find_by_slug(slug)
        if organization is None or not organization.is_active:
            raise OrganizationNotFoundError()
        return organization

    def list_organizations(self) -> list[Organization]:
        return self.organization_repository.list_all()

    def update_organization(self, organization_id: int, request: OrganizationUpdateRequest) -> Organization:
        organization = self.organization_repository.find_by_id(organization_id)
        if organization is None:
            raise OrganizationNotFoundError()
        if organization.status == OrganizationStatus.PROVISIONING:
            raise OrganizationStillProvisioningError()
        if request.name is not None:
            organization.name = request.name
        if request.is_active is not None:
            organization.status = OrganizationStatus.ACTIVE if request.is_active else OrganizationStatus.INACTIVE
        saved_organization = self.organization_repository.save(organization)
        if not saved_organization.is_active:
            tenant_engine_registry.dispose_engine(saved_organization.slug)
        return saved_organization
