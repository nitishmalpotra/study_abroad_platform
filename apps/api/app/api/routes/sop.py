from fastapi import APIRouter, Depends, Request

from sop_review.schemas import (
    CriterionFeedback,
    GatekeeperResponse,
    SOPGrade,
    StudentProfile,
)
from sop_review.service import SOPReviewService
from sop_review.validation import validate_profile
from study_abroad_contracts import SOPReviewRequest, SOPReviewResponse

from app.api.deps import get_live_sop_service
from app.core.rate_limits import client_key

router = APIRouter(prefix="/api/v1/sop", tags=["sop"])


def _profile_from_request(payload: SOPReviewRequest) -> StudentProfile:
    valid, profile, message = validate_profile(
        payload.full_name,
        payload.mobile,
        payload.university,
        payload.intake,
        payload.country,
    )
    if not valid or profile is None:
        raise ValueError(message)
    return profile


def _mock_response() -> SOPReviewResponse:
    return SOPReviewResponse(
        mode="mock",
        gatekeeper=GatekeeperResponse(
            is_valid=True, reason="Valid SOP for demo output."
        ),
        grade=SOPGrade(
            overall_score=7.8,
            criteria_breakdown=[
                CriterionFeedback(
                    name="Academic Fit",
                    score=8.0,
                    feedback="Shows relevant preparation for the chosen field.",
                ),
                CriterionFeedback(
                    name="University Specificity",
                    score=7.0,
                    feedback="Mentions program fit but could cite one concrete resource.",
                ),
                CriterionFeedback(
                    name="Career Clarity",
                    score=8.0,
                    feedback="Connects the degree to a plausible next step.",
                ),
                CriterionFeedback(
                    name="Narrative Flow",
                    score=8.0,
                    feedback="Progression is coherent and easy to follow.",
                ),
                CriterionFeedback(
                    name="Language & Tone",
                    score=8.0,
                    feedback="Clear, professional, and concise.",
                ),
            ],
            summary="A credible SOP with good fit and clear direction; the main improvement is sharper program specificity.",
        ),
    )


@router.post("/review/mock", response_model=SOPReviewResponse)
def review_mock(payload: SOPReviewRequest) -> SOPReviewResponse:
    _profile_from_request(payload)
    return _mock_response()


@router.post("/review", response_model=SOPReviewResponse)
def review_live(
    payload: SOPReviewRequest,
    request: Request,
    service: SOPReviewService = Depends(get_live_sop_service),
) -> SOPReviewResponse:
    request.app.state.live_rate_limiter.check(client_key(request))
    result = service.review(_profile_from_request(payload), payload.sop_text, "api-sop")
    return SOPReviewResponse(
        mode="live", gatekeeper=result.gatekeeper, grade=result.grade
    )
