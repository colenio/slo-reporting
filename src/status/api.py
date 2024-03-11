from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi_restful.cbv import cbv
from starlette.responses import JSONResponse

from status.service import StatusService, get_status_service

router = APIRouter()


@cbv(router)
class StatusController:
    service: StatusService = Depends(get_status_service)

    @router.get("/")
    def get_status(self, update: bool = False) -> JSONResponse:
        alerts, status_code = self.service.get_status(update)
        return JSONResponse(content=jsonable_encoder(alerts), status_code=status_code)
