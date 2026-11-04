from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.core.security import (
    build_tenant_scope,
    create_access_token,
    generate_refresh_token,
    hash_refresh_token,
)
from app.core.settings import get_settings
from app.exceptions.domain_exceptions import InvalidAccessTokenError
from app.models.platform.organization import Organization
from app.models.tenant.user import User
from app.models.tenant.user_session import UserSession
from app.repositories.user_repository import UserRepository
from app.repositories.user_session_repository import UserSessionRepository
from app.schemas.auth_schema import AccessTokenResponse


@dataclass(frozen=True)
class IssuedSession:
    access: AccessTokenResponse
    refresh_token: str


class MemberSessionService:
    def __init__(self, tenant_session: Session, organization: Organization) -> None:
        self.organization = organization
        self.user_repository = UserRepository(tenant_session)
        self.session_repository = UserSessionRepository(tenant_session)

    def open_session(self, user: User) -> IssuedSession:
        now = datetime.now(UTC)
        self.session_repository.delete_expired_for_user(user.id, now)
        refresh_token = generate_refresh_token()
        self.session_repository.save(
            UserSession(
                user_id=user.id,
                token_hash=hash_refresh_token(refresh_token),
                expires_at=self.build_expiration(now),
                last_used_at=now,
            )
        )
        return IssuedSession(self.build_access_response(user), refresh_token)

    def rotate_session(self, refresh_token: str | None) -> IssuedSession:
        if not refresh_token:
            raise InvalidAccessTokenError()
        now = datetime.now(UTC)
        user_session = self.session_repository.find_active_by_hash(hash_refresh_token(refresh_token), now)
        if user_session is None:
            raise InvalidAccessTokenError()
        user = self.user_repository.find_by_id(user_session.user_id)
        if user is None:
            raise InvalidAccessTokenError()
        rotated_token = generate_refresh_token()
        user_session.token_hash = hash_refresh_token(rotated_token)
        user_session.expires_at = self.build_expiration(now)
        user_session.last_used_at = now
        self.session_repository.save(user_session)
        return IssuedSession(self.build_access_response(user), rotated_token)

    def close_session(self, refresh_token: str | None) -> None:
        if not refresh_token:
            return
        user_session = self.session_repository.find_by_hash(hash_refresh_token(refresh_token))
        if user_session is not None:
            self.session_repository.delete(user_session)

    def build_access_response(self, user: User) -> AccessTokenResponse:
        scope = build_tenant_scope(self.organization.slug)
        return AccessTokenResponse(access_token=create_access_token(user.id, scope, user.role), role=user.role)

    def build_expiration(self, now: datetime) -> datetime:
        return now + timedelta(days=get_settings().refresh_token_expire_days)
