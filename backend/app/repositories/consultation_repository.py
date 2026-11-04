from sqlalchemy import delete, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.models.tenant.consultation import Consultation

HISTORY_LIMIT = 100


class ConsultationRepository:
    def __init__(self, tenant_session: Session) -> None:
        self.session = tenant_session

    def upsert(self, user_id: int, registration_number: str, product_name: str, active_ingredient: str | None) -> None:
        statement = insert(Consultation).values(
            user_id=user_id,
            registration_number=registration_number,
            product_name=product_name,
            active_ingredient=active_ingredient,
        )
        statement = statement.on_conflict_do_update(
            constraint="uq_consultations_user_registration",
            set_={
                "product_name": statement.excluded.product_name,
                "active_ingredient": statement.excluded.active_ingredient,
                "consulted_at": func.now(),
            },
        )
        self.session.execute(statement)
        self.session.commit()

    def list_recent(self, user_id: int) -> list[Consultation]:
        statement = (
            select(Consultation)
            .where(Consultation.user_id == user_id)
            .order_by(Consultation.consulted_at.desc(), Consultation.id.desc())
            .limit(HISTORY_LIMIT)
        )
        return list(self.session.scalars(statement))

    def find_owned(self, user_id: int, consultation_id: int) -> Consultation | None:
        return self.session.scalar(
            select(Consultation).where(Consultation.id == consultation_id, Consultation.user_id == user_id)
        )

    def delete(self, consultation: Consultation) -> None:
        self.session.delete(consultation)
        self.session.commit()

    def delete_all(self, user_id: int) -> None:
        self.session.execute(delete(Consultation).where(Consultation.user_id == user_id))
