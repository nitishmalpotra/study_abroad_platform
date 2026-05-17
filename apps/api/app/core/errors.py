from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from ai_runtime import redact_secrets
from study_abroad_contracts import ApiError


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
        return JSONResponse(status_code=422, content=payload.model_dump())

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        payload = ApiError(
            code="validation_error",
            message="Request validation failed.",
            details=[redact_secrets(exc)],
        )
        return JSONResponse(status_code=422, content=payload.model_dump())

    @app.exception_handler(HTTPException)
    async def http_error_handler(request: Request, exc: HTTPException) -> JSONResponse:
        code = "rate_limited" if exc.status_code == 429 else "http_error"
        payload = ApiError(code=code, message=str(exc.detail), details=[])
        return JSONResponse(status_code=exc.status_code, content=payload.model_dump())

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
        redact_secrets(exc)
        payload = ApiError(
            code="internal_error",
            message="An internal error occurred.",
            details=[],
        )
        return JSONResponse(status_code=500, content=payload.model_dump())
