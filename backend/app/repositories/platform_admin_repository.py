from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.platform.platform_admin import PlatformAdmin


class PlatformAdminRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def find_by_email(self, email: str) -> PlatformAdmin | None:
        return self.session.scalar(select(PlatformAdmin).where(PlatformAdmin.email == email))

    def find_by_id(self, platform_admin_id: int) -> PlatformAdmin | None:
        return self.session.get(PlatformAdmin, platform_admin_id)

    def save(self, platform_admin: PlatformAdmin) -> PlatformAdmin:
        self.session.add(platform_admin)
        self.session.commit()
        self.session.refresh(platform_admin)
        return platform_admin
