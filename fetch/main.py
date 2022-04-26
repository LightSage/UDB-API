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
from datetime import datetime, timezone

import aiohttp
import aioredis

import config


async def main():
    redis = await aioredis.from_url(config.REDIS)
    async with aiohttp.ClientSession() as session:
        async with session.get("https://db.universal-team.net/data/full.json") as resp:
            r = await resp.json()

    await redis.set("udb:cache", json.dumps(r))
    await redis.set("udb:integrity", datetime.now(timezone.utc).isoformat())


if __name__ == "__main__":
    asyncio.run(main())