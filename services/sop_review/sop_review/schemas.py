from dataclasses import dataclass
from typing import List

from pydantic import BaseModel, Field, field_validator


EXPECTED_CRITERIA: List[str] = [
    "Academic Fit",
    "University Specificity",
    "Career Clarity",
    "Narrative Flow",
    "Language & Tone",
]


@dataclass
class StudentProfile:
    full_name: str
    mobile: str
    university: str
    intake: str
    country: str


class GatekeeperResponse(BaseModel):
    is_valid: bool = Field(description="True only if input is a valid SOP in English.")
    reason: str = Field(description="One concise reason for the decision.")


class CriterionFeedback(BaseModel):
    name: str
    score: float
    feedback: str

    @field_validator("score")
    @classmethod
    def validate_score(cls, value: float) -> float:
        if not 1 <= value <= 10:
            raise ValueError("Criterion score must be between 1 and 10.")
        return round(float(value), 2)


class SOPGrade(BaseModel):
    overall_score: float
    criteria_breakdown: List[CriterionFeedback]
    summary: str

    @field_validator("overall_score")
    @classmethod
    def validate_overall_score(cls, value: float) -> float:
        if not 1 <= value <= 10:
            raise ValueError("overall_score must be between 1 and 10.")
        return round(float(value), 2)

    @field_validator("criteria_breakdown")
    @classmethod
    def validate_criteria_breakdown(
        cls, value: List[CriterionFeedback]
    ) -> List[CriterionFeedback]:
        names = [item.name for item in value]
        missing = [name for name in EXPECTED_CRITERIA if name not in names]
        if missing:
            raise ValueError(
                f"Missing required criteria in criteria_breakdown: {', '.join(missing)}"
            )
        return value
