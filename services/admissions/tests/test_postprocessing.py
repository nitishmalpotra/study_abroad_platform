from admissions.postprocessing import align_predictions_to_targets, enforce_alternative_recommendations
from admissions.schemas import AdmissionPrediction, ProgramPrediction


def prediction() -> AdmissionPrediction:
    return AdmissionPrediction(
        target_predictions=[
            ProgramPrediction(
                program_name="Georgia Tech MS CS",
                chance_category="Reach",
                estimated_probability_percentage=30,
                brief_reasoning="Competitive target with a strong applicant pool.",
            )
        ],
        profile_strengths=["Strong GPA", "Research", "Work experience"],
        profile_weaknesses=["Few publications", "Limited leadership", "No GMAT"],
        actionable_roadmap=["Improve SOP", "Add projects", "Apply early"],
        recommended_universities=[
            "Georgia Tech MS CS: overlaps with target.",
            "Northeastern University (MS CS): Good co-op.",
            "Northeastern University (MS CS): Good co-op.",
        ],
    )


def test_align_predictions_preserves_requested_order_and_adds_placeholder() -> None:
    aligned = align_predictions_to_targets(
        prediction(),
        ["MS CS at Georgia Tech", "MS CS at Purdue"],
    )

    assert [item.program_name for item in aligned.target_predictions] == [
        "MS CS at Georgia Tech",
        "MS CS at Purdue",
    ]
    assert aligned.target_predictions[0].estimated_probability_percentage == 30
    assert aligned.target_predictions[1].estimated_probability_percentage == 20


def test_enforce_alternative_recommendations_removes_targets_and_duplicates() -> None:
    curated = enforce_alternative_recommendations(
        prediction(),
        ["Georgia Tech MS CS"],
    )

    assert curated.recommended_universities == [
        "Northeastern University (MS CS): Good co-op.",
        "Arizona State University (MS CS): Broad intake capacity with solid applied research opportunities.",
        "University at Buffalo, SUNY (MS CS): Balanced selectivity with a good ROI for international students.",
    ]
