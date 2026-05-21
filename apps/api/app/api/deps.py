from functools import lru_cache
from typing import Protocol

from ai_runtime import AIRuntime, DeepSeekProvider, load_runtime_settings
from admissions.providers import RuntimePredictionProvider
from admissions.schemas import AdmissionPrediction
from admissions.schemas import StudentProfile as AdmissionsProfile
from admissions.service import AdmissionsPredictionService
from app.core.config import load_api_settings
from app.persistence.database import Database
from app.persistence.repositories import (
    NullAdmissionsPredictionRepository,
    NullSOPSubmissionRepository,
    PostgresAdmissionsPredictionRepository,
    PostgresLeadRepository,
    PostgresSOPSubmissionRepository,
)
from sop_review.config import load_settings as load_sop_settings
from sop_review.providers import RuntimeReviewProvider
from sop_review.schemas import SOPGrade
from sop_review.schemas import StudentProfile as SOPProfile
from sop_review.service import SOPReviewService


class SOPSubmissionRepository(Protocol):
    def save(
        self,
        profile: SOPProfile,
        sop_text: str,
        grade: SOPGrade,
        raw_json: str,
    ) -> int: ...


class AdmissionsPredictionRepository(Protocol):
    def save_prediction(
        self,
        profile: AdmissionsProfile,
        target_programs: list[str],
        prediction: AdmissionPrediction,
    ) -> None: ...


class LeadRepository(Protocol):
    def save_lead(self, lead: dict[str, str]) -> None: ...


@lru_cache
def get_runtime() -> AIRuntime:
    settings = load_runtime_settings()
    return AIRuntime(settings, DeepSeekProvider(settings.api_key, settings.base_url))


@lru_cache
def get_database() -> Database | None:
    settings = load_api_settings()
    if settings.database_url is None:
        return None
    return Database(settings.database_url)


def get_sop_submission_repository() -> SOPSubmissionRepository:
    settings = load_api_settings()
    database = get_database()
    if settings.persistence_enabled and database is not None:
        return PostgresSOPSubmissionRepository(database)
    return NullSOPSubmissionRepository()


def get_admissions_prediction_repository() -> AdmissionsPredictionRepository:
    settings = load_api_settings()
    database = get_database()
    if settings.persistence_enabled and database is not None:
        return PostgresAdmissionsPredictionRepository(database)
    return NullAdmissionsPredictionRepository()


def get_lead_repository() -> LeadRepository | None:
    database = get_database()
    if database is not None:
        return PostgresLeadRepository(database)
    return None


def get_live_sop_service() -> SOPReviewService:
    return SOPReviewService(
        load_sop_settings(),
        RuntimeReviewProvider(get_runtime()),
        get_sop_submission_repository(),
    )


def get_live_admissions_service() -> AdmissionsPredictionService:
    return AdmissionsPredictionService(RuntimePredictionProvider(get_runtime()))
