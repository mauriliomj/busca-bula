from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session

from app.core.database_urls import build_catalog_reader_url, build_catalog_writer_url


class CatalogBase(DeclarativeBase):
    pass


@lru_cache
def get_catalog_writer_engine() -> Engine:
    return create_engine(build_catalog_writer_url(), pool_size=2, max_overflow=2, pool_pre_ping=True)


@lru_cache
def get_catalog_reader_engine() -> Engine:
    return create_engine(build_catalog_reader_url(), pool_pre_ping=True)


def open_catalog_writer_session() -> Session:
    return Session(bind=get_catalog_writer_engine(), expire_on_commit=False)


def open_catalog_reader_session() -> Session:
    return Session(bind=get_catalog_reader_engine(), expire_on_commit=False)


def get_catalog_writer_session() -> Iterator[Session]:
    with open_catalog_writer_session() as session:
        yield session


def get_catalog_reader_session() -> Iterator[Session]:
    with open_catalog_reader_session() as session:
        yield session


def dispose_catalog_engines() -> None:
    for engine_factory in (get_catalog_writer_engine, get_catalog_reader_engine):
        if engine_factory.cache_info().currsize:
            engine_factory().dispose()
        engine_factory.cache_clear()
