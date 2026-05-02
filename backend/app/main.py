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
from .api import health
from .config import settings
from .core.middleware import AccessLogMiddleware, RequestIdMiddleware
from .exceptions import register_exception_handlers
from .logging import configure_logging, get_logger

configure_logging(level=settings.LOG_LEVEL, as_json=(settings.LOG_FORMAT == "json"))
logger = get_logger("app")


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Startup/shutdown hook'u — DB/Redis/ML init ileride eklenecek."""
    logger.info("app_starting", env=settings.APP_ENV, version=__version__)
    yield
    logger.info("app_stopping")


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
