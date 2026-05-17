from typing import Protocol

import httpx


class ChatProvider(Protocol):
    def complete(
        self,
        messages: list[dict[str, str]],
        *,
        model: str,
        timeout_seconds: float,
    ) -> object: ...


class DeepSeekProvider:
    def __init__(self, api_key: str, base_url: str) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def complete(
        self,
        messages: list[dict[str, str]],
        *,
        model: str,
        timeout_seconds: float,
    ) -> object:
        response = httpx.post(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"model": model, "messages": messages, "temperature": 0.0},
            timeout=timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        return payload["choices"][0]["message"]["content"]
