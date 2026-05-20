import hashlib
import hmac
import json
from typing import Any

from admissions.schemas import AdmissionPrediction
from admissions.schemas import StudentProfile as AdmissionsProfile
from sop_review.schemas import SOPGrade
from sop_review.schemas import StudentProfile as SOPProfile


def hash_identifier(value: str, salt: str) -> str:
    normalized = value.strip().lower().encode("utf-8")
    return hmac.new(salt.encode("utf-8"), normalized, hashlib.sha256).hexdigest()


def sop_record(
    profile: SOPProfile,
    sop_text: str,
    grade: SOPGrade,
) -> dict[str, Any]:
    return {
        "university": profile.university,
        "intake": profile.intake,
        "country": profile.country,
        "sop_word_count": len(sop_text.split()),
        "overall_score": grade.overall_score,
        "grade_json": grade.model_dump(mode="json"),
    }


def admissions_profile_summary(profile: AdmissionsProfile) -> dict[str, Any]:
    return {
        "target_intake": profile.target_intake,
        "target_country": profile.target_country,
        "undergrad_degree_name": profile.undergrad_degree_name,
        "cgpa": profile.cgpa,
        "cgpa_scale": profile.cgpa_scale,
        "gre_score": profile.gre_score,
        "gmat_score": profile.gmat_score,
        "english_test": profile.english_test,
        "english_score": profile.english_score,
        "work_experience_months": profile.work_experience_months,
        "research_publications": profile.research_publications,
    }


def admissions_record(
    profile: AdmissionsProfile,
    target_programs: list[str],
    prediction: AdmissionPrediction,
) -> dict[str, Any]:
    return {
        "target_intake": profile.target_intake,
        "target_country": profile.target_country,
        "profile_summary_json": admissions_profile_summary(profile),
        "target_programs_json": target_programs,
        "prediction_json": prediction.model_dump(mode="json"),
    }


def json_dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, sort_keys=True)
