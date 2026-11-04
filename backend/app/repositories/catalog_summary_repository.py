from sqlalchemy import exists, func, select
from sqlalchemy.orm import Session

from app.models.catalog.leaflet import Leaflet
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

    def count_medicines(self) -> int:
        return self.count_rows(Medicine)

    def count_leaflets(self) -> int:
        return self.count_rows(Leaflet)

    def count_presentations(self) -> int:
        return self.count_rows(MedicinePresentation)
