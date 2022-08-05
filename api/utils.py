from __future__ import annotations

import asyncio

import aioredis
import sentry_sdk

import config


def log_exception(task: asyncio.Task):
    try:
        exc = task.exception()
    except asyncio.CancelledError:
        return

    sentry_sdk.capture_exception(exc)
    print(f"An exception occurred {exc}")


async def setup_redis() -> aioredis.Redis:
    pool = await aioredis.from_url(config.REDIS)
    await pool.ping()
    return pool
