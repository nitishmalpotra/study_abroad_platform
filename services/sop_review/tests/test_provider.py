from ai_runtime.runtime import CompletionResult

from sop_review.providers import RuntimeReviewProvider


class FakeRuntime:
    def __init__(self, responses):
        self.responses = responses

    def complete(self, messages, request_id):
        return self.responses.pop(0)


def test_runtime_provider_uses_shared_runtime_for_both_sop_steps() -> None:
    provider = RuntimeReviewProvider(
        FakeRuntime(
            [
                CompletionResult('{"is_valid": true, "reason": "ok"}', "deepseek-chat"),
                CompletionResult(
                    """
                    {
                      "overall_score": 8,
                      "criteria_breakdown": [
                        {"name":"Academic Fit","score":8,"feedback":"Strong"},
                        {"name":"University Specificity","score":8,"feedback":"Strong"},
                        {"name":"Career Clarity","score":8,"feedback":"Strong"},
                        {"name":"Narrative Flow","score":8,"feedback":"Strong"},
                        {"name":"Language & Tone","score":8,"feedback":"Strong"}
                      ],
                      "summary": "Good SOP"
                    }
                    """,
                    "deepseek-chat",
                ),
            ]
        )
    )
    gatekeeper, gatekeeper_model = provider.gatekeep("sop", "req")
    grade, _, grading_model = provider.grade("sop", "Example University", "UK", "req")
    assert gatekeeper.is_valid is True
    assert gatekeeper_model == grading_model == "deepseek-chat"
    assert grade.overall_score == 8
