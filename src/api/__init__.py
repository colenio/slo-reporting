from fastapi import FastAPI

from models.settings import settings

from api.api import api_router


def add_api(app: FastAPI) -> None:
    app.include_router(api_router, prefix=settings.api_base)
