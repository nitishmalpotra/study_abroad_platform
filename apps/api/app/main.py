from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import admissions, health, sop
from app.core.config import load_api_settings
from app.core.errors import register_error_handlers
from app.core.rate_limits import InMemoryRateLimiter


def create_app() -> FastAPI:
    app = FastAPI(
        title="Study Abroad Platform API",
        version="0.1.0",
        description="Public API for SOP review and admissions prediction.",
    )
    settings = load_api_settings()
    app.state.live_rate_limiter = InMemoryRateLimiter(settings)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type"],
    )
    register_error_handlers(app)
    app.include_router(health.router)
    app.include_router(sop.router)
    app.include_router(admissions.router)
    return app


app = create_app()
