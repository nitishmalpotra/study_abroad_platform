from admissions.schemas import AdmissionPrediction, ProgramPrediction
from admissions.service import AdmissionsPredictionService
from admissions.validation import validate_submission


class FakeProvider:
    def predict(self, profile, target_programs):
        return (
            AdmissionPrediction(
                target_predictions=[
                    ProgramPrediction(
                        program_name="Georgia Tech MS CS",
                        chance_category="Reach",
                        estimated_probability_percentage=30,
                        brief_reasoning="Competitive target with a strong applicant pool.",
                    )
                ],
                profile_strengths=["Strong GPA", "Research", "Work experience"],
                profile_weaknesses=[
                    "Few publications",
                    "Limited leadership",
                    "No GMAT",
                ],
                actionable_roadmap=["Improve SOP", "Add projects", "Apply early"],
                recommended_universities=[
                    "Georgia Tech MS CS: overlaps with target.",
                    "Arizona State University (MS CS): Good fit.",
                    "University at Buffalo, SUNY (MS CS): Good value.",
                ],
            ),
            '{"ok": true}',
        )


def test_service_is_callable_without_streamlit() -> None:
    profile, target_programs, errors = validate_submission(
        full_name="Ada Lovelace",
        target_intake="Fall 2026",
        target_country="United Kingdom",
        undergrad_degree="BSc Computer Science",
        cgpa=8.5,
        cgpa_scale=10,
        gre_raw="320",
        gmat_raw="",
        english_test="IELTS",
        english_score_raw="8",
        work_experience_months=12,
        research_publications=1,
        program_inputs=["MS CS at Georgia Tech", "MS CS at Purdue", "", "", ""],
    )
    assert errors == []

    result = AdmissionsPredictionService(FakeProvider()).predict(
        profile, target_programs
    )

    assert [
        item.program_name for item in result.prediction.target_predictions
    ] == target_programs
    assert result.raw_output == '{"ok": true}'
