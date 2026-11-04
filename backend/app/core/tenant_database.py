from threading import Lock

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session

from app.core.database_urls import build_tenant_database_url


class TenantBase(DeclarativeBase):
    pass


class TenantEngineRegistry:
    def __init__(self) -> None:
        self._engines: dict[str, Engine] = {}
        self._lock = Lock()

    def get_engine(self, slug: str) -> Engine:
        with self._lock:
            if slug not in self._engines:
                self._engines[slug] = create_engine(
                    build_tenant_database_url(slug),
                    pool_size=2,
                    max_overflow=3,
                    pool_pre_ping=True,
                )
            return self._engines[slug]

    def dispose_engine(self, slug: str) -> None:
        with self._lock:
            engine = self._engines.pop(slug, None)
        if engine is not None:
            engine.dispose()

    def dispose_all_engines(self) -> None:
        with self._lock:
            engines = list(self._engines.values())
            self._engines.clear()
        for engine in engines:
            engine.dispose()


tenant_engine_registry = TenantEngineRegistry()


def open_tenant_session(slug: str) -> Session:
    return Session(bind=tenant_engine_registry.get_engine(slug), expire_on_commit=False)
