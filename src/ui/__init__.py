from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

import slo.ui
import ui.home
from ui.deps import UI_ROOT


def add_ui(app: FastAPI) -> None:
    app.mount("/static", StaticFiles(directory=str(UI_ROOT / "static")), name="static")
    app.include_router(ui.home.router, include_in_schema=False)
    app.include_router(slo.ui.router, prefix="/slo", include_in_schema=False)
