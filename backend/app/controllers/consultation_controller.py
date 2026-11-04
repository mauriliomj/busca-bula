from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies.authentication import get_current_member
from app.dependencies.tenant import get_tenant_session
from app.models.tenant.user import User
from app.schemas.consultation_schema import ConsultationConsentRequest, ConsultationHistoryResponse
from app.services.consultation_history_service import ConsultationHistoryService

router = APIRouter(prefix="/api/users/me/consultations", tags=["consultations"])


@router.get("", response_model=ConsultationHistoryResponse)
def show_consultation_history(
    current_member: User = Depends(get_current_member),
    tenant_session: Session = Depends(get_tenant_session),
):
    return ConsultationHistoryService(tenant_session).show_history(current_member)


@router.put("/consent", response_model=ConsultationHistoryResponse)
def update_consultation_history_consent(
    request: ConsultationConsentRequest,
    current_member: User = Depends(get_current_member),
    tenant_session: Session = Depends(get_tenant_session),
):
    return ConsultationHistoryService(tenant_session).update_consent(current_member, request.enabled)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def clear_consultation_history(
    current_member: User = Depends(get_current_member),
    tenant_session: Session = Depends(get_tenant_session),
) -> None:
    ConsultationHistoryService(tenant_session).clear_history(current_member)


@router.delete("/{consultation_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_consultation(
    consultation_id: int,
    current_member: User = Depends(get_current_member),
    tenant_session: Session = Depends(get_tenant_session),
) -> None:
    ConsultationHistoryService(tenant_session).remove_consultation(current_member, consultation_id)
