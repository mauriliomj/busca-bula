from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies.tenant import get_current_organization, get_tenant_session
from app.models.platform.organization import Organization
from app.schemas.auth_schema import AccessTokenResponse, LoginRequest
from app.schemas.user_schema import UserRegisterRequest, UserResponse
from app.services.member_auth_service import MemberAuthService

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
    organization: Organization = Depends(get_current_organization),
    tenant_session: Session = Depends(get_tenant_session),
):
    return MemberAuthService(tenant_session, organization).authenticate_member(request)
