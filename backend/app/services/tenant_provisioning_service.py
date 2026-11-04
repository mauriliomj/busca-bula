from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database_administration import DatabaseAdministrator
from app.core.database_migrations import upgrade_tenant_database
from app.core.security import hash_password
from app.core.tenant_credentials import (
    build_tenant_database_name,
    build_tenant_role_name,
    derive_tenant_password,
)
from app.core.tenant_database import open_tenant_session, tenant_engine_registry
from app.exceptions.domain_exceptions import SlugAlreadyInUseError, TenantDatabaseConflictError
from app.models.platform.organization import Organization, OrganizationStatus
from app.models.tenant.user import User, UserRole
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.user_repository import UserRepository
from app.schemas.organization_schema import OrganizationCreateRequest


class TenantProvisioningService:
    def __init__(
        self,
        platform_session: Session,
        database_administrator: DatabaseAdministrator | None = None,
    ) -> None:
        self.organization_repository = OrganizationRepository(platform_session)
        self.database_administrator = database_administrator or DatabaseAdministrator()

    def provision_organization(self, request: OrganizationCreateRequest) -> Organization:
        organization = self.reserve_organization(request)
        try:
            self.ensure_tenant_database_is_absent(organization.slug)
        except TenantDatabaseConflictError:
            self.organization_repository.delete(organization)
            raise
        try:
            self.create_tenant_role_and_database(organization.slug)
            upgrade_tenant_database(organization.slug)
            self.create_organization_admin(organization.slug, request)
        except Exception:
            self.drop_tenant_database(organization.slug)
            self.organization_repository.delete(organization)
            raise
        organization.status = OrganizationStatus.ACTIVE
        return self.organization_repository.save(organization)

    def reserve_organization(self, request: OrganizationCreateRequest) -> Organization:
        if self.organization_repository.find_by_slug(request.slug) is not None:
            raise SlugAlreadyInUseError()
        organization = Organization(
            name=request.name,
            slug=request.slug,
            status=OrganizationStatus.PROVISIONING,
        )
        try:
            return self.organization_repository.save(organization)
        except IntegrityError as error:
            self.organization_repository.session.rollback()
            raise SlugAlreadyInUseError() from error

    def ensure_tenant_database_is_absent(self, slug: str) -> None:
        database_name = build_tenant_database_name(slug)
        role_name = build_tenant_role_name(slug)
        if self.database_administrator.database_exists(database_name) or self.database_administrator.role_exists(role_name):
            raise TenantDatabaseConflictError()

    def create_tenant_role_and_database(self, slug: str) -> None:
        database_name = build_tenant_database_name(slug)
        role_name = build_tenant_role_name(slug)
        self.database_administrator.create_role(role_name, derive_tenant_password(slug))
        self.database_administrator.create_database(database_name, owner=role_name)
        self.database_administrator.revoke_public_access(database_name)

    def create_organization_admin(self, slug: str, request: OrganizationCreateRequest) -> User:
        organization_admin = User(
            role=UserRole.ORG_ADMIN,
            name=request.admin_name,
            email=request.admin_email,
            password_hash=hash_password(request.admin_password),
        )
        with open_tenant_session(slug) as tenant_session:
            return UserRepository(tenant_session).save(organization_admin)

    def drop_tenant_database(self, slug: str) -> None:
        tenant_engine_registry.dispose_engine(slug)
        self.database_administrator.drop_database(build_tenant_database_name(slug))
        self.database_administrator.drop_role(build_tenant_role_name(slug))
