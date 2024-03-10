from typing import Dict

import json_logging
from fastapi import FastAPI
from fastapi_health import health
from starlette_exporter import PrometheusMiddleware, handle_metrics

from config.settings import settings


def is_healthy() -> Dict[str, str]:
    return {"status": "UP"}


def add_health(app: FastAPI) -> None:
    app.add_api_route("/health", health([is_healthy]))


def add_logging(app: FastAPI) -> None:
    enable_json = json_logging.ENABLE_JSON_LOGGING
    if not enable_json:
        return
    json_logging.init_fastapi(enable_json=True)
    json_logging.init_request_instrument(app)


def add_metrics(app: FastAPI) -> None:
    # https://github.com/stephenhillier/starlette_exporter?tab=readme-ov-file#options
    app.add_middleware(PrometheusMiddleware, group_paths=True, app_name=settings.project, prefix="http", skip_paths=[],
                       filter_unhandled_paths=True, )
    app.add_route("/metrics", handle_metrics)


def add_observability(app: FastAPI) -> None:
    add_health(app)
    add_logging(app)
    add_metrics(app)
