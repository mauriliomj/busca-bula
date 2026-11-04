from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.catalog_database import CatalogBase
from app.core.settings import get_settings
from app.etl.catalog_loader import replace_catalog_rows, replace_dataset_leaflet_documents
from app.etl.chatbulario_parser import parse_chatbulario_dataset
from app.etl.csv_normalization import ParsedCatalogFile
from app.etl.leaflet_index_parser import parse_leaflet_index
from app.etl.medicine_catalog_parser import parse_medicine_catalog
from app.etl.price_table_parser import parse_price_table
from app.models.catalog.leaflet import Leaflet
from app.models.catalog.medicine import Medicine
from app.models.catalog.medicine_presentation import MedicinePresentation

CHATBULARIO_SPLITS = ("train", "validation", "test")


class CatalogSource(StrEnum):
    MEDICINES = "medicines"
    LEAFLETS = "leaflets"
    PRICES = "prices"
    LEAFLET_TEXTS = "leaflet_texts"


@dataclass(frozen=True)
class CatalogDownload:
    url: str
    file_name: str


@dataclass(frozen=True)
class CatalogSourceDefinition:
    source: CatalogSource
    downloads: tuple[CatalogDownload, ...]
    parse: Callable[[list[Path]], ParsedCatalogFile]
    load: Callable[[Session, list[dict]], int]


def parse_first_file(parser: Callable[[Path], ParsedCatalogFile]) -> Callable[[list[Path]], ParsedCatalogFile]:
    def parse(paths: list[Path]) -> ParsedCatalogFile:
        return parser(paths[0])

    return parse


def replace_rows_of(model: type[CatalogBase]) -> Callable[[Session, list[dict]], int]:
    def load(session: Session, records: list[dict]) -> int:
        return replace_catalog_rows(session, model, records)

    return load


def build_catalog_source_definitions() -> dict[CatalogSource, CatalogSourceDefinition]:
    settings = get_settings()
    return {
        CatalogSource.MEDICINES: CatalogSourceDefinition(
            CatalogSource.MEDICINES,
            (CatalogDownload(settings.anvisa_medicines_url, "DADOS_ABERTOS_MEDICAMENTOS.csv"),),
            parse_first_file(parse_medicine_catalog),
            replace_rows_of(Medicine),
        ),
        CatalogSource.LEAFLETS: CatalogSourceDefinition(
            CatalogSource.LEAFLETS,
            (CatalogDownload(settings.anvisa_leaflets_url, "TA_CONSULTA_BULA_PRODUTO.CSV"),),
            parse_first_file(parse_leaflet_index),
            replace_rows_of(Leaflet),
        ),
        CatalogSource.PRICES: CatalogSourceDefinition(
            CatalogSource.PRICES,
            (CatalogDownload(settings.cmed_prices_url, "TA_PRECO_MEDICAMENTO.csv"),),
            parse_first_file(parse_price_table),
            replace_rows_of(MedicinePresentation),
        ),
        CatalogSource.LEAFLET_TEXTS: CatalogSourceDefinition(
            CatalogSource.LEAFLET_TEXTS,
            tuple(
                CatalogDownload(f"{settings.chatbulario_dataset_url}/{split}.parquet", f"chatbulario_{split}.parquet")
                for split in CHATBULARIO_SPLITS
            ),
            parse_chatbulario_dataset,
            replace_dataset_leaflet_documents,
        ),
    }
