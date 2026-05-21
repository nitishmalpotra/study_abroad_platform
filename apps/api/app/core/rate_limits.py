import time
from dataclasses import dataclass, field
from typing import Callable

from fastapi import HTTPException, Request, status

from .config import ApiSettings
from app.persistence.database import Database
from app.persistence.privacy import hash_identifier


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


@dataclass
class PostgresRateLimiter:
    settings: ApiSettings
    database: Database

    def __post_init__(self) -> None:
        if self.settings.rate_limit_hash_salt is None:
            raise RuntimeError(
                "API_RATE_LIMIT_HASH_SALT is required for Postgres rate limiting."
            )

    def check(self, key: str) -> None:
        key_hash = hash_identifier(key, self.settings.rate_limit_hash_salt or "")
        with self.database.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO rate_limit_buckets (
                        scope,
                        key_hash,
                        window_start,
                        window_seconds,
                        hit_count
                    )
                    VALUES (
                        'live_ai',
                        %(key_hash)s,
                        to_timestamp(
                            floor(extract(epoch FROM now()) / %(window_seconds)s)
                            * %(window_seconds)s
                        ),
                        %(window_seconds)s,
                        1
                    )
                    ON CONFLICT (scope, key_hash, window_start)
                    DO UPDATE SET
                        hit_count = rate_limit_buckets.hit_count + 1,
                        updated_at = now()
                    RETURNING hit_count
                    """,
                    {
                        "key_hash": key_hash,
                        "window_seconds": self.settings.live_rate_limit_window_seconds,
                    },
                )
                row = cursor.fetchone()
        hit_count = int(row[0])
        if hit_count > self.settings.live_rate_limit_count:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Live request rate limit exceeded.",
            )


def client_key(request: Request) -> str:
    settings = getattr(request.app.state, "settings", None)
    trust_proxy_headers = bool(getattr(settings, "trust_proxy_headers", False))
    forwarded = request.headers.get("x-forwarded-for")
    if trust_proxy_headers and forwarded:
        return forwarded.split(",", 1)[0].strip()
    if request.client is not None:
        return request.client.host
    return "anonymous"
