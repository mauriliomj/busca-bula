from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.platform.organization import Organization


class OrganizationRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def find_by_slug(self, slug: str) -> Organization | None:
        return self.session.scalar(select(Organization).where(Organization.slug == slug))

    def find_by_id(self, organization_id: int) -> Organization | None:
        return self.session.get(Organization, organization_id)

    def list_all(self) -> list[Organization]:
        return list(self.session.scalars(select(Organization).order_by(Organization.id.desc())))

    def save(self, organization: Organization) -> Organization:
        self.session.add(organization)
        self.session.commit()
        self.session.refresh(organization)
        return organization

    def delete(self, organization: Organization) -> None:
        self.session.delete(organization)
        self.session.commit()
