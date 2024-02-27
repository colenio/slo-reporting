from typing import List

import uvicorn
from fastapi import FastAPI, APIRouter
from fastapi_restful.tasks import repeat_every

from api import config, slo, status
from models.settings import settings
from monitors.aggregate import AggregateMonitor
from monitors.alertmanager import AlertManagerMonitor
from monitors.azure import AzureMonitor
from monitors.models import Monitor
from monitors.prometheus import PrometheusMonitor
from observability import add_observability
from ui import add_ui


def add_api(the_app: FastAPI) -> None:
    api_router = APIRouter()
    api_router.include_router(config.router, prefix="/config", tags=["config"])
    if settings.metrics.enabled:
        api_router.include_router(slo.router, prefix="/slo", tags=["slo"])
    if settings.status.enabled:
        api_router.include_router(status.router, prefix="/status", tags=["status"])
    the_app.include_router(api_router, prefix=settings.api_base)


def create_app() -> FastAPI:
    the_app = FastAPI(title=settings.project, openapi_url=f"{settings.api_base}/openapi.json")
    add_observability(the_app)
    add_api(the_app)
    add_ui(the_app)
    return the_app


app = create_app()

if __name__ == "__main__":
    if settings.status.enabled:
        mon = settings.status.monitors
        monitors: List[Monitor] = [AzureMonitor.of(m) for m in mon.azure]
        monitors += [PrometheusMonitor.of(m) for m in mon.prometheus]
        monitors += [AlertManagerMonitor.of(m) for m in mon.alertmanager]
        monitor = AggregateMonitor(monitors)


        @app.on_event("startup")
        @repeat_every(seconds=settings.status.interval.total_seconds())
        def scrape_status() -> None:
            monitor.scrape()

    uvicorn.run(app, host='0.0.0.0', port=8000)
