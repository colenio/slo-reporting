import json
from typing import Dict

from fastapi import APIRouter
from fastapi_restful.cbv import cbv

from models.settings import settings

router = APIRouter()


@cbv(router)
class ConfigController:
    @router.get("/")
    def get_config(self) -> Dict:
        all_settings = [settings]
        return {s.__class__.__name__: json.loads(s.model_dump_json(by_alias=True)) for s in all_settings}



