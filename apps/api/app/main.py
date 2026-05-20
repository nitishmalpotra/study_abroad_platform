from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import admissions, health, sop
from app.core.config import load_api_settings
from app.core.errors import register_error_handlers
from app.core.logging import RequestLoggingMiddleware
from app.core.middleware import RequestGuardMiddleware
from app.core.rate_limits import InMemoryRateLimiter, PostgresRateLimiter
from app.persistence.database import Database


def create_app() -> FastAPI:
    app = FastAPI(
        title="Study Abroad Platform API",
        version="0.1.0",
        description="Public API for SOP review and admissions prediction.",
    )
    settings = load_api_settings()
    app.state.settings = settings
    if settings.rate_limit_store == "postgres":
        if settings.database_url is None:
            raise RuntimeError("DATABASE_URL is required for Postgres rate limiting.")
        app.state.live_rate_limiter = PostgresRateLimiter(
            settings, Database(settings.database_url)
        )
    else:
        app.state.live_rate_limiter = InMemoryRateLimiter(settings)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type"],
    )
    app.add_middleware(
        RequestGuardMiddleware,
        max_body_bytes=settings.max_request_body_bytes,
    )
    app.add_middleware(RequestLoggingMiddleware)
    register_error_handlers(app)
    app.include_router(health.router)
    app.include_router(sop.router)
    app.include_router(admissions.router)
    return app


app = create_app()
