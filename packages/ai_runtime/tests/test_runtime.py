import logging

from pydantic import BaseModel

from ai_runtime.config import RuntimeSettings
from ai_runtime.parsing import extract_json_payload, parse_model_json
from ai_runtime.runtime import AIRuntime
from ai_runtime.security import redact_secrets


class Payload(BaseModel):
    ok: bool


class FakeProvider:
    def __init__(self, responses: list[object]) -> None:
        self.responses = responses
        self.models: list[str] = []

    def complete(
        self,
        messages: list[dict[str, str]],
        *,
        model: str,
        timeout_seconds: float,
    ) -> object:
        self.models.append(model)
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


def settings(**overrides: object) -> RuntimeSettings:
    values = {
        "api_key": "placeholder-key",
        "model_candidates": ("deepseek-v4-flash", "deepseek-v4-pro"),
        "base_url": "https://api.deepseek.com",
        "timeout_seconds": 1.0,
        "retry_attempts": 0,
        "retry_backoff_seconds": 0.0,
    }
    values.update(overrides)
    return RuntimeSettings(**values)


def test_runtime_falls_back_to_next_model() -> None:
    provider = FakeProvider([RuntimeError("boom"), {"text": "ok"}])
    result = AIRuntime(settings(), provider, logging.getLogger("test")).complete([], "req")
    assert result.text == "ok"
    assert result.model == "deepseek-v4-pro"
    assert provider.models == ["deepseek-v4-flash", "deepseek-v4-pro"]


def test_shared_json_helpers_extract_and_validate_payload() -> None:
    raw = "```json\n{\"ok\": true}\n```"
    assert extract_json_payload(raw) == '{"ok": true}'
    assert parse_model_json(Payload, raw).ok is True


def test_redaction_removes_api_keys() -> None:
    assert (
        redact_secrets("failure " + "sk-" + "secretvalue123456")
        == "failure [REDACTED_API_KEY]"
    )


def test_redaction_removes_key_value_and_bearer_tokens() -> None:
    message = redact_secrets(
        "provider failed with API_KEY=secret123 and Authorization: Bearer token123"
    )

    assert "secret123" not in message
    assert "token123" not in message
    assert message == (
        "provider failed with API_KEY=[REDACTED_API_KEY] and "
        "Authorization: [REDACTED_API_KEY]"
    )
