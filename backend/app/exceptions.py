"""Uygulama exception sınıfları ve RFC 7807 Problem Details handler'ları.

Kaynak: MASTER_BACKEND_GELISTIRME_RAPORU_PART2.md §15.3.
"""
from __future__ import annotations

from typing import Any

import structlog
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class AppException(Exception):
    """Uygulama özelinde tüm hatalar için kök sınıf."""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    code: str = "internal_error"
    title: str = "Internal Server Error"

    def __init__(
        self,
        message: str = "",
        *,
        status_code: int | None = None,
        code: str | None = None,
        details: Any = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        if code is not None:
            self.code = code
        self.details = details


class NotFoundError(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    code = "not_found"
    title = "Not Found"


class ValidationAppError(AppException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    code = "validation_error"
    title = "Validation Error"


class AuthError(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "auth_error"
    title = "Authentication Error"


class ForbiddenError(AppException):
    status_code = status.HTTP_403_FORBIDDEN
    code = "forbidden"
    title = "Forbidden"


class ConflictError(AppException):
    status_code = status.HTTP_409_CONFLICT
    code = "conflict"
    title = "Conflict"


class RateLimitError(AppException):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    code = "rate_limited"
    title = "Too Many Requests"


def _problem_details(
    *,
    request: Request,
    status_code: int,
    code: str,
    title: str,
    detail: Any,
) -> JSONResponse:
    """RFC 7807 formatında JSON response üretir."""
    request_id = structlog.contextvars.get_contextvars().get("request_id", "")
    body: dict[str, Any] = {
        "type": f"https://raw2value.ai/errors/{code}",
        "title": title,
        "status": status_code,
        "detail": detail,
        "instance": str(request.url),
        "code": code,
        "request_id": request_id,
    }
    return JSONResponse(status_code=status_code, content=body)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return _problem_details(
        request=request,
        status_code=exc.status_code,
        code=exc.code,
        title=exc.title,
        detail=exc.details if exc.details is not None else exc.message or exc.title,
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return _problem_details(
        request=request,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        code="validation_error",
        title="Validation Error",
        detail=exc.errors(),
    )


async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    return _problem_details(
        request=request,
        status_code=exc.status_code,
        code=f"http_{exc.status_code}",
        title=exc.detail if isinstance(exc.detail, str) else "HTTP Error",
        detail=exc.detail,
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger = structlog.get_logger("exceptions")
    logger.exception("unhandled_exception", error=str(exc))
    return _problem_details(
        request=request,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="internal_error",
        title="Internal Server Error",
        detail="An internal error occurred. Refer to request_id for tracing.",
    )


def register_exception_handlers(app: FastAPI) -> None:
    """FastAPI uygulamasına tüm handler'ları takar."""
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
