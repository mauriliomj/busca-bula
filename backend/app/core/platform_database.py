from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session

from app.core.database_urls import build_platform_database_url


class PlatformBase(DeclarativeBase):
    pass


@lru_cache
def get_platform_engine() -> Engine:
    return create_engine(build_platform_database_url(), pool_pre_ping=True)


def open_platform_session() -> Session:
    return Session(bind=get_platform_engine(), expire_on_commit=False)


def get_platform_session() -> Iterator[Session]:
    with open_platform_session() as session:
        yield session
