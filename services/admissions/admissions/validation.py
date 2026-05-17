from typing import Any

from .schemas import StudentProfile
from .utils import sanitize_text


def parse_optional_int(raw_value: str, field_name: str) -> tuple[int | None, str | None]:
    text = sanitize_text(raw_value)
    if not text:
        return None, None
    try:
        return int(text), None
    except ValueError:
        return None, f"{field_name} must be a whole number."


def parse_optional_float(raw_value: str, field_name: str) -> tuple[float | None, str | None]:
    text = sanitize_text(raw_value)
    if not text:
        return None, None
    try:
        return float(text), None
    except ValueError:
        return None, f"{field_name} must be numeric."


def validate_submission(
    *,
    full_name: str,
    target_intake: str,
    target_country: str,
    undergrad_degree: str,
    cgpa: float,
    cgpa_scale: int,
    gre_raw: str,
    gmat_raw: str,
    english_test: str,
    english_score_raw: str,
    work_experience_months: int,
    research_publications: int,
    program_inputs: list[str],
) -> tuple[StudentProfile, list[str], list[str]]:
    errors: list[str] = []

    clean_name = sanitize_text(full_name)
    clean_intake = sanitize_text(target_intake)
    clean_country = sanitize_text(target_country)
    clean_degree = sanitize_text(undergrad_degree)

    if not clean_name:
        errors.append("Full Name is required.")
    if len(clean_name) > 120:
        errors.append("Full Name must be at most 120 characters.")
    if len(clean_intake) > 40:
        errors.append("Target Intake must be at most 40 characters.")
    if not clean_country:
        errors.append("Target Country is required.")
    if len(clean_country) > 60:
        errors.append("Target Country must be at most 60 characters.")
    if not clean_degree:
        errors.append("Undergrad Degree Name is required.")
    if len(clean_degree) > 160:
        errors.append("Undergrad Degree Name must be at most 160 characters.")
    if cgpa <= 0:
        errors.append("CGPA must be greater than 0.")
    if cgpa_scale not in {4, 10}:
        errors.append("CGPA scale must be 4 or 10.")
    if cgpa > cgpa_scale:
        errors.append(f"CGPA cannot exceed {cgpa_scale} for the selected scale.")

    gre_score, gre_error = parse_optional_int(gre_raw, "GRE score")
    if gre_error:
        errors.append(gre_error)
    if gre_score is not None and not (260 <= gre_score <= 340):
        errors.append("GRE score must be between 260 and 340.")

    gmat_score, gmat_error = parse_optional_int(gmat_raw, "GMAT score")
    if gmat_error:
        errors.append(gmat_error)
    if gmat_score is not None and not (200 <= gmat_score <= 805):
        errors.append("GMAT score must be between 200 and 805.")

    clean_english_test = sanitize_text(english_test)
    english_score: float | None = None
    if clean_english_test == "None":
        if sanitize_text(english_score_raw):
            errors.append("Select IELTS or TOEFL when providing an English score.")
    else:
        english_score, english_error = parse_optional_float(english_score_raw, "English score")
        if english_error:
            errors.append(english_error)
        if english_score is None:
            errors.append("English score is required when IELTS/TOEFL is selected.")
        elif clean_english_test == "IELTS" and not (0 <= english_score <= 9):
            errors.append("IELTS score must be between 0 and 9.")
        elif clean_english_test == "TOEFL" and not (0 <= english_score <= 120):
            errors.append("TOEFL score must be between 0 and 120.")

    if work_experience_months < 0 or work_experience_months > 600:
        errors.append("Work Experience must be between 0 and 600 months.")
    if research_publications < 0 or research_publications > 200:
        errors.append("Research Publications must be between 0 and 200.")

    sanitized_programs: list[str] = []
    for index, raw_program in enumerate(program_inputs, start=1):
        clean_program = sanitize_text(raw_program)
        if index == 1 and not clean_program:
            errors.append("Target Program 1 is mandatory.")
        if clean_program:
            if len(clean_program) > 200:
                errors.append(f"Target Program {index} must be at most 200 characters.")
            sanitized_programs.append(clean_program)

    if sanitized_programs and len(sanitized_programs) != len({item.lower() for item in sanitized_programs}):
        errors.append("Target programs must be distinct.")

    profile = StudentProfile(
        full_name=clean_name,
        target_intake=clean_intake,
        target_country=clean_country,
        undergrad_degree_name=clean_degree,
        cgpa=round(float(cgpa), 2),
        cgpa_scale=cgpa_scale,
        gre_score=gre_score,
        gmat_score=gmat_score,
        english_test=None if clean_english_test == "None" else clean_english_test,
        english_score=english_score,
        work_experience_months=int(work_experience_months),
        research_publications=int(research_publications),
    )
    return profile, sanitized_programs, errors


def profile_to_payload(profile: StudentProfile) -> dict[str, Any]:
    return profile.model_dump()
