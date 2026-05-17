import os

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from .utils import sanitize_text


FALLBACK_RECOMMENDATIONS = [
    "Northeastern University (MS CS): Strong co-op ecosystem and industry-aligned curriculum.",
    "Arizona State University (MS CS): Broad intake capacity with solid applied research opportunities.",
    "University at Buffalo, SUNY (MS CS): Balanced selectivity with a good ROI for international students.",
]


class AppSettings(BaseModel):
    google_api_key: str = Field(..., min_length=20)
    gemini_model: str = Field(default="gemini-1.5-pro", min_length=1, max_length=120)
    llm_timeout_seconds: int = Field(default=45, ge=10, le=180)
    llm_retry_attempts: int = Field(default=2, ge=0, le=5)
    model_config = ConfigDict(extra="forbid")

    @field_validator("google_api_key")
    @classmethod
    def validate_google_key(cls, value: str) -> str:
        cleaned = sanitize_text(value)
        if not cleaned:
            raise ValueError("GOOGLE_API_KEY is required.")
        return cleaned

    @field_validator("gemini_model")
    @classmethod
    def validate_model_name(cls, value: str) -> str:
        cleaned = sanitize_text(value)
        if not cleaned:
            raise ValueError("GEMINI_MODEL is required.")
        return cleaned


def load_settings() -> AppSettings:
    raw_timeout = sanitize_text(os.getenv("LLM_TIMEOUT_SECONDS", "45"))
    raw_retries = sanitize_text(os.getenv("LLM_RETRY_ATTEMPTS", "2"))
    model_name = sanitize_text(os.getenv("GEMINI_MODEL", "gemini-1.5-pro"))

    try:
        timeout_seconds = int(raw_timeout)
        retry_attempts = int(raw_retries)
    except ValueError as exc:
        raise RuntimeError("LLM_TIMEOUT_SECONDS and LLM_RETRY_ATTEMPTS must be integers.") from exc

    try:
        return AppSettings(
            google_api_key=sanitize_text(os.getenv("GOOGLE_API_KEY", "")),
            gemini_model=model_name or "gemini-1.5-pro",
            llm_timeout_seconds=timeout_seconds,
            llm_retry_attempts=retry_attempts,
        )
    except ValidationError as exc:
        raise RuntimeError(f"Invalid runtime configuration: {sanitize_text(str(exc))}") from exc
