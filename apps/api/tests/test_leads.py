from fastapi.testclient import TestClient

from app.api.routes.leads import get_lead_repository_factory
from app.main import create_app


class FakeLeadRepository:
    def __init__(self) -> None:
        self.saved: list[dict[str, str]] = []

    def save_lead(self, lead: dict[str, str]) -> None:
        self.saved.append(lead)


def lead_payload() -> dict[str, str]:
    return {
        "tool_name": "sop-review",
        "phone": "1234567890",
        "email": "applicant@example.com",
        "target_country": "United States",
        "target_intake": "Fall 2026",
        "target_college": "MIT",
        "target_course": "MSBA",
        "journey_stage": "Just exploring options",
    }


def test_lead_is_saved_when_repository_available() -> None:
    fake = FakeLeadRepository()
    app = create_app()
    app.dependency_overrides[get_lead_repository_factory] = lambda: lambda: fake
    response = TestClient(app).post("/api/v1/leads", json=lead_payload())
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert len(fake.saved) == 1
    assert fake.saved[0]["email"] == "applicant@example.com"
    assert fake.saved[0]["tool_name"] == "sop-review"


def test_lead_returns_503_when_repository_missing() -> None:
    app = create_app()
    app.dependency_overrides[get_lead_repository_factory] = lambda: lambda: None
    response = TestClient(app, raise_server_exceptions=False).post(
        "/api/v1/leads", json=lead_payload()
    )
    assert response.status_code == 503


def test_lead_rejects_invalid_payload() -> None:
    fake = FakeLeadRepository()
    app = create_app()
    app.dependency_overrides[get_lead_repository_factory] = lambda: lambda: fake
    client = TestClient(app, raise_server_exceptions=False)

    missing_email = lead_payload()
    missing_email["email"] = "nope"
    assert client.post("/api/v1/leads", json=missing_email).status_code == 422

    short_phone = lead_payload()
    short_phone["phone"] = "12"
    assert client.post("/api/v1/leads", json=short_phone).status_code == 422

    assert fake.saved == []
