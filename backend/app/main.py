from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.controllers import (
    auth_controller,
    health_controller,
    member_controller,
    organization_controller,
    platform_controller,
    user_controller,
)
from app.core.platform_database import get_platform_engine
from app.core.tenant_database import tenant_engine_registry
from app.exceptions.exception_handlers import register_exception_handlers


@asynccontextmanager
async def release_database_connections(application: FastAPI) -> AsyncIterator[None]:
    yield
    tenant_engine_registry.dispose_all_engines()
    get_platform_engine().dispose()


def create_application() -> FastAPI:
    application = FastAPI(title="Busca Bula API", lifespan=release_database_connections)
    register_exception_handlers(application)
    for controller in (
        health_controller,
        organization_controller,
        auth_controller,
        user_controller,
        member_controller,
        platform_controller,
    ):
        application.include_router(controller.router)
    return application


app = create_application()
