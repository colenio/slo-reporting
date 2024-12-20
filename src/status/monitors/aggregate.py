from typing import List

from pydantic import TypeAdapter

from config.settings import settings
from status.config import Monitors
from status.monitors.alertmanager import AlertManagerMonitor
from status.monitors.azure import AzureMonitor
from status.monitors.models import Monitor, Alert
from status.monitors.prometheus import PrometheusMonitor


class AggregateMonitor(Monitor):
    path = settings.status.path

    def __init__(self, monitors: List[Monitor]) -> None:
        super().__init__('aggregate')
        self.monitors = monitors
        self.adapter = TypeAdapter(List[Alert])

    def scrape(self) -> List[Alert]:
        alerts: List[Alert] = []
        for monitor in self.monitors:
            alerts += monitor.scrape()
        return alerts

    @staticmethod
    def of_monitors(mon: Monitors) -> 'AggregateMonitor':
        monitors: List[Monitor] = [AzureMonitor.of(m) for m in mon.azure]
        monitors += [PrometheusMonitor.of(m) for m in mon.prometheus]
        monitors += [AlertManagerMonitor.of(m) for m in mon.alertmanager]
        return AggregateMonitor(monitors)
