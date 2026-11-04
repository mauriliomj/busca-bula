import logging

from app.core.database_migrations import upgrade_platform_database, upgrade_tenant_database
from app.core.platform_database import open_platform_session
from app.models.platform.organization import OrganizationStatus
from app.repositories.organization_repository import OrganizationRepository

logger = logging.getLogger("busca_bula.migrations")


def list_provisioned_organization_slugs() -> list[str]:
    with open_platform_session() as platform_session:
        organizations = OrganizationRepository(platform_session).list_all()
    return [
        organization.slug
        for organization in organizations
        if organization.status != OrganizationStatus.PROVISIONING
    ]


def migrate_all_databases() -> None:
    upgrade_platform_database()
    logger.info("Banco da plataforma atualizado.")
    for slug in list_provisioned_organization_slugs():
        upgrade_tenant_database(slug)
        logger.info("Banco da organização %s atualizado.", slug)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="[busca-bula] %(message)s")
    migrate_all_databases()
