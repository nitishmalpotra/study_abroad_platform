from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from admissions.schemas import AdmissionPrediction
from sop_review.schemas import GatekeeperResponse, SOPGrade


class ApiError(BaseModel):
    code: str
    message: str
    details: list[str] = Field(default_factory=list)
    model_config = ConfigDict(extra="forbid")


class HealthResponse(BaseModel):
    status: str = "ok"


class SOPReviewRequest(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=120)
    mobile: str = Field(..., min_length=10, max_length=20)
    university: str = Field(..., min_length=1, max_length=160)
    intake: str = Field(..., min_length=1, max_length=80)
    country: str = Field(..., min_length=1, max_length=80)
    sop_text: str = Field(..., min_length=1)
    model_config = ConfigDict(extra="forbid")


class SOPReviewResponse(BaseModel):
    mode: Literal["mock", "live"]
    gatekeeper: GatekeeperResponse
    grade: SOPGrade | None
    model_config = ConfigDict(extra="forbid")


class AdmissionsPredictionRequest(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=120)
    target_intake: str = Field(..., max_length=40)
    target_country: str = Field(..., min_length=1, max_length=60)
    undergrad_degree_name: str = Field(..., min_length=1, max_length=160)
    cgpa: float = Field(..., gt=0)
    cgpa_scale: int
    gre_score: int | None = None
    gmat_score: int | None = None
    english_test: str | None = None
    english_score: float | None = None
    work_experience_months: int = Field(..., ge=0, le=600)
    research_publications: int = Field(..., ge=0, le=200)
    target_programs: list[str] = Field(..., min_length=1, max_length=5)
    model_config = ConfigDict(extra="forbid")

    @field_validator("cgpa_scale")
    @classmethod
    def validate_cgpa_scale(cls, value: int) -> int:
        if value not in {4, 10}:
            raise ValueError("cgpa_scale must be 4 or 10.")
        return value

    @field_validator("target_programs")
    @classmethod
    def validate_programs(cls, values: list[str]) -> list[str]:
        cleaned = [value.strip() for value in values]
        if any(not value for value in cleaned):
            raise ValueError("target_programs cannot contain empty values.")
        if len({value.lower() for value in cleaned}) != len(cleaned):
            raise ValueError("target_programs must be distinct.")
        return cleaned


class AdmissionsPredictionResponse(BaseModel):
    mode: Literal["mock", "live"]
    prediction: AdmissionPrediction
    model_config = ConfigDict(extra="forbid")
