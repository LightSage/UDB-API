import aioredis

import config


async def setup_redis() -> aioredis.Redis:
    pool = await aioredis.from_url(config.REDIS)
    await pool.ping()
    return pool
