from dataclasses import dataclass
from typing import Protocol, Tuple

from .config import AppSettings
from .schemas import GatekeeperResponse, SOPGrade, StudentProfile
from .validation import validate_sop_text, word_count_gate


class ReviewProvider(Protocol):
    def gatekeep(self, sop_text: str, request_id: str) -> Tuple[GatekeeperResponse, str]: ...

    def grade(
        self, sop_text: str, university: str, country: str, request_id: str
    ) -> Tuple[SOPGrade, str, str]: ...


class SubmissionRepository(Protocol):
    def save(
        self, profile: StudentProfile, sop_text: str, grade: SOPGrade, raw_json: str
    ) -> int: ...


@dataclass(frozen=True)
class SOPReviewResult:
    gatekeeper: GatekeeperResponse
    gatekeeper_model: str
    grade: SOPGrade | None
    grading_model: str | None
    raw_json: str | None
    submission_id: int | None


class SOPReviewService:
    def __init__(
        self,
        settings: AppSettings,
        provider: ReviewProvider,
        repository: SubmissionRepository,
    ) -> None:
        self.settings = settings
        self.provider = provider
        self.repository = repository

    def review(
        self, profile: StudentProfile, sop_text: str, request_id: str
    ) -> SOPReviewResult:
        validate_sop_text(sop_text, self.settings)
        local_gate = word_count_gate(sop_text, self.settings)
        if local_gate is not None:
            return SOPReviewResult(local_gate, "local-word-count", None, None, None, None)

        gatekeeper, gatekeeper_model = self.provider.gatekeep(sop_text, request_id)
        if not gatekeeper.is_valid:
            return SOPReviewResult(gatekeeper, gatekeeper_model, None, None, None, None)

        grade, raw_json, grading_model = self.provider.grade(
            sop_text, profile.university, profile.country, request_id
        )
        submission_id = self.repository.save(profile, sop_text, grade, raw_json)
        return SOPReviewResult(
            gatekeeper,
            gatekeeper_model,
            grade,
            grading_model,
            raw_json,
            submission_id,
        )
