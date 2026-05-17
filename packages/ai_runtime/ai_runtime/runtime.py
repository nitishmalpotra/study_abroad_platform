import logging
import time
from dataclasses import dataclass
from typing import Sequence

from .config import RuntimeSettings
from .providers import ChatProvider
from .security import redact_secrets


@dataclass(frozen=True)
class CompletionResult:
    text: str
    model: str


def normalize_content(content: object) -> str:
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, dict):
        value = content.get("text") or content.get("content") or ""
        return str(value).strip()
    if isinstance(content, Sequence):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                value = item.get("text") or item.get("content") or ""
                parts.append(str(value))
            else:
                parts.append(str(item))
        return "\n".join(part for part in parts if part).strip()
    return str(content).strip()


class AIRuntime:
    def __init__(
        self,
        settings: RuntimeSettings,
        provider: ChatProvider,
        logger: logging.Logger | None = None,
    ) -> None:
        self.settings = settings
        self.provider = provider
        self.logger = logger or logging.getLogger("ai_runtime")

    def complete(self, messages: list[dict[str, str]], request_id: str) -> CompletionResult:
        errors: list[str] = []
        total_attempts = self.settings.retry_attempts + 1
        for model in self.settings.model_candidates:
            for attempt in range(1, total_attempts + 1):
                try:
                    content = self.provider.complete(
                        messages,
                        model=model,
                        timeout_seconds=self.settings.timeout_seconds,
                    )
                    return CompletionResult(normalize_content(content), model)
                except Exception as exc:
                    message = f"{model} attempt {attempt}: {redact_secrets(exc)}"
                    errors.append(message)
                    self.logger.warning("[%s] LLM call failed: %s", request_id, message)
                    if attempt < total_attempts and self.settings.retry_backoff_seconds > 0:
                        time.sleep(self.settings.retry_backoff_seconds * attempt)
        raise RuntimeError(
            "Failed to get a response from configured models.\n" + "\n".join(errors)
        )
