from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from ui.deps import UI_ROOT
from ui.home import home_router


def add_ui(app: FastAPI) -> None:
    app.mount("/static", StaticFiles(directory=str(UI_ROOT / "static")), name="static")
    app.include_router(home_router, tags=["home"], include_in_schema=False)
