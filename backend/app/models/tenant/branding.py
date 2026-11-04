from datetime import datetime

from sqlalchemy import DateTime, LargeBinary, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.tenant_database import TenantBase

BRANDING_ROW_ID = 1


class Branding(TenantBase):
    __tablename__ = "branding"

    id: Mapped[int] = mapped_column(primary_key=True, default=BRANDING_ROW_ID)
    primary_color: Mapped[str | None] = mapped_column(String(7))
    secondary_color: Mapped[str | None] = mapped_column(String(7))
    logo: Mapped[bytes | None] = mapped_column(LargeBinary, deferred=True)
    logo_content_type: Mapped[str | None] = mapped_column(String(40))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    @property
    def has_logo(self) -> bool:
        return self.logo_content_type is not None
