from typing import Any, Dict, List

import rapidfuzz
from fastapi import APIRouter

from ..request import Request

router = APIRouter(prefix="/v0", tags=['applications', 'v0'])


@router.get("/search/{application}", deprecated=True)
async def search_apps(application: str, request: Request) -> Dict[str, List[Dict[str, Any]]]:
    """Searches for applications."""
    apps = []
    for name, _, _ in rapidfuzz.process.extract_iter(application, request.app.state.cache.get_app_names(),
                                                     score_cutoff=70):
        a = request.app.state.cache.get_app(name)
        apps.append(a)

    return {"results": apps}
