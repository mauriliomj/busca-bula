from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.tenant.user import User


class UserRepository:
    def __init__(self, tenant_session: Session) -> None:
        self.session = tenant_session

    def find_by_email(self, email: str) -> User | None:
        return self.session.scalar(select(User).where(User.email == email))

    def find_by_id(self, user_id: int) -> User | None:
        return self.session.get(User, user_id)

    def save(self, user: User) -> User:
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def list_all(self) -> list[User]:
        return list(self.session.scalars(select(User).order_by(User.name, User.id)))

    def delete(self, user: User) -> None:
        self.session.delete(user)
        self.session.commit()
