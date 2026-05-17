from fastapi.testclient import TestClient

from admissions.schemas import AdmissionPrediction, ProgramPrediction
from admissions.service import AdmissionsPredictionResult
from app.api.deps import get_live_admissions_service, get_live_sop_service
from app.core.config import ApiSettings
from app.core.rate_limits import InMemoryRateLimiter
from app.main import create_app
from sop_review.schemas import (
    CriterionFeedback,
    GatekeeperResponse,
    SOPGrade,
)
from sop_review.service import SOPReviewResult


def sop_payload() -> dict[str, object]:
    return {
        "full_name": "Ada Lovelace",
        "mobile": "1234567890",
        "university": "Example University",
        "intake": "Fall 2026",
        "country": "UK",
        "sop_text": "one two three four five six seven eight nine ten",
    }


def admissions_payload() -> dict[str, object]:
    return {
        "full_name": "Ada Lovelace",
        "target_intake": "Fall 2026",
        "target_country": "United Kingdom",
        "undergrad_degree_name": "BSc Computer Science",
        "cgpa": 8.5,
        "cgpa_scale": 10,
        "gre_score": 320,
        "gmat_score": None,
        "english_test": "IELTS",
        "english_score": 8,
        "work_experience_months": 12,
        "research_publications": 1,
        "target_programs": ["MS CS at Oxford"],
    }


def live_sop_result() -> SOPReviewResult:
    return SOPReviewResult(
        gatekeeper=GatekeeperResponse(is_valid=True, reason="ok"),
        gatekeeper_model="fake-gate",
        grade=SOPGrade(
            overall_score=8,
            criteria_breakdown=[
                CriterionFeedback(name="Academic Fit", score=8, feedback="Strong"),
                CriterionFeedback(
                    name="University Specificity", score=8, feedback="Strong"
                ),
                CriterionFeedback(name="Career Clarity", score=8, feedback="Strong"),
                CriterionFeedback(name="Narrative Flow", score=8, feedback="Strong"),
                CriterionFeedback(name="Language & Tone", score=8, feedback="Strong"),
            ],
            summary="Good SOP",
        ),
        grading_model="fake-grade",
        raw_json='{"overall_score":8}',
        submission_id=1,
    )


def live_admissions_result() -> AdmissionsPredictionResult:
    return AdmissionsPredictionResult(
        prediction=AdmissionPrediction(
            target_predictions=[
                ProgramPrediction(
                    program_name="MS CS at Oxford",
                    chance_category="Reach",
                    estimated_probability_percentage=30,
                    brief_reasoning="Competitive target with a strong applicant pool.",
                )
            ],
            profile_strengths=["Strong GPA", "Research", "Experience"],
            profile_weaknesses=["Few publications", "Leadership", "No GMAT"],
            actionable_roadmap=["Improve SOP", "Add projects", "Apply early"],
            recommended_universities=["A", "B", "C"],
        ),
        raw_output='{"ok":true}',
    )


class FakeSOPService:
    def __init__(self) -> None:
        self.calls = 0

    def review(self, profile, sop_text, request_id):
        self.calls += 1
        return live_sop_result()


class FakeAdmissionsService:
    def __init__(self) -> None:
        self.calls = 0

    def predict(self, profile, target_programs):
        self.calls += 1
        return live_admissions_result()


def client() -> TestClient:
    app = create_app()
    app.state.live_rate_limiter = InMemoryRateLimiter(ApiSettings(2, 3600))
    return TestClient(app, raise_server_exceptions=False)


def test_health() -> None:
    response = client().get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_validation_errors_use_structured_shape() -> None:
    response = client().post("/api/v1/sop/review/mock", json={})
    assert response.status_code == 422
    assert response.json()["code"] == "validation_error"
    assert response.json()["message"] == "Request validation failed."


def test_mock_endpoints_return_deterministic_responses_without_live_services() -> None:
    app = create_app()
    app.dependency_overrides[get_live_sop_service] = lambda: (_ for _ in ()).throw(
        AssertionError("live SOP dependency should not be used")
    )
    app.dependency_overrides[get_live_admissions_service] = lambda: (
        _ for _ in ()
    ).throw(AssertionError("live admissions dependency should not be used"))
    test_client = TestClient(app)

    sop_first = test_client.post("/api/v1/sop/review/mock", json=sop_payload())
    sop_second = test_client.post("/api/v1/sop/review/mock", json=sop_payload())
    admissions_first = test_client.post(
        "/api/v1/admissions/predict/mock", json=admissions_payload()
    )
    admissions_second = test_client.post(
        "/api/v1/admissions/predict/mock", json=admissions_payload()
    )

    assert sop_first.status_code == 200
    assert sop_first.json() == sop_second.json()
    assert admissions_first.status_code == 200
    assert admissions_first.json() == admissions_second.json()


def test_live_endpoints_are_testable_with_fakes() -> None:
    app = create_app()
    fake_sop = FakeSOPService()
    fake_admissions = FakeAdmissionsService()
    app.dependency_overrides[get_live_sop_service] = lambda: fake_sop
    app.dependency_overrides[get_live_admissions_service] = lambda: fake_admissions
    test_client = TestClient(app)

    sop_response = test_client.post("/api/v1/sop/review", json=sop_payload())
    admissions_response = test_client.post(
        "/api/v1/admissions/predict", json=admissions_payload()
    )

    assert sop_response.status_code == 200
    assert admissions_response.status_code == 200
    assert sop_response.json()["mode"] == "live"
    assert admissions_response.json()["mode"] == "live"
    assert fake_sop.calls == 1
    assert fake_admissions.calls == 1


def test_live_rate_limiting_applies_but_mock_calls_are_excluded() -> None:
    app = create_app()
    app.state.live_rate_limiter = InMemoryRateLimiter(ApiSettings(1, 3600))
    app.dependency_overrides[get_live_sop_service] = lambda: FakeSOPService()
    test_client = TestClient(app)

    assert (
        test_client.post("/api/v1/sop/review/mock", json=sop_payload()).status_code
        == 200
    )
    assert test_client.post("/api/v1/sop/review", json=sop_payload()).status_code == 200
    limited = test_client.post("/api/v1/sop/review", json=sop_payload())

    assert limited.status_code == 429
    assert limited.json() == {
        "code": "rate_limited",
        "message": "Live request rate limit exceeded.",
        "details": [],
    }


def test_unhandled_errors_are_safe_and_redacted() -> None:
    class ExplodingSOPService:
        def review(self, profile, sop_text, request_id):
            raise RuntimeError("provider failed with sk-secretsecretsecret")

    app = create_app()
    app.dependency_overrides[get_live_sop_service] = lambda: ExplodingSOPService()
    response = TestClient(app, raise_server_exceptions=False).post(
        "/api/v1/sop/review", json=sop_payload()
    )

    assert response.status_code == 500
    assert response.json() == {
        "code": "internal_error",
        "message": "An internal error occurred.",
        "details": [],
    }
    assert "secret" not in response.text.lower()
