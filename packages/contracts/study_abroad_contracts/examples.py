from .api import AdmissionsPredictionResponse, SOPReviewResponse


SOP_REVIEW_MOCK_RESPONSE = SOPReviewResponse.model_validate(
    {
        "mode": "mock",
        "gatekeeper": {
            "is_valid": True,
            "reason": "Valid SOP for demo output.",
        },
        "grade": {
            "overall_score": 7.8,
            "criteria_breakdown": [
                {
                    "name": "Academic Fit",
                    "score": 8.0,
                    "feedback": "Shows relevant preparation for the chosen field.",
                },
                {
                    "name": "University Specificity",
                    "score": 7.0,
                    "feedback": "Mentions program fit but could cite one concrete resource.",
                },
                {
                    "name": "Career Clarity",
                    "score": 8.0,
                    "feedback": "Connects the degree to a plausible next step.",
                },
                {
                    "name": "Narrative Flow",
                    "score": 8.0,
                    "feedback": "Progression is coherent and easy to follow.",
                },
                {
                    "name": "Language & Tone",
                    "score": 8.0,
                    "feedback": "Clear, professional, and concise.",
                },
            ],
            "summary": "A credible SOP with good fit and clear direction; the main improvement is sharper program specificity.",
        },
    }
)


def admissions_prediction_mock_response(
    target_programs: list[str],
) -> AdmissionsPredictionResponse:
    categories = ["Target", "Reach", "Safe", "Unrealistic", "Target"]
    probabilities = [62, 38, 74, 18, 56]

    return AdmissionsPredictionResponse.model_validate(
        {
            "mode": "mock",
            "prediction": {
                "target_predictions": [
                    {
                        "program_name": program,
                        "chance_category": categories[index],
                        "estimated_probability_percentage": probabilities[index],
                        "brief_reasoning": "Profile is competitive for this target with room to strengthen evidence.",
                    }
                    for index, program in enumerate(target_programs)
                ],
                "profile_strengths": [
                    "Relevant academic background",
                    "Clear target direction",
                    "Balanced profile for the intended intake",
                ],
                "profile_weaknesses": [
                    "Limited differentiating evidence",
                    "Recommendations could be stronger",
                    "Target list may need broader spread",
                ],
                "actionable_roadmap": [
                    "Add one concrete project or research outcome",
                    "Refine the SOP around program fit",
                    "Include one safer alternative program",
                ],
                "recommended_universities": [
                    "Northeastern University (MS CS): Strong applied curriculum.",
                    "Arizona State University (MS CS): Broad opportunity set.",
                    "University at Buffalo, SUNY (MS CS): Balanced selectivity.",
                ],
            },
        }
    )
