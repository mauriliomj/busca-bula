import argparse
import logging

from app.core.catalog_database import open_catalog_writer_session
from app.etl.catalog_sources import CatalogSource
from app.exceptions.domain_exceptions import CatalogImportAlreadyRunningError
from app.models.catalog.catalog_import import CatalogImportStatus
from app.services.catalog_import_service import CatalogImportService


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Importa o catálogo de medicamentos, bulas e preços da ANVISA.")
    parser.add_argument(
        "--source",
        action="append",
        choices=[source.value for source in CatalogSource],
        help="Fonte a importar. Pode ser repetido. Sem esta opção, importa todas.",
    )
    return parser.parse_args()


def import_catalog() -> None:
    arguments = parse_arguments()
    sources = [CatalogSource(source) for source in arguments.source] if arguments.source else None
    with open_catalog_writer_session() as catalog_writer_session:
        service = CatalogImportService(catalog_writer_session)
        try:
            catalog_imports = service.start_imports(sources)
        except CatalogImportAlreadyRunningError as error:
            raise SystemExit(error.message) from error
        service.run_imports([catalog_import.id for catalog_import in catalog_imports])
    failed_sources = [item.source for item in catalog_imports if item.status == CatalogImportStatus.FAILED]
    for catalog_import in catalog_imports:
        print(f"{catalog_import.source}: {catalog_import.status} ({catalog_import.rows_loaded or 0} registros)")
    if failed_sources:
        raise SystemExit(f"Falha ao importar: {', '.join(failed_sources)}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="[busca-bula] %(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)
    import_catalog()
