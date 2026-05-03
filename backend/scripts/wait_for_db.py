"""DB hazır olana kadar bekle — `docker compose up` lifespan'ından önce çağrılır."""
from __future__ import annotations

import asyncio
import os
import sys
import time

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine


async def main() -> int:
    url = os.environ.get(
        "DATABASE_URL", "postgresql+asyncpg://raw2value:secret@db:5432/raw2value"
    )
    timeout_sec = int(os.environ.get("WAIT_FOR_DB_TIMEOUT", "60"))
    deadline = time.time() + timeout_sec
    last_err: Exception | None = None
    while time.time() < deadline:
        engine = create_async_engine(url, pool_pre_ping=True)
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            await engine.dispose()
            print("db_ready")
            return 0
        except Exception as exc:
            last_err = exc
            await engine.dispose()
            await asyncio.sleep(1)
    print(f"db_not_ready last_error={last_err}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
