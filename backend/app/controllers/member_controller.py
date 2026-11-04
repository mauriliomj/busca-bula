from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies.authentication import require_organization_admin
from app.dependencies.tenant import get_tenant_session
from app.schemas.user_schema import MemberResponse
from app.services.member_management_service import MemberManagementService

router = APIRouter(
    prefix="/api/members",
    tags=["members"],
    dependencies=[Depends(require_organization_admin)],
)


@router.get("", response_model=list[MemberResponse])
def list_members(tenant_session: Session = Depends(get_tenant_session)):
    return MemberManagementService(tenant_session).list_members()


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_member(member_id: int, tenant_session: Session = Depends(get_tenant_session)) -> None:
    MemberManagementService(tenant_session).remove_member(member_id)
