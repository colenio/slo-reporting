from fastapi import APIRouter

from api import config, slo, systems_health

api_router = APIRouter()
api_router.include_router(config.router, prefix="/config", tags=["config"])
api_router.include_router(slo.router, prefix="/slo", tags=["slo"])
api_router.include_router(systems_health.router, prefix="/systems-health", tags=["monitoring"])

