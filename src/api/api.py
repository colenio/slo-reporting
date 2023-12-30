from fastapi import APIRouter

from api import config, slo

api_router = APIRouter()
api_router.include_router(config.router, prefix="/config", tags=["config"])
api_router.include_router(slo.router, prefix="/slo", tags=["slo"])