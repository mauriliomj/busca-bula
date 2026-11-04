from enum import StrEnum

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.tenant_database import TenantBase
from app.models.timestamp_columns import TimestampColumns


class UserRole(StrEnum):
    ORG_ADMIN = "org_admin"
    MEMBER = "member"


class User(TimestampColumns, TenantBase):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    role: Mapped[str] = mapped_column(String(20), default=UserRole.MEMBER)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    age: Mapped[int | None]
    gender: Mapped[str | None] = mapped_column(String(20))
    phone: Mapped[str | None] = mapped_column(String(20))
    address: Mapped[str | None] = mapped_column(String(200))
    city: Mapped[str | None] = mapped_column(String(100))
    state: Mapped[str | None] = mapped_column(String(2))
    password_hash: Mapped[str] = mapped_column(String(255))
