from typing import Any

from fastapi.testclient import TestClient

from app.api.routes.admissions import get_live_admissions_service_factory
from app.api.routes.sop import get_live_sop_service_factory
from app.core.config import ApiSettings
from app.core.rate_limits import InMemoryRateLimiter
from app.main import create_app

from test_api import (
    FakeAdmissionsService,
    FakeSOPService,
    admissions_payload,
    sop_payload,
)


def smoke_client(rate_limit_count: int = 2) -> TestClient:
    app = create_app()
    app.state.live_rate_limiter = InMemoryRateLimiter(
        ApiSettings(rate_limit_count, 3600, ())
    )
    return TestClient(app, raise_server_exceptions=False)


def test_backend_smoke_health_and_mock_tool_flows() -> None:
    client = smoke_client()

    health = client.get("/health")
    sop = client.post("/api/v1/sop/review/mock", json=sop_payload())
    admissions = client.post(
        "/api/v1/admissions/predict/mock", json=admissions_payload()
    )

    assert health.status_code == 200
    assert health.json() == {"status": "ok"}
    assert sop.status_code == 200
    assert sop.json()["mode"] == "mock"
    assert sop.json()["grade"]["criteria_breakdown"][0]["name"] == "Academic Fit"
    assert admissions.status_code == 200
    assert admissions.json()["mode"] == "mock"
    assert len(admissions.json()["prediction"]["target_predictions"]) == 1


def test_backend_smoke_live_tool_flow_with_fake_services() -> None:
    app = create_app()
    app.state.live_rate_limiter = InMemoryRateLimiter(ApiSettings(3, 3600, ()))
    fake_sop = FakeSOPService()
    fake_admissions = FakeAdmissionsService()
    app.dependency_overrides[get_live_sop_service_factory] = lambda: lambda: fake_sop
    app.dependency_overrides[get_live_admissions_service_factory] = lambda: (
        lambda: fake_admissions
    )
    client = TestClient(app, raise_server_exceptions=False)

    sop = client.post("/api/v1/sop/review", json=sop_payload())
    admissions = client.post("/api/v1/admissions/predict", json=admissions_payload())

    assert sop.status_code == 200
    assert sop.json()["mode"] == "live"
    assert admissions.status_code == 200
    assert admissions.json()["mode"] == "live"
    assert fake_sop.calls == 1
    assert fake_admissions.calls == 1


def test_backend_smoke_live_rate_limit_blocks_second_model_call() -> None:
    app = create_app()
    app.state.live_rate_limiter = InMemoryRateLimiter(ApiSettings(1, 3600, ()))
    fake_admissions = FakeAdmissionsService()
    app.dependency_overrides[get_live_admissions_service_factory] = lambda: (
        lambda: fake_admissions
    )
    client = TestClient(app, raise_server_exceptions=False)

    first = client.post("/api/v1/admissions/predict", json=admissions_payload())
    second = client.post("/api/v1/admissions/predict", json=admissions_payload())

    assert first.status_code == 200
    assert second.status_code == 429
    assert second.json()["code"] == "rate_limited"
    assert fake_admissions.calls == 1


def test_backend_smoke_validation_errors_are_structured() -> None:
    client = smoke_client()
    payload: dict[str, Any] = admissions_payload() | {"cgpa": 11}

    response = client.post("/api/v1/admissions/predict/mock", json=payload)

    assert response.status_code == 422
    assert response.json()["code"] == "validation_error"
    assert response.json()["details"] == ["cgpa cannot exceed cgpa_scale."]
