from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .utils import sanitize_text


class StudentProfile(BaseModel):
    full_name: str
    target_intake: str
    target_country: str
    undergrad_degree_name: str
    cgpa: float
    cgpa_scale: int
    gre_score: int | None
    gmat_score: int | None
    english_test: str | None
    english_score: float | None
    work_experience_months: int
    research_publications: int
    model_config = ConfigDict(extra="forbid")


class ProgramPrediction(BaseModel):
    program_name: str = Field(..., min_length=3, max_length=200)
    chance_category: Literal["Safe", "Target", "Reach", "Unrealistic"]
    estimated_probability_percentage: int = Field(..., ge=0, le=100)
    brief_reasoning: str = Field(..., min_length=10, max_length=500)
    model_config = ConfigDict(extra="forbid")

    @field_validator("program_name", "brief_reasoning")
    @classmethod
    def validate_text_fields(cls, value: str) -> str:
        cleaned = sanitize_text(value)
        if not cleaned:
            raise ValueError("Text fields cannot be empty.")
        return cleaned


class AdmissionPrediction(BaseModel):
    target_predictions: list[ProgramPrediction] = Field(..., min_length=1, max_length=5)
    profile_strengths: list[str] = Field(..., min_length=3, max_length=3)
    profile_weaknesses: list[str] = Field(..., min_length=3, max_length=3)
    actionable_roadmap: list[str] = Field(..., min_length=3, max_length=3)
    recommended_universities: list[str] = Field(..., min_length=3, max_length=3)
    model_config = ConfigDict(extra="forbid")

    @field_validator("target_predictions")
    @classmethod
    def validate_unique_programs(cls, predictions: list[ProgramPrediction]) -> list[ProgramPrediction]:
        names = [sanitize_text(item.program_name).lower() for item in predictions]
        if len(names) != len(set(names)):
            raise ValueError("target_predictions must contain distinct programs.")
        return predictions

    @field_validator(
        "profile_strengths",
        "profile_weaknesses",
        "actionable_roadmap",
        "recommended_universities",
    )
    @classmethod
    def validate_list_items(cls, values: list[str]) -> list[str]:
        cleaned_values = [sanitize_text(item) for item in values if sanitize_text(item)]
        if len(cleaned_values) != len(values):
            raise ValueError("List items cannot be empty.")
        return cleaned_values
