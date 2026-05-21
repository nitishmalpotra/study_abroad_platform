import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppSettings:
    db_path: Path
    min_words: int
    max_words: int
    max_upload_mb: int
    max_sop_chars: int
    max_requests_per_window: int
    rate_limit_window_minutes: int
    app_env: str


def _env_int(name: str, default: int, min_value: int, max_value: int) -> int:
    raw = os.getenv(name, str(default))
    try:
        parsed = int(raw)
    except ValueError:
        return default
    return max(min_value, min(parsed, max_value))


def _env_float(name: str, default: float, min_value: float, max_value: float) -> float:
    raw = os.getenv(name, str(default))
    try:
        parsed = float(raw)
    except ValueError:
        return default
    return max(min_value, min(parsed, max_value))


def load_settings() -> AppSettings:
    return AppSettings(
        db_path=Path(os.getenv("SOP_DB_PATH", "sop_app.db")),
        min_words=_env_int("SOP_MIN_WORDS", 100, 50, 1000),
        max_words=_env_int("SOP_MAX_WORDS", 2500, 500, 10000),
        max_upload_mb=_env_int("SOP_MAX_UPLOAD_MB", 10, 1, 50),
        max_sop_chars=_env_int("SOP_MAX_CHARS", 30000, 1000, 200000),
        max_requests_per_window=_env_int("SOP_RATE_LIMIT_COUNT", 6, 1, 200),
        rate_limit_window_minutes=_env_int("SOP_RATE_LIMIT_WINDOW_MIN", 60, 1, 1440),
        app_env=os.getenv("APP_ENV", "prod").strip().lower(),
    )
