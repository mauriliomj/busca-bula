from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password, hash_refresh_token, verify_password
from app.exceptions.domain_exceptions import (
    EmailAlreadyRegisteredError,
    IncorrectPasswordError,
    OrganizationAdminAccountDeletionError,
)
from app.models.tenant.user import User, UserRole
from app.repositories.user_repository import UserRepository
from app.repositories.user_session_repository import UserSessionRepository
from app.schemas.user_schema import AccountDeletionRequest, PasswordChangeRequest, UserUpdateRequest


class ProfileService:
    def __init__(self, tenant_session: Session) -> None:
        self.user_repository = UserRepository(tenant_session)
        self.session_repository = UserSessionRepository(tenant_session)

    def update_profile(self, user: User, request: UserUpdateRequest) -> User:
        owner_of_email = self.user_repository.find_by_email(request.email)
        if owner_of_email is not None and owner_of_email.id != user.id:
            raise EmailAlreadyRegisteredError()
        for field, value in request.model_dump().items():
            setattr(user, field, value)
        try:
            return self.user_repository.save(user)
        except IntegrityError as error:
            self.user_repository.session.rollback()
            raise EmailAlreadyRegisteredError() from error

    def change_password(self, user: User, request: PasswordChangeRequest, current_refresh_token: str | None) -> None:
        self.ensure_password_matches(user, request.current_password)
        user.password_hash = hash_password(request.new_password)
        self.user_repository.save(user)
        kept_token_hash = hash_refresh_token(current_refresh_token) if current_refresh_token else None
        self.session_repository.delete_all_for_user(user.id, except_token_hash=kept_token_hash)

    def delete_account(self, user: User, request: AccountDeletionRequest) -> None:
        if user.role == UserRole.ORG_ADMIN:
            raise OrganizationAdminAccountDeletionError()
        self.ensure_password_matches(user, request.password)
        self.user_repository.delete(user)

    def ensure_password_matches(self, user: User, password: str) -> None:
        if not verify_password(password, user.password_hash):
            raise IncorrectPasswordError()
