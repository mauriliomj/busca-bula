from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.exceptions.domain_exceptions import EmailAlreadyRegisteredError, InvalidCredentialsError
from app.models.platform.organization import Organization
from app.models.tenant.user import User, UserRole
from app.repositories.user_repository import UserRepository
from app.schemas.auth_schema import LoginRequest
from app.schemas.user_schema import UserRegisterRequest
from app.services.member_session_service import IssuedSession, MemberSessionService


class MemberAuthService:
    def __init__(self, tenant_session: Session, organization: Organization) -> None:
        self.user_repository = UserRepository(tenant_session)
        self.session_service = MemberSessionService(tenant_session, organization)

    def register_member(self, request: UserRegisterRequest) -> User:
        if self.user_repository.find_by_email(request.email) is not None:
            raise EmailAlreadyRegisteredError()
        user = User(
            role=UserRole.MEMBER,
            name=request.name,
            email=request.email,
            age=request.age,
            gender=request.gender,
            phone=request.phone,
            address=request.address,
            city=request.city,
            state=request.state,
            password_hash=hash_password(request.password),
        )
        try:
            return self.user_repository.save(user)
        except IntegrityError as error:
            self.user_repository.session.rollback()
            raise EmailAlreadyRegisteredError() from error

    def authenticate_member(self, request: LoginRequest) -> IssuedSession:
        user = self.user_repository.find_by_email(request.email)
        if user is None or not verify_password(request.password, user.password_hash):
            raise InvalidCredentialsError()
        return self.session_service.open_session(user)
