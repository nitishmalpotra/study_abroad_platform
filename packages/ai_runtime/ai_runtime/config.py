import os
from dataclasses import dataclass


DEFAULT_MODEL = "deepseek-chat"


@dataclass(frozen=True)
class RuntimeSettings:
    api_key: str
    model_candidates: tuple[str, ...]
    base_url: str
    timeout_seconds: float
    retry_attempts: int
    retry_backoff_seconds: float


def _env_int(name: str, default: int, min_value: int, max_value: int) -> int:
    try:
        value = int(os.getenv(name, str(default)))
    except ValueError:
        return default
    return max(min_value, min(value, max_value))


def _env_float(name: str, default: float, min_value: float, max_value: float) -> float:
    try:
        value = float(os.getenv(name, str(default)))
    except ValueError:
        return default
    return max(min_value, min(value, max_value))


def _model_candidates() -> tuple[str, ...]:
    configured = os.getenv("DEEPSEEK_MODELS", "")
    candidates = tuple(item.strip() for item in configured.split(",") if item.strip())
    if candidates:
        return candidates
    model = os.getenv("DEEPSEEK_MODEL", DEFAULT_MODEL).strip()
    return (model or DEFAULT_MODEL,)


def load_runtime_settings() -> RuntimeSettings:
    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("DEEPSEEK_API_KEY is missing. Add it to your .env file.")
    return RuntimeSettings(
        api_key=api_key,
        model_candidates=_model_candidates(),
        base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/"),
        timeout_seconds=_env_float("LLM_TIMEOUT_SECONDS", 45.0, 1.0, 180.0),
        retry_attempts=_env_int("LLM_RETRY_ATTEMPTS", 2, 0, 5),
        retry_backoff_seconds=_env_float("LLM_RETRY_BACKOFF_SECONDS", 1.0, 0.0, 10.0),
    )
