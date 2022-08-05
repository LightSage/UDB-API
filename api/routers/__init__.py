from fastapi import FastAPI

from . import admin, apps, v0


def add_routers(app: FastAPI):
    app.include_router(apps.router)
    app.include_router(admin.router)
    app.include_router(v0.router)
