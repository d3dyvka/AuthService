import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.domain.exceptions import (
    DomainException,
    InvalidCredentialsException,
    InvalidPasswordException,
    InvalidTokenException,
    InvalidVerificationCodeException,
    TooManyAttemptsException,
    UserAlreadyExistsException,
    UserNotActiveException,
    UserNotFoundException,
)

logger = logging.getLogger(__name__)

EXCEPTION_STATUS_MAP: dict[type[DomainException], int] = {
    UserAlreadyExistsException: 409,
    UserNotFoundException: 404,
    UserNotActiveException: 403,
    InvalidCredentialsException: 401,
    InvalidVerificationCodeException: 400,
    TooManyAttemptsException: 429,
    InvalidTokenException: 401,
    InvalidPasswordException: 400,
}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainException)
    async def domain_exception_handler(request: Request, exc: DomainException) -> JSONResponse:
        status_code = EXCEPTION_STATUS_MAP.get(type(exc), 400)
        logger.warning(
            "Domain exception [%s] %s on %s %s",
            exc.error_code,
            exc.message,
            request.method,
            request.url.path,
        )
        return JSONResponse(
            status_code=status_code,
            content={"error": exc.error_code, "message": exc.message},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error(
            "Unhandled exception on %s %s",
            request.method,
            request.url.path,
            exc_info=True,
        )
        return JSONResponse(
            status_code=500,
            content={"error": "internal_server_error", "message": "An unexpected error occurred"},
        )
