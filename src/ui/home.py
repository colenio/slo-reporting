import typing

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastapi_restful.cbv import cbv
from starlette.requests import Request
from starlette.responses import RedirectResponse

from config.settings import settings
from ui.deps import get_templates

router = APIRouter()


@cbv(router)
class HomePages:
    @router.get("/", response_class=HTMLResponse)
    @typing.no_type_check
    async def get_home(self) -> RedirectResponse:
        return RedirectResponse("/slo")

    @router.get("/about", response_class=HTMLResponse)
    @typing.no_type_check
    async def get_about(self, request: Request):
        return get_templates().TemplateResponse(request, "about.html", {"settings": settings, "config": settings.ui.about})
