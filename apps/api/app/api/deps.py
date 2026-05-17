from functools import lru_cache

from ai_runtime import AIRuntime, DeepSeekProvider, load_runtime_settings
from admissions.providers import RuntimePredictionProvider
from admissions.service import AdmissionsPredictionService
from sop_review.config import load_settings as load_sop_settings
from sop_review.providers import RuntimeReviewProvider
from sop_review.schemas import SOPGrade, StudentProfile
from sop_review.service import SOPReviewService


class NoOpSubmissionRepository:
    def save(
        self,
        profile: StudentProfile,
        sop_text: str,
        grade: SOPGrade,
        raw_json: str,
    ) -> int:
        return 0


@lru_cache
def get_runtime() -> AIRuntime:
    settings = load_runtime_settings()
    return AIRuntime(settings, DeepSeekProvider(settings.api_key, settings.base_url))


def get_live_sop_service() -> SOPReviewService:
    return SOPReviewService(
        load_sop_settings(),
        RuntimeReviewProvider(get_runtime()),
        NoOpSubmissionRepository(),
    )


def get_live_admissions_service() -> AdmissionsPredictionService:
    return AdmissionsPredictionService(RuntimePredictionProvider(get_runtime()))
