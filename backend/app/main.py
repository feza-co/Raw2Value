"""Raw2Value AI backend FastAPI uygulamasının giriş noktası.

ADIM 1: config + logging + middleware + exception handler + /health.
DB, Redis, ML lifespan ve diğer router'lar sonraki adımlarda eklenir.
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from pathlib import Path

from fastapi.staticfiles import StaticFiles

from . import __version__
from .api import (
    analyze,
    auth,
    evidence,
    files as files_router,
    fx,
    health,
    history as history_router,
    organizations,
    processors,
    whatif,
)
from .config import settings
from .core.cache import close_redis
from .core.middleware import AccessLogMiddleware, RequestIdMiddleware
from .core.rate_limit import limiter
from .core.security_headers import SecurityHeadersMiddleware
from .exceptions import register_exception_handlers
from .logging import configure_logging, get_logger
from .services.ml_service import warmup_ml

configure_logging(level=settings.LOG_LEVEL, as_json=(settings.LOG_FORMAT == "json"))
logger = get_logger("app")


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Startup/shutdown — ML warmup + Redis cleanup."""
    logger.info("app_starting", env=settings.APP_ENV, version=__version__)
    if settings.ML_WARMUP_ON_STARTUP:
        await warmup_ml()
    try:
        yield
    finally:
        logger.info("app_stopping")
        await close_redis()


app = FastAPI(
    title="Raw2Value AI",
    version=__version__,
    lifespan=lifespan,
    default_response_class=ORJSONResponse,
)

# Slowapi state binding'i — limiter decorator'larının çalışması için zorunlu.
app.state.limiter = limiter


async def _rate_limit_handler(request, exc: RateLimitExceeded):
    from .exceptions import _problem_details

    return _problem_details(
        request=request,
        status_code=429,
        code="rate_limited",
        title="Too Many Requests",
        detail=str(exc.detail) if exc.detail else "Rate limit exceeded",
    )


app.add_exception_handler(RateLimitExceeded, _rate_limit_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# AccessLog en dışta — RequestId tarafından bind edilen context'i kullanmalı.
# Starlette middleware execution order: en son eklenen önce çalışır.
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(AccessLogMiddleware)
app.add_middleware(RequestIdMiddleware)
app.add_middleware(SlowAPIMiddleware)

register_exception_handlers(app)

if settings.PROMETHEUS_ENABLED:
    Instrumentator().instrument(app).expose(
        app, endpoint="/metrics", include_in_schema=False
    )

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(fx.router)
app.include_router(evidence.router)
app.include_router(analyze.router)
app.include_router(whatif.router)
app.include_router(processors.router)
app.include_router(organizations.router)
app.include_router(history_router.router)
app.include_router(files_router.router)

# Static dosyalar — local FS upload backend için public URL.
_uploads_dir = Path(settings.UPLOAD_DIR).resolve()
_uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount(
    "/static/uploads",
    StaticFiles(directory=str(_uploads_dir)),
    name="uploads",
)
