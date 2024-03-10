from datetime import timedelta
from pathlib import Path
from typing import List

from pydantic import BaseModel, Field

from config import PROJECT_ROOT
from status.monitors.alertmanager import AlertManagerConfig
from status.monitors.azure import AzureMonitorConfig
from status.monitors.prometheus import PrometheusMonitorConfig


class Monitors(BaseModel):
    azure: List[AzureMonitorConfig] = []
    prometheus: List[PrometheusMonitorConfig] = []
    alertmanager: List[AlertManagerConfig] = []


class Status(BaseModel):
    enabled: bool = True
    monitors: Monitors = Monitors()
    interval: timedelta = Field(default=timedelta(minutes=1), description="Scrape interval")
    code: int = 418  # I'm a teapot

    @property
    def path(self) -> Path:
        return Path(PROJECT_ROOT / "data" / "alerts.json").resolve().absolute()
