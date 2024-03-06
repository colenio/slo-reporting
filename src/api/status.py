import json

from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi_restful.cbv import cbv
from starlette.responses import JSONResponse

from models.settings import settings

router = APIRouter()


@cbv(router)
class StatusController:
    status = settings.status

    @router.get("/")
    def get_status(self) -> JSONResponse:
        status_code = 200
        json_data = []
        if self.status.path.exists():
            with open(file=self.status.path, mode='r', encoding='utf-8') as fp:
                json_data = json.load(fp)
        if json_data:
            status_code = self.status.code
        return JSONResponse(content=jsonable_encoder(json_data), status_code=status_code)
