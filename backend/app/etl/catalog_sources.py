from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from app.core.catalog_database import CatalogBase
from app.core.settings import get_settings
from app.etl.csv_normalization import ParsedCatalogFile
from app.etl.leaflet_index_parser import parse_leaflet_index
from app.etl.medicine_catalog_parser import parse_medicine_catalog
from app.etl.price_table_parser import parse_price_table
from app.models.catalog.leaflet import Leaflet
from app.models.catalog.medicine import Medicine
from app.models.catalog.medicine_presentation import MedicinePresentation


class CatalogSource(StrEnum):
    MEDICINES = "medicines"
    LEAFLETS = "leaflets"
    PRICES = "prices"


@dataclass(frozen=True)
class CatalogSourceDefinition:
    source: CatalogSource
    url: str
    file_name: str
    parse: Callable[[Path], ParsedCatalogFile]
    model: type[CatalogBase]


def build_catalog_source_definitions() -> dict[CatalogSource, CatalogSourceDefinition]:
    settings = get_settings()
    return {
        CatalogSource.MEDICINES: CatalogSourceDefinition(
            CatalogSource.MEDICINES,
            settings.anvisa_medicines_url,
            "DADOS_ABERTOS_MEDICAMENTOS.csv",
            parse_medicine_catalog,
            Medicine,
        ),
        CatalogSource.LEAFLETS: CatalogSourceDefinition(
            CatalogSource.LEAFLETS,
            settings.anvisa_leaflets_url,
            "TA_CONSULTA_BULA_PRODUTO.CSV",
            parse_leaflet_index,
            Leaflet,
        ),
        CatalogSource.PRICES: CatalogSourceDefinition(
            CatalogSource.PRICES,
            settings.cmed_prices_url,
            "TA_PRECO_MEDICAMENTO.csv",
            parse_price_table,
            MedicinePresentation,
        ),
    }
