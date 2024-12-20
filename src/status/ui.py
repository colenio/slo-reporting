import typing

from fastapi import APIRouter, Depends
from fastapi_restful.cbv import cbv
from starlette.requests import Request
from starlette.responses import HTMLResponse

from config.settings import settings
from status.service import StatusService, get_status_service
from ui.deps import get_templates

router = APIRouter()


@cbv(router)
class StatusPages:
    service: StatusService = Depends(get_status_service)

    @router.get("/", response_class=HTMLResponse)
    @typing.no_type_check
    def get_status(self, request: Request):
        alerts, _ = self.service.get_status()
        config = settings.ui.status
        return get_templates().TemplateResponse(request, name="status.html", context={"alerts": alerts, "config": config})
