from sqlalchemy.orm import Session, undefer

from app.models.tenant.branding import BRANDING_ROW_ID, Branding


class BrandingRepository:
    def __init__(self, tenant_session: Session) -> None:
        self.session = tenant_session

    def find_current(self) -> Branding | None:
        return self.session.get(Branding, BRANDING_ROW_ID)

    def find_current_with_logo(self) -> Branding | None:
        return self.session.get(Branding, BRANDING_ROW_ID, options=[undefer(Branding.logo)])

    def find_or_create_current(self) -> Branding:
        return self.find_current() or Branding(id=BRANDING_ROW_ID)

    def save(self, branding: Branding) -> Branding:
        self.session.add(branding)
        self.session.commit()
        self.session.refresh(branding)
        return branding
