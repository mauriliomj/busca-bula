from sqlalchemy.orm import Session

from app.exceptions.domain_exceptions import MemberNotFoundError, OrganizationAdminRemovalError
from app.models.tenant.user import User, UserRole
from app.repositories.user_repository import UserRepository


class MemberManagementService:
    def __init__(self, tenant_session: Session) -> None:
        self.user_repository = UserRepository(tenant_session)

    def list_members(self) -> list[User]:
        return self.user_repository.list_all()

    def remove_member(self, member_id: int) -> None:
        member = self.user_repository.find_by_id(member_id)
        if member is None:
            raise MemberNotFoundError()
        if member.role == UserRole.ORG_ADMIN:
            raise OrganizationAdminRemovalError()
        self.user_repository.delete(member)
