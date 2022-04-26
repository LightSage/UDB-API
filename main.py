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
from __future__ import annotations

import asyncio
import random
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import aiohttp
import psutil
import rapidfuzz.fuzz
import rapidfuzz.process
import sentry_sdk
from fastapi import FastAPI, HTTPException
from jinja2 import Environment, FileSystemLoader
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from starlette.responses import HTMLResponse

import config

try:
    import uvloop
except ModuleNotFoundError:
    pass
else:
    uvloop.install()


app = FastAPI(title="UDB API", version="0.4.0")
process = psutil.Process()
jinja_env = Environment(loader=FileSystemLoader('templates'), enable_async=True)
# Sentry.io
sentry_sdk.init(config.sentry_dsn, traces_sample_rate=config.samples_rate)
app.add_middleware(SentryAsgiMiddleware)
# constants
CUTOFF_SCORE = 70


class Universal_DB:
    __slots__ = ("cache", "integrity")

    def __init__(self, cache: Dict[str, Any]) -> None:
        self.cache: Dict[str, Any] = cache
        self.integrity: datetime = datetime.now(timezone.utc)

    def get_app_names(self) -> List[str]:
        return [app['title'] for app in self.cache]

    def get_app(self, application) -> Optional[Dict[str, Any]]:
        for app in self.cache:
            if app['title'] == application:
                return app
        return None

    def get_random_app(self) -> Dict[str, Any]:
        return random.choice(self.cache)


async def udb_cache_loop():
    while True:
        async with app.state.session.get("https://db.universal-team.net/data/full.json") as resp:
            r = await resp.json()

        app.state.cache = Universal_DB(r)
        await asyncio.sleep(600)


def _log_exception(task):
    try:
        exc = task.exception()
    except asyncio.CancelledError:
        return

    sentry_sdk.capture_exception(exc)
    print(f"An exception occurred {exc}")


@app.on_event("startup")
async def on_startup():
    app.state.session = aiohttp.ClientSession(headers={"User-Agent": "UDB-API v0.2.0/https://github.com/LightSage/UDB-API"})
    # TODO: Make this refresh on a request to a /refresh endpoint
    task = asyncio.create_task(udb_cache_loop())
    task.add_done_callback(_log_exception)


@app.on_event("shutdown")
async def on_shutdown():
    await app.state.session.close()


@app.get("/search/{application}")
async def search_apps(application: str) -> Dict[str, list]:
    """Searches for applications."""
    apps = []
    all_apps: List[str] = app.state.cache.get_app_names()
    all_apps.sort(key=len)
    for name, _, _ in rapidfuzz.process.extract_iter(application, all_apps, scorer=rapidfuzz.fuzz.QRatio,
                                                     score_cutoff=65):
        a = app.state.cache.get_app(name)
        apps.append(a)

    return {"results": apps}


@app.get("/lsearch/{application}")
async def lsearch_apps(application: str) -> Dict[str, list]:
    """Legacy search endpoint.

    Searches for applications."""
    apps = []
    for name, _, _ in rapidfuzz.process.extract_iter(application, app.state.cache.get_app_names(),
                                                     score_cutoff=CUTOFF_SCORE):
        a = app.state.cache.get_app(name)
        apps.append(a)

    return {"results": apps}


@app.get("/get/{application}")
async def get_app(application: str):
    """Gets an application.

    WARNING: This route will not fuzzy search like /search does."""
    a = app.state.cache.get_app(application)

    if a is None:
        raise HTTPException(status_code=404, detail="Application not found")

    return a


@app.get("/random")
async def get_random_app(limit: Optional[int] = None):
    """Gets a random application"""
    limit = limit or 1

    if limit > len(app.state.cache.cache):
        raise HTTPException(400, "Limit is too high.")

    apps = []
    for _ in range(limit):
        # TODO: Unique only
        appl = app.state.cache.get_random_app()
        apps.append(appl)

    return apps


@app.get("/all")
async def get_raw_cache():
    """Gets all applications that are cached"""
    return app.state.cache.cache


@app.get("/stats")
async def get_stats():
    mem = process.memory_full_info().uss / 1024**2
    return {"memory": f"{mem:.2f}", "cached_applications": len(app.state.cache.cache),
            "last_update": app.state.cache.integrity.isoformat()}


@app.get("/", include_in_schema=False)
async def home():
    tmpl = jinja_env.get_template("home.html")
    stats = await get_stats()
    rendered = await tmpl.render_async(usage=stats['memory'])
    return HTMLResponse(rendered)
