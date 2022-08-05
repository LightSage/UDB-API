from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import Request as _Request

if TYPE_CHECKING:
    from .app import App


class Request(_Request):
    app: App
