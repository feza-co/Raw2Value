"""HTTP middleware'leri — RequestID propagation ve access log.

Kaynak: MASTER_BACKEND_GELISTIRME_RAPORU_PART2.md §14.2.
"""
from __future__ import annotations

import time
import uuid

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


def _generate_request_id() -> str:
    """RFC 4122 UUIDv4 tabanlı kısa request id üretir."""
    return f"req_{uuid.uuid4().hex[:20]}"


class RequestIdMiddleware(BaseHTTPMiddleware):
    """`X-Request-ID` header'ını üret/propagate eder ve structlog context'e bind'lar."""

    header_name = "X-Request-ID"

    async def dispatch(self, request: Request, call_next):
        rid = request.headers.get(self.header_name) or _generate_request_id()
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=rid,
            method=request.method,
            path=request.url.path,
        )
        request.state.request_id = rid
        try:
            response = await call_next(request)
        finally:
            # Outgoing header — istemciye request_id görünmesi için
            pass
        response.headers[self.header_name] = rid
        return response


class AccessLogMiddleware(BaseHTTPMiddleware):
    """Her request için tek satır JSON access log üretir."""

    def __init__(self, app, logger_name: str = "http") -> None:
        super().__init__(app)
        self._logger = structlog.get_logger(logger_name)

    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            duration_ms = int((time.perf_counter() - start) * 1000)
            self._logger.exception(
                "http_request_failed",
                duration_ms=duration_ms,
                method=request.method,
                path=request.url.path,
            )
            raise

        duration_ms = int((time.perf_counter() - start) * 1000)
        self._logger.info(
            "http_request",
            status=response.status_code,
            duration_ms=duration_ms,
            method=request.method,
            path=request.url.path,
        )
        return response
