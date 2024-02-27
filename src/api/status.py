import json
import logging

from fastapi import APIRouter
from fastapi_restful.cbv import cbv
from starlette.responses import JSONResponse


router = APIRouter()


@cbv(router)
class StatusController:
    @router.get("/")
    def get_status(self) -> JSONResponse:
        status_code = 200
        with open(file='alerts.json', mode='r', encoding='utf-8') as fp:
            json_data = json.load(fp)
        if json_data:
            status_code = 418  # TODO: returning I'm a Teapot in case there is an alert
        return JSONResponse(json_data, status_code=status_code)
