import re
from typing import Tuple

from .config import AppSettings
from .schemas import GatekeeperResponse, StudentProfile


def sanitize_text(value: str, max_length: int = 200) -> str:
    value = (value or "").replace("\x00", " ")
    value = re.sub(r"\s+", " ", value).strip()
    value = re.sub(r"[^a-zA-Z0-9\s.,'&()\-+/]", "", value)
    return value[:max_length]


def sanitize_mobile(value: str) -> str:
    digits = re.sub(r"\D", "", (value or "").strip())
    return digits if 10 <= len(digits) <= 15 else ""


def count_words(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def validate_profile(
    full_name: str, mobile: str, university: str, intake: str, country: str
) -> Tuple[bool, StudentProfile | None, str]:
    profile = StudentProfile(
        full_name=sanitize_text(full_name, max_length=120),
        mobile=sanitize_mobile(mobile),
        university=sanitize_text(university, max_length=160),
        intake=sanitize_text(intake, max_length=80),
        country=sanitize_text(country, max_length=80),
    )
    if not profile.full_name:
        return False, None, "Full Name is required."
    if not profile.mobile:
        return False, None, "Mobile must be 10 to 15 digits."
    if not profile.university:
        return False, None, "Target University is required."
    if not profile.intake:
        return False, None, "Intake is required."
    if not profile.country:
        return False, None, "Country is required."
    return True, profile, ""


def validate_sop_text(sop_text: str, settings: AppSettings) -> None:
    if not sop_text.strip():
        raise ValueError("Provide SOP text using either 'Paste Text' or 'Upload File'.")
    if len(sop_text) > settings.max_sop_chars:
        raise ValueError(
            f"SOP text is too long. Maximum allowed length is {settings.max_sop_chars} characters."
        )


def word_count_gate(sop_text: str, settings: AppSettings) -> GatekeeperResponse | None:
    word_count = count_words(sop_text)
    if settings.min_words <= word_count <= settings.max_words:
        return None
    return GatekeeperResponse(
        is_valid=False,
        reason=(
            f"Word count is {word_count}. SOP must be between "
            f"{settings.min_words} and {settings.max_words} words."
        ),
    )
