import random
from datetime import datetime
from typing import List, Optional


class Universal_DB:
    __slots__ = ("cache", "integrity")

    def __init__(self, cache: dict, integrity: datetime) -> None:
        self.cache: dict = cache
        self.integrity: datetime = integrity

    def get_app_names(self) -> List[str]:
        return [app['title'] for app in self.cache]

    def get_app(self, application: str) -> Optional[dict]:
        for app in self.cache:
            if app['title'] == application:
                return app
        return None

    def get_random_app(self) -> dict:
        return random.choice(self.cache)

    @classmethod
    async def from_redis(cls, pool) -> str:
        integrity = await pool.get("udb:integrity")
        cache = await pool.get("udb:cache")
        return cls(cache, integrity)
