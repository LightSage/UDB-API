from __future__ import annotations

import json
from datetime import datetime
from functools import cached_property
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, Union

from pydantic import AnyUrl, BaseModel, Field
from redis import asyncio as aioredis
from typing_extensions import TypedDict

if TYPE_CHECKING:
    from typing_extensions import Self


App = Dict[str, Any]


class Universal_DB:
    __slots__ = ("_cache", "integrity")

    def __init__(self, cache: List[App], integrity: datetime) -> None:
        self._cache: List[App] = cache
        self.integrity: datetime = integrity

    @cached_property
    def get_app_names(self) -> List[str]:
        return [app['title'] for app in self._cache]

    def get_app(self, application: str) -> Optional[App]:
        for app in self._cache:
            if app['title'] == application:
                return app
        return None

    def get_apps_by_system(self, system: str):
        system = system.upper()
        return [app for app in self._cache if system in app["systems"]]

    @property
    def all_applications(self):
        return self._cache

    @classmethod
    async def from_redis(cls, pool: aioredis.Redis) -> Self:
        integrity = await pool.get("udb:integrity")
        cache = await pool.get("udb:cache")
        cache = json.loads(cache)
        return cls(cache, datetime.fromisoformat(integrity))


class BitbucketSource(BaseModel):
    branch: str
    repo: str


class NightlyApplicationDownload(TypedDict):
    url: AnyUrl


class NightlyApplication(BaseModel):
    download_page: Optional[str] = None
    downloads: Optional[Dict[str, NightlyApplicationDownload]] = None
    qr: Optional[Dict[str, str]] = None


class ScriptMessage(BaseModel):
    at: str
    count: int
    for_: str = Field(..., alias='for')
    message: str


class PreReleaseApplication(BaseModel):
    download_page: str
    downloads: ApplicationDownload
    qr: Optional[Dict[str, str]] = None
    update_notes: Optional[str] = None
    update_notes_md: Optional[str] = None
    updated: str
    version: str
    version_title: Optional[str] = None


class ApplicationDownloadInner(BaseModel):
    size: Optional[int] = None
    size_str: Optional[str] = None
    url: AnyUrl


ApplicationDownload = Dict[str, Optional[ApplicationDownloadInner]]


class ApplicationScreenshot(TypedDict):
    description: str
    url: str


class ApplicationScript(BaseModel):
    type: str
    directory: Optional[str] = None
    file: Optional[str] = None
    input: Optional[str] = None
    output: Optional[str] = None


class NightlyApplicationScript(BaseModel):
    script: List[ApplicationScript]
    type: str


class SizeableApplicationScript(BaseModel):
    script: List[ApplicationScript]
    size: str


class Application(BaseModel):
    # Based on genson & datamodel-code-gen
    author: str
    avatar: Optional[AnyUrl] = None
    categories: List[str]
    color: Optional[str] = None
    color_bg: Optional[str] = None
    created: Optional[datetime] = None
    description: Optional[str] = None
    download_page: Optional[str] = None
    downloads: Optional[ApplicationDownload] = None
    github: Optional[str] = None
    icon: Optional[AnyUrl] = None
    icon_index: Optional[int] = None
    image: Optional[AnyUrl] = None
    image_length: Optional[int] = None
    license: Optional[str] = None
    license_name: Optional[str] = None
    long_description: Optional[str] = None
    priority: bool
    scripts: Optional[Dict[str, Union[List[ApplicationScript], NightlyApplicationScript, SizeableApplicationScript]]] = None
    slug: str
    source: Optional[AnyUrl] = None
    systems: List[Literal['3DS', 'DS']]
    title: str
    unique_ids: Optional[List[int]] = None
    update_notes: Optional[str] = None
    update_notes_md: Optional[str] = None
    updated: Optional[datetime] = None
    urls: List[AnyUrl]
    version: Optional[str] = None
    version_title: Optional[str] = None
    qr: Optional[Dict[str, AnyUrl]] = None
    prerelease: Optional[PreReleaseApplication] = None
    archive: Optional[Dict[str, Any]] = None
    autogen_scripts: Optional[bool] = None
    download_filter: Optional[str] = None
    screenshots: Optional[List[ApplicationScreenshot]] = None
    unistore_exclude: Optional[bool] = None
    website: Optional[str] = None
    script_message: Optional[Union[str, ScriptMessage]] = None
    wiki: Optional[AnyUrl] = None
    gitlab: Optional[str] = None
    gbatemp: Optional[str] = None
    icon_static: Optional[AnyUrl] = None
    bitbucket: Optional[BitbucketSource] = None
    nightly: Optional[NightlyApplication] = None
    eval_notes_md: Optional[bool] = None
