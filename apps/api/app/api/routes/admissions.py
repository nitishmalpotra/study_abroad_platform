from fastapi import APIRouter, Depends, Request

from admissions.schemas import AdmissionPrediction, ProgramPrediction, StudentProfile
from admissions.service import AdmissionsPredictionService
from study_abroad_contracts import (
    AdmissionPredictionResponse,
    AdmissionsPredictionRequest,
)

from app.api.deps import get_live_admissions_service
from app.core.rate_limits import client_key

router = APIRouter(prefix="/api/v1/admissions", tags=["admissions"])


def _profile_from_request(payload: AdmissionsPredictionRequest) -> StudentProfile:
    if payload.cgpa > payload.cgpa_scale:
        raise ValueError("cgpa cannot exceed cgpa_scale.")
    if payload.gre_score is not None and not 260 <= payload.gre_score <= 340:
        raise ValueError("gre_score must be between 260 and 340.")
    if payload.gmat_score is not None and not 200 <= payload.gmat_score <= 805:
        raise ValueError("gmat_score must be between 200 and 805.")
    if payload.english_test not in {None, "IELTS", "TOEFL"}:
        raise ValueError("english_test must be IELTS, TOEFL, or null.")
    if payload.english_test == "IELTS" and (
        payload.english_score is None or not 0 <= payload.english_score <= 9
    ):
        raise ValueError("IELTS english_score must be between 0 and 9.")
    if payload.english_test == "TOEFL" and (
        payload.english_score is None or not 0 <= payload.english_score <= 120
    ):
        raise ValueError("TOEFL english_score must be between 0 and 120.")
    if payload.english_test is None and payload.english_score is not None:
        raise ValueError("english_test is required when english_score is provided.")
    return StudentProfile(**payload.model_dump(exclude={"target_programs"}))


def _mock_response(payload: AdmissionsPredictionRequest) -> AdmissionPredictionResponse:
    first_program = payload.target_programs[0]
    return AdmissionPredictionResponse(
        mode="mock",
        prediction=AdmissionPrediction(
            target_predictions=[
                ProgramPrediction(
                    program_name=first_program,
                    chance_category="Target",
                    estimated_probability_percentage=62,
                    brief_reasoning="Profile is competitive for this target with room to strengthen evidence.",
                )
            ],
            profile_strengths=[
                "Relevant academic background",
                "Clear target direction",
                "Balanced profile for the intended intake",
            ],
            profile_weaknesses=[
                "Limited differentiating evidence",
                "Recommendations could be stronger",
                "Target list may need broader spread",
            ],
            actionable_roadmap=[
                "Add one concrete project or research outcome",
                "Refine the SOP around program fit",
                "Include one safer alternative program",
            ],
            recommended_universities=[
                "Northeastern University (MS CS): Strong applied curriculum.",
                "Arizona State University (MS CS): Broad opportunity set.",
                "University at Buffalo, SUNY (MS CS): Balanced selectivity.",
            ],
        ),
    )


@router.post("/predict/mock", response_model=AdmissionPredictionResponse)
def predict_mock(payload: AdmissionsPredictionRequest) -> AdmissionPredictionResponse:
    _profile_from_request(payload)
    return _mock_response(payload)


@router.post("/predict", response_model=AdmissionPredictionResponse)
def predict_live(
    payload: AdmissionsPredictionRequest,
    request: Request,
    service: AdmissionsPredictionService = Depends(get_live_admissions_service),
) -> AdmissionPredictionResponse:
    request.app.state.live_rate_limiter.check(client_key(request))
    profile = _profile_from_request(payload)
    result = service.predict(profile, payload.target_programs)
    return AdmissionPredictionResponse(mode="live", prediction=result.prediction)
