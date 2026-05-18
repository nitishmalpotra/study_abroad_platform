import os
from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class ApiSettings:
    live_rate_limit_count: int
    live_rate_limit_window_seconds: int
    cors_origins: Tuple[str, ...]


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


def load_api_settings() -> ApiSettings:
    return ApiSettings(
        live_rate_limit_count=_env_int("API_LIVE_RATE_LIMIT_COUNT", 6, 1, 1000),
        live_rate_limit_window_seconds=_env_int(
            "API_LIVE_RATE_LIMIT_WINDOW_SECONDS", 3600, 1, 86400
        ),
        cors_origins=_env_list(
            "API_CORS_ORIGINS",
            "http://localhost:3000,http://127.0.0.1:3000",
        ),
    )
