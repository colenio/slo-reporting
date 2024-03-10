import typing

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastapi_restful.cbv import cbv
from starlette.requests import Request

from config.settings import settings
from ui.deps import TEMPLATES

router = APIRouter()


@cbv(router)
class HomePages:
    @router.get("/", response_class=HTMLResponse)
    @typing.no_type_check
    async def get_home(self, request: Request):
        return TEMPLATES.TemplateResponse(request, "index.html")

    @router.get("/about", response_class=HTMLResponse)
    @typing.no_type_check
    async def get_about(self, request: Request):
        return TEMPLATES.TemplateResponse(request, "about.html", {"settings": settings})
