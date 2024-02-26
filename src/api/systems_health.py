import json

from fastapi import APIRouter
from fastapi_restful.cbv import cbv
from starlette.responses import JSONResponse


router = APIRouter()


@cbv(router)
class SystemsHealthController:
    @router.get("/")
    def get_systems_health(self) -> JSONResponse:
        statusCode = 200
        jsonData = []

        with open('alerts.json', 'r') as fp:
            jsonData = json.load(fp)

        if (len(jsonData) > 0):
            statusCode = 418  # TODO: returning I'm a Teapot in case there is an alert

        print(len(jsonData))
        
        response = JSONResponse(jsonData, status_code=statusCode)
        return response
