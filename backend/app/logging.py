"""Structlog tabanlı yapısal loglama — JSON veya konsol render.

Kaynak: MASTER_BACKEND_GELISTIRME_RAPORU_PART2.md §14.1.
"""
from __future__ import annotations

import logging
import sys

import structlog


def configure_logging(level: str = "INFO", as_json: bool = True) -> None:
    """Structlog'u tek noktadan yapılandırır.

    Stdlib `logging`'i de sarar; `logging.getLogger()` çıkışları aynı
    formatla akar. Request ID gibi context değişkenleri
    `structlog.contextvars` ile thread-safe propagate edilir.
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(stream=sys.stdout, level=log_level, format="%(message)s")

    timestamper = structlog.processors.TimeStamper(fmt="iso", utc=True)

    shared_processors: list = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        timestamper,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    renderer: structlog.types.Processor
    if as_json:
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=False)

    structlog.configure(
        processors=[*shared_processors, renderer],
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Modüllerin kullanması için bağlı logger döner."""
    return structlog.get_logger(name)
