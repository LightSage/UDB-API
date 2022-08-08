import psutil
from fastapi import APIRouter

from ..request import Request

process = psutil.Process()
router = APIRouter(tags=['admin'])


@router.get("/stats")
async def get_stats(request: Request):
    integrity = await request.app.redis.get("udb:integrity")
    mem = process.memory_full_info().uss / 1024**2
    return {"memory": f"{mem:.2f}", "cached_applications": len(request.app.state.cache.cache),
            "last_update": integrity}
