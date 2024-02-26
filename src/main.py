from datetime import timedelta
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler

from api import add_api
from models.settings import settings
from monitors.orchestrator import AggregateMonitor
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


# TODO: check if there's a supertype which might be returned
def create_querier_scheduler(querierOrchestrator: AggregateMonitor,interval: timedelta) -> BackgroundScheduler:
    scheduler = BackgroundScheduler()

    # NOTE: timedelta and APScheduler support different time-units...
    scheduler.add_job(querierOrchestrator.execute, 'interval',days=interval.days, seconds=interval.seconds)

    return scheduler


app = create_app()
querierOrchestrator = AggregateMonitor(settings.status.monitors)
scheduler = create_querier_scheduler(querierOrchestrator, settings.status.interval)

if __name__ == "__main__":
    scheduler.start()
    uvicorn.run(app, host='0.0.0.0', port=8000)
