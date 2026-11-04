from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.tenant.user_session import UserSession


class UserSessionRepository:
    def __init__(self, tenant_session: Session) -> None:
        self.session = tenant_session

    def save(self, user_session: UserSession) -> UserSession:
        self.session.add(user_session)
        self.session.commit()
        return user_session

    def find_active_by_hash(self, token_hash: str, now: datetime) -> UserSession | None:
        return self.session.scalar(
            select(UserSession).where(UserSession.token_hash == token_hash, UserSession.expires_at > now)
        )

    def find_by_hash(self, token_hash: str) -> UserSession | None:
        return self.session.scalar(select(UserSession).where(UserSession.token_hash == token_hash))

    def delete(self, user_session: UserSession) -> None:
        self.session.delete(user_session)
        self.session.commit()

    def delete_all_for_user(self, user_id: int, except_token_hash: str | None = None) -> None:
        statement = delete(UserSession).where(UserSession.user_id == user_id)
        if except_token_hash is not None:
            statement = statement.where(UserSession.token_hash != except_token_hash)
        self.session.execute(statement)
        self.session.commit()

    def delete_expired_for_user(self, user_id: int, now: datetime) -> None:
        self.session.execute(
            delete(UserSession).where(UserSession.user_id == user_id, UserSession.expires_at <= now)
        )
