from __future__ import annotations

import asyncio

import sentry_sdk
from redis import asyncio as aioredis


def log_exception(task: asyncio.Task):
    try:
        exc = task.exception()
    except asyncio.CancelledError:
        return

    sentry_sdk.capture_exception(exc)
    print(f"An exception occurred {exc}")


async def setup_redis(redis_dsn) -> aioredis.Redis:
    pool = await aioredis.from_url(redis_dsn, decode_responses=True)
    await pool.ping()
    return pool
