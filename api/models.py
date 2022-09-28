from __future__ import annotations

import json
import random
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, TypedDict

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


class Application(TypedDict):
    # This is kinda a guess, hopefully it's right.
    updated: Optional[str]
    categories: Optional[List[str]]
    image: Optional[str]
    # keys I can (hopefully) be certain on existing and being the correct type
    title: str
    author: str
    avatar: str
    version: str
    systems: List[Literal['3DS', 'DS']]
    downloads: Dict[str, ApplicationDownload]
    created: str
    screenshots: Optional[List[ApplicationScreenshot]]
    scripts: Optional[Dict[str, ApplicationScript]]
    priority: Optional[bool]
    license: Optional[str]
    # Guessing at this point, kms
    # Icons????
    icon: str
    icon_index: int
    # IDK
    description: Optional[str]
    # colors
    color: str
    color_bg: str
    # update notes
    update_notes: str
    update_notes_md: str
    # urls
    urls: List[str]



class ApplicationDownload(TypedDict):
    size: int
    size_str: str
    url: str


class ApplicationScreenshot(TypedDict):
    description: str
    url: str


class ApplicationScript(TypedDict):
    type: str
    directory: Optional[str]
    file: Optional[str]
    input: Optional[str]
    output: Optional[str]

