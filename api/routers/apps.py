"""
Copyright 2021-2024 LightSage

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
import random
from typing import Any, Dict, List, Optional, Literal

import rapidfuzz
from fastapi import APIRouter, HTTPException

from ..request import Request

router = APIRouter(tags=['applications'])


@router.get("/search/{application}")
async def search_apps(application: str,
                      request: Request,
                      system: Optional[Literal['3ds', 'ds']] = None) -> Dict[str, List[Dict[str, Any]]]:
    """Searches for applications with optional filter query params"""
    apps = []
    if system:
        sys_apps = request.app.state.cache.get_apps_by_system(system)
        all_apps = [app['title'] for app in sys_apps]
    else:
        all_apps: List[str] = request.app.state.cache.get_app_names()

    all_apps.sort(key=len)
    for name, _, _ in rapidfuzz.process.extract(application, all_apps, scorer=rapidfuzz.fuzz.QRatio,
                                                score_cutoff=50):
        a = request.app.state.cache.get_app(name)
        apps.append(a)

    return {"results": apps}


@router.get("/get/{application}", deprecated=True)
async def get_app(application: str, request: Request):
    """Gets an application.

    WARNING: This route will not fuzzy search like /search does."""
    a = request.app.state.cache.get_app(application)

    if a is None:
        raise HTTPException(status_code=404, detail="Application not found")

    return a


@router.get("/random")
async def get_random_app(request: Request,
                         limit: Optional[int] = None,
                         system: Optional[Literal['3ds', 'ds']] = None):
    """Gets a random application with optional filter query params"""
    limit = limit or 1

    if system:
        all_apps = request.app.state.cache.get_apps_by_system(system)
    else:
        all_apps = request.app.state.cache.all_applications

    if limit > len(all_apps):
        raise HTTPException(400, "Limit is too high.")

    apps = []
    for _ in range(limit):
        # TODO: Unique only
        appl = random.choice(all_apps)
        apps.append(appl)

    return apps


@router.get("/all")
async def get_all_apps(request: Request):
    """Gets all applications that are cached"""
    return request.app.state.cache.all_applications
