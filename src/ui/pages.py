import typing

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastapi_restful.cbv import cbv
from starlette.requests import Request

from models.settings import settings
from ui.deps import TEMPLATES

pages_router = APIRouter()

@cbv(pages_router)
class UiPages:
    @pages_router.get("/", response_class=HTMLResponse)
    @typing.no_type_check
    async def get_home(self, request: Request):
        return TEMPLATES.TemplateResponse("index.html", {"request": request})

    @pages_router.get("/about", response_class=HTMLResponse)
    @typing.no_type_check
    async def get_about(self, request: Request):
        return TEMPLATES.TemplateResponse("about.html", {"request": request, "settings": settings})

    @pages_router.get("/slo", response_class=HTMLResponse)
    @typing.no_type_check
    async def get_slo(self, request: Request):
        # TODO
        return TEMPLATES.TemplateResponse("slo.html", {"request": request})
