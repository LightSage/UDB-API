from __future__ import annotations

import json
import random
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional

import aioredis

if TYPE_CHECKING:
    from typing_extensions import Self


App = Dict[str, Any]


class Universal_DB:
    __slots__ = ("cache", "integrity")

    def __init__(self, cache: List[App], integrity: datetime) -> None:
        self.cache: List[App] = cache
        self.integrity: datetime = integrity

    def get_app_names(self) -> List[str]:
        return [app['title'] for app in self.cache]

    def get_app(self, application: str) -> Optional[App]:
        for app in self.cache:
            if app['title'] == application:
                return app
        return None

    def get_random_app(self) -> App:
        return random.choice(self.cache)

    @classmethod
    async def from_redis(cls, pool: aioredis.Redis) -> Self:
        integrity = await pool.get("udb:integrity")
        cache = await pool.get("udb:cache")
        cache = json.loads(cache)
        return cls(cache, datetime.fromisoformat(integrity))
