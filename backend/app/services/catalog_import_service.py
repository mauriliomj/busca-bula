import logging
from datetime import UTC, datetime, timedelta
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.catalog_database import open_catalog_writer_session
from app.etl.anvisa_download import AnvisaFileDownloader
from app.etl.catalog_sources import CatalogSource, CatalogSourceDefinition, build_catalog_source_definitions
from app.exceptions.domain_exceptions import CatalogImportAlreadyRunningError
from app.models.catalog.catalog_import import CatalogImport, CatalogImportStatus
from app.repositories.catalog_import_repository import CatalogImportRepository

logger = logging.getLogger("busca_bula.catalog")

STALE_IMPORT_TIMEOUT = timedelta(hours=2)
MAXIMUM_ERROR_MESSAGE_LENGTH = 500
INTERRUPTED_IMPORT_MESSAGE = "Sincronização interrompida antes de terminar."


def download_catalog_source_files(definition: CatalogSourceDefinition) -> list[Path]:
    downloader = AnvisaFileDownloader()
    return [downloader.download(download.url, download.file_name) for download in definition.downloads]


def summarize_error(error: Exception) -> str:
    return f"{type(error).__name__}: {error}"[:MAXIMUM_ERROR_MESSAGE_LENGTH]


class CatalogImportService:
    def __init__(self, catalog_writer_session: Session) -> None:
        self.session = catalog_writer_session
        self.catalog_import_repository = CatalogImportRepository(catalog_writer_session)
        self.source_definitions = build_catalog_source_definitions()

    def start_imports(self, sources: list[CatalogSource] | None = None) -> list[CatalogImport]:
        self.fail_stale_imports()
        if self.catalog_import_repository.list_running():
            raise CatalogImportAlreadyRunningError()
        selected_sources = sources or list(CatalogSource)
        catalog_imports = [
            CatalogImport(source=source, status=CatalogImportStatus.RUNNING) for source in selected_sources
        ]
        return self.catalog_import_repository.save_all(catalog_imports)

    def fail_stale_imports(self) -> None:
        now = datetime.now(UTC)
        stale_imports = [
            catalog_import
            for catalog_import in self.catalog_import_repository.list_running()
            if now - catalog_import.started_at > STALE_IMPORT_TIMEOUT
        ]
        for catalog_import in stale_imports:
            self.catalog_import_repository.mark_finished(
                catalog_import, CatalogImportStatus.FAILED, now, INTERRUPTED_IMPORT_MESSAGE
            )
        if stale_imports:
            self.session.commit()

    def run_imports(self, import_ids: list[int]) -> list[CatalogImport]:
        catalog_imports = self.catalog_import_repository.find_by_ids(import_ids)
        for catalog_import in catalog_imports:
            self.run_import(catalog_import)
        return catalog_imports

    def run_import(self, catalog_import: CatalogImport) -> None:
        definition = self.source_definitions[CatalogSource(catalog_import.source)]
        try:
            parsed_file = definition.parse(download_catalog_source_files(definition))
            rows_loaded = definition.load(self.session, parsed_file.records)
            catalog_import.rows_read = parsed_file.rows_read
            catalog_import.rows_loaded = rows_loaded
            self.catalog_import_repository.mark_finished(
                catalog_import, CatalogImportStatus.SUCCEEDED, datetime.now(UTC)
            )
            self.session.commit()
            logger.info("Fonte %s importada: %s registros.", catalog_import.source, rows_loaded)
        except Exception as error:
            self.session.rollback()
            logger.exception("Falha ao importar a fonte %s.", catalog_import.source)
            self.catalog_import_repository.mark_finished(
                catalog_import, CatalogImportStatus.FAILED, datetime.now(UTC), summarize_error(error)
            )
            self.session.commit()


def run_catalog_imports_in_background(import_ids: list[int]) -> None:
    with open_catalog_writer_session() as catalog_writer_session:
        CatalogImportService(catalog_writer_session).run_imports(import_ids)
