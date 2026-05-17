import json
from pathlib import Path

from admissions.prompts import PREDICTION_PROMPT_METADATA, PREDICTION_PROMPT_VERSION
from admissions.schemas import AdmissionPrediction


FIXTURES_PATH = Path(__file__).parents[1] / "evals" / "fixtures.json"


def load_fixtures():
    return json.loads(FIXTURES_PATH.read_text())


def word_count(text: str) -> int:
    return len(text.split())


def test_active_prompt_is_versioned_and_documents_quality_philosophy() -> None:
    assert PREDICTION_PROMPT_VERSION == "v2"
    assert "careful judgment over volume" in PREDICTION_PROMPT_METADATA[
        "quality_philosophy"
    ]
    assert PREDICTION_PROMPT_METADATA["response_contract"] == [
        "target_predictions",
        "profile_strengths",
        "profile_weaknesses",
        "actionable_roadmap",
        "recommended_universities",
    ]


def test_eval_fixtures_cover_required_cases() -> None:
    fixtures = {fixture["id"] for fixture in load_fixtures()}
    assert fixtures == {"strong", "borderline", "weak", "unrealistic_target"}


def test_golden_outputs_match_stable_schema_contract() -> None:
    for fixture in load_fixtures():
        parsed = AdmissionPrediction.model_validate(fixture["golden_output"])
        assert [item.program_name for item in parsed.target_predictions] == fixture[
            "target_programs"
        ]


def test_golden_outputs_are_concise_and_profile_grounded() -> None:
    banned_generic_phrases = {
        "strong profile",
        "holistic admissions",
        "competitive applicant pool",
    }
    concrete_signal_markers = {
        "cgpa",
        "gre",
        "ielts",
        "toefl",
        "publication",
        "experience",
        "degree",
        "bcom",
        "mechanical engineering",
        "electronics",
        "computer science",
    }

    for fixture in load_fixtures():
        parsed = AdmissionPrediction.model_validate(fixture["golden_output"])
        for prediction in parsed.target_predictions:
            assert word_count(prediction.brief_reasoning) <= 32
            lowered = prediction.brief_reasoning.lower()
            assert not any(phrase in lowered for phrase in banned_generic_phrases)
            assert any(marker in lowered for marker in concrete_signal_markers)
        for item in [
            *parsed.profile_strengths,
            *parsed.profile_weaknesses,
            *parsed.actionable_roadmap,
            *parsed.recommended_universities,
        ]:
            assert word_count(item) <= 28


def test_golden_outputs_capture_category_calibration_tendencies() -> None:
    fixtures = {fixture["id"]: fixture for fixture in load_fixtures()}

    strong = AdmissionPrediction.model_validate(fixtures["strong"]["golden_output"])
    borderline = AdmissionPrediction.model_validate(
        fixtures["borderline"]["golden_output"]
    )
    weak = AdmissionPrediction.model_validate(fixtures["weak"]["golden_output"])
    unrealistic = AdmissionPrediction.model_validate(
        fixtures["unrealistic_target"]["golden_output"]
    )

    assert [item.chance_category for item in strong.target_predictions] == [
        "Safe",
        "Target",
        "Reach",
    ]
    assert [item.chance_category for item in borderline.target_predictions] == [
        "Target",
        "Reach",
        "Unrealistic",
    ]
    assert {item.chance_category for item in weak.target_predictions} == {
        "Unrealistic"
    }
    assert {item.chance_category for item in unrealistic.target_predictions} == {
        "Unrealistic"
    }
    assert max(item.estimated_probability_percentage for item in unrealistic.target_predictions) < min(
        item.estimated_probability_percentage for item in borderline.target_predictions
    )
