import os
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple


DEFAULT_MODEL_CANDIDATES: Tuple[str, ...] = (
    "gemini-2.5-flash",
    "gemini-3-flash-preview",
)


@dataclass(frozen=True)
class AppSettings:
    db_path: Path
    min_words: int
    max_words: int
    max_upload_mb: int
    max_sop_chars: int
    llm_retries: int
    llm_retry_backoff_sec: float
    max_requests_per_window: int
    rate_limit_window_minutes: int
    app_env: str
    model_candidates: Tuple[str, ...]


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


def parse_model_candidates(raw_value: str) -> Tuple[str, ...]:
    models = tuple(item.strip() for item in (raw_value or "").split(",") if item.strip())
    return models or DEFAULT_MODEL_CANDIDATES


def load_settings() -> AppSettings:
    return AppSettings(
        db_path=Path(os.getenv("SOP_DB_PATH", "sop_app.db")),
        min_words=_env_int("SOP_MIN_WORDS", 100, 50, 1000),
        max_words=_env_int("SOP_MAX_WORDS", 2500, 500, 10000),
        max_upload_mb=_env_int("SOP_MAX_UPLOAD_MB", 10, 1, 50),
        max_sop_chars=_env_int("SOP_MAX_CHARS", 30000, 1000, 200000),
        llm_retries=_env_int("SOP_LLM_RETRIES", 2, 1, 5),
        llm_retry_backoff_sec=_env_float("SOP_LLM_RETRY_BACKOFF_SEC", 1.5, 0.5, 10.0),
        max_requests_per_window=_env_int("SOP_RATE_LIMIT_COUNT", 6, 1, 200),
        rate_limit_window_minutes=_env_int("SOP_RATE_LIMIT_WINDOW_MIN", 60, 1, 1440),
        app_env=os.getenv("APP_ENV", "prod").strip().lower(),
        model_candidates=parse_model_candidates(
            os.getenv("SOP_GEMINI_MODELS", ",".join(DEFAULT_MODEL_CANDIDATES))
        ),
    )
