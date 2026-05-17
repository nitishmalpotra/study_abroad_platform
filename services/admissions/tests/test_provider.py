from ai_runtime.runtime import CompletionResult

from admissions.providers import RuntimePredictionProvider
from admissions.schemas import StudentProfile


class FakeRuntime:
    def __init__(self, responses):
        self.responses = responses
        self.calls = []

    def complete(self, messages, request_id):
        self.calls.append((messages, request_id))
        return self.responses.pop(0)


def profile() -> StudentProfile:
    return StudentProfile(
        full_name="Ada Lovelace",
        target_intake="Fall 2026",
        target_country="United Kingdom",
        undergrad_degree_name="BSc Computer Science",
        cgpa=8.5,
        cgpa_scale=10,
        gre_score=320,
        gmat_score=None,
        english_test="IELTS",
        english_score=8,
        work_experience_months=12,
        research_publications=1,
    )


def test_runtime_provider_repairs_invalid_prediction_output() -> None:
    runtime = FakeRuntime(
        [
            CompletionResult("not-json", "deepseek-chat"),
            CompletionResult(
                """
                {
                  "target_predictions": [{
                    "program_name": "MS CS at Oxford",
                    "chance_category": "Reach",
                    "estimated_probability_percentage": 30,
                    "brief_reasoning": "Competitive."
                  }],
                  "profile_strengths": ["Strong GPA", "Research", "Experience"],
                  "profile_weaknesses": ["Few publications", "Leadership", "No GMAT"],
                  "actionable_roadmap": ["Improve SOP", "Add projects", "Apply early"],
                  "recommended_universities": ["A", "B", "C"]
                }
                """,
                "deepseek-chat",
            ),
        ]
    )
    provider = RuntimePredictionProvider(runtime)
    prediction, raw = provider.predict(profile(), ["MS CS at Oxford"])
    assert prediction.target_predictions[0].program_name == "MS CS at Oxford"
    assert '"target_predictions"' in raw
    assert [message["role"] for message in runtime.calls[0][0]] == ["system", "user"]


def test_runtime_provider_uses_openai_compatible_roles_for_active_prompt() -> None:
    runtime = FakeRuntime(
        [
            CompletionResult(
                """
                {
                  "target_predictions": [{
                    "program_name": "MS CS at Oxford",
                    "chance_category": "Reach",
                    "estimated_probability_percentage": 30,
                    "brief_reasoning": "Strong GPA and GRE make this plausible but selective."
                  }],
                  "profile_strengths": ["Strong GPA", "Research", "Experience"],
                  "profile_weaknesses": ["Few publications", "Leadership", "No GMAT"],
                  "actionable_roadmap": ["Improve SOP", "Add projects", "Apply early"],
                  "recommended_universities": ["A", "B", "C"]
                }
                """,
                "deepseek-chat",
            )
        ]
    )
    provider = RuntimePredictionProvider(runtime)
    provider.predict(profile(), ["MS CS at Oxford"])

    assert [message["role"] for message in runtime.calls[0][0]] == ["system", "user"]
