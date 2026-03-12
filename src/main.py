import logging
import logging.config

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from src.infrastructure.config import get_settings
from src.interfaces.http.controllers import auth_router, user_router
from src.interfaces.http.middlewares.exception_handler import register_exception_handlers

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"],
    },
    "loggers": {
        "uvicorn": {"propagate": True},
        "sqlalchemy.engine": {"level": "WARNING", "propagate": True},
    },
}


def create_app() -> FastAPI:
    logging.config.dictConfig(LOGGING_CONFIG)
    settings = get_settings()

    limiter = Limiter(key_func=get_remote_address)

    app = FastAPI(
        title="Authentication Service",
        version="1.0.0",
        description="Two-factor authentication service with JWT tokens",
        docs_url="/docs",
        redoc_url="/redoc",
        swagger_ui_parameters={"persistAuthorization": True},
        openapi_tags=[
            {"name": "Authentication", "description": "Registration, login, and token management"},
            {"name": "Users", "description": "User profile operations"},
        ],
    )

    # Rate limiter
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Domain exception handlers (before generic ones)
    register_exception_handlers(app)

    # Routers
    app.include_router(auth_router)
    app.include_router(user_router)

    @app.get("/health", tags=["Health"], include_in_schema=False)
    async def health() -> dict:
        return {"status": "ok"}

    return app


app = create_app()
