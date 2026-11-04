import psycopg
from psycopg import sql

from app.core.settings import get_settings


class DatabaseAdministrator:
    def _connect(self, database_name: str | None = None) -> psycopg.Connection:
        settings = get_settings()
        return psycopg.connect(
            host=settings.database_host,
            port=settings.database_port,
            user=settings.database_admin_user,
            password=settings.database_admin_password,
            dbname=database_name or settings.database_maintenance_name,
            autocommit=True,
        )

    def database_exists(self, database_name: str) -> bool:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s", (database_name,)
            ).fetchone()
        return row is not None

    def role_exists(self, role_name: str) -> bool:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT 1 FROM pg_roles WHERE rolname = %s", (role_name,)
            ).fetchone()
        return row is not None

    def create_role(self, role_name: str, password: str) -> None:
        with self._connect() as connection:
            connection.execute(
                sql.SQL(
                    "CREATE ROLE {} WITH LOGIN PASSWORD {} NOSUPERUSER NOCREATEDB NOCREATEROLE"
                ).format(sql.Identifier(role_name), sql.Literal(password))
            )

    def create_database(self, database_name: str, owner: str | None = None) -> None:
        statement = sql.SQL("CREATE DATABASE {}").format(sql.Identifier(database_name))
        if owner is not None:
            statement = sql.SQL("{} OWNER {}").format(statement, sql.Identifier(owner))
        with self._connect() as connection:
            connection.execute(statement)

    def revoke_public_access(self, database_name: str) -> None:
        with self._connect() as connection:
            connection.execute(
                sql.SQL("REVOKE ALL ON DATABASE {} FROM PUBLIC").format(
                    sql.Identifier(database_name)
                )
            )

    def create_extension(self, database_name: str, extension_name: str) -> None:
        with self._connect(database_name) as connection:
            connection.execute(
                sql.SQL("CREATE EXTENSION IF NOT EXISTS {}").format(sql.Identifier(extension_name))
            )

    def drop_database(self, database_name: str) -> None:
        with self._connect() as connection:
            connection.execute(
                sql.SQL("DROP DATABASE IF EXISTS {} WITH (FORCE)").format(
                    sql.Identifier(database_name)
                )
            )

    def drop_role(self, role_name: str) -> None:
        with self._connect() as connection:
            connection.execute(
                sql.SQL("DROP ROLE IF EXISTS {}").format(sql.Identifier(role_name))
            )

    def list_databases_with_prefix(self, prefix: str) -> list[str]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT datname FROM pg_database WHERE starts_with(datname, %s)", (prefix,)
            ).fetchall()
        return [row[0] for row in rows]

    def list_roles_with_prefix(self, prefix: str) -> list[str]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT rolname FROM pg_roles WHERE starts_with(rolname, %s)", (prefix,)
            ).fetchall()
        return [row[0] for row in rows]
