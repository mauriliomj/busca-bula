from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy.engine import URL

from app.core.database_urls import build_platform_database_url, build_tenant_database_url

ALEMBIC_CONFIG_PATH = Path(__file__).resolve().parents[2] / "alembic.ini"


def build_alembic_config(section: str, database_url: URL) -> Config:
    config = Config(str(ALEMBIC_CONFIG_PATH), ini_section=section)
    config.attributes["database_url"] = database_url
    return config


def upgrade_platform_database() -> None:
    command.upgrade(build_alembic_config("platform", build_platform_database_url()), "head")


def upgrade_tenant_database(slug: str) -> None:
    command.upgrade(build_alembic_config("tenant", build_tenant_database_url(slug)), "head")
