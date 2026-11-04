from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.exceptions.domain_exceptions import DomainError

INVALID_PAYLOAD_MESSAGE = "Verifique os dados informados."


async def handle_domain_error(request: Request, error: DomainError) -> JSONResponse:
    return JSONResponse(status_code=error.status_code, content={"detail": error.message})


async def handle_validation_error(request: Request, error: RequestValidationError) -> JSONResponse:
    invalid_fields = sorted({str(issue["loc"][-1]) for issue in error.errors() if issue.get("loc")})
    return JSONResponse(
        status_code=422,
        content={"detail": INVALID_PAYLOAD_MESSAGE, "fields": invalid_fields},
    )


def register_exception_handlers(application: FastAPI) -> None:
    application.add_exception_handler(DomainError, handle_domain_error)
    application.add_exception_handler(RequestValidationError, handle_validation_error)
