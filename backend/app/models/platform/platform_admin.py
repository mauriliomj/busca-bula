from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.platform_database import PlatformBase
from app.models.timestamp_columns import CreatedAtColumn

PLATFORM_ADMIN_ROLE = "platform_admin"


class PlatformAdmin(CreatedAtColumn, PlatformBase):
    __tablename__ = "platform_admins"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
