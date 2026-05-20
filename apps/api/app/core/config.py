import os
from dataclasses import dataclass
from typing import Literal, Tuple


@dataclass(frozen=True)
class ApiSettings:
    live_rate_limit_count: int
    live_rate_limit_window_seconds: int
    cors_origins: Tuple[str, ...]
    max_request_body_bytes: int = 64_000
    trust_proxy_headers: bool = False
    database_url: str | None = None
    persistence_enabled: bool = False
    rate_limit_store: Literal["memory", "postgres"] = "memory"
    rate_limit_hash_salt: str | None = None


def _env_int(name: str, default: int, min_value: int, max_value: int) -> int:
    try:
        value = int(os.getenv(name, str(default)))
    except ValueError:
        return default
    return max(min_value, min(value, max_value))


def _env_list(name: str, default: str) -> Tuple[str, ...]:
    raw = os.getenv(name, default)
    values = tuple(value.strip() for value in raw.split(",") if value.strip())
    return values or tuple(value.strip() for value in default.split(",") if value.strip())


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _env_rate_limit_store(name: str, default: str) -> Literal["memory", "postgres"]:
    raw = os.getenv(name, default).strip().lower()
    if raw == "postgres":
        return "postgres"
    return "memory"


def load_api_settings() -> ApiSettings:
    database_url = os.getenv("DATABASE_URL", "").strip() or None
    persistence_enabled = _env_bool("API_PERSISTENCE_ENABLED", database_url is not None)
    return ApiSettings(
        live_rate_limit_count=_env_int("API_LIVE_RATE_LIMIT_COUNT", 6, 1, 1000),
        live_rate_limit_window_seconds=_env_int(
            "API_LIVE_RATE_LIMIT_WINDOW_SECONDS", 3600, 1, 86400
        ),
        cors_origins=_env_list(
            "API_CORS_ORIGINS",
            "http://localhost:3000,http://127.0.0.1:3000",
        ),
        max_request_body_bytes=_env_int(
            "API_MAX_REQUEST_BODY_BYTES", 64_000, 1_000, 1_000_000
        ),
        trust_proxy_headers=_env_bool("API_TRUST_PROXY_HEADERS", False),
        database_url=database_url,
        persistence_enabled=persistence_enabled,
        rate_limit_store=_env_rate_limit_store("API_RATE_LIMIT_STORE", "memory"),
        rate_limit_hash_salt=os.getenv("API_RATE_LIMIT_HASH_SALT", "").strip() or None,
    )
