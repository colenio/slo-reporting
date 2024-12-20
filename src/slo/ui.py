import typing

from fastapi import APIRouter, Depends
from fastapi_restful.cbv import cbv
from starlette.requests import Request
from starlette.responses import HTMLResponse

from config.settings import settings
from slo.service import SloService, get_slo_service
from ui.deps import get_templates

router = APIRouter()


@cbv(router)
class SloPages:
    service: SloService = Depends(get_slo_service)

    @router.get("/", response_class=HTMLResponse)
    @typing.no_type_check
    async def get_slo(self, request: Request):
        slo = self.service.get_slo_values()
        config = settings.ui.slo
        return get_templates().TemplateResponse(request, name="slo.html", context={"slo": slo, "config": config})
