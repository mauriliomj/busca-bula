from alembic import context
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

from app.core.database_urls import build_tenant_database_url
from app.core.tenant_database import TenantBase
from app.models.tenant import user

config = context.config


def resolve_database_url():
    if "database_url" in config.attributes:
        return config.attributes["database_url"]
    slug = context.get_x_argument(as_dictionary=True).get("organization")
    if not slug:
        raise SystemExit("Informe a organização com: alembic -n tenant -x organization=<slug> ...")
    return build_tenant_database_url(slug)


def run_migrations() -> None:
    engine = create_engine(resolve_database_url(), poolclass=NullPool)
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=TenantBase.metadata)
        with context.begin_transaction():
            context.run_migrations()


run_migrations()
