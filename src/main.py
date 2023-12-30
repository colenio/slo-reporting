import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import add_api
from models.settings import settings
from observability import add_observability
from ui import add_ui


def create_app() -> FastAPI:
    the_app = FastAPI(title=settings.project, openapi_url=f"{settings.api_base}/openapi.json")
    add_observability(the_app)
    add_api(the_app)
    the_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    add_ui(the_app)
    return the_app


app = create_app()

if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8000)
