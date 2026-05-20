from fastapi import status
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from study_abroad_contracts import ApiError


class RequestBodyTooLarge(Exception):
    pass


class RequestGuardMiddleware:
    def __init__(self, app: ASGIApp, max_body_bytes: int) -> None:
        self.app = app
        self.max_body_bytes = max_body_bytes

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        method = str(scope.get("method", ""))
        if method not in {"POST", "PUT", "PATCH"}:
            await self.app(scope, receive, send)
            return

        headers = {
            key.decode("latin-1").lower(): value.decode("latin-1")
            for key, value in scope.get("headers", [])
        }
        content_type = headers.get("content-type", "")
        if not content_type.lower().startswith("application/json"):
            await self._send_error(
                scope,
                send,
                status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                "unsupported_media_type",
                "Only application/json requests are supported.",
            )
            return

        content_length = headers.get("content-length")
        if content_length is not None:
            try:
                body_bytes = int(content_length)
            except ValueError:
                body_bytes = self.max_body_bytes + 1
            if body_bytes > self.max_body_bytes:
                await self._send_too_large(scope, send)
                return

        limited_receive = self._limited_receive(receive)
        try:
            await self.app(scope, limited_receive, send)
        except RequestBodyTooLarge:
            await self._send_too_large(scope, send)

    def _limited_receive(self, receive: Receive) -> Receive:
        total_bytes = 0

        async def wrapped_receive() -> Message:
            nonlocal total_bytes
            message = await receive()
            if message["type"] == "http.request":
                total_bytes += len(message.get("body", b""))
                if total_bytes > self.max_body_bytes:
                    raise RequestBodyTooLarge
            return message

        return wrapped_receive

    async def _send_too_large(self, scope: Scope, send: Send) -> None:
        await self._send_error(
            scope,
            send,
            status.HTTP_413_CONTENT_TOO_LARGE,
            "request_too_large",
            "Request body is too large.",
        )

    @staticmethod
    async def _send_error(
        scope: Scope,
        send: Send,
        status_code: int,
        code: str,
        message: str,
    ) -> None:
        payload = ApiError(code=code, message=message, details=[])
        response = JSONResponse(
            content=payload.model_dump(),
            status_code=status_code,
        )

        async def empty_receive() -> Message:
            return {"type": "http.request", "body": b"", "more_body": False}

        await response(scope, empty_receive, send)
