import uvicorn
from fastapi import FastAPI, APIRouter
from fastapi_restful.tasks import repeat_every
from starlette.staticfiles import StaticFiles

from config.api import router as config_api_router
from config.settings import settings
from observability import add_observability
from slo.api import router as slo_api_router
from slo.ui import router as slo_router
from status.api import router as status_api_router
from status.ui import router as status_router
from status.service import get_status_service
from ui.deps import UI_ROOT, get_templates
from ui.home import router as home_router


def add_api(the_app: FastAPI) -> None:
    api_router = APIRouter()
    api_router.include_router(config_api_router, prefix="/config", tags=["config"])
    if settings.metrics.enabled:
        api_router.include_router(slo_api_router, prefix="/slo", tags=["slo"])
    if settings.status.enabled:
        api_router.include_router(status_api_router, prefix="/status", tags=["status"])
    the_app.include_router(api_router, prefix=settings.api_base)


def add_ui(the_app: FastAPI) -> None:
    the_app.mount("/static", StaticFiles(directory=str(UI_ROOT / "static")), name="static")
    get_templates().env.globals.update(icons=settings.ui.icons.model_dump())
    the_app.include_router(home_router, include_in_schema=False)
    the_app.include_router(slo_router, prefix="/slo", include_in_schema=False)
    the_app.include_router(status_router, prefix="/status", include_in_schema=False)


def create_app() -> FastAPI:
    the_app = FastAPI(title=settings.project, openapi_url=f"{settings.api_base}/openapi.json")
    add_observability(the_app)
    add_api(the_app)
    add_ui(the_app)
    return the_app


app = create_app()

if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8000)
