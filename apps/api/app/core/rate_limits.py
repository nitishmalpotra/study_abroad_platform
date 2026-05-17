import time
from dataclasses import dataclass, field
from typing import Callable

from fastapi import HTTPException, Request, status

from .config import ApiSettings


@dataclass
class InMemoryRateLimiter:
    settings: ApiSettings
    now: Callable[[], float] = time.time
    hits: dict[str, list[float]] = field(default_factory=dict)

    def check(self, key: str) -> None:
        current = self.now()
        cutoff = current - self.settings.live_rate_limit_window_seconds
        recent = [hit for hit in self.hits.get(key, []) if hit > cutoff]
        if len(recent) >= self.settings.live_rate_limit_count:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Live request rate limit exceeded.",
            )
        recent.append(current)
        self.hits[key] = recent


def client_key(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",", 1)[0].strip()
    if request.client is not None:
        return request.client.host
    return "anonymous"
