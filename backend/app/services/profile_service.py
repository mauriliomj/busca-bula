from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.exceptions.domain_exceptions import (
    EmailAlreadyRegisteredError,
    IncorrectPasswordError,
    OrganizationAdminAccountDeletionError,
)
from app.models.tenant.user import User, UserRole
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import AccountDeletionRequest, PasswordChangeRequest, UserUpdateRequest


class ProfileService:
    def __init__(self, tenant_session: Session) -> None:
        self.user_repository = UserRepository(tenant_session)

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

    def change_password(self, user: User, request: PasswordChangeRequest) -> None:
        self.ensure_password_matches(user, request.current_password)
        user.password_hash = hash_password(request.new_password)
        self.user_repository.save(user)

    def delete_account(self, user: User, request: AccountDeletionRequest) -> None:
        if user.role == UserRole.ORG_ADMIN:
            raise OrganizationAdminAccountDeletionError()
        self.ensure_password_matches(user, request.password)
        self.user_repository.delete(user)

    def ensure_password_matches(self, user: User, password: str) -> None:
        if not verify_password(password, user.password_hash):
            raise IncorrectPasswordError()
