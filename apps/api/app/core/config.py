import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ApiSettings:
    live_rate_limit_count: int
    live_rate_limit_window_seconds: int


def _env_int(name: str, default: int, min_value: int, max_value: int) -> int:
    try:
        value = int(os.getenv(name, str(default)))
    except ValueError:
        return default
    return max(min_value, min(value, max_value))


def load_api_settings() -> ApiSettings:
    return ApiSettings(
        live_rate_limit_count=_env_int("API_LIVE_RATE_LIMIT_COUNT", 6, 1, 1000),
        live_rate_limit_window_seconds=_env_int(
            "API_LIVE_RATE_LIMIT_WINDOW_SECONDS", 3600, 1, 86400
        ),
    )
