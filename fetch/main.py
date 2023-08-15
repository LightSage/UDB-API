"""
Copyright 2021-2022 LightSage

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import asyncio
import json
import os.path
from datetime import datetime, timezone

import aiohttp
from redis import asyncio as aioredis
import sentry_sdk


async def actual_work(redis_dsn: str):
    redis = await aioredis.from_url(redis_dsn)
    async with aiohttp.ClientSession() as session:
        async with session.get("https://db.universal-team.net/data/full.json") as resp:
            r = await resp.json()

    await redis.set("udb:cache", json.dumps(r))
    await redis.set("udb:integrity", datetime.now(timezone.utc).isoformat())


async def main():
    with open("config.json") as fp:
        config = json.load(fp)

    sentry_sdk.init(config['SENTRY_DSN'])

    if not os.path.exists("/.dockerenv"):
        await actual_work(config['REDIS'])
        return

    while True:

        try:
            await actual_work(config['REDIS'])
        except Exception as exc:
            sentry_sdk.capture_exception(exc)
            exit(1)

        await asyncio.sleep(600)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        exit(0)