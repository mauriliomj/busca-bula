from enum import StrEnum

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.platform_database import PlatformBase
from app.models.timestamp_columns import TimestampColumns


class OrganizationStatus(StrEnum):
    PROVISIONING = "provisioning"
    ACTIVE = "active"
    INACTIVE = "inactive"


class Organization(TimestampColumns, PlatformBase):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    slug: Mapped[str] = mapped_column(String(40), unique=True)
    status: Mapped[str] = mapped_column(String(20), default=OrganizationStatus.PROVISIONING)

    @property
    def is_active(self) -> bool:
        return self.status == OrganizationStatus.ACTIVE
