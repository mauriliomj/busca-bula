from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.platform_database import get_platform_session
from app.core.security import PLATFORM_SCOPE, build_tenant_scope, decode_access_token
from app.dependencies.tenant import get_current_organization, get_tenant_session
from app.exceptions.domain_exceptions import (
    InvalidAccessTokenError,
    OrganizationAdminRequiredError,
)
from app.models.platform.organization import Organization
from app.models.platform.platform_admin import PlatformAdmin
from app.models.tenant.user import User, UserRole
from app.repositories.platform_admin_repository import PlatformAdminRepository
from app.repositories.user_repository import UserRepository

bearer_scheme = HTTPBearer(auto_error=False)


def extract_bearer_token(credentials: HTTPAuthorizationCredentials | None) -> str:
    if credentials is None:
        raise InvalidAccessTokenError()
    return credentials.credentials


def get_current_member(
    organization: Organization = Depends(get_current_organization),
    tenant_session: Session = Depends(get_tenant_session),
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> User:
    payload = decode_access_token(
        extract_bearer_token(credentials), build_tenant_scope(organization.slug)
    )
    user = UserRepository(tenant_session).find_by_id(payload.subject_id)
    if user is None:
        raise InvalidAccessTokenError()
    return user


def require_organization_admin(current_member: User = Depends(get_current_member)) -> User:
    if current_member.role != UserRole.ORG_ADMIN:
        raise OrganizationAdminRequiredError()
    return current_member


def require_platform_admin(
    platform_session: Session = Depends(get_platform_session),
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> PlatformAdmin:
    payload = decode_access_token(extract_bearer_token(credentials), PLATFORM_SCOPE)
    platform_admin = PlatformAdminRepository(platform_session).find_by_id(payload.subject_id)
    if platform_admin is None:
        raise InvalidAccessTokenError()
    return platform_admin
