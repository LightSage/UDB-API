"""
Copyright 2021 LightSage

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
import random
from dataclasses import dataclass
from typing import Dict, Optional

import aiohttp
import psutil
import sentry_sdk
from fastapi import FastAPI, HTTPException
from jinja2 import Environment, FileSystemLoader
from rapidfuzz import process as fwprocess
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from starlette.responses import HTMLResponse

import config

try:
    import uvloop
except ModuleNotFoundError:
    pass
else:
    uvloop.install()


app = FastAPI(title="UDB API", version="0.2.0")
process = psutil.Process()
jinja_env = Environment(loader=FileSystemLoader('templates'), enable_async=True)
# Sentry.io
sentry_sdk.init(config.sentry_dsn, traces_sample_rate=config.samples_rate)
app.add_middleware(SentryAsgiMiddleware)
# constants
CUTOFF_SCORE = 70


@dataclass
class Universal_DB:
    cache: dict

    def get_app_names(self) -> list:
        apps = []
        for app in self.cache:
            apps.append(app['title'])
        return apps

    def get_app(self, application) -> Optional[dict]:
        for app in self.cache:
            if app['title'] == application:
                return app
        return None

    def get_random_app(self) -> dict:
        choice = random.choice(self.cache)
        return choice


async def udb_cache_loop():
    while True:
        url = "https://raw.githubusercontent.com/Universal-Team/db/master/docs/data/full.json"
        resp = await app.state.session.get(url)
        r = json.loads(await resp.text())
        app.state.cache = Universal_DB(r)
        await asyncio.sleep(600)


@app.on_event("startup")
async def on_startup():
    app.state.session = aiohttp.ClientSession(headers={"User-Agent": "UDB-API v0.2.0/https://github.com/LightSage/UDB-API"})
    loop = asyncio.get_running_loop()
    # TODO: Make this refresh on a request to a /refresh endpoint
    loop.create_task(udb_cache_loop())


@app.on_event("shutdown")
async def on_shutdown():
    await app.state.session.close()


@app.get("/search/{application}")
async def search_apps(application: str) -> Dict[str, list]:
    """Searches for applications."""
    results = fwprocess.extract(application, app.state.cache.get_app_names())
    apps = []
    for name, score, _ in results:
        # Why waste a lookup
        if score < CUTOFF_SCORE:
            continue

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
    for i in range(limit):
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
    return {"memory": f"{mem:.2f}", "cached_applications": len(app.state.cache.cache)}


@app.get("/", include_in_schema=False)
async def home():
    tmpl = jinja_env.get_template("home.html")
    stats = await get_stats()
    rendered = await tmpl.render_async(usage=stats['memory'])
    return HTMLResponse(rendered)
