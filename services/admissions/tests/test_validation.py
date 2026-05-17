from admissions.validation import validate_submission


def valid_kwargs() -> dict:
    return {
        "full_name": "Ada Lovelace",
        "target_intake": "Fall 2026",
        "target_country": "United Kingdom",
        "undergrad_degree": "BSc Computer Science",
        "cgpa": 8.5,
        "cgpa_scale": 10,
        "gre_raw": "320",
        "gmat_raw": "",
        "english_test": "IELTS",
        "english_score_raw": "8",
        "work_experience_months": 12,
        "research_publications": 1,
        "program_inputs": ["MS CS at Oxford", "MS AI at Cambridge", "", "", ""],
    }


def test_validate_submission_sanitizes_profile_and_targets() -> None:
    kwargs = valid_kwargs()
    kwargs["full_name"] = " Ada   Lovelace "
    kwargs["program_inputs"] = [" MS CS at Oxford ", "", "", "", ""]

    profile, target_programs, errors = validate_submission(**kwargs)

    assert errors == []
    assert profile.full_name == "Ada Lovelace"
    assert target_programs == ["MS CS at Oxford"]


def test_validate_submission_rejects_duplicate_target_programs() -> None:
    kwargs = valid_kwargs()
    kwargs["program_inputs"] = ["MS CS at Oxford", "ms cs at oxford", "", "", ""]

    _, _, errors = validate_submission(**kwargs)

    assert "Target programs must be distinct." in errors


def test_validate_submission_rejects_invalid_score_ranges() -> None:
    kwargs = valid_kwargs()
    kwargs["cgpa"] = 11
    kwargs["gre_raw"] = "250"
    kwargs["gmat_raw"] = "900"
    kwargs["english_score_raw"] = "10"

    _, _, errors = validate_submission(**kwargs)

    assert "CGPA cannot exceed 10 for the selected scale." in errors
    assert "GRE score must be between 260 and 340." in errors
    assert "GMAT score must be between 200 and 805." in errors
    assert "IELTS score must be between 0 and 9." in errors
