from sqlalchemy import exists, func, select
from sqlalchemy.orm import Session

from app.models.catalog.leaflet import Leaflet
from app.models.catalog.leaflet_document import LeafletDocument
from app.models.catalog.medicine import Medicine
from app.models.catalog.medicine_presentation import MedicinePresentation


class CatalogSummaryRepository:
    def __init__(self, catalog_session: Session) -> None:
        self.session = catalog_session

    def count_rows(self, model) -> int:
        return self.session.scalar(select(func.count()).select_from(model)) or 0

    def count_active_medicines(self) -> int:
        return self.session.scalar(select(func.count()).where(Medicine.is_active)) or 0

    def count_active_medicines_with_leaflet(self) -> int:
        has_leaflet = exists().where(Leaflet.registration_number == Medicine.registration_number)
        return self.session.scalar(select(func.count()).where(Medicine.is_active, has_leaflet)) or 0

    def count_active_medicines_with_price(self) -> int:
        has_price = exists().where(
            MedicinePresentation.medicine_registration_number == Medicine.registration_number
        )
        return self.session.scalar(select(func.count()).where(Medicine.is_active, has_price)) or 0

    def count_active_medicines_with_leaflet_text(self) -> int:
        has_text = exists().where(LeafletDocument.registration_number == Medicine.registration_number)
        return self.session.scalar(select(func.count()).where(Medicine.is_active, has_text)) or 0

    def count_leaflet_texts(self) -> int:
        return self.count_rows(LeafletDocument)

    def count_outdated_leaflet_texts(self) -> int:
        statement = (
            select(func.count())
            .select_from(LeafletDocument)
            .join(Leaflet, Leaflet.registration_number == LeafletDocument.registration_number)
            .where(Leaflet.expedient_number.is_not(None), Leaflet.expedient_number != LeafletDocument.expedient_number)
        )
        return self.session.scalar(statement) or 0

    def count_medicines(self) -> int:
        return self.count_rows(Medicine)

    def count_leaflets(self) -> int:
        return self.count_rows(Leaflet)

    def count_presentations(self) -> int:
        return self.count_rows(MedicinePresentation)
