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

from . import __version__
from .api import analyze, auth, evidence, fx, health, processors, whatif
from .config import settings
from .core.cache import close_redis
from .services.ml_service import warmup_ml
from .core.middleware import AccessLogMiddleware, RequestIdMiddleware
from .exceptions import register_exception_handlers
from .logging import configure_logging, get_logger

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# AccessLog en dışta — RequestId tarafından bind edilen context'i kullanmalı.
# Starlette middleware execution order: en son eklenen önce çalışır.
app.add_middleware(AccessLogMiddleware)
app.add_middleware(RequestIdMiddleware)

register_exception_handlers(app)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(fx.router)
app.include_router(evidence.router)
app.include_router(analyze.router)
app.include_router(whatif.router)
app.include_router(processors.router)
