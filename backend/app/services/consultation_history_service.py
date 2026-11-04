from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.exceptions.domain_exceptions import ConsultationNotFoundError
from app.models.catalog.medicine import Medicine
from app.models.tenant.user import User
from app.repositories.consultation_repository import ConsultationRepository
from app.schemas.consultation_schema import ConsultationHistoryResponse, ConsultationResponse


class ConsultationHistoryService:
    def __init__(self, tenant_session: Session) -> None:
        self.session = tenant_session
        self.consultation_repository = ConsultationRepository(tenant_session)

    def record_consultation(self, user: User, medicine: Medicine) -> None:
        if user.consultation_history_consented_at is None:
            return
        self.consultation_repository.upsert(
            user.id, medicine.registration_number, medicine.product_name, medicine.active_ingredient
        )

    def show_history(self, user: User) -> ConsultationHistoryResponse:
        enabled = user.consultation_history_consented_at is not None
        items = self.consultation_repository.list_recent(user.id) if enabled else []
        return ConsultationHistoryResponse(
            enabled=enabled,
            consented_at=user.consultation_history_consented_at,
            items=[ConsultationResponse.model_validate(item) for item in items],
        )

    def update_consent(self, user: User, enabled: bool) -> ConsultationHistoryResponse:
        if enabled and user.consultation_history_consented_at is None:
            user.consultation_history_consented_at = datetime.now(UTC)
        if not enabled:
            self.consultation_repository.delete_all(user.id)
            user.consultation_history_consented_at = None
        self.session.commit()
        return self.show_history(user)

    def remove_consultation(self, user: User, consultation_id: int) -> None:
        consultation = self.consultation_repository.find_owned(user.id, consultation_id)
        if consultation is None:
            raise ConsultationNotFoundError()
        self.consultation_repository.delete(consultation)

    def clear_history(self, user: User) -> None:
        self.consultation_repository.delete_all(user.id)
        self.session.commit()
