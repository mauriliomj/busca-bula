from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.session_cookie import clear_session_cookie, read_session_cookie, set_session_cookie
from app.dependencies.tenant import get_current_organization, get_tenant_session
from app.models.platform.organization import Organization
from app.schemas.auth_schema import AccessTokenResponse, LoginRequest
from app.schemas.user_schema import UserRegisterRequest, UserResponse
from app.services.member_auth_service import MemberAuthService
from app.services.member_session_service import MemberSessionService

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    request: UserRegisterRequest,
    organization: Organization = Depends(get_current_organization),
    tenant_session: Session = Depends(get_tenant_session),
):
    return MemberAuthService(tenant_session, organization).register_member(request)


@router.post("/login", response_model=AccessTokenResponse)
def login(
    request: LoginRequest,
    response: Response,
    organization: Organization = Depends(get_current_organization),
    tenant_session: Session = Depends(get_tenant_session),
):
    issued_session = MemberAuthService(tenant_session, organization).authenticate_member(request)
    set_session_cookie(response, issued_session.refresh_token)
    return issued_session.access


@router.post("/refresh", response_model=AccessTokenResponse)
def refresh(
    response: Response,
    refresh_token: str | None = Depends(read_session_cookie),
    organization: Organization = Depends(get_current_organization),
    tenant_session: Session = Depends(get_tenant_session),
):
    issued_session = MemberSessionService(tenant_session, organization).rotate_session(refresh_token)
    set_session_cookie(response, issued_session.refresh_token)
    return issued_session.access


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    response: Response,
    refresh_token: str | None = Depends(read_session_cookie),
    organization: Organization = Depends(get_current_organization),
    tenant_session: Session = Depends(get_tenant_session),
) -> None:
    MemberSessionService(tenant_session, organization).close_session(refresh_token)
    clear_session_cookie(response)
