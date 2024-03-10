import typing

from fastapi import APIRouter, Depends
from fastapi_restful.cbv import cbv
from starlette.requests import Request
from starlette.responses import HTMLResponse

from slo.deps import get_slo_service
from slo.service import SloService
from ui.deps import TEMPLATES

router = APIRouter()


@cbv(router)
class SloPages:
    service: SloService = Depends(get_slo_service)

    @router.get("/", response_class=HTMLResponse)
    @typing.no_type_check
    async def get_slo(self, request: Request):
        slo = self.service.get_slo_values()
        return TEMPLATES.TemplateResponse(request, "slo.html", {"slo": slo})
