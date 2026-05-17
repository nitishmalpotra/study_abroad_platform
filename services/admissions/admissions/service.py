from dataclasses import dataclass
from typing import Protocol

from .persistence import PredictionRepository
from .postprocessing import (
    align_predictions_to_targets,
    enforce_alternative_recommendations,
)
from .schemas import AdmissionPrediction, StudentProfile


class PredictionProvider(Protocol):
    def predict(
        self, profile: StudentProfile, target_programs: list[str]
    ) -> tuple[AdmissionPrediction, str]: ...


@dataclass(frozen=True)
class AdmissionsPredictionResult:
    prediction: AdmissionPrediction
    raw_output: str


class AdmissionsPredictionService:
    def __init__(
        self,
        provider: PredictionProvider,
        repository: PredictionRepository | None = None,
    ) -> None:
        self.provider = provider
        self.repository = repository

    def predict(
        self, profile: StudentProfile, target_programs: list[str]
    ) -> AdmissionsPredictionResult:
        prediction, raw_output = self.provider.predict(profile, target_programs)
        aligned = align_predictions_to_targets(prediction, target_programs)
        post_processed = enforce_alternative_recommendations(aligned, target_programs)
        if self.repository is not None:
            self.repository.save(profile, target_programs, raw_output)
        return AdmissionsPredictionResult(post_processed, raw_output)
