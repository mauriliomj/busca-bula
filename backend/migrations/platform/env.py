from alembic import context
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

from app.core.database_urls import build_platform_database_url
from app.core.platform_database import PlatformBase
from app.models.platform import organization, platform_admin

config = context.config


def resolve_database_url():
    return config.attributes.get("database_url") or build_platform_database_url()


def run_migrations() -> None:
    engine = create_engine(resolve_database_url(), poolclass=NullPool)
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=PlatformBase.metadata)
        with context.begin_transaction():
            context.run_migrations()


run_migrations()
