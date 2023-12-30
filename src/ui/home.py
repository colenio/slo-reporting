import typing

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from starlette.requests import Request

from models.settings import settings
from ui.deps import TEMPLATES

home_router = APIRouter()


@home_router.get("/", response_class=HTMLResponse)
@typing.no_type_check
async def get_home(request: Request):
    return TEMPLATES.TemplateResponse("index.html", {"request": request})


@home_router.get("/about", response_class=HTMLResponse)
@typing.no_type_check
async def get_about(request: Request):
    return TEMPLATES.TemplateResponse("about.html", {"request": request, "settings": settings})
