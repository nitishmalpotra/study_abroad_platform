import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from ai_runtime import redact_secrets
from study_abroad_contracts import ApiError

from .logging import log_event


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        details = [str(error["msg"]) for error in exc.errors()]
        payload = ApiError(
            code="validation_error",
            message="Request validation failed.",
            details=details,
        )
        log_event(
            logging.INFO,
            "request_validation_failed",
            request_id=getattr(request.state, "request_id", ""),
            path=request.url.path,
            details=details,
        )
        return JSONResponse(status_code=422, content=payload.model_dump())

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        payload = ApiError(
            code="validation_error",
            message="Request validation failed.",
            details=[redact_secrets(exc)],
        )
        log_event(
            logging.INFO,
            "domain_validation_failed",
            request_id=getattr(request.state, "request_id", ""),
            path=request.url.path,
            error=exc,
        )
        return JSONResponse(status_code=422, content=payload.model_dump())

    @app.exception_handler(HTTPException)
    async def http_error_handler(request: Request, exc: HTTPException) -> JSONResponse:
        code = "rate_limited" if exc.status_code == 429 else "http_error"
        payload = ApiError(code=code, message=str(exc.detail), details=[])
        log_event(
            logging.WARNING if exc.status_code >= 500 else logging.INFO,
            code,
            request_id=getattr(request.state, "request_id", ""),
            path=request.url.path,
            status_code=exc.status_code,
        )
        return JSONResponse(status_code=exc.status_code, content=payload.model_dump())

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
        log_event(
            logging.ERROR,
            "unhandled_error",
            request_id=getattr(request.state, "request_id", ""),
            path=request.url.path,
            error=exc,
        )
        payload = ApiError(
            code="internal_error",
            message="An internal error occurred.",
            details=[],
        )
        return JSONResponse(status_code=500, content=payload.model_dump())
