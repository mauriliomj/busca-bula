from sqlalchemy.orm import Session

from app.core.security import PLATFORM_SCOPE, create_access_token, hash_password, verify_password
from app.exceptions.domain_exceptions import EmailAlreadyRegisteredError, InvalidCredentialsError
from app.models.platform.platform_admin import PLATFORM_ADMIN_ROLE, PlatformAdmin
from app.repositories.platform_admin_repository import PlatformAdminRepository
from app.schemas.auth_schema import AccessTokenResponse, LoginRequest
from app.schemas.email_normalization import normalize_email


class PlatformAdminAuthService:
    def __init__(self, platform_session: Session) -> None:
        self.platform_admin_repository = PlatformAdminRepository(platform_session)

    def create_platform_admin(self, name: str, email: str, password: str) -> PlatformAdmin:
        normalized_email = normalize_email(email)
        if self.platform_admin_repository.find_by_email(normalized_email) is not None:
            raise EmailAlreadyRegisteredError()
        platform_admin = PlatformAdmin(
            name=name,
            email=normalized_email,
            password_hash=hash_password(password),
        )
        return self.platform_admin_repository.save(platform_admin)

    def authenticate_platform_admin(self, request: LoginRequest) -> AccessTokenResponse:
        platform_admin = self.platform_admin_repository.find_by_email(request.email)
        if platform_admin is None or not verify_password(request.password, platform_admin.password_hash):
            raise InvalidCredentialsError()
        return AccessTokenResponse(
            access_token=create_access_token(platform_admin.id, PLATFORM_SCOPE, PLATFORM_ADMIN_ROLE),
            role=PLATFORM_ADMIN_ROLE,
        )
