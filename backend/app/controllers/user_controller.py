from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.session_cookie import read_session_cookie
from app.dependencies.authentication import get_current_member
from app.dependencies.tenant import get_tenant_session
from app.models.tenant.user import User
from app.schemas.user_schema import (
    AccountDeletionRequest,
    PasswordChangeRequest,
    UserResponse,
    UserUpdateRequest,
)
from app.services.profile_service import ProfileService

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
def show_current_user(current_member: User = Depends(get_current_member)):
    return current_member


@router.put("/me", response_model=UserResponse)
def update_current_user(
    request: UserUpdateRequest,
    current_member: User = Depends(get_current_member),
    tenant_session: Session = Depends(get_tenant_session),
):
    return ProfileService(tenant_session).update_profile(current_member, request)


@router.put("/me/password", status_code=status.HTTP_204_NO_CONTENT)
def change_current_user_password(
    request: PasswordChangeRequest,
    current_member: User = Depends(get_current_member),
    tenant_session: Session = Depends(get_tenant_session),
    refresh_token: str | None = Depends(read_session_cookie),
) -> None:
    ProfileService(tenant_session).change_password(current_member, request, refresh_token)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_current_user(
    request: AccountDeletionRequest,
    current_member: User = Depends(get_current_member),
    tenant_session: Session = Depends(get_tenant_session),
) -> None:
    ProfileService(tenant_session).delete_account(current_member, request)
