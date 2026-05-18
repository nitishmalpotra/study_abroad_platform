from collections.abc import Callable

from fastapi import APIRouter, Depends, Request

from sop_review.config import load_settings as load_sop_settings
from sop_review.schemas import StudentProfile
from sop_review.service import SOPReviewService
from sop_review.validation import validate_profile, validate_sop_text, word_count_gate
from study_abroad_contracts import SOPReviewRequest, SOPReviewResponse
from study_abroad_contracts.examples import SOP_REVIEW_MOCK_RESPONSE

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
    return SOP_REVIEW_MOCK_RESPONSE


def get_live_sop_service_factory() -> Callable[[], SOPReviewService]:
    return get_live_sop_service


@router.post("/review/mock", response_model=SOPReviewResponse)
def review_mock(payload: SOPReviewRequest) -> SOPReviewResponse:
    _profile_from_request(payload)
    return _mock_response()


@router.post("/review", response_model=SOPReviewResponse)
def review_live(
    payload: SOPReviewRequest,
    request: Request,
    service_factory: Callable[[], SOPReviewService] = Depends(
        get_live_sop_service_factory
    ),
) -> SOPReviewResponse:
    profile = _profile_from_request(payload)
    settings = load_sop_settings()
    validate_sop_text(payload.sop_text, settings)
    local_gate = word_count_gate(payload.sop_text, settings)
    if local_gate is not None:
        return SOPReviewResponse(mode="live", gatekeeper=local_gate, grade=None)

    request.app.state.live_rate_limiter.check(client_key(request))
    result = service_factory().review(profile, payload.sop_text, "api-sop")
    return SOPReviewResponse(
        mode="live", gatekeeper=result.gatekeeper, grade=result.grade
    )
