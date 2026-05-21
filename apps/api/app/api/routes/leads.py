from collections.abc import Callable

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, field_validator

from app.api.deps import LeadRepository, get_lead_repository

router = APIRouter(prefix="/api/v1", tags=["leads"])

_MAX_FIELD = 200


class LeadRequest(BaseModel):
    tool_name: str = Field(min_length=1, max_length=_MAX_FIELD)
    phone: str = Field(min_length=5, max_length=40)
    email: str = Field(min_length=5, max_length=_MAX_FIELD)
    target_country: str = Field(min_length=1, max_length=_MAX_FIELD)
    journey_stage: str = Field(min_length=1, max_length=_MAX_FIELD)
    target_intake: str = Field(default="", max_length=_MAX_FIELD)
    target_college: str = Field(default="", max_length=_MAX_FIELD)
    target_course: str = Field(default="", max_length=_MAX_FIELD)

    @field_validator("email")
    @classmethod
    def _email_has_at(cls, value: str) -> str:
        if "@" not in value:
            raise ValueError("email must contain '@'")
        return value

    @field_validator("phone")
    @classmethod
    def _phone_has_enough_digits(cls, value: str) -> str:
        if sum(character.isdigit() for character in value) < 7:
            raise ValueError("phone must contain at least 7 digits")
        return value


class LeadResponse(BaseModel):
    status: str = "ok"


def get_lead_repository_factory() -> Callable[[], LeadRepository | None]:
    return get_lead_repository


@router.post("/leads", response_model=LeadResponse)
def create_lead(
    payload: LeadRequest,
    repository_factory: Callable[[], LeadRepository | None] = Depends(
        get_lead_repository_factory
    ),
) -> LeadResponse:
    repository = repository_factory()
    if repository is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Lead capture is not configured.",
        )
    try:
        repository.save_lead(
            {
                "tool_name": payload.tool_name,
                "phone": payload.phone,
                "email": payload.email,
                "target_country": payload.target_country,
                "target_intake": payload.target_intake,
                "target_college": payload.target_college,
                "target_course": payload.target_course,
                "journey_stage": payload.journey_stage,
            }
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Lead capture is temporarily unavailable.",
        ) from exc
    return LeadResponse()
