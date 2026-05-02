"""Alembic env — async engine üzerinden migration uygular.

`Settings.DATABASE_URL` env'den okunur; CLI'dan override mümkündür
(`alembic -x url=postgresql+asyncpg://... upgrade head`).
"""
from __future__ import annotations

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.config import settings  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.db.models import (  # noqa: E402, F401  (modeller register edilsin)
    AnalysisRecord,
    BuyerProfile,
    Organization,
    ProcessorProfile,
    ProducerProfile,
    User,
)

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _resolve_url() -> str:
    """CLI -x url=... önceliği, sonra Settings."""
    x_args = context.get_x_argument(as_dictionary=True)
    return x_args.get("url") or settings.DATABASE_URL


def run_migrations_offline() -> None:
    """SQL string üretip stdout'a basar (DB'ye bağlanmadan)."""
    context.configure(
        url=_resolve_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    cfg = config.get_section(config.config_ini_section) or {}
    cfg["sqlalchemy.url"] = _resolve_url()
    connectable = async_engine_from_config(
        cfg, prefix="sqlalchemy.", poolclass=pool.NullPool
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
